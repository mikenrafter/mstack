import math
import unittest

import replay
import weighting


class WeightingTests(unittest.TestCase):
    def test_two_files(self):
        # WHY: catches reversed wins or a wrong K; equal expectations give 32/2=16.
        for average in [False, True]:
            self.assertEqual(weighting.block_update({}, {'a': 0.8, 'b': 0.2}, average=average),
                             {'a': 1516, 'b': 1484})

    def test_three_files(self):
        # WHY: CLAIM(block-frozen); a wins twice; b/c lose once and draw together.
        rates = {'a': 0.8, 'b': 0.2, 'c': 0.2}
        self.assertEqual(weighting.block_update({}, rates, average=False),
                         {'a': 1532, 'b': 1484, 'c': 1484})
        self.assertEqual(weighting.block_update({}, rates, average=True),
                         {'a': 1516, 'b': 1492, 'c': 1492})

    def test_conservation_inactive_and_order(self):
        # WHY: catches dropped counter-updates, inactive drift and online update leakage.
        initial = {'a': 1200, 'b': 1700, 'c': 1500, 'inactive': 1800}
        rates = {'a': 0.2, 'b': 0.8, 'c': 0.5}
        for average in [False, True]:
            result = weighting.block_update(initial, rates, average=average)
            self.assertAlmostEqual(math.fsum(result.values()), 6200)
            self.assertEqual(result['inactive'], 1800)
            self.assertEqual(result, weighting.block_update(initial, rates, average=average, reverse=True))

    def test_empty_and_singleton(self):
        # WHY: absent comparisons must preserve ratings and avoid division by zero.
        for rates in [{}, {'a': 0.8}]:
            self.assertEqual(weighting.block_update({'a': 1630}, rates, average=True), {'a': 1630})

    def test_extreme_expectation(self):
        # WHY: summed block updates can create gaps beyond naive exponential range.
        self.assertEqual(weighting.expected(-1000000, 1000000), 0)
        self.assertEqual(weighting.expected(1000000, -1000000), 1)
        self.assertAlmostEqual(weighting.expected(1900, 1500), 10/11)

    def test_runner_and_future_separation(self):
        # WHY: runner must use real block labels and never consume future commits.
        training = [replay.Commit('a', '', 'fix: a', ('a',)),
                    replay.Commit('b', '', 'feature', ('b', 'c'))]
        for average, expected in [(True, {'a': 1516, 'b': 1492, 'c': 1492, 'z': 1500}),
                                  (False, {'a': 1532, 'b': 1484, 'c': 1484, 'z': 1500})]:
            actual, detail = weighting.scores(training, 2, {'a','b','c','z'}, average=average)
            self.assertEqual(actual, expected)
            changed, _ = weighting.scores(training + [replay.Commit('future','','fix:',('b',))],
                                           2, {'a','b','c','z'}, average=average)
            self.assertEqual(changed, actual)
            self.assertEqual(detail['total_pairs'], 3)
            self.assertEqual(detail['file_comparison_exposures'], {'a':2,'b':2,'c':2})


if __name__ == '__main__':
    unittest.main()
