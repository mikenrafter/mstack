"""Catch plausible wrong planning formulas without altering the frozen outputs."""
import inspect
import io
import json
from pathlib import Path
import unittest
import planning
import test_planning

mutations = [
    ('population_capture', 'prevalence * sensitivity + (1 - prevalence) * false_positive',
     'prevalence * sensitivity', 'test_null_trigger_cannot_improve_population_capture',
     'ignore trigger false positives'),
    ('critical_capture', '<= .025', '<= .05',
     'test_ten_positives_are_not_sufficient_for_significance', 'relax the fixed significance threshold'),
    ('design_effect', '1 + (cluster_size - 1) * correlation', '1.0',
     'test_design_effect_hand_oracle', 'treat correlated projects as independent'),
]
results = []
for symbol, before, after, test_name, description in mutations:
    original = getattr(planning, symbol)
    namespace = dict(vars(planning))
    source = inspect.getsource(original)
    if before not in source:
        raise ValueError(f'Mutation target absent: {description}')
    exec(source.replace(before, after), namespace)
    replacement = namespace[symbol]
    setattr(planning, symbol, replacement)
    setattr(test_planning, symbol, replacement)
    try:
        outcome = unittest.TextTestRunner(stream=io.StringIO()).run(
            unittest.TestSuite([test_planning.PlanningTests(test_name)]))
        results.append({'mutation': description, 'caught': bool(outcome.failures),
                        'errors': len(outcome.errors)})
    finally:
        setattr(planning, symbol, original)
        setattr(test_planning, symbol, original)
Path(__file__).with_name('mutation-results.json').write_text(json.dumps(results, indent=2) + '\n')
print(json.dumps(results))
if not all(result['caught'] and not result['errors'] for result in results):
    raise SystemExit('An intended mutation survived or failed without an assertion')
