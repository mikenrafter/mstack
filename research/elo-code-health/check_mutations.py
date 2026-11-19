"""Run plausible evaluator defects in isolated copies, preserving the real run."""
import json
import subprocess
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parent
original = (root / 'replay.py').read_text()
mutations = {
    'future_leakage': ('training = commits[:cutoff]', 'training = commits'),
    'reversed_elo_update': ('change = k * (actual - expected)', 'change = k * (expected - actual)'),
    'overselect_ties': ('weight = min(1.0, remaining / len(files))', 'weight = 1.0'),
}
results = []
for name, (before, after) in mutations.items():
    assert original.count(before) == 1, name
    with tempfile.TemporaryDirectory() as directory:
        temporary = Path(directory)
        (temporary / 'replay.py').write_text(original.replace(before, after))
        (temporary / 'test_replay.py').write_bytes((root / 'test_replay.py').read_bytes())
        run = subprocess.run(['python3', '-m', 'unittest', '-q', 'test_replay'],
                             cwd=directory, capture_output=True, text=True)
        killed = run.returncode != 0 and 'FAIL:' in run.stderr
        results.append(dict(mutation=name, killed=killed, exit_code=run.returncode,
                            failing_tests=[line for line in run.stderr.splitlines()
                                           if line.startswith('FAIL:')]))
(root / 'mutation-checks.json').write_text(json.dumps(results, indent=2) + '\n')
print(json.dumps(results, indent=2))
raise SystemExit(0 if all(r['killed'] for r in results) else 1)
