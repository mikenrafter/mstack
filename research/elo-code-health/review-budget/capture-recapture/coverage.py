#!/usr/bin/env python3
"""Exact descriptive coverage curves for finite published inspector pools."""
import hashlib
import json
import math
from pathlib import Path
import statistics

HERE = Path(__file__).resolve().parent
SOURCE_HASH = '696c9397d1213da986db451ab83c369e328e46d6d22afd9091c2ea066faffbcd'


def finite_curve(reference_count: int, inspectors: list[dict]) -> dict:
    """Enumerate every team; team quantiles are not confidence intervals.

    CLAIM(finite-coverage): every subset of size k has equal weight; the
    hypergeometric mean below is an independent check [COVERAGE-PROTOCOL.md;
    test_coverage hand-computed three-inspector fixture].
    """
    if type(reference_count) is not int or reference_count < 1 or not 1 <= len(inspectors) <= 20:
        raise ValueError('Unsupported reference count or pool size')
    if len({row['inspector_id'] for row in inspectors}) != len(inspectors):
        raise ValueError('Duplicate inspector ID')
    detection_sets = [set(row['detections']) for row in inspectors]
    if any(len(found) != len(row['detections']) for row, found in zip(inspectors, detection_sets)):
        raise ValueError('Duplicate reference-fault ID')
    if any(type(fault) is not int or not 1 <= fault <= reference_count
           for found in detection_sets for fault in found):
        raise ValueError('Invalid reference-fault ID')
    masks = [sum(1 << (fault - 1) for fault in found) for found in detection_sets]
    unions = [0] * (1 << len(masks))
    by_size = [[] for _ in range(len(masks) + 1)]
    for team in range(1, len(unions)):
        member = team & -team
        unions[team] = unions[team ^ member] | masks[member.bit_length() - 1]
        by_size[team.bit_count()].append(unions[team].bit_count())
    frequencies = [sum(fault in found for found in detection_sets)
                   for fault in range(1, reference_count + 1)]
    curve, previous = [], 0
    for size in range(1, len(inspectors) + 1):
        observed = sorted(by_size[size])
        mean = statistics.mean(observed)
        denominator = math.comb(len(inspectors), size)
        expected = sum(1 - (math.comb(len(inspectors)-frequency, size) / denominator
                       if len(inspectors)-frequency >= size else 0) for frequency in frequencies)
        if abs(mean - expected) > 1e-12 or len(observed) != denominator:
            raise ValueError('Enumeration disagrees with combinatorial oracle')
        curve.append({'inspectors': size, 'teams': len(observed), 'mean_found': mean,
                      'mean_reference_coverage': mean / reference_count,
                      'marginal_mean_found': mean - previous,
                      'minimum_found': observed[0], 'maximum_found': observed[-1],
                      'team_p05_found': observed[max(0, math.ceil(.05*len(observed))-1)],
                      'team_p95_found': observed[math.ceil(.95*len(observed))-1],
                      'combinatorial_mean_agrees': True})
        previous = mean
    return {'inspectors': len(inspectors), 'reference_defects': reference_count,
            'never_detected_reference_faults': [i+1 for i, frequency in enumerate(frequencies) if frequency == 0],
            'teams_enumerated': sum(len(rows) for rows in by_size), 'curve': curve}


def main():
    normalized_path = HERE / 'normalized-matrices.json'
    normalized = json.loads(normalized_path.read_text())
    if normalized['source_sha256'] != SOURCE_HASH or hashlib.sha256(
            (HERE / 'sources/umd-total.cc').read_bytes()).hexdigest() != SOURCE_HASH:
        raise ValueError('Published source changed')
    results = []
    for matrix in normalized['matrices']:
        curve = finite_curve(matrix['reference_defects'], matrix['inspectors'])
        results.append({'matrix': matrix['matrix'], 'artifact': matrix['artifact'],
                        'cohort': matrix['cohort'], **curve})
    output = {'status': 'finite-pool-descriptive-only',
              'normalized_sha256': hashlib.sha256(normalized_path.read_bytes()).hexdigest(),
              'protocol_sha256': hashlib.sha256((HERE / 'COVERAGE-PROTOCOL.md').read_bytes()).hexdigest(),
              'results': results,
              'limits': ['Fixed human requirements artifacts with study reference faults.',
                         'Overlapping teams are not independent samples.',
                         'Team percentiles are not population confidence intervals.',
                         'No new-reviewer prediction, code-quality score or optimal-round claim.']}
    (HERE / 'coverage-results.json').write_text(json.dumps(output, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'matrices': len(results), 'teams': sum(r['teams_enumerated'] for r in results)}))


if __name__ == '__main__':
    main()
