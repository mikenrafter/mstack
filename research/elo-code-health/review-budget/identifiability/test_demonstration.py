"""Exact arithmetic oracles for a synthetic, explicitly assumed process."""
from fractions import Fraction as F
import unittest
from demonstration import World, count_likelihood, residual_risk, utility, elo_trace

A, B = World('A', F(1, 5), F(1)), World('B', F(4, 5), F(1, 4))


class IdentifiabilityTests(unittest.TestCase):
    def test_exact_finite_count_likelihood(self):
        # WHY: CLAIM(nonidentifiable-q). Different p/s must give equal count likelihood.
        self.assertEqual(A.finding_probability, F(1, 5))
        self.assertEqual(B.finding_probability, F(1, 5))
        for n, k in ((0, 0), (1, 0), (1, 1), (4, 2), (20, 4)):
            self.assertEqual(count_likelihood(A, n, k), count_likelihood(B, n, k))
        # Four screens, two findings:6*(1/5)^2*(4/5)^2=96/625.
        self.assertEqual(count_likelihood(A, 4, 2), F(96, 625))
        self.assertEqual(sum(count_likelihood(A, 4, k) for k in range(5)), 1)

    def test_immediate_equal_yield_has_equal_utility(self):
        # WHY: CLAIM(immediate-utility). Cannot invent an immediate difference from p.
        for world in (A, B):
            outcome = utility(world.prevalence, world.sensitivity, F(1), F(1, 10), F(100), F(5))
            self.assertEqual(outcome['avoided_defect_loss'], 20)
            self.assertEqual(outcome['fix_hazard_cost'], 2)
            self.assertEqual(outcome['net_utility'], 13)

    def test_conditional_mixture(self):
        # WHY: CLAIM(residual-mixture). No-finding must use Bayes, not zero risk.
        for world, expected in ((A, F(1, 50)), (B, F(31, 50))):
            q = world.finding_probability
            positive = residual_risk(world, F(1), F(1, 10), True)
            negative = residual_risk(world, F(1), F(1, 10), False)
            self.assertEqual(positive, F(1, 10))
            self.assertEqual(negative, 0 if world == A else F(3, 4))
            self.assertEqual(residual_risk(world, F(1), F(1, 10)), expected)
            self.assertEqual(q * positive + (1 - q) * negative, expected)

    def test_frozen_next_review_decisions(self):
        # WHY: CLAIM(next-utility). Same initial finding law allows opposite next actions.
        for finding, expected in ((None, (F(-16, 5), F(179, 20))),
                                  (True, (F(4), F(-11, 4))),
                                  (False, (F(-5), F(95, 8)))):
            for world, net in zip((A, B), expected):
                risk = residual_risk(world, F(1), F(1, 10), finding)
                outcome = utility(risk, world.sensitivity, F(1), F(1, 10), F(100), F(5))
                self.assertEqual(outcome['net_utility'], net)
                self.assertEqual(outcome['decision'], 'review' if net > 0 else 'stop')

    def test_invalid_probabilities_and_impossible_conditioning_refuse(self):
        # WHY: CLAIM(probability-boundary). Undefined conditioning cannot become a score.
        with self.assertRaises(ValueError):
            World('invalid', F(6, 5), F(1))
        with self.assertRaises(ValueError):
            count_likelihood(A, 3, 4)
        with self.assertRaises(ValueError):
            residual_risk(World('none', F(0), F(1)), F(1), F(0), True)
        with self.assertRaises(ValueError):
            residual_risk(World('certain', F(1), F(1)), F(1), F(0), False)

    def test_elo_first_update_arithmetic(self):
        # WHY: CLAIM(elo-input-only). K32 times(0-.5) moves1500 to1484.
        self.assertEqual(elo_trace([0], 32), [1500.0, 1484.0])
        self.assertEqual(elo_trace([1], 8), [1500.0, 1504.0])
        self.assertEqual(elo_trace([1], 64), [1500.0, 1532.0])


if __name__ == '__main__':
    unittest.main()
