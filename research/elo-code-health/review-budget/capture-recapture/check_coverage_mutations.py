"""Isolated errors that would misstate finite-pool coverage or team variation."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
source = (HERE / 'coverage.py').read_text()
mutations = {
    'intersection-instead-of-union': (
        'unions[team ^ member] | masks[member.bit_length() - 1]',
        'unions[team ^ member] & masks[member.bit_length() - 1]'),
    'forget-never-detected-reference-faults': (
        'mean / reference_count', 'mean / max(1, sum(frequency > 0 for frequency in frequencies))'),
    'wrong-upper-team-quantile': (
        'observed[math.ceil(.95*len(observed))-1]', 'observed[math.ceil(.05*len(observed))-1]'),
}
results = []
for name, (before, after) in mutations.items():
    if source.count(before) != 1:
        raise ValueError(f'Mutation site changed: {name}')
    with tempfile.TemporaryDirectory(prefix='coverage-mutant-') as directory:
        temporary = Path(directory)
        (temporary / 'coverage.py').write_text(source.replace(before, after))
        (temporary / 'test_coverage.py').write_bytes((HERE / 'test_coverage.py').read_bytes())
        run = subprocess.run([sys.executable, '-m', 'unittest', 'test_coverage.py'],
                             cwd=temporary, capture_output=True, text=True)
        caught = run.returncode == 1 and ('AssertionError' in run.stderr or
                 'ValueError: Enumeration disagrees with combinatorial oracle' in run.stderr)
        results.append({'name': name, 'caught': caught})
(HERE / 'coverage-mutations.json').write_text(json.dumps(results, indent=2)+'\n')
print(json.dumps(results))
raise SystemExit(0 if all(row['caught'] for row in results) else 1)
