"""Run specified plausible wrong implementations against the independent tests."""
import contextlib
import io
import inspect
import json
from pathlib import Path
import unittest

import forecast
from test_forecast import ForecastTests


def main():
    broken_namespace = dict(vars(forecast))
    exec(inspect.getsource(forecast.logistic_fit).replace('step = 1.0 / lipschitz', 'step = 0.5'), broken_namespace)
    mutations = [
        ('logistic_fit', broken_namespace['logistic_fit'],
         'test_logistic_large_penalty_descends', 'restore unstable fixed gradient step'),
        ('elo_update', lambda rating, outcome, k: rating - k * (outcome - forecast.elo_probability(rating)),
         'test_elo_hand_arithmetic', 'reverse risk update direction'),
        ('effective_k', lambda k, schedule, groups: k,
         'test_dynamic_k_independent_group_oracle', 'erase independent-group decay'),
        ('allocation', lambda outcomes, probabilities, fraction=0.8: {
            'expected_reviews': len(outcomes) * fraction, 'captured_positives': sum(outcomes),
            'missed_positives': 0, 'recall': 1},
         'test_tie_allocation_has_equal_fraction_and_exact_budget', 'pretend every positive is allocated'),
        ('features', lambda row: (float(row.get('score', 0)),),
         'test_future_fields_cannot_change_features', 'read target-round score as a predictor'),
    ]
    result = []
    for symbol, replacement, test_name, description in mutations:
        original = getattr(forecast, symbol)
        setattr(forecast, symbol, replacement)
        # test_forecast imported direct functions, so mutate its binding too.
        import test_forecast
        test_original = getattr(test_forecast, symbol)
        setattr(test_forecast, symbol, replacement)
        try:
            stream = io.StringIO()
            test = unittest.TestSuite([ForecastTests(test_name)])
            outcome = unittest.TextTestRunner(stream=stream).run(test)
            result.append({'mutation': description, 'test': test_name,
                           'caught': not outcome.wasSuccessful(),
                           'failures': len(outcome.failures), 'errors': len(outcome.errors)})
        finally:
            setattr(forecast, symbol, original)
            setattr(test_forecast, symbol, test_original)
    Path(__file__).with_name('mutation-results.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
    if not all(record['caught'] and record['failures'] for record in result):
        raise SystemExit('An intended mutation survived or failed without assertion evidence')


if __name__ == '__main__':
    main()
