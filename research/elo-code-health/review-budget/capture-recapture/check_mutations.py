"""Isolated checks of three plausible wrong synthetic accounting rules."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
source = (HERE / 'simulate.py').read_text()
mutations = {
    'union-instead-of-overlap': ('overlap = len(first & second)', 'overlap = len(first | second)'),
    'omit-already-observed-subtraction': (
        'return (len(first) - overlap) * (len(second) - overlap) / (overlap + 1)',
        'return len(first) * len(second) / (overlap + 1)'),
    'forget-introduced-defects': ('return (initial - removed) | introduced', 'return initial - removed'),
}
results = []
for name, (before, after) in mutations.items():
    if source.count(before) != 1:
        raise ValueError(f'Mutation site changed: {name}')
    with tempfile.TemporaryDirectory(prefix='capture-mutant-') as directory:
        temporary = Path(directory)
        (temporary / 'simulate.py').write_text(source.replace(before, after))
        (temporary / 'test_simulate.py').write_bytes((HERE / 'test_simulate.py').read_bytes())
        run = subprocess.run([sys.executable, '-m', 'unittest', 'test_simulate.py'],
                             cwd=temporary, capture_output=True, text=True)
        results.append({'name': name, 'caught': run.returncode == 1 and 'AssertionError' in run.stderr})
(HERE / 'simulation-mutations.json').write_text(json.dumps(results, indent=2)+'\n')
print(json.dumps(results))
raise SystemExit(0 if all(row['caught'] for row in results) else 1)
