"""Independent boundary, arithmetic, and leakage checks for the frozen pilot."""
import copy
import math
import unittest
from unittest.mock import patch

from forecast import (Observation, allocation, effective_k, elo_probability,
                      elo_update, features, fit_predict, grouped_folds,
                      logistic_fit, logistic_objective, observations, prior, run)


def raw(group='a', ordinal=2, outcome=True, score=6, verdict='CHANGES'):
    return {'group_id': group, 'project': 'edge', 'ordinal': ordinal,
            'documented_accepted_consequential_discovery': outcome,
            'features_before_round': {'previous_score': score, 'previous_verdict': verdict}}


def sample(group, outcome, ordinal=2):
    return observations([raw(group, ordinal, outcome)])[0][0]


class ForecastTests(unittest.TestCase):
    def test_elo_hand_arithmetic(self):
        # WHY: CLAIM(elo-arithmetic). Catches a reversed risk sign or wrong scale.
        # Equal ratings forecast1/2;32*(1-1/2)=16. A400point gap means10:1 odds.
        self.assertEqual(elo_probability(1500), 0.5)
        self.assertEqual(elo_update(1500, 1, 32), 1516)
        self.assertEqual(elo_update(1500, 0, 32), 1484)
        self.assertAlmostEqual(elo_probability(1900), 10 / 11)
        self.assertAlmostEqual(elo_update(1900, 0, 32), 1870.909090909091)

    def test_dynamic_k_independent_group_oracle(self):
        # WHY: CLAIM(k-groups). Four prior groups halveK; eight divide it by3.
        self.assertEqual(effective_k(32, 'fixed', 400), 32)
        self.assertEqual(effective_k(32, 'decay', 0), 32)
        self.assertEqual(effective_k(32, 'decay', 4), 16)
        self.assertAlmostEqual(effective_k(32, 'decay', 8), 10.666666666666666)
        with self.assertRaises(ValueError):
            effective_k(32, 'decay', -1)

    def test_group_folds_keep_all_rounds_together(self):
        # WHY: CLAIM(group-holdout). A later round of the held change cannot leak.
        rows = [sample('a', True, 2), sample('a', False, 3), sample('b', False)]
        folds = list(grouped_folds(rows))
        self.assertEqual(len(folds), 2)
        self.assertEqual([row.group for row in folds[0][1]], ['b'])
        self.assertEqual([row.ordinal for row in folds[0][2]], [2, 3])
        self.assertEqual([row.group for row in folds[1][1]], ['a', 'a'])

    def test_future_fields_cannot_change_features(self):
        # WHY: CLAIM(predictor-boundary). Final fixes and current verdict leak labels.
        row = raw()
        changed = copy.deepcopy(row)
        changed.update(verdict='APPROVE', score=10, new_accepted_consequential_proxy=99,
                       final_status='fixed', reconstructed_prior_finding_features={'reported_consequential': 50},
                       reviewed_sha='future', next_recorded_round=300,
                       documented_accepted_consequential_discovery=False)
        self.assertEqual(features(row), (1.0, 0.2, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0))
        self.assertEqual(features(row), features(changed))
        changed['features_before_round']['previous_score'] = 2
        self.assertNotEqual(features(row), features(changed))

    def test_unknown_labels_are_excluded_and_counts_are_not_labels(self):
        # WHY: CLAIM(label-unknown). Missing or numeric outcomes must never become0.
        rows, excluded = observations([raw('a', outcome=None), raw('b', outcome=0),
                                       raw('c', ordinal=1), raw('d', outcome=False)])
        self.assertEqual([(row.group, row.outcome) for row in rows], [('d', 0)])
        self.assertEqual(excluded, {'unknown_label': 2, 'first_or_invalid_ordinal': 1})

    def test_one_class_abstains_without_dropping_test_rows(self):
        # WHY: CLAIM(one-class-coverage). A rare-class heldoutgroup must stay evaluated.
        train, test = [sample('a', True), sample('b', True)], [sample('c', False)]
        for model, config in [('pooled', None), ('lag_bucket', None),
                              ('logistic', 1), ('anchored_elo', (32, 'decay'))]:
            predictions, abstained = fit_predict(train, test, model, config)
            self.assertEqual(predictions, [0.75])  # Beta(1+2,1+0) mean3/4.
            self.assertTrue(abstained)
        empty_predictions, abstained = fit_predict([], test, 'pooled')
        self.assertEqual(empty_predictions, [0.5])
        self.assertTrue(abstained)

    def test_global_one_class_does_not_fit(self):
        # WHY: CLAIM(no-one-class-fit). No favorable numeric result from positivesonly.
        result = run([raw('a'), raw('b')])
        self.assertEqual(result['status'], 'insufficient-evidence-no-fit')
        self.assertNotIn('loco', result)

    def test_tie_allocation_has_equal_fraction_and_exact_budget(self):
        # WHY: CLAIM(tie-budget). Arbitrary roworder cannot improvecapture within a tie.
        result = allocation([1, 0, 1], [0.9, 0.5, 0.5])
        self.assertAlmostEqual(result['expected_reviews'], 2.4)
        self.assertAlmostEqual(result['captured_positives'], 1.7)
        self.assertAlmostEqual(result['missed_positives'], 0.3)
        self.assertAlmostEqual(result['recall'], 0.85)
        tied = allocation([1, 0, 1], [0.5, 0.5, 0.5])
        self.assertAlmostEqual(tied['captured_positives'], 1.6)
        self.assertEqual(allocation([1], [0.5], 0)['captured_positives'], 0)

    def test_missing_and_invalid_scores_have_explicit_indicator(self):
        # WHY: CLAIM(score-missing). Unknownscore cannot masqueradeas a real midpoint.
        for score in (None, True, math.nan, 11, -1):
            self.assertEqual(features(raw(score=score))[1:3], (0.0, 1.0))
        self.assertEqual(features(raw(score=5))[1:3], (0.0, 0.0))

    def test_prior_and_cold_bucket_hand_oracle(self):
        # WHY: CLAIM(cold-prior). No trainingmatch must returntrainingonly Beta prior.
        train = [sample('a', True), sample('b', True), sample('c', False)]
        cold = observations([raw('d', ordinal=4, verdict='unknown')])[0]
        self.assertEqual(prior(train), 0.6)  # (2successes+1)/(3rows+2).
        for model, config in [('lag_bucket', None), ('anchored_elo', (32, 'fixed'))]:
            probabilities, fallback = fit_predict(train, cold, model, config)
            self.assertEqual(probabilities, [0.6])
            self.assertFalse(fallback)

    def test_duplicate_round_identity_rejected(self):
        # WHY: CLAIM(real-observation-once). A duplicate export cannot multiply evidence.
        with self.assertRaises(ValueError):
            observations([raw(), raw()])

    def test_logistic_large_penalty_descends(self):
        # WHY: CLAIM(logistic-descent). Fixed step .5 explodes at lambda10.
        # Balanced scores -1/+1 leave only the score coefficient nonzero.
        # The stationarity equation 10*w = 1-sigmoid(w) has root .04878072.
        rows, _ = observations([raw('a', outcome=False, score=0),
                                 raw('b', outcome=True, score=10)])
        history = []
        weights = logistic_fit(rows, 10, history)
        self.assertAlmostEqual(history[0], math.log(2))
        self.assertLess(history[-1], math.log(2))
        self.assertTrue(all(math.isfinite(value) for value in weights + history))
        self.assertTrue(all(after <= before + 1e-14 for before, after in zip(history, history[1:])))
        self.assertAlmostEqual(weights[1], 0.04878072, places=6)
        self.assertTrue(all(abs(weight) < 1e-12 for index, weight in enumerate(weights) if index != 1))
        self.assertAlmostEqual(logistic_objective(rows, [0.0] * 9, 10), math.log(2))

    def test_dynamic_k_counts_groups_once_in_actual_fit(self):
        # WHY: CLAIM(k-groups). Three two-round changes must count as3, not6.
        rows = [sample(group, outcome, ordinal) for group in ('a', 'b', 'c')
                for ordinal, outcome in ((2, True), (3, False))]
        counts = []
        original = effective_k

        def observe(k, schedule, groups):
            counts.append(groups)
            return original(k, schedule, groups)

        with patch('forecast.effective_k', side_effect=observe):
            fit_predict(rows, [sample('held', True)], 'anchored_elo', (32, 'decay'), 17)
        self.assertEqual(counts, [0, 1, 2])


if __name__ == '__main__':
    unittest.main()
