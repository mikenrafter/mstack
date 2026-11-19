import unittest
from coverage import finite_curve


class CoverageTests(unittest.TestCase):
    def test_known_finite_pool(self):
        # WHY: CLAIM(finite-coverage). Singles find2,2,1; pairs find3,3,2;
        # all three find3. Referencefault4 remains unseen by every inspector.
        result = finite_curve(4, [{'inspector_id': 1, 'detections': [1, 2]},
                                  {'inspector_id': 2, 'detections': [2, 3]},
                                  {'inspector_id': 3, 'detections': [3]}])
        self.assertEqual(result['teams_enumerated'], 7)
        self.assertEqual(result['never_detected_reference_faults'], [4])
        rows = result['curve']
        self.assertEqual([row['teams'] for row in rows], [3, 3, 1])
        for actual, expected in zip([row['mean_found'] for row in rows], [5/3, 8/3, 3]):
            self.assertAlmostEqual(actual, expected)
        self.assertEqual(rows[1]['team_p05_found'], 2)
        self.assertEqual(rows[1]['team_p95_found'], 3)
        self.assertEqual(rows[2]['mean_reference_coverage'], .75)
        for actual, expected in zip([row['marginal_mean_found'] for row in rows], [5/3, 1, 1/3]):
            self.assertAlmostEqual(actual, expected)

    def test_no_capture_preserves_reference_denominator(self):
        # WHY: CLAIM(finite-coverage). Nothing detected is no evidence of no defects.
        result = finite_curve(3, [{'inspector_id': 7, 'detections': []}])
        self.assertEqual(result['never_detected_reference_faults'], [1, 2, 3])
        self.assertEqual(result['curve'][0]['mean_reference_coverage'], 0)

    def test_invalid_incidence_data_refuses(self):
        # WHY: CLAIM(finite-coverage). Duplicate people/faults and invalid IDs distort teams.
        for rows in ([], [{'inspector_id': 1, 'detections': [0]}],
                     [{'inspector_id': 1, 'detections': [True]}],
                     [{'inspector_id': 1, 'detections': [1, 1]}],
                     [{'inspector_id': 1, 'detections': [1]}, {'inspector_id': 1, 'detections': [2]}]):
            with self.assertRaises(ValueError):
                finite_curve(3, rows)


if __name__ == '__main__':
    unittest.main()
