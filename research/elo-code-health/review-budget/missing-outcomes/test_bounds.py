import unittest
from bounds import bounds, enumerate_bounds


class BoundTests(unittest.TestCase):
    def test_hand_computed_extremes(self):
        # WHY: CLAIM(sharp-bound). Unknown labels must permit both completions.
        # Known contribution .04-.09=-.05; unknown contribution -.6 or+.6.
        rows = [{'outcome': True, 'baseline': .8, 'candidate': .7},
                {'outcome': None, 'baseline': .2, 'candidate': .8}]
        lower, upper = bounds(rows)
        self.assertAlmostEqual(lower, -.325)
        self.assertAlmostEqual(upper, .275)
        gate = bounds(rows, .9)
        self.assertAlmostEqual(gate[0], -.329)
        self.assertAlmostEqual(gate[1], .241)
        self.assertIsNone(rows[1]['outcome'])

    def test_extremes_match_full_loss_enumeration(self):
        # WHY: CLAIM(sharp-bound). Full squared-loss completion is an independent oracle.
        rows = [{'outcome': None, 'baseline': .1, 'candidate': .7},
                {'outcome': False, 'baseline': .4, 'candidate': .2},
                {'outcome': None, 'baseline': .8, 'candidate': .3}]
        for factor in (1, .9):
            for actual, expected in zip(bounds(rows, factor), enumerate_bounds(rows, factor)):
                self.assertAlmostEqual(actual, expected)

    def test_numeric_unknown_is_not_a_negative(self):
        # WHY: CLAIM(sharp-bound). A numeric sentinel cannot silently be scored as false.
        with self.assertRaises(ValueError):
            bounds([{'outcome': 0, 'baseline': .2, 'candidate': .8}])
        with self.assertRaises(ValueError):
            bounds([])


if __name__ == '__main__':
    unittest.main()
