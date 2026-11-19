#!/usr/bin/env python3
"""Expose every frozen Elo K/schedule as outer-holdout sensitivity, not selection."""
import argparse
import hashlib
import json
from pathlib import Path
from forecast import (K_GRID, SCHEDULES, allocation, brier, fit_predict,
                      grouped_folds, observations, paired_interval)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('corpus', type=Path)
    parser.add_argument('main_results', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    content = args.corpus.read_bytes()
    original = json.loads(args.main_results.read_text())
    if hashlib.sha256(content).hexdigest() != original['input_sha256']:
        raise ValueError('Corpus changed after main fit; freeze a matching snapshot')
    rows, _ = observations([json.loads(line) for line in content.splitlines() if line.strip()],
                           original['inventory']['label'])
    if 'loco' not in original:
        args.output.write_text(json.dumps({'status': 'insufficient-evidence-no-fit'}) + '\n')
        return
    baseline = original['loco']['best_simple_descriptive']
    lookup = {(record['group'], record['ordinal']): record for record in original['loco']['predictions']}
    records = []
    for _, train, test in grouped_folds(rows):
        probabilities = {}
        for k in K_GRID:
            for schedule in SCHEDULES:
                name = f'K{k}_{schedule}'
                probabilities[name], _ = fit_predict(train, test, 'anchored_elo', (k, schedule))
        for index, row in enumerate(test):
            records.append({'group': row.group, 'ordinal': row.ordinal, 'outcome': row.outcome,
                            'predictions': {baseline: lookup[row.group, row.ordinal]['predictions'][baseline],
                                            **{name: values[index] for name, values in probabilities.items()}}})
    metrics = {}
    outcomes = [record['outcome'] for record in records]
    for name in probabilities:
        forecasts = [record['predictions'][name] for record in records]
        metrics[name] = {'brier': brier(outcomes, forecasts), 'allocation80': allocation(outcomes, forecasts),
                         'paired_group_bootstrap95_vs_best_simple': paired_interval(records, baseline, name)}
    result = {'status': 'predeclared-grid-sensitivity-only', 'baseline': baseline,
              'input_sha256': original['input_sha256'], 'metrics': metrics, 'predictions': records}
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(metrics))


if __name__ == '__main__':
    main()
