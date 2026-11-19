"""Check parser tests detect evidence loss/leakage without modifying sources."""
import contextlib
import io
import json
from pathlib import Path
import sys
import types
import unittest

HERE=Path(__file__).resolve().parent
source=(HERE/'extract.py').read_text()
mutations={
    'future_round_feature_leak': ('previous = rounds[:index]', 'previous = rounds[:index+1]'),
    'missing_findings_become_zero': ('len(consequential) if explicit else None', 'len(consequential) if explicit else 0'),
    'repeat_discoveries_every_round': ("if f['discovery_round'] == raw['n']", "if f['discovery_round'] <= raw['n']"),
}
results=[]
for name,(before,after) in mutations.items():
    if source.count(before)!=1:
        raise ValueError('Mutation target must be unique')
    module=types.ModuleType('extract')
    module.__file__=str(HERE/'extract.py')
    exec(compile(source.replace(before,after),module.__file__,'exec'),module.__dict__)
    sys.modules['extract']=module
    sys.modules.pop('test_extract',None)
    suite=unittest.defaultTestLoader.loadTestsFromName('test_extract')
    output=io.StringIO()
    with contextlib.redirect_stdout(output),contextlib.redirect_stderr(output):
        result=unittest.TextTestRunner(stream=output).run(suite)
    if result.wasSuccessful() or result.errors:
        raise AssertionError(f'{name}: expected assertion failure, got {output.getvalue()}')
    results.append(dict(mutation=name,detected=True,failed_tests=len(result.failures)))
(HERE/'mutation-results.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results))
