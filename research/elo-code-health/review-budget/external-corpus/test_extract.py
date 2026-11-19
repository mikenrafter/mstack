import unittest

import extract


class ExternalTests(unittest.TestCase):
    def source(self,number):
        return dict(path=f'fixture-r{number}',sha256=f'fixture{number}')

    def reports(self):
        metadata=dict(project='fixture',reviewed_sha='abc1234',chronology_evidence='fixture')
        return [(1,extract.report('VERDICT: CHANGES\nA1 [should] source:1 loses value\n'),self.source(1),metadata),
                (2,extract.report('VERDICT: APPROVE\nA1 CLOSED; test fails without fix\nNo new findings.\n'),self.source(2),metadata)]

    def test_prompt_exclusion(self):
        # WHY: CLAIM(report-only); requested reply syntax is not an actual verdict.
        with self.assertRaises(ValueError):
            extract.report('Review only.\nReply format: VERDICT: APPROVE|CHANGES then A<n> [should].')

    def test_discovery_resolution_and_censor(self):
        # WHY: repeated status entries must resolve the first report, not add discoveries.
        rows,findings=extract.assemble('fixture',self.reports())
        self.assertEqual([r['new_recorded_findings'] for r in rows],[1,0])
        self.assertEqual([r['documented_consequential_discovery'] for r in rows],[True,False])
        self.assertEqual([r['documented_accepted_consequential_discovery'] for r in rows],[True,False])
        self.assertEqual(findings[0]['resolution_events'][0]['observed_in_round'],2)
        self.assertEqual(rows[1]['next_round_status'],'right_censored')

    def test_approval_without_no_new_evidence_unknown(self):
        # WHY: absence of findings in a partial approval is not a negative.
        rows,_=extract.assemble('fixture',[(1,extract.report('VERDICT: APPROVE\n'),self.source(1),dict(project='fixture',chronology_evidence='fixture'))])
        self.assertIsNone(rows[0]['documented_consequential_discovery'])
        self.assertIsNone(rows[0]['documented_accepted_consequential_discovery'])

    def test_lag(self):
        # WHY: CLAIM(lag-only); changing current outcome cannot change its prior features.
        reports=self.reports()
        rows,_=extract.assemble('fixture',reports)
        self.assertEqual(rows[1]['features_before_round']['previous_verdict'],'CHANGES')
        self.assertIsNone(rows[1]['features_before_round']['previous_score'])
        changed=list(reports)
        changed[1]=(2,extract.report('VERDICT: CHANGES\nB1 [blocker] source:2 break\n'),self.source(2),reports[1][3])
        other,_=extract.assemble('fixture',changed)
        self.assertEqual(rows[1]['features_before_round'],other[1]['features_before_round'])

    def test_repeated_tagged_id_not_new_and_unaccepted_unknown(self):
        # WHY: repeating an unresolved item must not inflate marginal discovery yield.
        reports=self.reports()
        reports[1]=(2,extract.report('VERDICT: CHANGES\nA1 [should] source:1 still loses value\n'),self.source(2),reports[1][3])
        rows,findings=extract.assemble('fixture',reports)
        self.assertEqual(len(findings),1)
        self.assertEqual(rows[1]['repeated_tagged_ids'],['A1'])
        self.assertIsNone(rows[1]['documented_consequential_discovery'])
        self.assertIsNone(rows[0]['documented_accepted_consequential_discovery'])

    def test_nits_and_consider_are_separate(self):
        # WHY: formatting normalization must retain distinct nonconsequential categories.
        parsed=extract.report('VERDICT: APPROVE\nR2-10 [nit] source:1 wording\nT14 [consider] source:2 followup\n')
        self.assertEqual([f['severity'] for f in parsed['findings']],['nit','consider'])
        self.assertEqual(parsed['findings'][0]['finding_id'],'R2-10')

    def test_reordered_or_duplicate_rounds_rejected(self):
        # WHY: future-to-past order would leak outcomes into lagged predictors.
        reports=self.reports()
        for invalid in [list(reversed(reports)),[reports[0],reports[0]]]:
            with self.assertRaises(ValueError): extract.assemble('fixture',invalid)

    def test_final_scope_does_not_supply_common_negative(self):
        # WHY: budget-driven shipping focus may omit should findings despite a clean-looking reply.
        reports=self.reports()
        reports[1][3]['final_budget_round']=True
        rows,_=extract.assemble('fixture',reports)
        self.assertFalse(rows[1]['raw_documented_consequential_discovery'])
        self.assertIsNone(rows[1]['documented_consequential_discovery'])
        self.assertIsNone(rows[1]['documented_accepted_consequential_discovery'])
        self.assertFalse(rows[1]['documented_new_blocker'])


if __name__=='__main__':
    unittest.main()
