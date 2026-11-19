#!/usr/bin/env python3
"""Evaluate locked training-only predictors on independently assembled chains."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from forecast import (MODELS, SEEDS, allocation, brier, features, fit_predict,
                      observations, paired_interval)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('external', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    here = Path(__file__).parent
    settings_content = (here / 'external-locked-settings.json').read_bytes()
    settings = json.loads(settings_content)
    train_content = (here / 'structured-training.jsonl').read_bytes()
    if hashlib.sha256(train_content).hexdigest() != settings['training_sha256']:
        raise ValueError('Training snapshot differs from locked settings')
    train, _ = observations([json.loads(line) for line in train_content.splitlines() if line.strip()], settings['label'])
    external_content = args.external.read_bytes()
    external_raw = [json.loads(line) for line in external_content.splitlines() if line.strip()]
    test, excluded = observations(external_raw, settings['label'])
    raw_external_groups = {row['group_id'] for row in external_raw}
    if raw_external_groups.intersection(settings['training_groups']):
        raise ValueError('External group overlaps structured training')
    inventory = {'eligible_rows': len(test), 'groups': len({row.group for row in test}),
                 'positive_rows': sum(row.outcome for row in test),
                 'negative_rows': sum(not row.outcome for row in test),
                 'missing_previous_score': sum(row.predictors[2] for row in test),
                 'excluded': excluded}
    metadata = {'inventory': inventory, 'training_sha256': settings['training_sha256'],
                'external_sha256': hashlib.sha256(external_content).hexdigest(),
                'locked_settings_sha256': hashlib.sha256(settings_content).hexdigest(),
                'settings': settings}
    if not test:
        args.output.write_text(json.dumps({'status': 'no-labeled-external-opportunities', **metadata}, indent=2) + '\n')
        return
    forecasts, fallbacks = {}, {}
    for model in MODELS:
        family = 'anchored_elo' if model.startswith('elo_seed_') else model
        config = settings['logistic_penalty'] if family == 'logistic' else settings['elo_config'] if family == 'anchored_elo' else None
        seed = int(model.rsplit('_', 1)[1]) if model.startswith('elo_seed_') else None
        forecasts[model], fallbacks[model] = fit_predict(train, test, family, config, seed)
    records = [{'group': row.group, 'project': row.project, 'ordinal': row.ordinal, 'outcome': row.outcome,
                'predictions': {model: forecasts[model][index] for model in MODELS}}
               for index, row in enumerate(test)]
    labels = [row.outcome for row in test]
    metrics = {model: {'brier': brier(labels, forecasts[model]),
                       'allocation80': allocation(labels, forecasts[model]), 'fallback': fallbacks[model]}
               for model in MODELS}
    # All baseline comparisons are reported; external outcomes select no parameters.
    for model in MODELS:
        metrics[model]['paired_group_bootstrap95_vs_each_simple'] = {
            baseline: paired_interval(records, baseline, model)
            for baseline in ('pooled', 'lag_bucket', 'logistic')}
    result = {'status': 'external-reported-finding-proxy-replication', **metadata,
              'metrics': metrics, 'predictions': records,
              'always_continue': allocation(labels, [1.0] * len(test), 1),
              'random_allocation80': allocation(labels, [1.0] * len(test)),
              'inference_limit': 'No generalization inference from one group; reported findings are not verified defects.'}
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': result['status'], **inventory, 'metrics': metrics}))


if __name__ == '__main__':
    main()
