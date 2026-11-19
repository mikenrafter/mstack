#!/usr/bin/env python3
"""Frozen synthetic assumption stress test; never a live stopping policy."""
import hashlib
import json
import math
from pathlib import Path
import random
import statistics

HERE = Path(__file__).resolve().parent
REGIMES = ('independent', 'unequal-abilities', 'shared-difficulty',
           'common-blind-spot', 'dependent-reports', 'changed-snapshot')
SEED = 20261117
TRIALS = 10000


def unseen_estimate(first: set[int], second: set[int]) -> float:
    """Chapman's estimated population minus the observed union.

    CLAIM(chapman-unseen): equals (nA-m)(nB-m)/(m+1), not a clean-code
    probability [SIMULATION-PROTOCOL.md; test_simulate hand overlap fixture].
    """
    overlap = len(first & second)
    return (len(first) - overlap) * (len(second) - overlap) / (overlap + 1)


def final_population(initial: set[int], removed: set[int], introduced: set[int]) -> set[int]:
    # CLAIM(population-transition): removed defects cannot be counted as still
    # present after repair [SIMULATION-PROTOCOL.md; test_changed_population].
    if not removed <= initial or initial & introduced:
        raise ValueError('Invalid synthetic population transition')
    return (initial - removed) | introduced


def trial(size: int, regime: str, rng: random.Random) -> tuple[int, int, int, int, float]:
    first, second = set(), set()
    for defect in range(size):
        if regime == 'unequal-abilities':
            probability_a, probability_b = .25, .75
        elif regime == 'shared-difficulty':
            probability_a = probability_b = .9 if defect < size // 2 else .1
        elif regime == 'common-blind-spot':
            probability_a = probability_b = .8 if defect < size // 2 else 0
        else:
            probability_a = probability_b = .5
        caught_a = rng.random() < probability_a
        if caught_a:
            first.add(defect)
        if regime == 'dependent-reports':
            caught_b = caught_a if rng.random() < .75 else rng.random() < probability_b
        elif regime == 'changed-snapshot':
            continue
        else:
            caught_b = rng.random() < probability_b
        if caught_b:
            second.add(defect)
    if regime == 'changed-snapshot':
        final = final_population(set(range(size)), first, set(range(size, size + 10)))
        second = {defect for defect in sorted(final) if rng.random() < .5}
        actual_unseen = len(final - second)
    else:
        actual_unseen = size - len(first | second)
    return len(first), len(second), len(first & second), actual_unseen, unseen_estimate(first, second)


def expected_unseen(size: int, regime: str) -> float:
    # Exact marginal expectations under the explicitly synthetic generators.
    return {'independent': .25 * size, 'unequal-abilities': .1875 * size,
            'shared-difficulty': .41 * size, 'common-blind-spot': .52 * size,
            'dependent-reports': .4375 * size, 'changed-snapshot': .25 * size + 5}[regime]


def main():
    results = []
    for size in (40, 100):
        for regime in REGIMES:
            seed_hash = hashlib.sha256(f'{SEED}|{size}|{regime}'.encode()).digest()
            rng = random.Random(int.from_bytes(seed_hash[:8], 'big'))
            rows, stream_hash = [], hashlib.sha256()
            for _ in range(TRIALS):
                row = trial(size, regime, rng)
                rows.append(row)
                stream_hash.update((json.dumps(row, separators=(',', ':')) + '\n').encode())
            actual = [row[3] for row in rows]
            estimated = [row[4] for row in rows]
            errors = [estimate - truth for estimate, truth in zip(estimated, actual)]
            nonzero = sum(truth > 0 for truth in actual)
            results.append({'size': size, 'regime': regime, 'trials': TRIALS,
                'seed_hex': seed_hash[:8].hex(), 'trial_stream_sha256': stream_hash.hexdigest(),
                'mean_actual_unseen': statistics.mean(actual),
                'theoretical_mean_actual_unseen': expected_unseen(size, regime),
                'mean_naive_estimated_unseen': statistics.mean(estimated),
                'mean_error': statistics.mean(errors),
                'mean_error_monte_carlo_standard_error': statistics.stdev(errors) / math.sqrt(TRIALS),
                'actual_nonzero_trials': nonzero,
                'fraction_under_half_actual_given_nonzero': sum(
                    truth > 0 and estimate < truth / 2 for estimate, truth in zip(estimated, actual)) / nonzero,
                'fraction_zero_estimate_with_unseen': sum(
                    truth > 0 and estimate == 0 for estimate, truth in zip(estimated, actual)) / TRIALS,
                'fraction_zero_overlap': sum(row[2] == 0 for row in rows) / TRIALS,
                'first_five_trials': rows[:5],
                'closed_population': regime != 'changed-snapshot',
                'homogeneous_defect_capture': regime in {'independent', 'unequal-abilities'},
                'independent_reports_given_fixed_defect': regime != 'dependent-reports'})
    output = {'status': 'synthetic-assumption-stress-test-only', 'seed': SEED,
              'protocol_sha256': hashlib.sha256((HERE / 'SIMULATION-PROTOCOL.md').read_bytes()).hexdigest(),
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'results': results,
              'live_review_policy': None, 'empirical_code_review_gain_established': False}
    (HERE / 'simulation-results.json').write_text(json.dumps(output, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'scenarios': len(results), 'trials': len(results)*TRIALS,
                      'empirical_gain_claim': False}))


if __name__ == '__main__':
    main()
