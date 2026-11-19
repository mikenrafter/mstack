"""Ensure the independent arithmetic checks catch specified wrong equations."""
import inspect
import io
import json
from pathlib import Path
import unittest
import demonstration
import test_demonstration

mutations = [
    ('count_likelihood', 'math.comb(trials, findings) * q ** findings', 'q ** findings',
     'test_exact_finite_count_likelihood', 'omit count permutations'),
    ('residual_risk', ' / (1 - q)', '',
     'test_conditional_mixture', 'omit conditional normalization'),
    ('utility', 'avoided_loss - fix_hazard_cost - review_cost',
     'avoided_loss + fix_hazard_cost - review_cost',
     'test_immediate_equal_yield_has_equal_utility', 'reward fix-induced hazard'),
]
results = []
for symbol, before, after, test_name, description in mutations:
    original = getattr(demonstration, symbol)
    namespace = dict(vars(demonstration))
    source = inspect.getsource(original)
    if before not in source:
        raise ValueError(f'Mutation target absent: {description}')
    exec(source.replace(before, after), namespace)
    replacement = namespace[symbol]
    setattr(demonstration, symbol, replacement)
    setattr(test_demonstration, symbol, replacement)
    try:
        outcome = unittest.TextTestRunner(stream=io.StringIO()).run(
            unittest.TestSuite([test_demonstration.IdentifiabilityTests(test_name)]))
        results.append({'mutation': description, 'caught': bool(outcome.failures),
                        'errors': len(outcome.errors)})
    finally:
        setattr(demonstration, symbol, original)
        setattr(test_demonstration, symbol, original)
Path(__file__).with_name('mutation-results.json').write_text(json.dumps(results, indent=2) + '\n')
print(json.dumps(results))
if not all(result['caught'] and not result['errors'] for result in results):
    raise SystemExit('An intended mutation survived or failed without an assertion')
