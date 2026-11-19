"""Run plausible wrong bound implementations in isolated temporary copies."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
source = (HERE / 'bounds.py').read_text()
mutations = {
    'unknown-as-negative': ('possibilities = (0, 1) if outcome is None',
                            'possibilities = (0,) if outcome is None'),
    'reverse-lower-extreme': ('lower += min(values)', 'lower += max(values)'),
    'ignore-relative-gate': ('return baseline_factor * (outcome - baseline)',
                             'return 1.0 * (outcome - baseline)'),
}
results = []
for name, (before, after) in mutations.items():
    if source.count(before) != 1:
        raise ValueError(f'Mutation site changed: {name}')
    with tempfile.TemporaryDirectory(prefix='bounds-mutant-') as directory:
        temporary = Path(directory)
        (temporary / 'bounds.py').write_text(source.replace(before, after))
        (temporary / 'test_bounds.py').write_bytes((HERE / 'test_bounds.py').read_bytes())
        run = subprocess.run([sys.executable, '-m', 'unittest', 'test_bounds.py'],
                             cwd=temporary, capture_output=True, text=True,
                             env={**os.environ, 'PYTHONPATH': str(HERE.parent / 'models')})
        caught = run.returncode == 1 and 'AssertionError' in run.stderr
        results.append(dict(name=name, caught=caught, exit_code=run.returncode))
(HERE / 'mutation-results.json').write_text(json.dumps(results, indent=2)+'\n')
print(json.dumps(results))
raise SystemExit(0 if all(row['caught'] for row in results) else 1)
