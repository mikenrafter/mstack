"""Run focused tests against in-memory defects without changing analysis files."""
import contextlib
import io
import json
import sys
import types
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
source = (HERE / 'weighting.py').read_text()
mutations = {
    'reverse_outcome': ('change = actual - expected(', 'change = (1 - actual) - expected('),
    'remove_normalization': ('32 / (len(files) - 1) if average else 32', '32'),
    'drop_counter_update': ('changes[right].append(-change)', 'changes[right].append(0)'),
}
results = []
for name, (before, after) in mutations.items():
    if source.count(before) != 1:
        raise ValueError('Mutation target must be unique')
    module = types.ModuleType('weighting')
    module.__file__ = str(HERE / 'weighting.py')
    exec(compile(source.replace(before, after), module.__file__, 'exec'), module.__dict__)
    sys.modules['weighting'] = module
    sys.modules.pop('test_weighting', None)
    suite = unittest.defaultTestLoader.loadTestsFromName('test_weighting')
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
        result = unittest.TextTestRunner(stream=stream).run(suite)
    if result.wasSuccessful() or result.errors:
        raise AssertionError(f'{name}: expected assertion failure, got {stream.getvalue()}')
    results.append(dict(mutation=name, detected=True, failed_tests=len(result.failures)))
(HERE / 'weighting-mutations.json').write_text(json.dumps(results, indent=2)+'\n')
print(json.dumps(results))
