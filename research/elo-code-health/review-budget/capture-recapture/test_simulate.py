import unittest
from simulate import final_population, unseen_estimate


class CaptureTests(unittest.TestCase):
    def test_hand_computed_overlap(self):
        # WHY: CLAIM(chapman-unseen). Nhat=4*5/3-1=17/3; union=5; unseen=2/3.
        self.assertAlmostEqual(unseen_estimate({1, 2, 3}, {2, 3, 4, 5}), 2/3)

    def test_no_overlap_does_not_mean_no_unseen(self):
        # WHY: CLAIM(chapman-unseen). Nhat=4*5-1=19, union=7; unseen=12.
        self.assertEqual(unseen_estimate({1, 2, 3}, {4, 5, 6, 7}), 12)

    def test_naive_empty_and_identical_lists_are_not_ground_truth(self):
        # WHY: CLAIM(chapman-unseen). A naive zero can coexist with an arbitrary
        # undetected population. Pin the mathematical pathology, not an approval.
        self.assertEqual(unseen_estimate(set(), set()), 0)
        self.assertEqual(unseen_estimate({1, 2, 3}, {1, 2, 3}), 0)
        self.assertEqual(unseen_estimate({1, 2, 3}, {1}), 0)

    def test_changed_population(self):
        # WHY: CLAIM(population-transition). Fixed first-review findings must leave
        # the population; newly introduced defects must enter its denominator.
        final = final_population({1, 2, 3, 4}, {1, 2}, {5})
        self.assertEqual(final, {3, 4, 5})
        self.assertEqual(final - {3, 5}, {4})
        with self.assertRaises(ValueError):
            final_population({1}, {2}, set())
        with self.assertRaises(ValueError):
            final_population({1}, set(), {1})


if __name__ == '__main__':
    unittest.main()
