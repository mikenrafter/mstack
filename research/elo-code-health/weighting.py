"""Exploratory block weighting diagnostic; see WEIGHTING-PROTOCOL.md."""
import hashlib
import itertools
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import replay

HERE = Path(__file__).resolve().parent


def expected(left, right):
    """Stable logistic expectation; extreme finite gaps saturate at 0/1."""
    gap = (right - left) / 400 * math.log(10)
    if gap >= 0:
        decay = math.exp(-gap)
        return decay / (1 + decay)
    return 1 / (1 + math.exp(gap))


def block_update(ratings, rates, *, average, reverse=False):
    # CLAIM(block-frozen): pair residuals use block-start ratings [test_three_files].
    files = sorted(rates)
    if len(files) < 2:
        return dict(ratings)
    changes = defaultdict(list)
    pairs = list(itertools.combinations(files, 2))
    if reverse:
        pairs.reverse()
    for left, right in pairs:
        actual = 1 if rates[left] > rates[right] else 0 if rates[left] < rates[right] else 0.5
        change = actual - expected(ratings.get(left, 1500), ratings.get(right, 1500))
        changes[left].append(change)
        changes[right].append(-change)
    scale = 32 / (len(files) - 1) if average else 32
    updated = dict(ratings)
    for file in files:
        updated[file] = ratings.get(file, 1500) + scale * math.fsum(changes[file])
    return updated


def scores(commits, cutoff, eligible, *, average):
    ratings = {}
    blocks = []
    exposures = Counter()
    for start in range(0, cutoff, 25):
        touches, fixes = Counter(), Counter()
        for commit in commits[start:min(start + 25, cutoff)]:
            touches.update(commit.files)
            if replay.fix_label(commit.title):
                fixes.update(commit.files)
        rates = {file: (fixes[file] + 1) / (count + 2) for file, count in touches.items()}
        ratings = block_update(ratings, rates, average=average)
        n = len(touches)
        exposures.update({file: max(0, n - 1) for file in touches})
        blocks.append(dict(start=start, commits=min(25, cutoff-start), files=n,
                           pairs=n*(n-1)//2, comparisons_per_file=max(0,n-1)))
    return ({file: ratings.get(file, 1500) for file in eligible},
            dict(blocks=blocks, total_pairs=sum(b['pairs'] for b in blocks),
                 file_comparison_exposures=dict(sorted(exposures.items())),
                 rating_min=min(ratings.values(), default=1500),
                 rating_max=max(ratings.values(), default=1500)))


def main():
    original = json.loads((HERE / 'results.json').read_text())
    histories = json.loads((HERE / 'history.json').read_text())
    output, exposures = [], []
    for row in original:
        if row['definition'] != 'broad' or row['model'] != 'elo':
            continue
        output.append(dict(row, model='sequential', evaluation_status='exploratory_reused_windows'))
        project = row['project']
        commits = [replay.Commit(c['sha'], c['date'], c['title'], tuple(c['files']))
                   for c in histories[project]]
        eligible = replay.tree_files(replay.ROOT / project, row['training_revision'])
        if len(eligible) != row['eligible_files']:
            raise ValueError('Prediction tree differs from original eligibility')
        for average, name in [(False, 'simultaneous_sum'), (True, 'simultaneous_average')]:
            ratings, detail = scores(commits, row['cutoff'], eligible, average=average)
            measured = replay.metrics(ratings, commits[row['cutoff']:row['end']], 'broad')
            if measured['eligible_fix_touches'] != row['eligible_fix_touches']:
                raise ValueError('Future event denominator differs')
            output.append({**row, **measured, 'model': name,
                           'evaluation_status': 'exploratory_reused_windows'})
            exposures.append(dict(project=project, window=row['window'], model=name, **detail))
    aggregates = []
    for project in sorted({row['project'] for row in output}):
        context = [row for row in original if row['definition'] == 'broad' and row['model'] in
                   {'recent_touch_count', 'fix_count', 'constant_control'}]
        combined = output + context
        for model in ['sequential', 'simultaneous_sum', 'simultaneous_average',
                      'recent_touch_count', 'fix_count', 'constant_control']:
            rows = [r for r in combined if r['project'] == project and r['model'] == model
                    and r['split'] == 'holdout']
            captured = math.fsum(r['captured_fix_touches'] for r in rows)
            total = sum(r['eligible_fix_touches'] for r in rows)
            aggregates.append(dict(project=project, model=model, captured=captured,
                                   total=total, recall=captured / total if total else None))
    payload = dict(evaluation_status='exploratory_reused_windows', results=output,
                   original_holdout_window_aggregates=aggregates, exposures=exposures,
                   sha256={p: hashlib.sha256((HERE / p).read_bytes()).hexdigest() for p in
                           ['WEIGHTING-PROTOCOL.md', 'weighting.py', 'test_weighting.py', 'replay.py', 'history.json',
                            'results.json', 'inventory.json']})
    (HERE / 'weighting-results.json').write_text(json.dumps(payload, indent=2, sort_keys=True)+'\n')
    for aggregate in aggregates:
        print(json.dumps(aggregate))


if __name__ == '__main__':
    main()
