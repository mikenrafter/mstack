"""Independent literal matrix and Chapman arithmetic checks for the public-data diagnostic."""
import unittest
from pathlib import Path

from empirical import parse_matrix, parse_source, pair_record, summarize


def fixture(first=None, second=None, header='ID P 1 2 3 4'):
    first = first or [7, 2, 1, 0, 1, 0] + [0] * 29
    second = second or [8, 0, 0, 1, 1, 0] + [0] * 29
    return ('const int MAX_COL=35;\ntypedef int scores[MAX_COL];\n'
            'const int DEMO_NOV=2;\nconst int DEMO_NOV_ERR=4;\n'
            'scores demo_nov[DEMO_NOV] = { /*\n' + header + '\n------------*/\n' +
            ','.join(map(str, first)) + ',\n' + ','.join(map(str, second)) + '\n};\n')


class EmpiricalTests(unittest.TestCase):
    def test_public_source_matches_independent_parent_tally_and_explicit_anomaly(self):
        # WHY: CLAIM(original-pair-oracle). Parent froze MANUAL-ORACLE.md before receiving parser counts.
        data = (Path(__file__).parent / 'sources/umd-total.cc').read_bytes()
        matrices = parse_source(data)
        self.assertEqual([(m['matrix'], len(m['inspectors']), m['reference_defects']) for m in matrices],
                         [('atm_nov', 12, 29), ('atm_jun', 14, 29), ('pg_nov', 12, 27), ('pg_jun', 14, 27),
                          ('a_nov', 12, 18), ('a_jun', 13, 15), ('b_nov', 12, 15), ('b_jun', 13, 15)])
        first, second = matrices[0]['inspectors'][:2]
        self.assertEqual(first['detections'], [2, 3, 4, 5, 8, 13, 18, 21, 25])
        self.assertEqual(second['detections'], [4, 8, 11, 16, 17, 21, 27])
        pair = pair_record('atm_nov', 'nov', 29, first, second)
        self.assertEqual((pair['first_count'], pair['second_count'], pair['overlap'], pair['observed_union']), (9, 7, 3, 13))
        self.assertEqual((pair['actual_remaining'], pair['estimated_total'], pair['estimated_remaining']), (16, 19, 6))
        pg = matrices[3]
        self.assertEqual(len(pg['anomalies']), 1)
        self.assertEqual(len(pg['header_tokens']) - 2, 29)
        self.assertEqual({row['padding_columns'] for row in pg['inspectors']}, {6})
        with self.assertRaises(ValueError): parse_source(data + b'\n')
        with self.assertRaises(ValueError): parse_matrix((data + b'\n').decode(), 'pg_jun', 14, 27)

    def test_metadata_excluded_and_padding_not_a_reference_population(self):
        # WHY: CLAIM(matrix-boundaries). ID7/P2 are metadata; N=4 comes from declared columns, not union3 or width35.
        matrix = parse_matrix(fixture(), 'demo_nov', 2, 4)
        self.assertEqual(matrix['reference_defects'], 4)
        self.assertEqual(matrix['inspectors'][0]['inspector_id'], 7)
        self.assertEqual(matrix['inspectors'][0]['perspective'], 2)
        self.assertEqual(matrix['inspectors'][0]['detections'], [1, 3])
        self.assertEqual(matrix['inspectors'][1]['detections'], [2, 3])

    def test_chapman_hand_oracle_keeps_total_and_remaining_separate(self):
        # WHY: CLAIM(chapman-targets). Literal sets have nA=nB=2,m=1,U=3,N=4; total9/2-1=3.5, remaining.5.
        result = pair_record('demo_nov', 'nov', 4, {'inspector_id': 7, 'detections': [1, 3]},
                             {'inspector_id': 8, 'detections': [2, 3]})
        self.assertEqual((result['first_count'], result['second_count'], result['overlap'], result['observed_union']), (2, 2, 1, 3))
        self.assertEqual(result['estimated_total'], 3.5)
        self.assertEqual(result['estimated_remaining'], 0.5)
        self.assertEqual(result['actual_remaining'], 1)
        self.assertEqual(result['remaining_error'], -0.5)
        self.assertEqual(result['total_relative_error'], -0.125)

    def test_zero_overlap_and_subset_are_retained(self):
        # WHY: CLAIM(all-pairs). Zero overlap is finite under Chapman; subset captures can falsely estimate zero unseen.
        zero = pair_record('demo_nov', 'nov', 4, {'inspector_id': 1, 'detections': [1]},
                           {'inspector_id': 2, 'detections': [2]})
        subset = pair_record('demo_nov', 'nov', 4, {'inspector_id': 1, 'detections': [1]},
                             {'inspector_id': 2, 'detections': [1, 2]})
        self.assertEqual((zero['overlap'], zero['estimated_total'], zero['estimated_remaining']), (0, 3, 1))
        self.assertEqual((subset['actual_remaining'], subset['estimated_remaining']), (2, 0))
        report = summarize([zero, subset])
        self.assertEqual(report['pairs'], 2)
        self.assertEqual(report['zero_overlap_pairs'], 1)
        self.assertEqual(report['less_than_half_remaining_fraction'], 0.5)  # Strictly less; zero-overlap case is exactly half.
        self.assertEqual(report['zero_estimate_with_reference_unseen_pairs'], 1)

    def test_width_nonbinary_padding_duplicate_and_perspective_refuse(self):
        # WHY: CLAIM(strict-matrix). Malformed source data must not silently create a new reference truth.
        valid = [7, 2, 1, 0, 1, 0] + [0] * 29
        cases = [valid[:-1], valid + [0], [7, 2, 2, 0, 1, 0] + [0] * 29,
                 [7, 2, 1, 0, 1, 0] + [1] + [0] * 28, [7, 4, 1, 0, 1, 0] + [0] * 29]
        for row in cases:
            with self.subTest(row=row):
                with self.assertRaises(ValueError): parse_matrix(fixture(first=row), 'demo_nov', 2, 4)
        with self.assertRaises(ValueError): parse_matrix(fixture(second=valid), 'demo_nov', 2, 4)

    def test_constants_declarations_and_header_refuse(self):
        # WHY: CLAIM(explicit-dimensions). A changed constant or mislabeled header cannot redefine the frozen matrix.
        for text in (fixture().replace('DEMO_NOV_ERR=4', 'DEMO_NOV_ERR=3'),
                     fixture().replace('DEMO_NOV=2', 'DEMO_NOV=3'),
                     fixture().replace('[DEMO_NOV] =', '[OTHER] ='),
                     fixture(header='ID P 1 2 3'), fixture(header='ID X 1 2 3 4'),
                     fixture(header='ID P 1 2 4 3')):
            with self.subTest(text=text):
                with self.assertRaises(ValueError): parse_matrix(text, 'demo_nov', 2, 4)


if __name__ == '__main__':
    unittest.main()
