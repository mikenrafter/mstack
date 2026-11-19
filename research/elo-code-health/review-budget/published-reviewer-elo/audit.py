#!/usr/bin/env python3
"""Descriptive arithmetic audit; no chronological replay or uncertainty claim."""
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    raw = (HERE / 'aggregate.json').read_bytes()
    source = json.loads(raw)
    counts = defaultdict(Counter)
    neighbors = defaultdict(set)
    pairs = []
    checks = {}
    checks['run_status_accounting'] = source['runHistory']['attempts'] == sum(
        source['runHistory'][key] for key in ('succeeded', 'canceled', 'failed', 'running'))
    checks['pair_comparison_accounting'] = source['pairwiseComparisons'] == sum(
        pair['comparisons'] for pair in source['pairs'])
    checks['rating_comparison_accounting'] = 2 * source['pairwiseComparisons'] == sum(
        rating['comparisons'] for rating in source['ratings'])
    for pair in source['pairs']:
        left, right = pair['left']['model'], pair['right']['model']
        games = pair['comparisons']
        checks[f'{left}:{right}:outcome_accounting'] = games == sum(
            pair[key] for key in ('wins', 'ties', 'losses'))
        for model, wins, losses in ((left, pair['wins'], pair['losses']),
                                    (right, pair['losses'], pair['wins'])):
            counts[model].update(comparisons=games, wins=wins, losses=losses, ties=pair['ties'])
        if not games:
            continue
        neighbors[left].add(right)
        neighbors[right].add(left)
        # CLAIM(pair-gap): inversion of the displayed logistic expected score,
        # not a replay [PROTOCOL.md; 1/2 share=>0, 3/4 share=>400log10(3)].
        points = pair['wins'] + pair['ties'] / 2
        gap = 400 * math.log10(points / (games - points)) if 0 < points < games else None
        pairs.append(dict(left=left, right=right, comparisons=games,
                          observed_point_share=points / games,
                          constant_gap_from_point_share=gap))
    for rating in source['ratings']:
        for key in ('comparisons', 'wins', 'ties', 'losses'):
            checks[f"{rating['model']}:{key}:reconstructed"] = counts[rating['model']][key] == rating[key]
    reached, pending = set(), [source['ratings'][0]['model']]
    while pending:
        model = pending.pop()
        if model in reached:
            continue
        reached.add(model)
        pending.extend(neighbors[model] - reached)
    checks['nonzero_graph_connected'] = reached == {rating['model'] for rating in source['ratings']}
    record = dict(source_sha256=hashlib.sha256(raw).hexdigest(), checks=checks,
                  all_accounting_checks_pass=all(checks.values()),
                  direct_opponents={model: sorted(others) for model, others in neighbors.items()},
                  pairs=pairs, chronological_k_replay_possible=False,
                  limits=['Aggregates omit ordered rounds and individual findings.',
                          'Related pairs can share a review round and code change.',
                          'Observed relative point share is not defect-detection recall.',
                          'This audit does not establish optional review benefit.'])
    (HERE / 'audit.json').write_text(json.dumps(record, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'checks': len(checks), 'all_pass': all(checks.values()),
                      'nonzero_pairs': len(pairs), 'models': len(counts)}))
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
