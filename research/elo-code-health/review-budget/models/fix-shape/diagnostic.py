#!/usr/bin/env python3
"""One frozen, post-hoc fix-shape diagnostic. No external validation or policy."""
from collections import defaultdict
from dataclasses import replace
import hashlib
import json
import math
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from forecast import (allocation, brier, choose_config, fit_predict, grouped_folds,
                      observations)

HERE = Path(__file__).resolve().parent
MODELS = ('pooled', 'lag_bucket', 'lag_logistic', 'augmented_logistic')


def count(value):
    """Unknown stays absent; Boolean counts and nonfinite numbers are invalid."""
    return (float(value) if isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value) and value >= 0 else None)


def snapshot_values(snapshot: dict | None) -> tuple[float, ...]:
    """CLAIM(snapshot-missing): observed zero and missing differ [test_diagnostic]."""
    features = (snapshot or {}).get('features') or {}
    if features.get('status') != 'observed':
        return (0.0,) * 5 + (1.0,) * 5
    source = count(features.get('source_changed_lines'))
    files = count(features.get('source_files'))
    tests = count(features.get('test_changed_lines'))
    state = count(features.get('state_path_files'))
    same = features.get('same_snapshot')
    known_same = type(same) is bool
    values = [min(math.log1p(source) / math.log1p(10000), 1) if source is not None else 0,
              min(math.log1p(files) / math.log1p(100), 1) if files is not None else 0,
              min(tests / (source + tests + 1), 1) if source is not None and tests is not None else 0,
              float(state > 0) if state is not None else 0,
              float(same) if known_same else 0]
    missing = [source is None, files is None, source is None or tests is None,
               state is None, not known_same]
    return tuple(map(float, values + missing))


def snapshot_join(raw: list[dict], snapshots: list[dict]) -> dict:
    """CLAIM(snapshot-identity): source and SHA mismatch refuses [test_diagnostic]."""
    index = {}
    for snapshot in snapshots:
        key = snapshot['group_id'], snapshot['ordinal']
        if key in index:
            raise ValueError(f'Duplicate snapshot key: {key}')
        index[key] = snapshot
    joined = {}
    seen_raw = set()
    for row in raw:
        key = row['group_id'], row['ordinal']
        if key in seen_raw:
            raise ValueError(f'Duplicate round key: {key}')
        seen_raw.add(key)
        snapshot = index.get(key)
        if snapshot is not None:
            for field in ('project', 'round', 'source'):
                if snapshot.get(field) != row.get(field):
                    raise ValueError(f'Snapshot {field} mismatch for {key}')
            features = snapshot.get('features') or {}
            if features.get('status') == 'observed':
                target = row.get('reviewed_sha')
                previous = (row.get('features_before_round') or {}).get('previous_reviewed_sha')
                if not target or not str(features.get('target', '')).startswith(target):
                    raise ValueError(f'Snapshot target SHA mismatch for {key}')
                if previous and not str(features.get('base', '')).startswith(previous):
                    raise ValueError(f'Snapshot previous SHA mismatch for {key}')
        joined[key] = snapshot_values(snapshot)
    extras = set(index) - seen_raw
    if extras:
        raise ValueError(f'Snapshot keys have no matching round: {sorted(extras)}')
    return joined


def fit_models(train, test):
    """Train both logistic feature sets independently inside the training fold."""
    baseline_train = [replace(row, predictors=row.predictors[:9]) for row in train]
    baseline_test = [replace(row, predictors=row.predictors[:9]) for row in test]
    lag_config = choose_config(baseline_train, 'logistic')
    augmented_config = choose_config(train, 'logistic')
    predictions, fallbacks = {}, {}
    for model in MODELS:
        family = 'logistic' if model.endswith('logistic') else model
        own_train = baseline_train if model == 'lag_logistic' else train
        own_test = baseline_test if model == 'lag_logistic' else test
        config = lag_config if model == 'lag_logistic' else augmented_config
        predictions[model], fallbacks[model] = fit_predict(own_train, own_test, family, config)
    return predictions, fallbacks, {'lag_logistic': lag_config, 'augmented_logistic': augmented_config}


def cluster_interval(records, baseline, candidate, cluster='group', repetitions=5000):
    by_cluster = defaultdict(list)
    for record in records:
        by_cluster[record[cluster]].append(record)
    names, differences = sorted(by_cluster), []
    rng = random.Random(20261117)
    for _ in range(repetitions):
        chosen = [record for name in rng.choices(names, k=len(names)) for record in by_cluster[name]]
        differences.append(sum((r['outcome'] - r['predictions'][baseline]) ** 2 -
                               (r['outcome'] - r['predictions'][candidate]) ** 2 for r in chosen) / len(chosen))
    differences.sort()
    return {'clusters': len(names), 'percentile95': [differences[int(.025 * (repetitions - 1))],
                                                    differences[int(.975 * (repetitions - 1))]]}


def fixed_ranks(values):
    source, _, _, state, _, source_missing, _, _, state_missing, _ = values
    return {'source_churn_only': (not source_missing, source),
            'stateful_then_churn': (not state_missing, state, not source_missing, source)}


def within_change_allocation(records):
    """80% budget within every held-out change avoids cross-fold prior ranks."""
    by_group = defaultdict(list)
    for record in records:
        by_group[record['group']].append(record)
    models = MODELS + ('source_churn_only', 'stateful_then_churn', 'random80', 'always_continue')
    totals = {name: {'expected_reviews': 0.0, 'captured_positives': 0.0, 'missed_positives': 0.0}
              for name in models}
    for group in by_group.values():
        labels = [row['outcome'] for row in group]
        for model in models:
            scores = ([row['predictions'][model] for row in group] if model in MODELS else
                      [tuple(row['ranks'][model]) for row in group] if model in {'source_churn_only', 'stateful_then_churn'} else
                      [1.0] * len(group))
            result = allocation(labels, scores, 1 if model == 'always_continue' else .8)
            for name in totals[model]:
                totals[model][name] += result[name]
    return totals


def validate(rows, feature_lookup, partition='group'):
    records, folds = [], []
    for held, train, test in grouped_folds(rows, partition):
        forecasts, fallbacks, settings = fit_models(train, test)
        folds.append({'held': held, 'training_groups': sorted({row.group for row in train}),
                      'test_groups': sorted({row.group for row in test}),
                      'settings': settings, 'fallbacks': fallbacks, 'test_rows': len(test)})
        for index, row in enumerate(test):
            records.append({'group': row.group, 'project': row.project, 'ordinal': row.ordinal,
                            'outcome': row.outcome,
                            'predictions': {model: forecasts[model][index] for model in MODELS},
                            'ranks': fixed_ranks(feature_lookup[row.group, row.ordinal])})
    labels = [r['outcome'] for r in records]
    metrics = {}
    for model in MODELS:
        by_group = defaultdict(list)
        for row in records:
            by_group[row['group']].append((row['outcome'] - row['predictions'][model]) ** 2)
        metrics[model] = {'brier': brier(labels, [r['predictions'][model] for r in records]),
                          'change_average_brier': sum(sum(losses) / len(losses) for losses in by_group.values()) / len(by_group),
                          'fallback_rows': sum(fold['test_rows'] for fold in folds if fold['fallbacks'][model])}
    best_simple = min(('pooled', 'lag_bucket', 'lag_logistic'), key=lambda model: metrics[model]['brier'])
    augmented = metrics['augmented_logistic']
    augmented['relative_improvement_vs_best_simple'] = (metrics[best_simple]['brier'] - augmented['brier']) / metrics[best_simple]['brier']
    augmented['paired95_vs_each_simple'] = {
        baseline: {cluster: cluster_interval(records, baseline, 'augmented_logistic', cluster)
                   for cluster in ('group', 'project')}
        for baseline in ('pooled', 'lag_bucket', 'lag_logistic')}
    return {'partition': partition, 'records': records, 'folds': folds, 'metrics': metrics,
            'best_simple_descriptive': best_simple, 'within_change_allocation80': within_change_allocation(records)}


def main():
    training = HERE.parent / 'structured-training.jsonl'
    snapshot_path = HERE / 'snapshot-features.jsonl'
    training_content, snapshot_content = training.read_bytes(), snapshot_path.read_bytes()
    raw = [json.loads(line) for line in training_content.splitlines() if line.strip()]
    snapshots = [json.loads(line) for line in snapshot_content.splitlines() if line.strip()]
    lookup = snapshot_join(raw, snapshots)
    rows, excluded = observations(raw)
    rows = [replace(row, predictors=row.predictors + lookup[row.group, row.ordinal]) for row in rows]
    result = {'status': 'posthoc-exploratory-only', 'meaningful_improvement_demonstrated': False,
              'group_independence_established': False,
              'input_sha256': {'training': hashlib.sha256(training_content).hexdigest(),
                               'snapshot': hashlib.sha256(snapshot_content).hexdigest(),
                               'protocol': hashlib.sha256((HERE / 'PROTOCOL.md').read_bytes()).hexdigest()},
              'inventory': {'rows': len(rows), 'groups': len({row.group for row in rows}),
                            'projects': len({row.project for row in rows}), 'positives': sum(row.outcome for row in rows),
                            'negatives': sum(not row.outcome for row in rows), 'excluded': excluded,
                            'feature_missing_rows': sum(any(lookup[row.group, row.ordinal][5:]) for row in rows)},
              'loco': validate(rows, lookup), 'project_holdout': validate(rows, lookup, 'project')}
    (HERE / 'results.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'inventory': result['inventory'],
                      'loco': result['loco']['metrics'], 'project_holdout': result['project_holdout']['metrics']}))


if __name__ == '__main__':
    main()
