"""Frozen-input integration smoke, without modifying subjects or fitting models."""
import collections
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
BASE = HERE.parent.parent
SOURCE_ROOT = Path('/home/mini/Documents/repos')
COLLECTOR = HERE.parent / 'collector.py'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def git(repo, *args):
    return subprocess.run(['git', '-c', 'core.fsmonitor=false', '-C', str(repo), *args],
                          capture_output=True, timeout=20,
                          env={**os.environ, 'GIT_NO_REPLACE_OBJECTS': '1'})

manifest_path = BASE / 'corpus/source-manifest.json'
groups_path = BASE / 'corpus/groups.jsonl'
snapshots_path = BASE / 'snapshot-features.jsonl'
manifest = json.loads(manifest_path.read_text())
groups = {g['source']['path']: g for g in map(json.loads, groups_path.read_text().splitlines())}
snapshots = list(map(json.loads, snapshots_path.read_text().splitlines()))
collector_hash = digest(COLLECTOR)
metadata = dict(started_at_utc=utc(), collector_sha256=collector_hash,
                input_hashes={str(p):digest(p) for p in [manifest_path, groups_path, snapshots_path, HERE/'PROTOCOL.md']},
                source_root=str(SOURCE_ROOT), purpose='historical-object-only integration smoke; not training labels')
records = []
for index, ledger_string in enumerate(manifest['reviewed_ledger_paths'], 1):
    ledger_path = Path(ledger_string)
    group = groups[ledger_string]
    repo = SOURCE_ROOT / group['project']
    row = dict(index=index, group_id=group['group_id'], ledger=ledger_string, repo=str(repo),
               expected_ledger_sha256=manifest['sha256'][ledger_string], started_at_utc=utc(),
               capture_attempted=False, optional_training_eligible=False)
    try:
        row['observed_ledger_sha256'] = digest(ledger_path)
        if row['observed_ledger_sha256'] != row['expected_ledger_sha256']:
            raise ValueError('frozen-ledger-hash-mismatch')
        ledger = json.loads(ledger_path.read_bytes())
        row['ledger_schema'] = ledger.get('schema')
        phase = ledger.get('phase', 0)
        current = [r for r in ledger.get('rounds', []) if r.get('phase',0)==phase]
        if not current:
            raise ValueError('no-current-phase-round')
        latest = current[-1]
        row.update(current_phase=phase, selected_round=latest.get('n'), recorded_revision=latest.get('sha'))
        if not isinstance(latest.get('sha'), str) or not latest['sha']:
            raise ValueError('missing-reviewed-revision')
        resolution = git(repo, 'rev-parse', '--verify', latest['sha']+'^{commit}')
        row['revision_resolution'] = dict(returncode=resolution.returncode,
             stdout=resolution.stdout.decode(errors='replace'), stderr=resolution.stderr.decode(errors='replace'))
        if resolution.returncode:
            raise ValueError('reviewed-revision-unavailable')
        full_revision = resolution.stdout.decode().strip()
        row['revision'] = full_revision
        matching = [s for s in snapshots if s['group_id']==group['group_id'] and s['round']==latest.get('n')]
        row['snapshot_map_target'] = [s.get('features',{}).get('target') for s in matching]
        if len(matching)!=1 or matching[0].get('features',{}).get('target') != full_revision:
            raise ValueError('frozen-snapshot-map-mismatch')
        if digest(COLLECTOR)!=collector_hash:
            raise ValueError('collector-changed-before-capture')
        command = [sys.executable, str(COLLECTOR), 'capture', '--source-root', str(SOURCE_ROOT),
                   '--ledger', ledger_string, '--repo', str(repo), '--revision', full_revision]
        row['command'] = command
        row['capture_attempted'] = True
        start = time.monotonic()
        result = subprocess.run(command, capture_output=True, timeout=45)
        row.update(returncode=result.returncode, elapsed_seconds=time.monotonic()-start)
        for stream in ('stdout','stderr'):
            raw = getattr(result, stream)
            target = HERE/f'{index:02d}.{stream}'
            target.write_bytes(raw)
            row[stream+'_file'] = target.name
            row[stream+'_sha256'] = hashlib.sha256(raw).hexdigest()
        row['parsed_stdout'] = json.loads(result.stdout)
        row['source_unchanged_after'] = digest(ledger_path)==row['expected_ledger_sha256']
        row['collector_unchanged_after'] = digest(COLLECTOR)==collector_hash
        row['smoke_status'] = 'observed' if row['source_unchanged_after'] and row['collector_unchanged_after'] else 'invalid-input-changed'
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        row['smoke_status'] = 'refused-before-capture' if not row['capture_attempted'] else 'invalid-capture'
        row['reason'] = str(error)
    row['finished_at_utc'] = utc()
    records.append(row)
    (HERE/'records.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in records))
metadata.update(finished_at_utc=utc(),groups=len(records),capture_attempted=sum(r['capture_attempted'] for r in records),
                statuses=dict(collections.Counter(r.get('parsed_stdout',{}).get('status',r['smoke_status']) for r in records)),
                collector_unchanged=digest(COLLECTOR)==collector_hash,
                input_files_unchanged=all(digest(Path(p))==h for p,h in metadata['input_hashes'].items()))
outputs=[r['parsed_stdout'] for r in records if 'parsed_stdout' in r]
metadata['execution_all_disabled']=all(o.get('execution_allowed') is False for o in outputs)
metadata['outcomes_all_unobserved']=all(o.get('outcome')=='unobserved' for o in outputs)
metadata['reason_counts']=dict(collections.Counter(reason for o in outputs for reason in o.get('reasons',[])))
(HERE/'summary.json').write_text(json.dumps(metadata,indent=2)+'\n')
print(json.dumps(metadata,indent=2))
