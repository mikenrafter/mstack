"""Revision-specific change features available at assignment of a review.

The reviewed target SHA is the input snapshot, not a future outcome. Neither
final dispositions nor the current working tree enter the diff. Missing Git
objects leave explicit unknowns. Output is observational, not a risk verdict.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPOS = HERE.parent.parent.parent.parent
STATE_PATH = re.compile(r'(?:^|[/_.-])(?:db|database|persist\w*|storage|session\w*|state\w*|sync\w*|job\w*|cancel\w*|lock\w*|lease\w*|supervisor\w*|migrat\w*)(?:[/_.-]|$)', re.I)
CODE_SUFFIXES = {'.rs', '.dart', '.ts', '.tsx', '.js', '.jsx', '.py', '.nix', '.sh',
                 '.kt', '.kts', '.java', '.c', '.h', '.cpp', '.hpp', '.swift'}


def git(repository, *arguments):
    return subprocess.check_output(['git', '-C', str(repository), *arguments], text=True,
                                   stderr=subprocess.PIPE)


def summarize_numstat(text):
    files, additions, deletions, binary = [], 0, 0, 0
    source_files, source_changes, test_changes = 0, 0, 0
    for line in text.splitlines():
        if not line:
            continue
        added, removed, path = line.split('\t', 2)
        files.append(path)
        if added == '-' or removed == '-':
            binary += 1
            continue
        count = int(added) + int(removed)
        additions += int(added)
        deletions += int(removed)
        if Path(path).suffix not in CODE_SUFFIXES:
            continue
        if re.search(r'(?:^|/)(?:tests?|__tests__|fixtures)(?:/|$)|(?:_test|\.test|\.spec)\.', path):
            test_changes += count
        else:
            source_files += 1
            source_changes += count
    return dict(changed_files=len(files), additions=additions, deletions=deletions,
                changed_lines=additions + deletions, binary_files=binary,
                source_files=source_files, source_changed_lines=source_changes,
                test_changed_lines=test_changes,
                directories=len({str(Path(p).parent) for p in files}),
                state_path_files=sum(bool(STATE_PATH.search(p)) for p in files),
                paths=files)


def snapshot_features(repository, base, target):
    if not base or not target:
        return dict(status='unknown', reason='base-or-target-not-recorded')
    try:
        before = git(repository, 'rev-parse', '--verify', str(base) + '^{commit}').strip()
        after = git(repository, 'rev-parse', '--verify', str(target) + '^{commit}').strip()
        text = git(repository, '-c', 'core.quotePath=false', 'diff', '--no-ext-diff',
                   '--no-renames', '--numstat', before, after)
        return dict(status='observed', base=before, target=after,
                    same_snapshot=before == after, **summarize_numstat(text))
    except subprocess.CalledProcessError as error:
        return dict(status='unknown', reason='git-objects-or-repository-unavailable',
                    diagnostic=error.stderr.strip()[-500:])


def main():
    groups_path = HERE / 'corpus/groups.jsonl'
    rounds_path = HERE / 'corpus/rounds.jsonl'
    groups = {g['group_id']: g for g in map(json.loads, groups_path.read_text().splitlines())}
    rounds = list(map(json.loads, rounds_path.read_text().splitlines()))
    rows = []
    for row in rounds:
        group = groups[row['group_id']]
        repository = REPOS / row['project']
        previous = row['features_before_round'].get('previous_reviewed_sha')
        base = previous or group.get('base')
        features = snapshot_features(repository, base, row.get('reviewed_sha'))
        rows.append(dict(group_id=row['group_id'], ordinal=row['ordinal'], round=row['round'],
                         project=row['project'], source=row['source'],
                         snapshot_role='input code version known before this review outcome',
                         comparison_role='previous reviewed snapshot, or initial declared base',
                         features=features))
    (HERE / 'snapshot-features.jsonl').write_text(''.join(json.dumps(r, sort_keys=True) + '\n' for r in rows))
    counts = dict(observed=sum(r['features']['status'] == 'observed' for r in rows),
                  unknown=sum(r['features']['status'] == 'unknown' for r in rows),
                  same_snapshot=sum(r['features'].get('same_snapshot', False) for r in rows),
                  rows=len(rows),
                  input_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in [groups_path, rounds_path]},
                  limitations=['Path names are coarse scope hints, not established concurrency/state defects.',
                               'Recorded reviewed revisions do not establish optional policy eligibility.',
                               'Inline tests share production file counts.',
                               'No wall-clock chronology is inferred from a filename or file mtime.'])
    (HERE / 'snapshot-summary.json').write_text(json.dumps(counts, indent=2) + '\n')
    print(json.dumps(counts, indent=2))


if __name__ == '__main__':
    main()
