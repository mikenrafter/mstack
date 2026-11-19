#!/usr/bin/env python3
"""Research forecasts for observed review yield. Frozen design: PROTOCOL.md.

CLAIM(predictor-boundary): only previous-round fields and assignment ordinal
enter features [test_forecast.test_future_fields_cannot_change_features].
CLAIM(group-holdout): complete changes remain outside their training fold
[test_forecast.test_group_folds_keep_all_rounds_together].
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import random
from typing import Callable

SEEDS = (17, 41, 97)
K_GRID = (8, 16, 32, 64)
SCHEDULES = ('fixed', 'decay')
LAMBDA_GRID = (0.1, 1.0, 10.0)
LABEL = 'documented_accepted_consequential_discovery'


@dataclass(frozen=True)
class Observation:
    group: str
    project: str
    ordinal: int
    outcome: int
    predictors: tuple[float, ...]
    bucket: tuple[str, str]


def previous_state(row: dict) -> tuple[str, str, float, bool]:
    before = row.get('features_before_round') or {}
    verdict = before.get('previous_verdict')
    verdict = verdict if verdict in {'APPROVE', 'CHANGES'} else 'unknown'
    ordinal = row['ordinal']
    stratum = '2' if ordinal == 2 else '3' if ordinal == 3 else '4plus'
    score = before.get('previous_score')
    known = isinstance(score, (float, int)) and not isinstance(score, bool)
    known = known and math.isfinite(score) and 0 <= score <= 10
    return verdict, stratum, float(score) if known else 5.0, not known


def features(row: dict) -> tuple[float, ...]:
    # CLAIM(predictor-boundary)
    verdict, stratum, score, missing = previous_state(row)
    return (1.0, (score - 5.0) / 5.0, float(missing),
            float(verdict == 'APPROVE'), float(verdict == 'CHANGES'),
            float(verdict == 'unknown'), float(stratum == '2'),
            float(stratum == '3'), float(stratum == '4plus'))


def observations(raw: list[dict], label: str = LABEL) -> tuple[list[Observation], dict]:
    result, excluded = [], Counter()
    seen = set()
    for row in raw:
        ordinal = row.get('ordinal')
        if not isinstance(ordinal, int) or isinstance(ordinal, bool) or ordinal <= 1:
            excluded['first_or_invalid_ordinal'] += 1
            continue
        outcome = row.get(label)
        if type(outcome) is not bool:
            excluded['unknown_label'] += 1
            continue
        identity = (row['group_id'], ordinal)
        if identity in seen:
            raise ValueError(f'Duplicate observation identity: {identity}')
        seen.add(identity)
        verdict, stratum, _, _ = previous_state(row)
        result.append(Observation(row['group_id'], row['project'], ordinal,
                                  int(outcome), features(row), (verdict, stratum)))
    return result, dict(excluded)


def prior(rows: list[Observation]) -> float:
    return (1.0 + sum(row.outcome for row in rows)) / (2.0 + len(rows))


def sigmoid(logodds: float) -> float:
    if logodds >= 0:
        return 1.0 / (1.0 + math.exp(-min(logodds, 700)))
    exponent = math.exp(max(logodds, -700))
    return exponent / (1.0 + exponent)


def elo_probability(rating: float, benchmark: float = 1500) -> float:
    return sigmoid(math.log(10) * (rating - benchmark) / 400)


def effective_k(k0: float, schedule: str, prior_groups: int) -> float:
    if schedule not in SCHEDULES or prior_groups < 0:
        raise ValueError('Unknown schedule or negative independent group count')
    return k0 if schedule == 'fixed' else k0 / (1.0 + prior_groups / 4.0)


def elo_update(rating: float, outcome: int, k: float) -> float:
    return rating + k * (outcome - elo_probability(rating))


def grouped_folds(rows: list[Observation], partition: str = 'group'):
    # CLAIM(group-holdout)
    if partition not in {'group', 'project'}:
        raise ValueError('Partition must name group or project')
    for held in sorted({getattr(row, partition) for row in rows}):
        yield held, [row for row in rows if getattr(row, partition) != held], [
            row for row in rows if getattr(row, partition) == held]


def logistic_objective(rows: list[Observation], weights: list[float], penalty: float) -> float:
    losses = []
    for row in rows:
        logodds = sum(w * x for w, x in zip(weights, row.predictors))
        # Stable log(1+exp(z)) - y*z.
        losses.append(max(logodds, 0) + math.log1p(math.exp(-abs(logodds))) - row.outcome * logodds)
    return sum(losses) / len(rows) + penalty * sum(w * w for w in weights[1:]) / 2


def logistic_fit(train: list[Observation], penalty: float, history=None) -> list[float]:
    """Fit the specified objective with a globally bounded descent step.

    CLAIM(logistic-descent): Hessian norm <= .25*max||x||^2 + lambda;
    step1/L therefore decreases the smooth convex objective
    [OPTIMIZER-AMENDMENT.md; test_logistic_large_penalty_descends].
    """
    mean = prior(train)
    weights = [math.log(mean / (1 - mean))] + [0.0] * (len(train[0].predictors) - 1)
    lipschitz = 0.25 * max(sum(x * x for x in row.predictors) for row in train) + penalty
    step = 1.0 / lipschitz
    if history is not None:
        history.append(logistic_objective(train, weights, penalty))
    for _ in range(400):
        gradient = [0.0] * len(weights)
        for row in train:
            error = sigmoid(sum(w * x for w, x in zip(weights, row.predictors))) - row.outcome
            for index, value in enumerate(row.predictors):
                gradient[index] += error * value / len(train)
        for index in range(len(weights)):
            weights[index] -= step * (gradient[index] + (penalty * weights[index] if index else 0))
        if history is not None:
            history.append(logistic_objective(train, weights, penalty))
    return weights


def fit_predict(train: list[Observation], test: list[Observation], model: str,
                config=None, seed: int | None = None) -> tuple[list[float], bool]:
    """Return probabilities and whether a one-class training fallback was used.

    The fallback includes empty training and preserves every test opportunity.
    Unknown model/config is an error, never a silently substituted forecast.
    """
    if model not in {'pooled', 'lag_bucket', 'logistic', 'anchored_elo'}:
        raise ValueError(f'Unknown model: {model}')
    mean = prior(train)
    fallback = len({row.outcome for row in train}) < 2
    if fallback or model == 'pooled':
        return [mean] * len(test), fallback
    if model == 'lag_bucket':
        buckets = defaultdict(list)
        for row in train:
            buckets[row.bucket].append(row.outcome)
        return [(sum(buckets[row.bucket]) + 4 * mean) /
                (len(buckets[row.bucket]) + 4) for row in test], False
    if model == 'logistic':
        penalty = float(config)
        weights = logistic_fit(train, penalty)
        return [sigmoid(sum(w * x for w, x in zip(weights, row.predictors))) for row in test], False
    k0, schedule = config
    seeds = SEEDS if seed is None else (seed,)
    per_seed = []
    for order_seed in seeds:
        initial = 1500 + 400 * math.log10(mean / (1 - mean))
        ratings = defaultdict(lambda: initial)
        bucket_groups = defaultdict(set)
        by_group = defaultdict(list)
        for row in train:
            by_group[row.group].append(row)
        order = sorted(by_group, key=lambda group: hashlib.sha256(
            f'{order_seed}:{group}'.encode()).hexdigest())
        for preceding_groups, group in enumerate(order):
            k = effective_k(k0, schedule, preceding_groups)
            for row in sorted(by_group[group], key=lambda row: row.ordinal):
                ratings[row.bucket] = elo_update(ratings[row.bucket], row.outcome, k)
                bucket_groups[row.bucket].add(group)
        probabilities = []
        for row in test:
            count = len(bucket_groups[row.bucket])
            probabilities.append((count * elo_probability(ratings[row.bucket]) + 4 * mean) / (count + 4))
        per_seed.append(probabilities)
    return [sum(values) / len(values) for values in zip(*per_seed)], False


def brier(outcomes: list[int], forecasts: list[float]) -> float:
    if len(outcomes) != len(forecasts) or not outcomes:
        raise ValueError('Brier requires aligned nonempty observations')
    return sum((y - probability) ** 2 for y, probability in zip(outcomes, forecasts)) / len(outcomes)


def choose_config(train: list[Observation], model: str):
    grid = LAMBDA_GRID if model == 'logistic' else tuple((k, schedule) for k in K_GRID for schedule in SCHEDULES)
    best_config, best_loss = grid[0], math.inf
    for config in grid:
        outcomes, probabilities = [], []
        for _, inner_train, inner_test in grouped_folds(train):
            predicted, _ = fit_predict(inner_train, inner_test, model, config)
            outcomes.extend(row.outcome for row in inner_test)
            probabilities.extend(predicted)
        loss = brier(outcomes, probabilities) if outcomes else math.inf
        if loss < best_loss:
            best_config, best_loss = config, loss
    return best_config


def allocation(outcomes: list[int], probabilities: list[float], fraction: float = 0.8) -> dict:
    """Expected positives under uniform random allocation within cutoff ties."""
    if len(outcomes) != len(probabilities) or not 0 <= fraction <= 1:
        raise ValueError('Allocation requires aligned rows and a fraction in [0,1]')
    budget = len(outcomes) * fraction
    by_probability = defaultdict(list)
    for outcome, probability in zip(outcomes, probabilities):
        by_probability[probability].append(outcome)
    captured, remaining = 0.0, budget
    for score in sorted(by_probability, reverse=True):
        labels = by_probability[score]
        selected = min(remaining, len(labels))
        captured += sum(labels) * selected / len(labels)
        remaining -= selected
    positives = sum(outcomes)
    return {'expected_reviews': budget, 'captured_positives': captured,
            'missed_positives': positives - captured,
            'recall': captured / positives if positives else None}


def paired_interval(records: list[dict], baseline: str, candidate: str,
                    repetitions: int = 5000, seed: int = 20261117) -> list[float]:
    by_group = defaultdict(list)
    for record in records:
        by_group[record['group']].append(record)
    groups, differences = sorted(by_group), []
    rng = random.Random(seed)
    for _ in range(repetitions):
        sample = [record for group in rng.choices(groups, k=len(groups)) for record in by_group[group]]
        differences.append(sum((record['outcome'] - record['predictions'][baseline]) ** 2 -
                               (record['outcome'] - record['predictions'][candidate]) ** 2
                               for record in sample) / len(sample))
    differences.sort()
    return [differences[int(0.025 * (repetitions - 1))], differences[int(0.975 * (repetitions - 1))]]


MODELS = ('pooled', 'lag_bucket', 'logistic', 'anchored_elo', 'elo_seed_17', 'elo_seed_41', 'elo_seed_97')


def validate(rows: list[Observation], partition: str = 'group') -> dict:
    records, folds = [], []
    for held, train, test in grouped_folds(rows, partition):
        logistic_config = choose_config(train, 'logistic')
        elo_config = choose_config(train, 'anchored_elo')
        predictions, fallback = {}, {}
        for model in MODELS:
            family = 'anchored_elo' if model.startswith('elo_seed_') else model
            config = logistic_config if family == 'logistic' else elo_config if family == 'anchored_elo' else None
            seed = int(model.rsplit('_', 1)[1]) if model.startswith('elo_seed_') else None
            predictions[model], fallback[model] = fit_predict(train, test, family, config, seed)
        folds.append({'held': held, 'training_groups': sorted({row.group for row in train}),
                      'test_groups': sorted({row.group for row in test}),
                      'logistic_penalty': logistic_config, 'elo_config': elo_config,
                      'fallback': fallback, 'test_rows': len(test)})
        for index, row in enumerate(test):
            records.append({'group': row.group, 'project': row.project, 'ordinal': row.ordinal,
                            'outcome': row.outcome,
                            'predictions': {model: predictions[model][index] for model in MODELS}})
    outcomes = [record['outcome'] for record in records]
    metrics = {}
    for model in MODELS:
        forecasts = [record['predictions'][model] for record in records]
        by_group = defaultdict(list)
        for record, probability in zip(records, forecasts):
            by_group[record['group']].append((record['outcome'] - probability) ** 2)
        metrics[model] = {'brier': brier(outcomes, forecasts),
                          'change_average_brier': sum(sum(losses) / len(losses) for losses in by_group.values()) / len(by_group),
                          'allocation80': allocation(outcomes, forecasts),
                          'fallback_test_rows': sum(fold['test_rows'] for fold in folds if fold['fallback'][model])}
    best_simple = min(('pooled', 'lag_bucket', 'logistic'), key=lambda model: metrics[model]['brier'])
    for model in MODELS:
        improvement = metrics[best_simple]['brier'] - metrics[model]['brier']
        interval = paired_interval(records, best_simple, model)
        metrics[model]['improvement_vs_best_simple'] = improvement
        metrics[model]['relative_brier_improvement'] = improvement / metrics[best_simple]['brier']
        metrics[model]['paired_group_bootstrap95'] = interval
        metrics[model]['meaningful_by_numeric_gates'] = (
            len({row.group for row in rows}) >= 10 and len({row.outcome for row in rows}) == 2 and
            metrics[model]['relative_brier_improvement'] >= 0.1 and interval[0] > 0 and
            metrics[model]['allocation80']['missed_positives'] <= metrics[best_simple]['allocation80']['missed_positives'] + 1e-12)
    return {'partition': partition, 'best_simple_descriptive': best_simple, 'folds': folds,
            'predictions': records, 'metrics': metrics,
            'always_continue': allocation(outcomes, [1.0] * len(rows), 1.0),
            'random_allocation80': allocation(outcomes, [1.0] * len(rows))}


def run(raw: list[dict], label: str = LABEL) -> dict:
    rows, excluded = observations(raw, label)
    inventory = {'label': label, 'eligible_rows': len(rows), 'groups': len({row.group for row in rows}),
                 'projects': len({row.project for row in rows}),
                 'positive_rows': sum(row.outcome for row in rows),
                 'negative_rows': sum(not row.outcome for row in rows), 'excluded': excluded}
    if len({row.outcome for row in rows}) < 2 or len({row.group for row in rows}) < 2:
        return {'status': 'insufficient-evidence-no-fit', 'inventory': inventory,
                'reason': 'Both outcome classes and at least two change groups required before fitting.'}
    result = {'status': 'exploratory-proxy-forecast', 'inventory': inventory,
              'independent_change_sampling_established': False,
              'meaningful_improvement_demonstrated': False,
              'interpretation_limits': ['Group IDs are not proof of independent changes.',
                                        'Pooled cross-fold allocation has varying training priors and is descriptive only.'],
              'loco': validate(rows)}
    if len({row.project for row in rows}) > 1:
        result['project_holdout'] = validate(rows, 'project')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('corpus', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--label', default=LABEL, choices=(LABEL, 'documented_consequential_discovery'))
    args = parser.parse_args()
    content = args.corpus.read_bytes()
    raw = [json.loads(line) for line in content.splitlines() if line.strip()]
    result = run(raw, args.label)
    result['input_sha256'] = hashlib.sha256(content).hexdigest()
    result['protocol_sha256'] = hashlib.sha256(Path(__file__).with_name('PROTOCOL.md').read_bytes()).hexdigest()
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': result['status'], **result['inventory']}))


if __name__ == '__main__':
    main()
