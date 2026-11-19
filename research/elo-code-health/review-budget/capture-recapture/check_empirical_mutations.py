"""Three explicit isolated wrong implementations against independent empirical oracles."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
source = (HERE / 'empirical.py').read_text()
test = (HERE / 'test_empirical.py').read_text()
mutations = [
    ('reference-population-from-observed-union', "'reference_defects': expected_defects,",
     "'reference_defects': len(set().union(*(set(r['detections']) for r in inspectors))),",
     'test_metadata_excluded_and_padding_not_a_reference_population'),
    ('ignore-nonzero-padding', 'or any(padding)', 'or False',
     'test_width_nonbinary_padding_duplicate_and_perspective_refuse'),
    ('confuse-total-with-remaining', 'estimated_remaining = estimated_total - observed',
     'estimated_remaining = estimated_total', 'test_chapman_hand_oracle_keeps_total_and_remaining_separate')
]
results = []
for name, before, after, target in mutations:
    assert source.count(before) == 1, name
    with tempfile.TemporaryDirectory(dir=HERE) as directory:
        path = Path(directory)
        (path / 'empirical.py').write_text(source.replace(before, after))
        (path / 'test_empirical.py').write_text(test)
        run = subprocess.run([sys.executable, '-m', 'unittest', f'test_empirical.EmpiricalTests.{target}'],
                             cwd=path, capture_output=True, text=True)
        caught = run.returncode == 1 and 'AssertionError' in run.stderr and 'failures=1' in run.stderr and 'errors=' not in run.stderr
        results.append({'mutation': name, 'test': target, 'caught_by_assertion': caught})
print(json.dumps(results, indent=2))
(HERE / 'empirical-mutations.json').write_text(json.dumps(results, indent=2) + '\n')
if not all(row['caught_by_assertion'] for row in results):
    raise SystemExit('An empirical mutant survived or failed outside an intended assertion.')
