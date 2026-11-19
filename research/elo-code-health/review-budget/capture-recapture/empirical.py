#!/usr/bin/env python3
"""Parse published UMD inspection matrices as data and apply the frozen Chapman diagnostic."""
from __future__ import annotations

import hashlib
from itertools import combinations
import json
import math
from pathlib import Path
import re
import statistics

HERE = Path(__file__).resolve().parent
SOURCE_SHA = '696c9397d1213da986db451ab83c369e328e46d6d22afd9091c2ea066faffbcd'
SOURCE_URL = 'https://www.cs.umd.edu/projects/SoftEng/ESEG/manual/pbr_package/docs/total.cc'
MATRICES = {'atm_nov': (12, 29), 'atm_jun': (14, 29), 'pg_nov': (12, 27), 'pg_jun': (14, 27),
            'a_nov': (12, 18), 'a_jun': (13, 15), 'b_nov': (12, 15), 'b_jun': (13, 15)}
PERSPECTIVES = {0: 'usual NASA technique', 1: 'designer', 2: 'tester', 3: 'user'}


def constant(text: str, name: str, expected: int):
    declarations = re.findall(r'\bconst\s+int\s+' + re.escape(name) + r'\s*=\s*(\d+)\s*;', text)
    if declarations != [str(expected)]:
        raise ValueError(f'{name}: expected one declaration equal to {expected}')


def parse_matrix(text: str, name: str, expected_rows: int, expected_defects: int) -> dict:
    """CLAIM(matrix-boundaries): ID/P excluded; zero padding checked against declared ERR, not discovered union."""
    constant(text, 'MAX_COL', 35)
    constant(text, name.upper(), expected_rows)
    constant(text, name.upper() + '_ERR', expected_defects)
    if len(re.findall(r'\btypedef\s+int\s+scores\s*\[\s*MAX_COL\s*\]\s*;', text)) != 1:
        raise ValueError('Unsupported scores type/width')
    declarations = list(re.finditer(r'\bscores\s+' + re.escape(name) +
                                   r'\s*\[\s*([A-Z_]+)\s*\]\s*=\s*(?://[^\n]*\n\s*)?\{(.*?)\};', text, re.S))
    if len(declarations) != 1 or declarations[0][1] != name.upper():
        raise ValueError(f'{name}: ambiguous or unsupported initializer')
    declaration = declarations[0]
    header = re.match(r'\s*/\*\s*([^\n]+)\n\s*-+\s*\*/', declaration[2])
    if not header:
        raise ValueError(f'{name}: missing structured ID/P header')
    tokens = header[1].split()
    expected_header = ['ID', 'P'] + [str(i % 10) for i in range(1, expected_defects + 1)]
    anomalies = []
    if tokens != expected_header:
        known_stale = (name == 'pg_jun' and hashlib.sha256(text.encode()).hexdigest() == SOURCE_SHA
                       and tokens == ['ID', 'P'] + [str(i % 10) for i in range(1, 30)])
        if not known_stale:
            raise ValueError(f'{name}: header does not match declared reference columns')
        anomalies.append('Known source-header anomaly: 29 printed labels, PG_JUN_ERR declares 27; amendment permits only this exact source hash.')
    lines = [line.strip() for line in declaration[2][header.end():].splitlines() if line.strip()]
    if len(lines) != expected_rows:
        raise ValueError(f'{name}: row count does not match declaration')
    inspectors, ids = [], set()
    cohort = name.rsplit('_', 1)[1]
    for line in lines:
        if not re.fullmatch(r'-?\d+(?:\s*,\s*-?\d+)*\s*,?', line):
            raise ValueError(f'{name}: nonliteral row data')
        row = [int(value.strip()) for value in line.rstrip(',').split(',')]
        if len(row) != 35:
            raise ValueError(f'{name}: row width must be exactly MAX_COL=35')
        inspector_id, perspective = row[:2]
        if inspector_id <= 0 or inspector_id in ids or perspective not in PERSPECTIVES:
            raise ValueError(f'{name}: duplicate/invalid inspector ID or synthetic/unknown perspective')
        ids.add(inspector_id)
        detection_values = row[2:2 + expected_defects]
        padding = row[2 + expected_defects:]
        if any(value not in (0, 1) for value in detection_values) or any(padding):
            raise ValueError(f'{name}: nonbinary reference detection or nonzero padding')
        inspectors.append({'inspector_id': inspector_id, 'cohort': cohort,
                           'participant_group': f'{cohort}:{inspector_id}',
                           'perspective': perspective, 'perspective_label': PERSPECTIVES[perspective],
                           'detections': [index + 1 for index, value in enumerate(detection_values) if value],
                           'padding_columns': len(padding)})
    return {'matrix': name, 'artifact': name.rsplit('_', 1)[0], 'cohort': cohort,
            'declared_inspectors': expected_rows, 'reference_defects': expected_defects,
            'reference_truth': 'study reference faults, not exhaustive natural defects',
            'source_initializer_line': text.count('\n', 0, declaration.start()) + 1,
            'header_tokens': tokens, 'anomalies': anomalies, 'inspectors': inspectors}


def parse_source(data: bytes) -> list[dict]:
    if hashlib.sha256(data).hexdigest() != SOURCE_SHA:
        raise ValueError('Unexpected public source hash; no unreviewed source exception is permitted')
    text = data.decode('utf-8')
    compact = re.sub(r'\s+', '', text)
    if 'for(j=2,sum=0;j<err+2;j++)' not in compact or 'for(l=2;l<err+2;l++)' not in compact:
        raise ValueError('Source computation no longer establishes metadata/reference-column boundary')
    declared_names = re.findall(r'\bscores\s+(\w+)\s*\[\s*[A-Z_]+\s*\]\s*=', text)
    if sorted(declared_names) != sorted(MATRICES):
        raise ValueError('Unexpected or missing embedded matrix declarations')
    return [parse_matrix(text, name, rows, defects) for name, (rows, defects) in MATRICES.items()]


def pair_record(matrix: str, cohort: str, reference: int, first: dict, second: dict) -> dict:
    # CLAIM(chapman-targets): total=(nA+1)(nB+1)/(m+1)-1; remaining=total-union.
    a, b = set(first['detections']), set(second['detections'])
    if reference <= 0 or not (a | b) <= set(range(1, reference + 1)):
        raise ValueError('Detection outside declared reference population')
    overlap, observed = len(a & b), len(a | b)
    estimated_total = (len(a) + 1) * (len(b) + 1) / (overlap + 1) - 1
    estimated_remaining = estimated_total - observed
    actual_remaining = reference - observed
    return {'matrix': matrix, 'cohort': cohort, 'first_id': first['inspector_id'], 'second_id': second['inspector_id'],
            'first_participant_group': f"{cohort}:{first['inspector_id']}",
            'second_participant_group': f"{cohort}:{second['inspector_id']}",
            'first_perspective': first.get('perspective'), 'second_perspective': second.get('perspective'),
            'first_count': len(a), 'second_count': len(b), 'overlap': overlap, 'observed_union': observed,
            'reference_defects': reference, 'actual_remaining': actual_remaining,
            'estimated_total': estimated_total, 'estimated_remaining': estimated_remaining,
            'remaining_error': estimated_remaining - actual_remaining,
            'remaining_relative_error': (estimated_remaining - actual_remaining) / actual_remaining if actual_remaining else None,
            'total_relative_error': (estimated_total - reference) / reference}


def summarize(pairs: list[dict]) -> dict:
    if not pairs:
        raise ValueError('A diagnostic summary needs at least one actual pair')
    actual = [pair['actual_remaining'] for pair in pairs]
    estimated = [pair['estimated_remaining'] for pair in pairs]
    errors = [pair['remaining_error'] for pair in pairs]
    relative_total = [pair['total_relative_error'] for pair in pairs]
    nonzero = sum(value > 0 for value in actual)
    under_half = sum(pair['actual_remaining'] > 0 and pair['estimated_remaining'] < pair['actual_remaining'] / 2 for pair in pairs)
    false_zero = sum(pair['estimated_remaining'] == 0 and pair['actual_remaining'] > 0 for pair in pairs)
    return {'pairs': len(pairs), 'zero_overlap_pairs': sum(pair['overlap'] == 0 for pair in pairs),
            'mean_actual_remaining': statistics.mean(actual), 'median_actual_remaining': statistics.median(actual),
            'mean_estimated_remaining': statistics.mean(estimated), 'median_estimated_remaining': statistics.median(estimated),
            'remaining_mean_error': statistics.mean(errors),
            'remaining_rmse': math.sqrt(statistics.mean(error * error for error in errors)),
            'actual_nonzero_remaining_pairs': nonzero, 'less_than_half_remaining_pairs': under_half,
            'less_than_half_remaining_fraction': under_half / nonzero if nonzero else None,
            'zero_estimate_with_reference_unseen_pairs': false_zero,
            'zero_estimate_with_reference_unseen_fraction_all_pairs': false_zero / len(pairs),
            'zero_estimate_with_reference_unseen_fraction_nonzero_remainder': false_zero / nonzero if nonzero else None,
            'total_population_relative_error': {'mean': statistics.mean(relative_total), 'median': statistics.median(relative_total),
                                                'rmse': math.sqrt(statistics.mean(error * error for error in relative_total))}}


def main():
    data = (HERE / 'sources/umd-total.cc').read_bytes()
    matrices = parse_source(data)
    normalized = {'source_url': SOURCE_URL, 'source_sha256': SOURCE_SHA,
                  'source_program_executed': False, 'cross_cohort_inspector_crosswalk': 'unknown',
                  'matrices': matrices}
    pairs, summaries = [], []
    for matrix in matrices:
        current = [pair_record(matrix['matrix'], matrix['cohort'], matrix['reference_defects'], first, second)
                   for first, second in combinations(matrix['inspectors'], 2)]
        pairs.extend(current)
        summaries.append({'matrix': matrix['matrix'], 'inspectors': len(matrix['inspectors']),
                          'reference_defects': matrix['reference_defects'], 'cohort': matrix['cohort'],
                          'anomalies': matrix['anomalies'], **summarize(current)})
    (HERE / 'normalized-matrices.json').write_text(json.dumps(normalized, indent=2) + '\n')
    (HERE / 'empirical-pairs.jsonl').write_text(''.join(json.dumps(pair, sort_keys=True) + '\n' for pair in pairs))
    results = {'status': 'descriptive-human-inspection-stress-diagnostic', 'source_sha256': SOURCE_SHA,
               'parser_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'protocol_sha256': hashlib.sha256((HERE / 'EMPIRICAL-PROTOCOL.md').read_bytes()).hexdigest(),
               'amendment_sha256': hashlib.sha256((HERE / 'EMPIRICAL-AMENDMENT.md').read_bytes()).hexdigest(),
               'manual_oracle_sha256': hashlib.sha256((HERE / 'MANUAL-ORACLE.md').read_bytes()).hexdigest(),
               'matrices': summaries, 'total_pair_records': len(pairs),
               'pairs_are_independent': False, 'parameters_fitted': False, 'pair_confidence_intervals': None,
               'manual_oracle_check': 'test_empirical.EmpiricalTests.test_public_source_matches_independent_parent_tally_and_explicit_anomaly'}
    (HERE / 'empirical-results.json').write_text(json.dumps(results, indent=2) + '\n')
    print(json.dumps({'matrices': len(matrices), 'pair_records': len(pairs), 'parameters_fitted': False}))


if __name__ == '__main__':
    main()
