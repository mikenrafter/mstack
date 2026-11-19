"""Feature-boundary and independent arithmetic oracles for the diagnostic."""
import copy
import math
import unittest
from diagnostic import snapshot_join, snapshot_values, within_change_allocation, MODELS


def fixture():
    row = {'group_id': 'a', 'ordinal': 2, 'round': 2, 'project': 'edge',
           'source': {'path': '/ledger', 'sha256': 'source'}, 'reviewed_sha': 'abcd',
           'features_before_round': {'previous_reviewed_sha': 'bcde'}}
    snapshot = {key: copy.deepcopy(row[key]) for key in ('group_id', 'ordinal', 'round', 'project', 'source')}
    snapshot['features'] = {'status': 'observed', 'target': 'abcd0000', 'base': 'bcde0000',
                            'source_changed_lines': 3, 'source_files': 0, 'test_changed_lines': 1,
                            'state_path_files': 0, 'same_snapshot': False}
    return row, snapshot


class DiagnosticTests(unittest.TestCase):
    def test_known_zero_and_unknown_differ(self):
        # WHY: CLAIM(snapshot-missing). A failed snapshot must not look unchanged.
        _, snapshot = fixture()
        snapshot['features'].update(source_changed_lines=0, source_files=0,
                                    test_changed_lines=0, state_path_files=0, same_snapshot=False)
        self.assertEqual(snapshot_values(snapshot), (0.0,) * 10)
        self.assertEqual(snapshot_values(None), (0.0,) * 5 + (1.0,) * 5)
        snapshot['features']['status'] = 'unknown'
        self.assertEqual(snapshot_values(snapshot), (0.0,) * 5 + (1.0,) * 5)

    def test_hand_computed_transform_and_caps(self):
        # WHY: CLAIM(transform-bounds). Tests share1/(3+1+1)=.2, state presence binary.
        _, snapshot = fixture()
        values = snapshot_values(snapshot)
        # Independent 40-digit Decimal logarithm oracle for ln4/ln10001.
        self.assertAlmostEqual(values[0], 0.150513363735610978087399779852, places=12)
        self.assertEqual(values[1:], (0.0, .2, 0.0, 0.0) + (0.0,) * 5)
        snapshot['features'].update(source_changed_lines=100000, source_files=1000,
                                    state_path_files=17, same_snapshot=True)
        capped = snapshot_values(snapshot)
        self.assertEqual(capped[0:2], (1.0, 1.0))
        self.assertEqual(capped[3:5], (1.0, 1.0))

    def test_invalid_counts_have_missing_flags(self):
        # WHY: CLAIM(snapshot-missing). Boolean or nonfinite counts cannot become data.
        for bad in (True, -1, math.nan, math.inf, None):
            _, snapshot = fixture()
            snapshot['features']['source_changed_lines'] = bad
            values = snapshot_values(snapshot)
            self.assertEqual(values[0], 0.0)
            self.assertEqual(values[5], 1.0)
            self.assertEqual(values[7], 1.0)  # Test share also needs a known source count.

    def test_future_outcome_fields_do_not_change_features(self):
        # WHY: CLAIM(snapshot-boundary). Current review findings remain outcomes.
        row, snapshot = fixture()
        before = snapshot_join([row], [snapshot])
        row.update(verdict='APPROVE', score=10, new_accepted_consequential_proxy=99,
                   final_status='resolved', documented_accepted_consequential_discovery=True)
        snapshot.update(outcome=True, final_status='fixed')
        self.assertEqual(snapshot_join([row], [snapshot]), before)
        snapshot['features']['source_changed_lines'] = 44
        self.assertNotEqual(snapshot_join([row], [snapshot]), before)

    def test_snapshot_key_and_revision_mismatch_refuse(self):
        # WHY: CLAIM(snapshot-identity). A different revision must never join by position.
        for field, value in (('source', {'path': '/ledger', 'sha256': 'different'}),
                             ('project', 'other'), ('round', 7)):
            row, snapshot = fixture()
            snapshot[field] = value
            with self.assertRaises(ValueError):
                snapshot_join([row], [snapshot])
        for field in ('target', 'base'):
            row, snapshot = fixture()
            snapshot['features'][field] = 'wrong'
            with self.assertRaises(ValueError):
                snapshot_join([row], [snapshot])
        row, snapshot = fixture()
        snapshot['ordinal'] = 9
        with self.assertRaises(ValueError):
            snapshot_join([row], [snapshot])

    def test_duplicate_snapshot_refuses_and_absence_is_unknown(self):
        # WHY: CLAIM(snapshot-identity). Duplicate rows can multiply feature evidence.
        row, snapshot = fixture()
        with self.assertRaises(ValueError):
            snapshot_join([row], [snapshot, snapshot])
        self.assertEqual(snapshot_join([row], [])[('a', 2)], (0.0,) * 5 + (1.0,) * 5)

    def test_allocation_budget_is_within_every_change(self):
        # WHY: CLAIM(within-change-allocation). Cross-fold priors cannot control budget.
        records = []
        for group, scores in (('a', [.9, .1]), ('b', [.1, .9])):
            for outcome, score in zip((1, 0), scores):
                records.append({'group': group, 'outcome': outcome,
                                'predictions': {model: score for model in MODELS},
                                'ranks': {'source_churn_only': (True, score),
                                          'stateful_then_churn': (True, True, True, score)}})
        results = within_change_allocation(records)
        for model in MODELS:
            self.assertAlmostEqual(results[model]['expected_reviews'], 3.2)
            self.assertAlmostEqual(results[model]['captured_positives'], 1.6)
            self.assertAlmostEqual(results[model]['missed_positives'], .4)
        self.assertEqual(results['always_continue']['missed_positives'], 0)


if __name__ == '__main__':
    unittest.main()
