"""Additional transition boundaries for the explicit review dialogue protocol."""
import copy
import unittest
import json
from pathlib import Path

from test_review_dialogue import DialogueCase, FOCUS, CLEAN_PASS


class DialogueTransitions(DialogueCase):
    def test_argument_brief_uses_snapshot_after_current_context_changes(self):
        # why: CLAIM(dialogue-focus) discussion must use the review's original evidence.
        # catches: argument brief reading mutable root context instead of round snapshot.
        ledger = self.ready_ledger()
        self.ok(ledger.rnd("s1", CLEAN_PASS))
        changed = copy.deepcopy(FOCUS)
        changed["evidence"] = ["Later evidence applies only to the next review."]
        self.ok(ledger.context(changed))
        brief = ledger.run("brief")
        self.assertIn(FOCUS["evidence"][0], brief)
        self.assertNotIn(changed["evidence"][0], brief)

    def test_phase_transitions_refuse_pending_exchange_without_writes(self):
        # why: CLAIM(dialogue-no-bypass) changing approach or phase must not strand dialogue.
        # catches: hardening or new-approach clearing the pending round from scheduling.
        ledger = self.ready_ledger()
        self.ok(ledger.rnd("s1", CLEAN_PASS))
        for command in ("new-approach", "hardening", "cull"):
            with self.subTest(command=command):
                args = ("--reply", ledger.file("cull.txt", "KEEP: none")) if command == "cull" else ()
                self.refused_unchanged(ledger, lambda: ledger.call(command, *args),
                                       "argu" if command != "cull" else "cull")
                self.assertEqual(ledger.head(), "ARGUE")

    def test_pending_exchange_from_earlier_phase_is_not_hidden(self):
        # why: CLAIM(dialogue-no-bypass) recover pending work even if another writer moved the phase.
        # catches: checking only phase_rounds or the newest appended row.
        ledger = self.ready_ledger()
        self.ok(ledger.rnd("s1", CLEAN_PASS))
        data = ledger.data()
        data["phase"] = 1
        Path(ledger.path).write_text(json.dumps(data))
        self.assertEqual(ledger.head(), "ARGUE")
        self.refused_unchanged(ledger, lambda: ledger.rnd("s2", CLEAN_PASS), "argu")
        self.ok(ledger.exchange())
        self.assertEqual(ledger.head(), "ROUND")

    def test_additional_distinct_exchange_can_revise_completed_round(self):
        # why: CLAIM(dialogue-revision) minimum discussion is not a cap on substantive follow-up.
        # catches: cmd_argue accepting only rounds below their minimum exchange count.
        ledger = self.ready_ledger()
        self.ok(ledger.rnd("s1", CLEAN_PASS))
        self.ok(ledger.exchange())
        self.assertEqual(ledger.head(), "CHECKPOINT")
        self.ok(ledger.exchange(2, tail="SCORE: 5/10\nVERDICT: CHANGES"))
        self.assertEqual(ledger.data()["rounds"][-1]["score"], 5)
        self.assertEqual(len(ledger.data()["rounds"][-1]["exchanges"]), 2)
        self.assertEqual(ledger.head(), "ROUND")

    def test_round_records_requested_model_and_effort(self):
        # why: observation history must identify the requested model and exposed effort.
        # catches: accepting CLI flags while losing them before round persistence.
        ledger = self.ready_ledger()
        self.ok(ledger.call("round", "--tier", "1", "--reviewer", "sol", "--author", "sonnet",
                            "--sha", "s1", "--reply", ledger.file("reply.txt", CLEAN_PASS),
                            "--model", "gpt-6.1-sol", "--effort", "high",
                            "--requested-effort", "medium", "--author-effort", "sonnet=low"))
        record = ledger.data()["rounds"][-1]
        self.assertEqual((record["model"], record["effort"], record["requested_effort"]),
                         ("gpt-6.1-sol", "high", "medium"))
        self.ok(ledger.exchange())
        self.ok(ledger.rnd("s2", CLEAN_PASS, "opus", tier=2))
        self.assertEqual(ledger.data()["rounds"][-1]["effort"], "unknown")

class SpeakerScores(unittest.TestCase):
    def test_orchestrator_request_does_not_set_reviewers_score(self):
        # WHY CLAIM(dialogue-revision): requesting approval is not a reviewer granting it.
        from test_review_dialogue import DialogueLedger, FOCUS, BELOW
        ledger = DialogueLedger(self)
        self.assertEqual(ledger.context(FOCUS)[0], 0)
        self.assertEqual(ledger.rnd('speaker-score', BELOW)[0], 0)
        note = ledger.file('speaker-score.txt', 'Orchestrator: Could this reach the following?\n'
            'SCORE: 9/10\nVERDICT: APPROVE\nReviewer: No, the unsupported path remains.\n'
            'SCORE: 6/10\nVERDICT: CHANGES\n')
        self.assertEqual(ledger.call('argue', '--note', note)[0], 0)
        self.assertEqual(ledger.data()['rounds'][-1]['score'], 6)
        self.assertEqual(ledger.data()['rounds'][-1]['verdict'], 'CHANGES')

class HistoricalFlags(DialogueCase):
    def test_legacy_argument_flag_only_applies_to_current_latest_round(self):
        # WHY CLAIM(dialogue-history): old completed phases must not acquire new obligations.
        ledger = self.ready_ledger()
        self.ok(ledger.rnd('historical', CLEAN_PASS))
        data = ledger.data()
        data['rounds'][-1].pop('exchange_minimum')
        data['rounds'][-1]['argue_required'] = True
        data['phase'] = 1
        Path(ledger.path).write_text(json.dumps(data))
        self.assertEqual(ledger.head(), 'ROUND')
        # The same legacy flag is still obligatory when it is the current latest review.
        data['phase'] = 0
        Path(ledger.path).write_text(json.dumps(data))
        self.assertEqual(ledger.head(), 'ARGUE')
        self.ok(ledger.exchange(1))
        self.assertEqual(ledger.head(), 'ARGUE')
        self.ok(ledger.exchange(2))
        self.assertEqual(ledger.head(), 'CHECKPOINT')
