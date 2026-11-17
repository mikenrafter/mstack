"""CLI contract for dialogue gates; spec: phoe-nix.research/review-behavior/dialogue-spec.md.

Historical v2 fixtures deliberately lack new round metadata. New CLI rounds must
carry focus and complete their own exchanges before another round can hide them.
"""
import copy
import json
import re
import unittest
from pathlib import Path

from test_review_ledger_v2 import V2, BELOW, CLEAN_PASS, CHANGES


FOCUS = {
    "most_important": ["Every reviewer challenges the release decision."],
    "invariants": ["An unfinished exchange cannot be skipped by a later round."],
    "priority_concerns": ["Stale implementation approval must not authorize another plan."],
    "lower_priority": ["Do not redesign scheduling."],
    "evidence": ["CLI tests use a temporary ledger; runtime deployment is not exercised."],
}
PLAN = {
    "goal": "Require explicit argument before review progression.",
    "simplest_change": "Capture a per-round exchange minimum and check it before transitions.",
    "assumptions": ["Historical completed rounds retain their old policy."],
    "questions": ["Does a clean Fable review require two exchanges?"],
    "non_goals": ["Changing model scheduling."],
}
ANSWER = {
    "response": "Yes, every Fable round requires two exchanges; keep the existing scheduler.",
    "decision": "proceed",
    "rationale": "The captured minimum prevents bypass without recomputing review intent.",
}


class DialogueLedger(V2):
    def json_file(self, name, value):
        return self.file(name, json.dumps(value))

    def context(self, focus=None):
        return self.call("context", "--file", self.json_file("focus.json", FOCUS if focus is None else focus))

    def exchange(self, number=1, tail=""):
        return self.call("argue", "--note", self.file(f"exchange-{number}.txt",
            f"Orchestrator: Challenge {number}: why does the simplest change preserve the invariant?\n"
            f"Reviewer: Answer {number}: the stored minimum blocks every transition before progression.\n{tail}"))


class DialogueCase(unittest.TestCase):
    def ok(self, result):
        code, out, err = result
        self.assertEqual(code, 0, f"stdout={out}\nstderr={err}")
        return out

    def ready_ledger(self):
        ledger = DialogueLedger(self)
        self.ok(ledger.context())
        return ledger

    def done_round(self, ledger, sha, reply=BELOW, reviewer="sol", tier=1, author="sonnet", count=1):
        self.ok(ledger.rnd(sha, reply, reviewer, author, tier))
        for number in range(count):
            self.ok(ledger.exchange(number + 1))

    def fable_round(self, reply=CLEAN_PASS):
        ledger = self.ready_ledger()
        self.done_round(ledger, "s1")
        self.done_round(ledger, "s2", reviewer="opus")
        self.ok(ledger.rnd("s3", reply, "fable", "sonnet"))
        return ledger

    def refused_unchanged(self, ledger, action, needle):
        before = Path(ledger.path).read_bytes()
        code, out, err = action()
        self.assertEqual(code, 2, f"stdout={out}\nstderr={err}")
        self.assertIn(needle, err.lower())
        self.assertEqual(Path(ledger.path).read_bytes(), before)


class ReviewContext(DialogueCase):
    def test_new_round_refuses_missing_context_without_inventing_focus(self):
        # why: CLAIM(dialogue-focus) reviewers need explicit priorities, not inferred intent.
        # catches: context remaining an optional command that agents can bypass.
        ledger = DialogueLedger(self)
        self.refused_unchanged(ledger, lambda: ledger.rnd("s1", CLEAN_PASS), "context")

    def test_context_is_in_each_review_brief_and_preserved_on_its_round(self):
        # why: CLAIM(dialogue-focus) later edits must not rewrite what the first reviewer received.
        # catches: focus printed only for the first round, or stored only as mutable root state.
        ledger = self.ready_ledger()
        for values in FOCUS.values():
            for value in values:
                self.assertIn(value, ledger.run("brief"))
        self.done_round(ledger, "s1")
        first = copy.deepcopy(ledger.data()["rounds"][0])
        changed = copy.deepcopy(FOCUS)
        changed["most_important"] = ["Keep revised scores effective after argument."]
        self.ok(ledger.context(changed))
        brief = ledger.run("brief")
        for values in changed.values():
            for value in values:
                self.assertIn(value, brief)
        self.ok(ledger.rnd("s2", BELOW, "opus", "sonnet"))
        rounds = ledger.data()["rounds"]
        self.assertEqual(rounds[0], first)
        self.assertEqual(rounds[0]["context"], FOCUS)
        self.assertEqual(rounds[1]["context"], changed)

    def test_context_remains_visible_in_argument_brief(self):
        # why: CLAIM(dialogue-focus) the argument must use the same priorities as the review.
        # catches: brief returning only "No brief" while dialogue is pending.
        ledger = self.ready_ledger()
        self.ok(ledger.rnd("s1", CLEAN_PASS))
        self.assertEqual(ledger.head(), "ARGUE")
        for values in FOCUS.values():
            for value in values:
                self.assertIn(value, ledger.run("brief"))

    def test_context_rejects_missing_fields_wrong_types_and_blank_items_atomically(self):
        # why: CLAIM(dialogue-focus) malformed context cannot erase valid focus.
        # catches: accepting any JSON object or replacing state before validation finishes.
        for invalid in ({}, {**FOCUS, "evidence": "tests passed"},
                        {**FOCUS, "invariants": []}, {**FOCUS, "most_important": [" "]}):
            with self.subTest(invalid=invalid):
                ledger = self.ready_ledger()
                self.refused_unchanged(ledger, lambda: ledger.context(invalid), "context")


class ReviewArguments(DialogueCase):
    def test_clean_early_review_requires_one_exchange_and_then_checkpoint(self):
        # why: CLAIM(dialogue-all-reviewers) approval still needs a challenged assumption.
        # catches: argument required only on CHANGES or late rounds.
        ledger = self.ready_ledger()
        self.ok(ledger.rnd("s1", CLEAN_PASS))
        self.assertEqual(ledger.head(), "ARGUE")
        self.ok(ledger.exchange())
        self.assertEqual(ledger.head(), "CHECKPOINT")

    def test_nonclean_early_review_requires_exchange_before_next_reviewer(self):
        # why: CLAIM(dialogue-all-reviewers) a below-bar reply also needs discussion.
        # catches: only clean reviews receiving the new minimum.
        ledger = self.ready_ledger()
        self.ok(ledger.rnd("s1", BELOW))
        self.assertEqual(ledger.head(), "ARGUE")
        self.ok(ledger.exchange())
        self.assertEqual(ledger.head(), "ROUND")

    def test_pending_exchange_cannot_be_hidden_by_another_round(self):
        # why: CLAIM(dialogue-no-bypass) appending another round must not hide unfinished work.
        # catches: next checking only the latest round while round accepts arbitrary progression.
        ledger = self.ready_ledger()
        self.ok(ledger.rnd("s1", BELOW))
        self.refused_unchanged(ledger, lambda: ledger.rnd("s2", CLEAN_PASS, "opus"), "argu")
        self.assertEqual(ledger.head(), "ARGUE")

    def test_checkpoint_cannot_skip_a_clean_round_exchange(self):
        # why: CLAIM(dialogue-no-bypass) checkpoint must not turn pending approval into agreement.
        # catches: a checkpoint flag that overrides the argument gate.
        ledger = self.ready_ledger()
        self.ok(ledger.rnd("s1", CLEAN_PASS))
        ledger.call("checkpoint")  # Either refuse or record the decision; progression must still wait.
        self.assertEqual(ledger.head(), "ARGUE")
        self.ok(ledger.exchange())
        self.assertNotEqual(ledger.head(), "ARGUE")

    def test_every_fable_review_requires_two_even_when_clean(self):
        # why: CLAIM(dialogue-fable) expanding coverage must preserve Fable's stronger discussion.
        # catches: globally replacing the existing two-exchange requirement with one.
        for reply in (CLEAN_PASS, CHANGES):
            with self.subTest(reply=reply):
                ledger = self.fable_round(reply)
                self.assertEqual(ledger.head(), "ARGUE")
                self.ok(ledger.exchange(1))
                self.assertEqual(ledger.head(), "ARGUE")
                self.ok(ledger.exchange(2))
                self.assertNotEqual(ledger.head(), "ARGUE")

    def test_nonclean_round_four_keeps_two_exchange_requirement(self):
        # why: CLAIM(dialogue-round-four) the existing round-four rule survives expansion.
        # catches: setting minimum two only when reviewer is Fable.
        ledger = self.fable_round(BELOW)
        self.ok(ledger.exchange(1))
        self.ok(ledger.exchange(2))
        self.ok(ledger.call("new-approach"))
        self.ok(ledger.rnd("s4", CHANGES))
        self.ok(ledger.exchange(1))
        self.assertEqual(ledger.head(), "ARGUE")
        self.ok(ledger.exchange(2))
        self.assertEqual(ledger.head(), "ROUND")

    def test_tier_two_opus_and_fable_receive_their_own_minimum(self):
        # why: CLAIM(dialogue-all-reviewers) final reviewers must also argue their approvals.
        # catches: requirements captured only on tier-one rounds.
        for author, reviewer, count in (("sonnet", "opus", 1), ("opus", "fable", 2)):
            with self.subTest(reviewer=reviewer):
                ledger = self.ready_ledger()
                self.done_round(ledger, "s1", CLEAN_PASS, author=author)
                self.ok(ledger.call("checkpoint"))
                self.ok(ledger.rnd("s2", CLEAN_PASS, reviewer, author, tier=2))
                self.assertEqual(ledger.head(), "ARGUE")
                self.ok(ledger.exchange(1))
                self.assertEqual(ledger.head(), "ARGUE" if count == 2 else "STOP-AGREED")
                if count == 2:
                    self.ok(ledger.exchange(2))
                    self.assertEqual(ledger.head(), "STOP-AGREED")

    def test_terminal_round_cap_does_not_waive_pending_argument(self):
        # why: CLAIM(dialogue-no-bypass) stopping at the cap must not discard the last dialogue.
        # catches: cap logic returning STOP before the exchange check.
        ledger = self.fable_round(BELOW)
        self.ok(ledger.exchange(1))
        self.ok(ledger.exchange(2))
        self.ok(ledger.call("new-approach"))
        self.done_round(ledger, "s4", count=1)  # BELOW without CHANGES is clean for old round-four rule.
        self.ok(ledger.rnd("s5", BELOW, "opus", "sonnet"))
        self.assertEqual(ledger.head(), "ARGUE")
        self.ok(ledger.exchange())
        self.assertEqual(ledger.head(), "STOP-STUCK")

    def test_blank_single_speaker_and_duplicate_notes_do_not_count(self):
        # why: CLAIM(dialogue-real-exchange) empty or repeated text is not another exchange.
        # catches: counting every nonempty note, or counting the same exchange twice.
        ledger = self.fable_round()
        for note in ("", "I agree", "Orchestrator: why?", "Reviewer: fine", "Orchestrator: \nReviewer: yes"):
            self.refused_unchanged(ledger, lambda: ledger.call("argue", "--note", ledger.file("bad.txt", note)), "exchange")
        self.ok(ledger.exchange(1))
        self.refused_unchanged(ledger, lambda: ledger.exchange(1), "duplicate")
        self.assertEqual(ledger.head(), "ARGUE")
        self.ok(ledger.exchange(2))
        self.assertEqual(ledger.head(), "CHECKPOINT")

    def test_argument_score_revision_remains_effective(self):
        # why: CLAIM(dialogue-revision) substantive agreement may change the score while preserving history.
        # catches: validating note speakers but dropping existing score revision handling.
        ledger = self.ready_ledger()
        self.ok(ledger.rnd("s1", BELOW))
        self.ok(ledger.exchange(tail="SCORE: 9/10\nVERDICT: APPROVE"))
        review = ledger.data()["rounds"][-1]
        self.assertEqual(review["original_score"], 6)
        self.assertEqual(review["score"], 9)
        self.assertEqual(ledger.head(), "CHECKPOINT")

    def test_legacy_and_completed_historical_rounds_are_not_retroactively_blocked(self):
        # why: CLAIM(dialogue-history) old completed ledgers remain usable.
        # catches: next deriving the new minimum for every historical row on load.
        for schema in (None, 2):
            with self.subTest(schema=schema):
                ledger = DialogueLedger(self, schema=schema)
                # Literal historical record, without new per-round metadata.
                data = ledger.data()
                data["rounds"] = [{"n": 1, "tier": 1, "approach": data["approach"], "reviewer": "sol",
                    "sha": "old", "score": 9, "verdict": "APPROVE", "phase": 0, "author": ["sonnet"]}]
                Path(ledger.path).write_text(json.dumps(data))
                self.assertEqual(ledger.head(), "CHECKPOINT")
                self.assertIn("old", ledger.run("status"))
                if schema is None:
                    self.ok(ledger.rnd("s2", CLEAN_PASS, "sol", None))
                    self.assertNotEqual(ledger.head(), "ARGUE")


class ImplementationPreflight(DialogueCase):
    def proposal(self, ledger, proposal=None, agent="sonnet"):
        out = self.ok(ledger.call("plan", "--agent", agent, "--file",
                      ledger.json_file("proposal.json", PLAN if proposal is None else proposal)))
        match = re.search(r"\b[0-9a-f]{64}\b", out)
        self.assertIsNotNone(match, f"plan must print its proposal digest: {out}")
        return match.group()

    def answer(self, ledger, digest, answer=None):
        return ledger.call("plan-answer", "--proposal-digest", digest, "--file",
                           ledger.json_file("answer.json", ANSWER if answer is None else answer))

    def status(self, ledger):
        return self.ok(ledger.call("plan-status")).strip().split(":")[0]

    def test_plan_ready_requires_proposal_then_orchestrator_proceed(self):
        # why: CLAIM(dialogue-preflight) implementers demonstrate understanding before receiving approval.
        # catches: a stored plan alone, or a bare approval with no plan, being READY.
        ledger = DialogueLedger(self)
        self.assertEqual(self.status(ledger), "NOT-READY")
        self.refused_unchanged(ledger, lambda: self.answer(ledger, "0" * 64), "proposal")
        digest = self.proposal(ledger)
        self.assertEqual(self.status(ledger), "NOT-READY")
        self.ok(self.answer(ledger, digest))
        self.assertEqual(self.status(ledger), "READY")
        raw = Path(ledger.path).read_text()
        for text in (PLAN["goal"], PLAN["questions"][0], ANSWER["response"], "sonnet", digest):
            self.assertIn(text, raw)

    def test_revision_and_changed_proposal_or_agent_revoke_readiness(self):
        # why: CLAIM(dialogue-preflight) agreement belongs to one proposal and implementer.
        # catches: an unconditional ready flag surviving changes to the plan or agent.
        ledger = DialogueLedger(self)
        digest = self.proposal(ledger)
        self.ok(self.answer(ledger, digest, {**ANSWER, "decision": "revise"}))
        self.assertEqual(self.status(ledger), "NOT-READY")
        self.ok(self.answer(ledger, digest))
        self.assertEqual(self.status(ledger), "READY")
        changed = {**PLAN, "simplest_change": "Only gate the last round; add an explicit append guard."}
        revised_digest = self.proposal(ledger, changed)
        self.assertNotEqual(revised_digest, digest)
        self.assertEqual(self.status(ledger), "NOT-READY")
        self.refused_unchanged(ledger, lambda: self.answer(ledger, digest), "digest")
        self.ok(self.answer(ledger, revised_digest))
        self.assertEqual(self.status(ledger), "READY")
        other_agent_digest = self.proposal(ledger, changed, agent="sol")
        self.assertEqual(self.status(ledger), "NOT-READY")
        self.ok(self.answer(ledger, other_agent_digest))
        self.assertEqual(self.status(ledger), "READY")

    def test_equivalent_json_resubmission_keeps_approval(self):
        # why: CLAIM(dialogue-preflight) formatting alone must not invalidate an unchanged agreement.
        # catches: digesting raw file bytes, or clearing readiness on every plan command.
        ledger = DialogueLedger(self)
        digest = self.proposal(ledger)
        self.ok(self.answer(ledger, digest))
        reordered = dict(reversed(list(PLAN.items())))
        self.assertEqual(self.proposal(ledger, reordered), digest)
        self.assertEqual(self.status(ledger), "READY")

    def test_malformed_proposals_and_answers_never_authorize_work(self):
        # why: CLAIM(dialogue-preflight) thin proposals and blank approval rationales carry no understanding.
        # catches: accepting arbitrary JSON or truthy answer text as approval.
        ledger = DialogueLedger(self)
        for invalid in ({}, {**PLAN, "goal": " "}, {**PLAN, "questions": "none"}):
            self.refused_unchanged(ledger, lambda: ledger.call("plan", "--agent", "sonnet", "--file",
                ledger.json_file("bad-plan.json", invalid)), "plan")
        digest = self.proposal(ledger)
        for invalid in ({}, {**ANSWER, "decision": "ship"}, {**ANSWER, "rationale": " "}):
            self.refused_unchanged(ledger, lambda: self.answer(ledger, digest, invalid), "answer")
        self.assertEqual(self.status(ledger), "NOT-READY")


if __name__ == "__main__":
    unittest.main()
