"""Check that plausible feature-boundary errors fail the diagnostic tests."""
import inspect
import io
import json
from pathlib import Path
import unittest
import diagnostic
import test_diagnostic

mutations = [
    ('snapshot_values', 'return (0.0,) * 5 + (1.0,) * 5', 'return (0.0,) * 10',
     'test_known_zero_and_unknown_differ', 'erase missing snapshot indicators'),
    ('snapshot_values', 'min(math.log1p(source) / math.log1p(10000), 1)',
     'math.log1p(source) / math.log1p(10000)',
     'test_hand_computed_transform_and_caps', 'remove source churn cap'),
    ('snapshot_join', "for field in ('project', 'round', 'source'):", 'for field in ():',
     'test_snapshot_key_and_revision_mismatch_refuse', 'ignore snapshot identity fields'),
]
results = []
for symbol, before, after, test_name, description in mutations:
    original = getattr(diagnostic, symbol)
    namespace = dict(vars(diagnostic))
    source = inspect.getsource(original)
    if before not in source:
        raise ValueError(f'Mutation target absent: {description}')
    exec(source.replace(before, after), namespace)
    replacement = namespace[symbol]
    setattr(diagnostic, symbol, replacement)
    setattr(test_diagnostic, symbol, replacement)
    try:
        outcome = unittest.TextTestRunner(stream=io.StringIO()).run(
            unittest.TestSuite([test_diagnostic.DiagnosticTests(test_name)]))
        results.append({'mutation': description, 'caught': bool(outcome.failures),
                        'errors': len(outcome.errors)})
    finally:
        setattr(diagnostic, symbol, original)
        setattr(test_diagnostic, symbol, original)
Path(__file__).with_name('mutation-results.json').write_text(json.dumps(results, indent=2) + '\n')
print(json.dumps(results))
if not all(result['caught'] and not result['errors'] for result in results):
    raise SystemExit('An intended mutation survived or failed without an assertion')
