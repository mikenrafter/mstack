"""Independent arithmetic oracles for the frozen synthetic planning formulas."""
import unittest
from planning import (population_capture, binomial_tail, critical_capture,
                      reference_power, design_effect)


class PlanningTests(unittest.TestCase):
    def test_null_trigger_cannot_improve_population_capture(self):
        # WHY: CLAIM(random-trigger). Independent trigger must reduce to random80%.
        for prevalence in (.1, .3, .6):
            result = population_capture(prevalence, .3, .3)
            self.assertAlmostEqual(result['recall'], .8)
            self.assertAlmostEqual(result['gain_vs_random'], 0)

    def test_fixed_population_arithmetic_and_oversubscribed_branch(self):
        # WHY: CLAIM(capture-budget). Distinguish sample-negative and sample-positive branches.
        moderate = population_capture(.3, .65, .15)
        self.assertAlmostEqual(moderate['trigger_share'], .3)
        self.assertAlmostEqual(moderate['recall'], .9)
        self.assertAlmostEqual(population_capture(.6, .8, .1)['recall'], 11 / 12)
        self.assertAlmostEqual(population_capture(.9, 1, 0)['recall'], 8 / 9)

    def test_binomial_independent_oracle(self):
        # WHY: CLAIM(positive-count). Ten tosses all positive has probability1/1024.
        self.assertEqual(binomial_tail(10, .5, 10), 1 / 1024)
        self.assertEqual(binomial_tail(10, .5, 11), 0)
        self.assertAlmostEqual(binomial_tail(10, .5, 0), 1)

    def test_ten_positives_are_not_sufficient_for_significance(self):
        # WHY: CLAIM(minimum-information). Even16/16 has nulltailabove.025.
        self.assertGreater(.8 ** 16, .025)
        self.assertLess(.8 ** 17, .025)
        self.assertIsNone(critical_capture(10))
        self.assertIsNone(critical_capture(16))
        self.assertEqual(critical_capture(17), 17)
        self.assertEqual(reference_power(16, .5, 1), 0)

    def test_design_effect_hand_oracle(self):
        # WHY: CLAIM(project-dependence). Three groups of20 atICC.05 inflatevariance1.95.
        result = design_effect(60, 3, .05)
        self.assertEqual(result['mean_cluster_size'], 20)
        self.assertAlmostEqual(result['design_effect'], 1.95)
        self.assertAlmostEqual(result['variance_equivalent_sample'], 400 / 13)

    def test_invalid_inputs_refuse(self):
        # WHY: CLAIM(planning-boundary). Impossible probabilities must not produce a plan.
        with self.assertRaises(ValueError):
            population_capture(1.1, .8, .1)
        with self.assertRaises(ValueError):
            binomial_tail(10, .5, -1)
        with self.assertRaises(ValueError):
            design_effect(60, 0, .1)


if __name__ == '__main__':
    unittest.main()
