#!/usr/bin/env python3
"""Research-only object-snapshot evidence collector. No review execution or approval."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import resource
import stat
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
POLICY = Path('/home/mini/.agents/skills/build-loop/scripts/review-ledger')
EXPECTED_POLICY_SHA = '7a3d78806ee6750cfa9efa04cee06610e3b0315f29b723f6a232b61903ab5920'
STEPS = {'ARGUE', 'ROUND', 'CHECKPOINT', 'OWNER-OK', 'NIT-CULL', 'FIX-KEPT',
         'STEP-BACK', 'STOP-STUCK', 'STOP-AGREED'}
PENDING = STEPS - {'STOP-STUCK', 'STOP-AGREED'}
CATEGORIES = {'async-wait', 'lock-or-lease', 'cancellation', 'transaction-publication', 'multi-stage-transition'}
GIT_OPTIONS = ['-c', 'core.fsmonitor=false', '-c', 'core.quotePath=true',
               '-c', 'diff.algorithm=myers', '-c', 'diff.mnemonicPrefix=false']
DIFF_OPTIONS = ['diff', '--binary', '--full-index', '--no-renames', '--no-ext-diff', '--no-textconv']


class Refusal(Exception):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(value: dict) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()


def confined(root: Path, path: Path) -> Path:
    absolute = Path(os.path.abspath(path))
    if not absolute.is_relative_to(root):
        raise Refusal('outside-source-root')
    cursor = root
    for part in absolute.relative_to(root).parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise Refusal('symlink-source-path')
    return absolute


def read_source(root: Path, path: Path, limit: int) -> bytes:
    """No-follow directory walk binds each opened parent, with bounded regular-file reads."""
    path = confined(root, path)
    parts = path.relative_to(root).parts
    if not parts:
        raise Refusal('source-is-not-file')
    directory = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in parts[:-1]:
            next_directory = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
            os.close(directory)
            directory = next_directory
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
        try:
            before = os.fstat(fd)
            if not stat.S_ISREG(before.st_mode) or before.st_size > limit:
                raise Refusal('source-type-or-size-limit')
            pieces, remaining = [], limit + 1
            while remaining:
                piece = os.read(fd, min(remaining, 65536))
                if not piece:
                    break
                pieces.append(piece); remaining -= len(piece)
            data = b''.join(pieces)
            after = os.fstat(fd)
            if len(data) > limit:
                raise Refusal('source-size-limit')
            if (before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
                    after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns):
                raise Refusal('source-changed-during-read')
            return data
        finally:
            os.close(fd)
    finally:
        os.close(directory)


def read_json(root: Path, path: Path, limit: int) -> tuple[dict, bytes]:
    data = read_source(root, path, limit)
    value = json.loads(data, parse_constant=lambda value: (_ for _ in ()).throw(Refusal('nonfinite-json')))
    if not isinstance(value, dict):
        raise Refusal('json-object-required')
    return value, data


def run_bounded(argv: list[str], limit: int = 2 * 1024 * 1024) -> bytes:
    def bounds():
        resource.setrlimit(resource.RLIMIT_FSIZE, (limit + 1, limit + 1))
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        environment = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
        completed = subprocess.run(argv, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                                   timeout=10, preexec_fn=bounds,
                                   env={**environment, 'GIT_TERMINAL_PROMPT': '0', 'GIT_OPTIONAL_LOCKS': '0',
                                        'GIT_NO_REPLACE_OBJECTS': '1',
                                        'LC_ALL': 'C'})
        if completed.returncode:
            raise Refusal('read-only-subprocess-failed')
        if stdout.tell() > limit or stderr.tell() > limit:
            raise Refusal('subprocess-output-limit')
        stdout.seek(0)
        return stdout.read(limit + 1)


def git(repo: Path, *arguments: str) -> bytes:
    return run_bounded(['git', '--no-replace-objects', *GIT_OPTIONS, '-C', str(repo), *arguments])


def revision(repo: Path, value: str, full: bool = False) -> str:
    pattern = r'(?:[0-9a-f]{40}|[0-9a-f]{64})' if full else r'[0-9a-f]{7,64}'
    if not isinstance(value, str) or not re.fullmatch(pattern, value):
        raise Refusal('invalid-commit-id')
    resolved = git(repo, 'rev-parse', '--verify', value + '^{commit}').decode().strip()
    if not re.fullmatch(r'(?:[0-9a-f]{40}|[0-9a-f]{64})', resolved):
        raise Refusal('invalid-resolved-commit')
    return resolved


def validate_ledger(ledger: dict):
    number = lambda value: type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 10
    integer = lambda value: type(value) is int and value >= 0
    if ledger.get('schema') != 2:
        raise Refusal('unsupported-ledger-schema')
    if not (isinstance(ledger.get('rounds'), list) and len(ledger['rounds']) <= 500
            and isinstance(ledger.get('findings'), dict) and len(ledger['findings']) <= 5000
            and number(ledger.get('bar')) and integer(ledger.get('approach'))
            and type(ledger.get('checkpoint')) is bool and integer(ledger.get('phase', 0))):
        raise Refusal('malformed-ledger')
    previous_phase, previous_number = 0, 0
    for item in ledger['rounds']:
        if not (isinstance(item, dict) and integer(item.get('n')) and type(item.get('tier')) is int and item.get('tier') in (1, 2)
                and integer(item.get('approach')) and integer(item.get('phase', 0))
                and isinstance(item.get('sha'), str) and isinstance(item.get('reviewer'), str)
                and (item.get('score') is None or number(item['score']))
                and isinstance(item.get('exchanges', []), list)
                and all(isinstance(note, str) and note.strip() for note in item.get('exchanges', []))
                and integer(item.get('exchange_minimum', 2 if item.get('argue_required') else 0))):
            raise Refusal('malformed-ledger-round')
        # Structural history checks do not authenticate that the supplied reviews happened.
        if (item['n'] <= previous_number or item.get('phase', 0) < previous_phase
                or item.get('phase', 0) > ledger.get('phase', 0)):
            raise Refusal('malformed-ledger-round-history')
        previous_phase = item.get('phase', 0)
        previous_number = item['n']
        if 'scores' in item and not (isinstance(item['scores'], dict) and
                all(value is None or number(value) for value in item['scores'].values())):
            raise Refusal('malformed-ledger-scores')
    for field in ('concerns', 'bar_table'):
        if field in ledger and not (isinstance(ledger[field], dict) and all(number(v) for v in ledger[field].values())):
            raise Refusal('malformed-ledger-bars')
    for item in ledger['findings'].values():
        if not (isinstance(item, dict) and item.get('severity') in ('nit', 'should', 'blocker')
                and item.get('status') in ('open', 'fixed', 'resolved', 'declined', 'pre-existing', 'repeat',
                                           'escaped', 'discarded', 'disagree')
                and isinstance(item.get('id'), str)):
            raise Refusal('malformed-ledger-finding')


def canonical_next(ledger_data: bytes) -> dict:
    policy_data = read_source(POLICY.parent, POLICY, 512 * 1024)
    if digest(policy_data) != EXPECTED_POLICY_SHA:
        raise Refusal('unsupported-policy-hash')
    with tempfile.TemporaryDirectory(prefix='ledger-capture-') as temporary:
        copy = Path(temporary) / 'ledger.json'
        copy.write_bytes(ledger_data)
        result = run_bounded([sys.executable, '-I', str(POLICY), '-l', str(copy), 'next'], 65536)
        if copy.read_bytes() != ledger_data:
            raise Refusal('canonical-mutated-ledger-copy')
    if read_source(POLICY.parent, POLICY, 512 * 1024) != policy_data:
        raise Refusal('policy-changed-during-capture')
    text = result.decode('utf-8')
    matched = re.fullmatch(r'([A-Z-]+): ([^\r\n]+)\n?', text)
    if not matched or matched[1] not in STEPS:
        raise Refusal('unknown-canonical-output')
    return {'step': matched[1], 'reason': matched[2], 'stdout': text,
            'script_path': str(POLICY), 'script_sha256': digest(policy_data),
            'ledger_copy_sha256': digest(ledger_data)}


def verify_fact(root: Path, repo: Path, target: str, path: Path) -> tuple[dict, list[tuple[Path, bytes]]]:
    fact, data = read_json(root, path, 65536)
    required = {'category', 'accepted', 'fix_revision', 'diff_sha256', 'artifact_path', 'artifact_sha256'}
    if set(fact) != required or fact['category'] not in CATEGORIES or type(fact['accepted']) is not bool:
        raise Refusal('unsupported-trigger-fact')
    fix = revision(repo, fact['fix_revision'], full=True)
    if git(repo, 'merge-base', target, fix).decode().strip() != fix:
        raise Refusal('fix-not-ancestor-of-object')
    parents = git(repo, 'rev-list', '--parents', '-n', '1', fix).decode().split()
    if len(parents) != 2:
        raise Refusal('fix-must-have-one-parent')
    patch = git(repo, *DIFF_OPTIONS, parents[1], fix, '--')
    if digest(patch) != fact['diff_sha256']:
        raise Refusal('fix-diff-hash-mismatch')
    artifact_path = Path(fact['artifact_path'])
    artifact = read_source(root, artifact_path, 256 * 1024)
    if digest(artifact) != fact['artifact_sha256']:
        raise Refusal('fix-artifact-hash-mismatch')
    return {'category': fact['category'], 'accepted': fact['accepted'],
            'accepted_basis': 'supplied-assertion', 'category_basis': 'supplied-assertion', 'fix_revision': fix,
            'diff_sha256': digest(patch), 'artifact_path': str(artifact_path),
            'artifact_sha256': digest(artifact), 'fact_sha256': digest(data)}, [(path, data), (artifact_path, artifact)]


def store_record(value: dict, directory: Path, kind: str) -> Path:
    directory = confined(HERE, directory)
    directory.mkdir(parents=True, exist_ok=True)
    payload = canonical_bytes(value)
    path = directory / f'{kind}-{digest(payload)}.json'
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o444)
    except FileExistsError:
        if read_source(HERE, path, 2 * 1024 * 1024) != payload:
            raise Refusal('content-address-collision-or-tampering')
    else:
        with os.fdopen(fd, 'wb') as output:
            output.write(payload); output.flush(); os.fsync(output.fileno())
    return path


def capture(args) -> dict:
    root = Path(os.path.abspath(args.source_root))
    if root.resolve(strict=True) != root:
        raise Refusal('symlink-source-root')
    repo = confined(root, Path(args.repo))
    if not repo.is_dir():
        raise Refusal('repo-directory-required')
    ledger_path = Path(args.ledger)
    ledger, ledger_data = read_json(root, ledger_path, 1024 * 1024)
    validate_ledger(ledger)
    target = revision(repo, args.revision, full=True) if args.revision else revision(
        repo, git(repo, 'rev-parse', '--verify', 'HEAD^{commit}').decode().strip(), full=True)
    tree = git(repo, 'rev-parse', target + '^{tree}').decode().strip()
    tree_data = git(repo, 'cat-file', 'tree', tree)
    canonical = canonical_next(ledger_data)
    phase = ledger.get('phase', 0)
    rounds = [row for row in ledger['rounds'] if row.get('phase', 0) == phase]
    result = {'version': 0, 'scope': 'git-object-only', 'current_worktree_coverage': 'unsupported',
              'captured_at_utc': datetime.now(timezone.utc).isoformat(),
              'collector_sha256': digest(read_source(HERE, Path(__file__), 128 * 1024)),
              'execution_allowed': False, 'allocation': 'unresolved', 'outcome': 'unobserved',
              'status': 'insufficient-evidence', 'boundary_observed': False,
              'ledger_path': str(ledger_path), 'ledger_sha256': digest(ledger_data),
              'revision': target, 'git_tree': tree, 'tree_object_sha256': digest(tree_data),
              'canonical': canonical, 'trigger': None, 'reasons': [],
              'historical_optional_boundary': 'unknown-without-authentic-as-of-capture'}
    result['boundary_basis'] = 'canonical-gate-on-supplied-ledger-and-git-object-now'
    result['policy_history_basis'] = 'supplied-ledger-not-independent-proof'
    rechecks = [(ledger_path, ledger_data)]
    if args.fact:
        result['trigger'], fact_rechecks = verify_fact(root, repo, target, Path(args.fact))
        rechecks.extend(fact_rechecks)
    exact = bool(rounds) and revision(repo, rounds[-1]['sha']) == target
    if not exact:
        result['reasons'] = ['stale-review-coverage']
    elif canonical['step'] in PENDING:
        result['status'] = 'required-review-still-pending'
        result['reasons'] = [canonical['reason']]
    elif canonical['step'] == 'STOP-STUCK':
        result['status'] = 'cap-reached-escalate'
        result['reasons'] = [canonical['reason']]
    elif canonical['step'] == 'STOP-AGREED':
        result['boundary_observed'] = True
        if sum(row['tier'] == 2 for row in rounds) >= 2 or sum(row['tier'] == 1 for row in rounds) >= 5:
            result['status'] = 'cap-reached-escalate'
            result['reasons'] = ['Declared review channel has exhausted its cap; no optional slot is inferred.']
        elif result['trigger'] and result['trigger']['accepted']:
            result['status'] = 'additional-review-recommended'
            result['reasons'] = ['Fixed conservative structural-fix trigger; not a learned probability.',
                                 'Object-only shadow candidate. No generic optional-review allocation exists.']
        else:
            result['reasons'] = ['No supported trigger; this does not recommend stopping or prove defect absence.']
    for path, before in rechecks:
        if read_source(root, path, max(len(before), 1)) != before:
            raise Refusal('source-changed-during-capture')
    result['observation_id'] = digest(canonical_bytes(result))
    if args.store:
        result['stored_path'] = str(store_record(result, Path(args.store), 'observation'))
    return result


def record_outcome(args) -> dict:
    observation_path = Path(args.observation)
    observation, raw = read_json(HERE, observation_path, 2 * 1024 * 1024)
    if observation_path.name != f'observation-{digest(raw)}.json' or observation.get('execution_allowed') is not False:
        raise Refusal('invalid-stored-observation')
    outcome, _ = read_json(HERE, Path(args.outcome), 65536)
    if outcome.get('state') == 'unobserved':
        if set(outcome) != {'state', 'reason'} or not isinstance(outcome['reason'], str) or not outcome['reason'].strip():
            raise Refusal('invalid-unobserved-outcome')
    elif outcome.get('state') == 'reported':
        if set(outcome) != {'state', 'report_path', 'report_sha256', 'scope'} or outcome['scope'] not in (
                'all-material-findings', 'blockers-only', 'partial'):
            raise Refusal('invalid-reported-outcome')
        report = read_source(HERE, Path(outcome['report_path']), 256 * 1024)
        if digest(report) != outcome['report_sha256']:
            raise Refusal('outcome-report-hash-mismatch')
    else:
        raise Refusal('unsupported-outcome-state')
    value = {'version': 0, 'record_type': 'outcome', 'observation_sha256': digest(raw),
             'observation_id': observation['observation_id'], 'outcome': outcome,
             'acceptance_or_clean_negative': 'not-inferred'}
    return {**value, 'stored_path': str(store_record(value, Path(args.store), 'outcome'))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    capture_parser = commands.add_parser('capture')
    for flag in ('source-root', 'ledger', 'repo'):
        capture_parser.add_argument('--' + flag, required=True)
    for flag in ('revision', 'fact', 'store'):
        capture_parser.add_argument('--' + flag)
    outcome_parser = commands.add_parser('record-outcome')
    for flag in ('observation', 'outcome', 'store'):
        outcome_parser.add_argument('--' + flag, required=True)
    args = parser.parse_args()
    try:
        result = capture(args) if args.command == 'capture' else record_outcome(args)
    except (Refusal, OSError, ValueError, TypeError, KeyError, subprocess.TimeoutExpired) as exc:
        result = {'version': 0, 'status': 'insufficient-evidence', 'execution_allowed': False,
                  'boundary_observed': False, 'outcome': 'unobserved', 'reasons': [str(exc)]}
        print(json.dumps(result, sort_keys=True)); return 2
    print(json.dumps(result, sort_keys=True)); return 0


if __name__ == '__main__':
    raise SystemExit(main())
