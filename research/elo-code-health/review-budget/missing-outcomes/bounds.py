#!/usr/bin/env python3
"""Fixed-forecast sensitivity; null labels are never changed or imputed.

CLAIM(sharp-bound): independent choices of unknown binary labels minimize or
maximize an additive loss difference row by row [PROTOCOL.md; test_bounds].
"""
import hashlib
import itertools
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
MODELS = HERE.parent / 'models'
sys.path.insert(0, str(MODELS))
from forecast import Observation, features, fit_predict, observations, previous_state


def contribution(outcome, baseline, candidate, baseline_factor=1.0):
    return baseline_factor * (outcome - baseline) ** 2 - (outcome - candidate) ** 2


def bounds(records, baseline_factor=1.0):
    """Return exact extrema conditional on fixed forecasts, not refitted models."""
    lower = upper = 0.0
    for row in records:
        outcome = row['outcome']
        if outcome is not None and type(outcome) is not bool:
            raise ValueError('Outcome must be literal Boolean or null')
        possibilities = (0, 1) if outcome is None else (int(outcome),)
        values = [contribution(y, row['baseline'], row['candidate'], baseline_factor)
                  for y in possibilities]
        lower += min(values)
        upper += max(values)
    if not records:
        raise ValueError('No opportunities')
    return [lower / len(records), upper / len(records)]


def enumerate_bounds(records, baseline_factor=1.0):
    """Slow independent full-completion oracle for the small frozen corpus."""
    unknown = [i for i, row in enumerate(records) if row['outcome'] is None]
    totals = []
    for completion in itertools.product((0, 1), repeat=len(unknown)):
        labels = [row['outcome'] for row in records]
        for index, label in zip(unknown, completion):
            labels[index] = label
        baseline_loss = sum((int(y) - row['baseline']) ** 2 for y, row in zip(labels, records))
        candidate_loss = sum((int(y) - row['candidate']) ** 2 for y, row in zip(labels, records))
        totals.append((baseline_factor * baseline_loss - candidate_loss) / len(records))
    return [min(totals), max(totals)]


def main():
    training_path = MODELS / 'structured-training.jsonl'
    raw = [json.loads(line) for line in training_path.read_text().splitlines()]
    known, _ = observations(raw)
    preserved = json.loads((MODELS / 'accepted-results.json').read_text())
    saved_predictions = {(r['group'], r['ordinal']): r for r in preserved['loco']['predictions']}
    eligible = [r for r in raw if type(r.get('ordinal')) is int and r['ordinal'] > 1]
    records = []
    for group in sorted({r['group_id'] for r in eligible}):
        train = [r for r in known if r.group != group]
        targets = [r for r in eligible if r['group_id'] == group]
        # Outcome zero here is only the required unused test-container slot;
        # no target outcome enters fit_predict, and saved labels remain null.
        test = [Observation(group, r['project'], r['ordinal'], 0, features(r),
                            tuple(previous_state(r)[:2])) for r in targets]
        base, _ = fit_predict(train, test, 'pooled')
        elo, _ = fit_predict(train, test, 'anchored_elo', (8, 'decay'))
        for row, baseline, candidate in zip(targets, base, elo):
            label = row.get('documented_accepted_consequential_discovery')
            if label is not None and type(label) is not bool:
                raise ValueError('Unsupported target label')
            identity = (group, row['ordinal'])
            if type(label) is bool:
                saved = saved_predictions[identity]['predictions']
                if abs(baseline - saved['pooled']) > 1e-12 or abs(candidate - saved['anchored_elo']) > 1e-12:
                    raise ValueError('Known predictions differ from preserved evaluation')
            records.append(dict(group=group, ordinal=row['ordinal'], outcome=label,
                                baseline=baseline, candidate=candidate))
    results = {}
    for name, factor in [('loss_improvement', 1.0), ('ten_percent_gate', 0.9)]:
        sharp = bounds(records, factor)
        enumerated = enumerate_bounds(records, factor)
        if any(abs(a - b) > 1e-12 for a, b in zip(sharp, enumerated)):
            raise ValueError('Additive bounds differ from full enumeration')
        results[name] = dict(lower=sharp[0], upper=sharp[1], enumeration_agrees=True)
    positives = sum(row['outcome'] is True for row in records)
    unknown = sum(row['outcome'] is None for row in records)
    output = dict(status='exploratory-fixed-forecast-sensitivity',
                  training_sha256=hashlib.sha256(training_path.read_bytes()).hexdigest(),
                  rows=len(records), known=len(records)-unknown, unknown=unknown,
                  completions=2 ** unknown, known_predictions_match_preserved=True,
                  prevalence_bounds=[positives / len(records), (positives+unknown) / len(records)],
                  bounds=results, predictions=records,
                  limits=['Bounds condition on fixed forecasts and do not refit hypothetical labels.',
                          'Only observed later reviews enter; unperformed reviews remain outside.',
                          'Accepted findings are proxies and group independence is unestablished.'])
    (HERE / 'results.json').write_text(json.dumps(output, indent=2, allow_nan=False)+'\n')
    print(json.dumps({key: value for key, value in output.items() if key != 'predictions'}, indent=2))


if __name__ == '__main__':
    main()
