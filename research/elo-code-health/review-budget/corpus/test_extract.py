import copy
from pathlib import Path
import unittest
from unittest import mock

import extract


class ExtractTests(unittest.TestCase):
    def parse(self, data):
        return extract.parse_ledger(data, extract.ROOT/'fixture.research/change.ledger.json', 'fixturehash')

    def fixture(self):
        return {'rounds': [{'n':1,'tier':1,'score':8,'verdict':'APPROVE','reviewer':'a'},
                           {'n':2,'tier':2,'score':5,'verdict':'CHANGES','reviewer':'b'}],
                'findings': {'S1': {'round':1,'severity':'nit','needed':'no','status':'resolved','claim':'wording'},
                             'S2': {'round':2,'severity':'should','needed':'yes','status':'resolved','claim':'lost data'}}}

    def test_discovery_once_and_lag(self):
        # WHY: CLAIM(discovery-once); a fixed finding must not recur in every round.
        _, rounds, findings = self.parse(self.fixture())
        self.assertEqual([r['new_finding_ids'] for r in rounds], [['S1'],['S2']])
        self.assertEqual([r['new_accepted_consequential_proxy'] for r in rounds], [0,1])
        self.assertEqual(rounds[1]['features_before_round']['previous_score'],8)
        self.assertEqual(rounds[0]['features_before_round']['previous_score'],None)
        self.assertNotIn('final_status',rounds[1]['features_before_round'])
        changed = self.fixture()
        changed['rounds'][1]['score'] = 1
        changed['findings']['S1']['status']='open'
        self.assertEqual(self.parse(changed)[1][1]['features_before_round'], rounds[1]['features_before_round'])

    def test_missing_findings_unknown(self):
        # WHY: older summary ledgers omit findings, which must not become clean rounds.
        data = {'rounds':[{'n':1,'verdict':'APPROVE'}]}
        _, rounds, _ = self.parse(data)
        self.assertIsNone(rounds[0]['new_reported_consequential'])
        self.assertIsNone(rounds[0]['new_accepted_consequential_proxy'])
        self.assertIsNone(rounds[0]['true_new_valid_consequential'])

    def test_gaps_and_censoring(self):
        # WHY: CLAIM(censor-unobserved); source round numbers do not prove intervening reviews.
        data={'rounds':[{'n':1},{'n':3}],'findings':{}}
        _, rounds, _ = self.parse(data)
        self.assertEqual([r['round'] for r in rounds],[1,3])
        self.assertEqual(rounds[0]['next_recorded_round'],3)
        self.assertEqual(rounds[1]['next_round_status'],'right_censored')
        self.assertIsNone(rounds[1]['next_recorded_round'])

    def test_status_and_severity_do_not_make_ground_truth(self):
        # WHY: nits, declined claims and unresolved serious reports are different outcomes.
        data=self.fixture()
        data['findings']['S2'].update(needed='no',status='open')
        _, rounds, _=self.parse(data)
        self.assertEqual(rounds[1]['new_reported_consequential'],1)
        self.assertEqual(rounds[1]['new_accepted_consequential_proxy'],0)
        self.assertEqual(rounds[1]['new_open_consequential'],1)
        self.assertIsNone(rounds[1]['true_new_valid_consequential'])
        data['findings']['S2']['status']='declined'
        self.assertEqual(self.parse(data)[2][1]['disposition'],'recorded_declined_or_preexisting')

    def test_exact_duplicate_and_unknown_semantic_duplicates(self):
        # WHY: repeated text cannot inflate accepted yield; semantic equivalence needs an audit.
        data=self.fixture()
        data['findings']['S3']=dict(data['findings']['S2'])
        _, rounds, findings=self.parse(data)
        self.assertEqual(rounds[1]['new_accepted_consequential_proxy'],1)
        self.assertEqual(findings[2]['exact_claim_duplicate_of'],'S2')
        self.assertEqual(findings[2]['semantic_duplicate_status'],'unknown')

    def test_unanchored_finding_and_duplicate_round_fail(self):
        # WHY: silently assigning unknown discovery rounds invents chronological evidence.
        for mutation in ['finding','duplicate','descending']:
            data=self.fixture()
            if mutation=='finding': data['findings']['S2']['round']=9
            elif mutation=='duplicate': data['rounds'][1]['n']=1
            else: data['rounds'].reverse()
            with self.assertRaises(ValueError): self.parse(data)

    def test_empty_ledger_round_has_unknown_discovery(self):
        # WHY: ledger omission cannot be interpreted as a negative review outcome.
        _, rounds, findings=self.parse({'rounds':[{'n':1}],'findings':{}})
        with mock.patch.object(extract,'VERIFIED_SUPPLEMENTS',[]):
            extract.augment(rounds,findings)
        self.assertIsNone(rounds[0]['documented_consequential_discovery'])
        self.assertIsNone(rounds[0]['new_reported_consequential'])
        self.assertEqual(rounds[0]['recorded_consequential_lower_bound'],0)

    def test_verified_supplement_discovers_once_and_resolves_later(self):
        # WHY: missing tier-2 reports must count discoveries, not repeat resolved IDs.
        fixture={'rounds':[{'n':1,'tier':2,'score':6,'verdict':'CHANGES'},
                            {'n':2,'tier':2,'score':9,'verdict':'APPROVE'}], 'findings':{}}
        _,rounds,findings=self.parse(fixture)
        reports=[b'SCORE: 6/10\nVERDICT: CHANGES\nT1 [should] [needed for bar: yes] [class: loss] loses state\n',
                 b'SCORE: 9/10\nVERDICT: APPROVE\nT1 resolved\nT2 [nit] [needed for bar: no] [class: wording] label\n']
        maps=[('fixture.research/change',1,'r1.txt'),('fixture.research/change',2,'r2.txt')]
        with mock.patch.object(extract,'VERIFIED_SUPPLEMENTS',maps), mock.patch.object(Path,'read_bytes',side_effect=reports):
            events=extract.augment(rounds,findings)
        self.assertEqual([r['new_finding_ids'] for r in rounds],[['T1'],['T2']])
        self.assertTrue(rounds[0]['documented_accepted_consequential_discovery'])
        self.assertFalse(rounds[1]['documented_consequential_discovery'])
        self.assertFalse(rounds[1]['documented_accepted_consequential_discovery'])
        self.assertEqual(findings[0]['final_status'],'resolved')
        self.assertEqual(events[0]['observed_in_round'],2)
        self.assertEqual(findings[0]['discovery_round'],1)

    def test_changed_supplement_mapping_fails(self):
        # WHY: silently reusing a rewritten report could assign its findings to the wrong round.
        _,rounds,findings=self.parse(self.fixture())
        with mock.patch.object(extract,'VERIFIED_SUPPLEMENTS',[('fixture.research/change',2,'r2.txt')]), mock.patch.object(Path,'read_bytes',return_value=b'SCORE: 9/10\nVERDICT: APPROVE\n'):
            with self.assertRaises(ValueError): extract.augment(rounds,findings)


if __name__=='__main__':
    unittest.main()
