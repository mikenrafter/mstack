"""WHY: record work-grounded check-ins without imposing an upfront planning gate."""
import copy
import datetime
import json
from pathlib import Path
import unittest
from test_review_dialogue import DialogueLedger


class CheckIn(unittest.TestCase):
    def setUp(self):
        self.ledger = DialogueLedger(self)
        self.note = {
            'agent': 'sonnet-job-17',
            'started_at': (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=5)).isoformat(),
            'inspected_files': ['src/cancel.py', 'tests/test_cancel.py'],
            'ambiguities': ['Whether partial output is retained.'],
            'questions': [
                {'question': 'Why a second cancellation registry?', 'answer': 'I assumed cancellation survives restart.'},
                {'question': 'Where did deleting partial output come from?', 'answer': 'It was an unconfirmed assumption.'}],
            'pushback': 'Existing job state is sufficient; restart persistence is outside this batch.',
            'resolution': 'Remove registry, retain partial output, test prevention of later UI updates.'}

    def call(self, note=None):
        path = self.ledger.file('checkin.json', json.dumps(self.note if note is None else note))
        return self.ledger.call('implementation-check', '--file', path)

    def test_record_actual_work_dialogue_without_a_prior_proposal(self):
        # CLAIM(implementation-checkin): implementation already started; no proposal READY required.
        code, out, err = self.call()
        self.assertEqual(code, 0, out + err)
        record = self.ledger.data()['implementation_checks'][-1]
        self.assertEqual(record['agent'], self.note['agent'])
        self.assertEqual(record['questions'], self.note['questions'])
        self.assertEqual(record['inspected_files'], self.note['inspected_files'])
        self.assertGreaterEqual(record['elapsed_s'], 299)
        self.assertNotIn('plan', self.ledger.data())

    def test_accept_short_completed_batch_without_waiting(self):
        # CLAIM(implementation-checkin): the handoff check must not delay a short task.
        self.note['started_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.assertEqual(self.call()[0], 0)
        self.assertLess(self.ledger.data()['implementation_checks'][-1]['elapsed_s'], 60)

    def test_reject_missing_answers_files_and_pushback_without_mutation(self):
        # CLAIM(implementation-checkin): a bare 'looks fine' is not the requested exchange.
        for key, invalid in [('questions', []), ('questions', [{'question': 'why?', 'answer': ''}] * 2),
                             ('inspected_files', []), ('inspected_files', ['x'] * 6),
                             ('inspected_files', ['same.py', 'same.py']), ('pushback', ' '),
                             ('started_at', '2026-11-16T10:00:00'), ('started_at', '9999-01-01T00:00:00Z')]:
            with self.subTest(key=key, invalid=invalid):
                note = copy.deepcopy(self.note)
                note[key] = invalid
                before = Path(self.ledger.path).read_bytes()
                code, _, _ = self.call(note)
                self.assertEqual(code, 2)
                self.assertEqual(Path(self.ledger.path).read_bytes(), before)

    def test_reject_exact_replay_but_keep_distinct_followup(self):
        # CLAIM(implementation-checkin): a copied exchange must not become a second observation.
        self.assertEqual(self.call()[0], 0)
        self.assertEqual(self.call()[0], 2)
        self.note['questions'][0] = {'question': 'Does the real caller retain partial output?',
                                    'answer': 'Yes; I exercised the caller with cancellation.'}
        self.assertEqual(self.call()[0], 0)
        self.assertEqual(len(self.ledger.data()['implementation_checks']), 2)
