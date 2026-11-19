"""Three explicit manual mutants, each isolated from the reviewed collector."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
source = (HERE / 'collector.py').read_text()
tests = (HERE / 'test_collector.py').read_text()
mutants = [
    ('ignore-reviewed-object', "exact = bool(rounds) and revision(repo, rounds[-1]['sha']) == target", 'exact = True',
     'test_mismatched_reviewed_commit_is_unknown_even_if_claimed_verified'),
    ('erase-source-read-confinement', '    path = confined(root, path)',
     "    root = Path('/')\n    path = confined(root, path)",
     'test_symlink_and_outside_root_are_rejected'),
    ('required-gate-as-extra-review', "result['status'] = 'required-review-still-pending'",
     "result['status'] = 'additional-review-recommended'", 'test_required_gate_cannot_become_optional')
]
results = []
for name, before, after, test in mutants:
    assert source.count(before) == 1, name
    with tempfile.TemporaryDirectory(dir=HERE) as directory:
        path = Path(directory)
        (path / 'collector.py').write_text(source.replace(before, after))
        (path / 'test_collector.py').write_text(tests)
        proc = subprocess.run([sys.executable, '-m', 'unittest', f'test_collector.CollectorTests.{test}'],
                              cwd=path, capture_output=True, text=True)
        caught = proc.returncode == 1 and 'AssertionError' in proc.stderr and 'FAILED (failures=1)' in proc.stderr
        results.append({'mutation': name, 'test': test, 'caught_by_assertion': caught})
print(json.dumps(results, indent=2))
(HERE / 'mutation-results.json').write_text(json.dumps(results, indent=2) + '\n')
if not all(row['caught_by_assertion'] for row in results):
    raise SystemExit('An intended mutation survived or failed outside its assertion.')
