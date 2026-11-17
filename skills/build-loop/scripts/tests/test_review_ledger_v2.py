"""RED tests for review loop v2 (spec: knowledge/research/agentic-practice-2026-11/review-loop-v2-spec.md,
A1-A7 and "Spec round 1 decisions" R1-R6). Drives scripts/review-ledger through its CLI.
Each test: `# why:` the rule, `# proves:` the spec id, `# catches:` one plausible wrong implementation.
Prose in the skill text is not tested here (R8); only ledger behaviour.
Run: python3 -I -m unittest discover -s scripts/tests

Two kinds of ledger (R1): `ledger(test)` is schema 2 (the helper sets "schema": 2 itself, so these tests do
not depend on init; `Init` below covers init), `legacy(test)` has no schema and keeps the v1 schedule.
"""
import contextlib
import io
import json
import re
import unittest
from pathlib import Path

from test_review_ledger import BUG, Ledger, rl

BELOW = "SCORE: 6/10"
CLEAN_PASS = "SCORE: 9/10\nVERDICT: APPROVE"
CHANGES = f"SCORE: 6/10\nVERDICT: CHANGES\n{BUG}"
APPROVE_WITH_SHOULD = f"SCORE: 9/10\nVERDICT: APPROVE\n{BUG}"
OTHER_SHOULD = "SCORE: 6/10\nVERDICT: CHANGES\nS2 [should] [class: other] x/y.py:3 other bug. Fix: z"
# Historical/unclassified nits still use the cull. Explicit `needed: no` now goes to hardening.
NIT1 = "S1 [nit] [class: other] a.py:1 rename x"
NIT2 = "S2 [nit] [class: other] b.py:2 reword y"
STASH1 = "- c.py:3 stashed nit"
MIXED_NITS = f"SCORE: 9/10\nVERDICT: APPROVE\n{NIT1}\n{NIT2}\nNIT-STASH:\n{STASH1}"
FINDINGS_ONLY_NITS = f"SCORE: 9/10\nVERDICT: APPROVE\n{NIT1}\n{NIT2}"
STASH_ONLY_NITS = "SCORE: 9/10\nVERDICT: APPROVE\nNIT-STASH:\n- c.py:3 stashed nit one\n- d.py:4 stashed nit two"


def names(value):
    """The set of model names in a stored author (a list or a comma string; the storage is not pinned)."""
    if isinstance(value, str):
        value = value.split(",")
    return {v.strip() for v in value}


class V2(Ledger):
    """Ledger driver with --author and the v2 commands. Exit codes and stderr are captured."""

    def __init__(self, test, schema=2, **kw):
        super().__init__(test, schema=schema, **kw)
        self.notes = 0

    def call(self, *args):
        out, err = io.StringIO(), io.StringIO()
        code = 0
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                rl.main(["-l", self.path, *args])
            except SystemExit as e:
                code = e.code if isinstance(e.code, int) else 1
                if isinstance(e.code, str):
                    err.write(e.code)
        return code, out.getvalue(), err.getvalue()

    def file(self, name, text):
        p = Path(self.dir.name) / name
        p.write_text(text)
        return str(p)

    def rnd(self, sha, reply, reviewer="sol", author="sonnet", tier=1):
        """Record a round. author=None omits --author (legacy ledgers; schema 2 must refuse)."""
        extra = ["--author", author] if author is not None else []
        return self.call("round", "--tier", str(tier), "--reviewer", reviewer, *extra,
                         "--sha", sha, "--reply", self.file(f"reply-{sha}.txt", reply))

    def focus(self):
        focus = {"most_important": ["Preserve the review scheduling contract."],
                 "invariants": ["Recorded findings keep their identity and outcomes."],
                 "priority_concerns": [], "lower_priority": [],
                 "evidence": ["Temporary CLI fixtures exercise persisted review state."]}
        code, _, err = self.call("context", "--file", self.file("focus.json", json.dumps(focus)))
        assert code == 0, err

    def rnd_ok(self, *a, pending=False, **kw):
        if self.data().get("schema") == 2 and not self.data().get("context"):
            self.focus()
        code, _, err = self.rnd(*a, **kw)
        assert code == 0, err
        # Scheduling tests complete real stored exchanges; argument tests opt out explicitly.
        if not pending and self.data().get("schema") == 2:
            self.argue(self.data()["rounds"][-1]["exchange_minimum"])

    def argue(self, n=1, first="argument"):
        for _ in range(n):
            self.notes += 1
            code, _, err = self.call("argue", "--note", self.file(
                f"note{self.notes}.txt", f"Orchestrator: {first} {self.notes}: why is this transition justified?\n"
                f"Reviewer: Answer {self.notes}: use the recorded score and outstanding findings."))
            assert code == 0, err

    def nxt(self):
        return self.run("next").strip()

    def head(self):
        return self.nxt().split(":")[0]

    def two_below(self):
        self.rnd_ok("sha1", BELOW, "sol", "sonnet")
        self.rnd_ok("sha2", BELOW, "opus", "sol")

    def checkpoint(self):
        self.run("checkpoint")


def ledger(test):
    result = V2(test)
    result.focus()
    return result


def legacy(test):
    return V2(test, schema=None)


class Init(unittest.TestCase):
    def test_init_writes_schema_2(self):
        # why: new ledgers must be marked so the v2 schedule applies to them and only to them (R1).
        # proves: R1
        # catches: an init that writes nothing, so every ledger is legacy and v2 never runs
        import tempfile
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        path = str(Path(d.name) / "l.json")
        rl.main(["-l", path, "init", "--repo", "r", "--base", "b0", "--bar", "8", "--category", "test",
                 "--intent", "x", "--usage-model", "one agent calls it, one request at a time; input comes from the same user"])
        self.assertEqual(json.loads(Path(path).read_text()).get("schema"), 2)


class Reviewer(unittest.TestCase):
    def test_round3_after_two_below_bar_rounds_is_fable(self):
        # why: Fable makes the ship call when A-model rounds stall (A1).
        # proves: A1
        # catches: a next() that always names "sol or opus" (or only checks the round number is 3 but not the reviewer)
        L = ledger(self)
        L.two_below()
        out = L.nxt()
        self.assertTrue(out.startswith("ROUND"), out)
        self.assertIn("round 3", out)
        self.assertIn("reviewer: fable", out)

    def test_round3_is_fable_also_when_round2_met_the_score_but_a_should_is_open(self):
        # why: "rounds 1-2 did not reach the bar" includes a round that scored 9 but left a should open (S7).
        # proves: A1 (S7)
        # catches: a round-3 rule keyed on the score only, so a high score with an open should stays on sol/opus
        L = ledger(self)
        L.rnd_ok("sha1", BELOW, "sol", "sonnet")
        L.rnd_ok("sha2", APPROVE_WITH_SHOULD, "opus", "sol")
        out = L.nxt()
        self.assertTrue(out.startswith("ROUND"), out)  # not CHECKPOINT: the should blocks the pass
        self.assertIn("round 3", out)
        self.assertIn("reviewer: fable", out)

    def test_rounds_1_and_2_advice_names_the_fix_author_not_a_recorded_name(self):
        # why: the next round's --author is whoever wrote the fixes since the last reviewed sha, which the
        #      ledger cannot know. Naming the LAST round's authors misdirects: Sonnet builds, Sol reviews,
        #      Sol fixes (B1); old `next` said "not sonnet", the orchestrator chose Sol, `round` exited 2 (R1 S1).
        # proves: A1, A2 (review round 1, S1)
        # catches: a next() that prints the last round's authors, or a bare "sol or opus" with no author clause
        L = ledger(self)
        line = L.nxt()  # no round yet: no author recorded
        self.assertIn("reviewer: sol or opus", line)
        self.assertNotRegex(line, r"\bnot (sonnet|sol|opus|fable)\b")
        for author, reviewer in (("sonnet", "sol"), ("sol", "opus"), ("sonnet,sol", "opus"), ("opus", "sol")):
            M = ledger(self)
            M.rnd_ok("sha1xxxxxxxxxxxx", BELOW, reviewer, author)
            out = M.nxt()
            self.assertIn("round 2", out)
            self.assertNotIn("fable", out)
            self.assertIn("reviewer: sol or opus, not the author of the fixes since sha1xxxxxx", out)
            self.assertNotRegex(out, r"\bnot (sonnet|sol|opus|fable)\b", f"author {author!r} leaked: {out!r}")

    def test_rounds_after_a_pivot_are_a_models_again_through_round_5(self):
        # why: only round 3 of an approach is Fable; rounds 4 and 5 return to A (A1, S9).
        # proves: A1 (S9)
        # catches: a next() keyed on "total tier-1 rounds >= 3" that stays on fable for rounds 4-5
        L = ledger(self)
        L.two_below()
        L.rnd_ok("sha3", BELOW, "fable", "sonnet")
        self.assertEqual(L.head(), "STEP-BACK")
        L.run("new-approach")
        out4 = L.nxt()  # the 4th round
        self.assertTrue(out4.startswith("ROUND"), out4)
        self.assertIn("reviewer: sol or opus", out4)
        self.assertNotIn("fable", out4)
        L.rnd_ok("sha4", BELOW, "sol", "sonnet")
        out5 = L.nxt()  # the 5th round
        self.assertTrue(out5.startswith("ROUND"), out5)
        self.assertIn("reviewer: sol or opus, not the author of the fixes since sha4", out5)
        self.assertNotIn("fable", out5)

    def test_passing_rounds_1_and_2_go_to_tier2_with_opus_reviewer(self):
        # why: control for A3: a pass in round 1 or 2 keeps the tier-2 pass (checkpoint, then a fresh Opus, then done).
        # proves: A3 (unchanged branch), R2
        # catches: an A3 change that also ends the loop (STOP-AGREED / NIT-CULL) after an early pass
        for pass_round in (1, 2):
            with self.subTest(pass_in_round=pass_round):
                L = ledger(self)
                if pass_round == 1:
                    L.rnd_ok("sha1", CLEAN_PASS, "sol", "sonnet")
                else:
                    L.rnd_ok("sha1", BELOW, "sol", "sonnet")
                    L.rnd_ok("sha2", CLEAN_PASS, "opus", "sol")
                self.assertEqual(L.head(), "CHECKPOINT")
                L.checkpoint()
                out = L.nxt()
                self.assertTrue(out.startswith("ROUND"), out)
                self.assertIn("tier 2", out)
                self.assertIn("reviewer: opus", out)
                self.assertNotIn("fable", out)
                L.rnd_ok("sha9", CLEAN_PASS, "opus", "sonnet,sol", tier=2)
                self.assertEqual(L.head(), "STOP-AGREED")

    def test_tier2_reviewer_is_fable_when_opus_is_among_the_authors(self):
        # why: a fresh Opus must not review code Opus wrote; Fable takes the tier-2 pass then (R2, S10).
        # proves: R2 (S10, S4)
        # catches: a tier-2 line that always says opus, or one that only looks at the last round's author
        def opus_wrote_round1_only(L):
            # round 1 diff written by opus (reviewed by sol); round 2 by sonnet+sol (reviewed by opus) passes
            L.rnd_ok("sha1", BELOW, "sol", "opus")
            L.rnd_ok("sha2", CLEAN_PASS, "opus", "sonnet,sol")

        def opus_in_the_pass_round_list(L):
            L.rnd_ok("sha1", CLEAN_PASS, "sol", "sonnet,opus")

        for build in (opus_wrote_round1_only, opus_in_the_pass_round_list):
            with self.subTest(build.__name__):
                L = ledger(self)
                build(L)
                self.assertEqual(L.head(), "CHECKPOINT")
                L.checkpoint()
                out = L.nxt()
                self.assertIn("tier 2", out)
                self.assertIn("reviewer: fable", out)
                self.assertNotIn("reviewer: opus", out)

    def test_tier2_record_refuses_opus_when_opus_is_in_the_author_list(self):
        # why: the refusal rule applies to tier 2 as well (R2).
        # proves: R2
        # catches: a refusal that only runs for tier-1 rounds
        L = ledger(self)
        L.rnd_ok("sha1", CLEAN_PASS, "sol", "sonnet,opus")
        L.checkpoint()
        before = Path(L.path).read_bytes()
        code, _, err = L.rnd("sha2", CLEAN_PASS, "opus", "sonnet,opus", tier=2)
        self.assertEqual(code, 2, err)
        self.assertEqual(Path(L.path).read_bytes(), before)


class Author(unittest.TestCase):
    def test_reviewer_in_the_author_list_is_refused_for_every_model(self):
        # why: a reviewer never reviews a diff it wrote (A2); the refusal names both roles, for each model.
        # proves: A2 (S11)
        # catches: a check hardcoded for one model (opus only), a warning-only check (exit 0), or one that records the round anyway
        for model in ("sonnet", "sol", "opus", "fable"):
            with self.subTest(model):
                L = ledger(self)
                before = Path(L.path).read_bytes()
                code, _, err = L.rnd("sha1", BELOW, model, model)
                self.assertEqual(code, 2, err)
                self.assertIn(model, err)
                self.assertIn("author", err.lower())
                self.assertIn("reviewer", err.lower())
                self.assertEqual(L.data()["rounds"], [])
                self.assertEqual(Path(L.path).read_bytes(), before)

    def test_reviewer_anywhere_in_a_comma_author_list_is_refused(self):
        # why: --author is a list of every model that wrote code in the diff (R2, S12).
        # proves: R2 (S12)
        # catches: comparing the reviewer to the whole string (so "sonnet,sol" never equals "sol"), or to the first entry only
        for author, reviewer in (("sol,sonnet", "sol"), ("sonnet,sol,opus", "sol"),
                                 ("sonnet,opus", "opus"), ("sonnet,sol,fable", "fable"), ("sonnet, sol", "sol")):
            with self.subTest(author=author, reviewer=reviewer):
                L = ledger(self)
                code, _, err = L.rnd("sha1", BELOW, reviewer, author)
                self.assertEqual(code, 2, err)
                self.assertIn(reviewer, err)
                self.assertEqual(L.data()["rounds"], [])

    def test_reviewer_outside_the_author_list_is_accepted(self):
        # why: positive control for the refusals above: a reviewer not in the list must pass (R2).
        # proves: R2
        # catches: a refusal that triggers on any multi-author list, or on a name that is only a substring
        for author, reviewer in (("sonnet,sol", "opus"), ("sonnet,opus", "sol"), ("sonnet", "fable"),
                                 ("sol,opus", "fable")):
            with self.subTest(author=author, reviewer=reviewer):
                L = ledger(self)
                if reviewer == "fable":
                    L.two_below()  # Positive authorship control at Fable's scheduled round.
                code, _, err = L.rnd("sha1", BELOW, reviewer, author)
                self.assertEqual(code, 0, err)

    def test_authors_are_stored_per_round_including_several_values(self):
        # why: the stored author is the input of the refusal and of the "not <author>" advice (A2, R2, S12).
        # proves: R2
        # catches: a round that accepts --author but drops it, or keeps only the first value of a list
        L = ledger(self)
        L.rnd_ok("sha1", BELOW, "opus", "sonnet,sol")
        L.rnd_ok("sha2", BELOW, "sol", "fable")
        rounds = L.data()["rounds"]
        self.assertEqual(names(rounds[0].get("author") or []), {"sonnet", "sol"})
        self.assertEqual(names(rounds[1].get("author") or []), {"fable"})
        M = ledger(self)
        M.rnd_ok("sha1", BELOW, "sol", "sonnet")
        self.assertEqual(names(M.data()["rounds"][0].get("author") or []), {"sonnet"})

    def test_schema2_round_requires_author(self):
        # why: without the author the reviewer check cannot run, so a schema-2 ledger refuses (R1, S13).
        # proves: R1 (S13)
        # catches: an --author that stays optional on every ledger
        L = ledger(self)
        before = Path(L.path).read_bytes()
        code, _, err = L.rnd("sha1", BELOW, "sol", None)
        self.assertEqual(code, 2, err)
        self.assertIn("author", err.lower())
        self.assertEqual(L.data()["rounds"], [])
        self.assertEqual(Path(L.path).read_bytes(), before)
        L.rnd_ok("sha1", CLEAN_PASS, "sol", "sonnet")
        L.checkpoint()
        code, _, err = L.rnd("sha2", CLEAN_PASS, "opus", None, tier=2)
        self.assertEqual(code, 2, err)

    def test_legacy_ledger_without_author_loads_and_keeps_working(self):
        # why: ledgers written before v2 have no schema and no author keys; every command must still work (A2, R1).
        # proves: A2, R1
        # catches: a next() that indexes round["author"] directly (KeyError), or a round that demands --author on old ledgers
        L = legacy(self)
        code, _, err = L.rnd("sha1", BELOW, "sol", None)
        self.assertEqual(code, 0, err)
        self.assertIn("round 2", L.run("status"))
        self.assertTrue(L.nxt().startswith("ROUND"))
        self.assertIn("See ONLY: git diff sha1", L.run("brief"))
        code, _, err = L.rnd("sha2", BELOW, "opus", None)
        self.assertEqual(code, 0, err)


class LegacySchedule(unittest.TestCase):
    """R1: a ledger without schema keeps the v1 schedule for its whole life."""

    def test_legacy_round3_is_not_fable_and_has_no_reviewer_line(self):
        # why: mixing v2 rules into an old ledger would change its schedule midway (R1, S13).
        # proves: R1 (S13)
        # catches: a next() that switches to Fable at round 3 for every ledger
        L = legacy(self)
        L.rnd_ok("sha1", BELOW, "sol", None)
        L.rnd_ok("sha2", BELOW, "sol", None)
        out = L.nxt()
        self.assertTrue(out.startswith("ROUND: tier 1 round 3"), out)
        self.assertNotIn("fable", out.lower())
        self.assertNotIn("reviewer:", out)

    def test_legacy_nonclean_round3_and_round4_do_not_argue(self):
        # why: ARGUE is a schema-2 rule; an old ledger at round 3/4 must not start asking for it (R1, S13).
        # proves: R1 (S13)
        # catches: ARGUE keyed on the round number alone, not on the schema
        L = legacy(self)
        L.rnd_ok("sha1", BELOW, "sol", None)
        L.rnd_ok("sha2", BELOW, "sol", None)
        L.rnd_ok("sha3", CHANGES, "sol", None)
        self.assertEqual(L.head(), "STEP-BACK")
        L.run("new-approach")
        L.rnd_ok("sha4", OTHER_SHOULD, "sol", None)
        self.assertEqual(L.head(), "ROUND")

    def test_legacy_pass_at_round3_goes_checkpoint_then_tier2_without_cull(self):
        # why: control for R4: the same passing round 3 on a legacy ledger still gets the tier-2 pass and no NIT-CULL (R1, S13, S15).
        # proves: R1, R4 (S15)
        # catches: a pass rule that ends legacy ledgers at round 3 or culls their nits
        L = legacy(self)
        L.rnd_ok("sha1", BELOW, "sol", None)
        L.rnd_ok("sha2", BELOW, "sol", None)
        L.rnd_ok("sha3", MIXED_NITS, "sol", None)
        self.assertEqual(L.head(), "CHECKPOINT")
        L.checkpoint()
        out = L.nxt()
        self.assertTrue(out.startswith("ROUND"), out)
        self.assertIn("tier 2", out)
        L.rnd_ok("sha4", CLEAN_PASS, "opus", None, tier=2)
        self.assertEqual(L.head(), "STOP-AGREED")

    def test_legacy_pass_at_round1_goes_to_tier2_even_with_nits(self):
        # why: legacy checkpoint/tier-2 path is untouched (R1, S13).
        # proves: R1
        # catches: a NIT-CULL step that runs for any ledger with nits at the checkpoint
        L = legacy(self)
        L.rnd_ok("sha1", MIXED_NITS, "sol", None)
        self.assertEqual(L.head(), "CHECKPOINT")
        L.checkpoint()
        out = L.nxt()
        self.assertNotEqual(out.split(":")[0], "NIT-CULL")
        self.assertIn("tier 2", out)


class Argue(unittest.TestCase):
    def test_nonclean_round3_returns_argue_until_two_exchanges(self):
        # why: the orchestrator must argue a non-clean Fable round twice before acting; ARGUE comes before STEP-BACK (A4, R3).
        # proves: A4, R3
        # catches: an ARGUE that clears after one exchange, never returns, or comes after STEP-BACK
        L = ledger(self)
        L.two_below()
        L.rnd_ok("sha3", CHANGES, "fable", "sonnet", pending=True)
        self.assertEqual(L.head(), "ARGUE")
        L.argue(1)
        self.assertEqual(L.head(), "ARGUE")
        L.argue(1)
        self.assertEqual(L.head(), "STEP-BACK")  # score 6 < bar 8: proceeds as before

    def test_approve_with_an_open_should_still_requires_argue_on_rounds_3_and_4(self):
        # why: "any blocker/should open" makes the reply non-clean even when the verdict is APPROVE and the score passes (A4, R3, S14).
        # proves: A4, R3 (S14)
        # catches: an ARGUE trigger that reads only the verdict, or only the score
        L = ledger(self)
        L.two_below()
        L.rnd_ok("sha3", APPROVE_WITH_SHOULD, "fable", "sonnet", pending=True)
        self.assertEqual(L.head(), "ARGUE")
        M = ledger(self)
        M.two_below()
        M.rnd_ok("sha3", BELOW, "fable", "sonnet")
        M.run("new-approach")
        M.rnd_ok("sha4", APPROVE_WITH_SHOULD, "sol", "sonnet", pending=True)
        self.assertEqual(M.head(), "ARGUE")

    def test_argue_required_survives_later_outcomes(self):
        # why: ARGUE is captured when the reply is recorded; closing the finding does not waive it (R3, S14).
        # proves: R3 (S14)
        # catches: an ARGUE recomputed from the current open findings, so `outcome S1 fixed` silently skips it
        # S14 r2: APPROVE with a should too, or `required = CHANGES or open should` passes.
        for reply, (status, extra) in [(r, s) for r in (CHANGES, APPROVE_WITH_SHOULD)
                                       for s in (("fixed", []), ("declined", ["--evidence", "does not reproduce"]))]:
            with self.subTest(reply=reply.splitlines()[1], status=status):
                L = ledger(self)
                L.two_below()
                L.rnd_ok("sha3", reply, "fable", "sonnet", pending=True)
                code, _, err = L.call("outcome", "S1", status, *extra)
                self.assertEqual(code, 0, err)
                self.assertEqual(L.head(), "ARGUE")
                L.argue(1)
                self.assertEqual(L.head(), "ARGUE")
                L.argue(1)
                self.assertNotEqual(L.head(), "ARGUE")

    def test_both_notes_are_stored_and_status_shows_count_and_first_lines(self):
        # why: the orchestrator and the next reader must see what was argued, not only how many times (R3, S14).
        # proves: R3 (S14)
        # catches: an argue that counts but discards the text, or keeps only the last note
        L = ledger(self)
        L.two_below()
        L.rnd_ok("sha3", CHANGES, "fable", "sonnet", pending=True)
        n1 = L.file("n1.txt", "Orchestrator: S1 does not reproduce on main\nsecond line one\nReviewer: it does, see test X")
        n2 = L.file("n2.txt", "Orchestrator: failing test attached, second push\nsecond line two\nReviewer: withdrawn")
        self.assertEqual(L.call("argue", "--note", n1)[0], 0)
        self.assertRegex(L.run("status"), r"\b1 exchanges?\b")
        self.assertEqual(L.call("argue", "--note", n2)[0], 0)
        status = L.run("status")
        self.assertRegex(status, r"\b2 exchanges?\b")
        self.assertIn("Orchestrator: S1 does not reproduce on main", status)
        self.assertIn("Orchestrator: failing test attached, second push", status)
        raw = Path(L.path).read_text()
        for needle in ("Reviewer: it does, see test X", "Reviewer: withdrawn", "second line one", "second line two"):
            self.assertIn(needle, raw)

    def argued_round3(self, second_note):
        """Round 3 Fable below the bar, S1 argued twice, S1 fixed in between; the second note is `second_note`."""
        L = ledger(self)
        L.two_below()
        L.rnd_ok("sha3", CHANGES, "fable", "sonnet", pending=True)
        L.argue(1)
        self.assertEqual(L.call("outcome", "S1", "fixed")[0], 0)
        if "Orchestrator:" not in second_note:
            second_note = "Orchestrator: Does the evidence warrant a score revision?\n" + second_note
        if "Reviewer:" not in second_note:
            second_note += "\nReviewer: The score below reflects my answer."
        n = L.file("revised.txt", second_note)
        code, _, err = L.call("argue", "--note", n)
        self.assertEqual(code, 0, err)
        return L

    def test_argue_note_with_a_revised_passing_score_replaces_the_round_score(self):
        # why: the argument exists to persuade Fable; a persuaded Fable must not trigger a pivot (S7). Bar is 8, round 3 was 6.
        # proves: R3 (S7)
        # catches: an argue that stores only text, so next still reads the original 6/10 and returns STEP-BACK
        L = self.argued_round3("Orchestrator: S1 fixed in sha4\nReviewer: persuaded.\nSCORE: 9/10\nVERDICT: APPROVE")
        self.assertEqual(L.head(), "CHECKPOINT")
        L.checkpoint()
        self.assertEqual(L.head(), "STOP-AGREED")  # no nits stashed, so no cull
        r = L.data()["rounds"][2]
        self.assertEqual((r["score"], r["verdict"]), (9.0, "APPROVE"))
        # the original reply is kept, and status shows both
        self.assertEqual((r["original_score"], r["original_verdict"]), (6.0, "CHANGES"))
        status = L.run("status")
        self.assertRegex(status, r"score 9/10 APPROVE")
        self.assertRegex(status, r"(?i)original.*6/10.*CHANGES|argued from.*6/10.*CHANGES")

    def test_argue_note_without_score_lines_changes_nothing(self):
        # why: control for S7. Only a note that carries SCORE or VERDICT lines may touch the round; prose that merely closes S1 does not.
        # proves: R3 (S7)
        # catches: an argue that raises the score whenever findings are closed, or on any digits in the note
        L = self.argued_round3("Orchestrator: S1 fixed in sha4, see 9/10 tests green\nReviewer: no change.")
        self.assertEqual(L.head(), "STEP-BACK")
        r = L.data()["rounds"][2]
        self.assertEqual((r["score"], r["verdict"]), (6.0, "CHANGES"))
        self.assertNotIn("original_score", r)

    def test_argue_note_with_a_revised_passing_score_but_a_still_open_blocker_does_not_pass(self):
        # why: a revised score must not hide an open should; blocking findings still gate (S7 + blocking()).
        # proves: R3 (S7)
        # catches: an argue that sets a passing flag instead of the score, skipping the open-finding check
        L = ledger(self)
        L.two_below()
        L.rnd_ok("sha3", CHANGES, "fable", "sonnet", pending=True)
        L.argue(1)
        L.call("argue", "--note", L.file("n.txt", "Orchestrator: Is the score justified despite the open blocker?\nReviewer: The blocker still gates approval.\nSCORE: 9/10\nVERDICT: APPROVE"))
        self.assertEqual(L.head(), "STEP-BACK")  # S1 [should, needed: yes] is still open

    def test_argue_note_with_per_concern_scores_revises_the_concern_scores(self):
        # why: with concern bars, round_meets_bar reads r["scores"]; revising only the summary would leave it failing (S7). The default ledger touches testability (bar 8).
        # proves: R3 (S7)
        # catches: an argue that overwrites r["score"] but not r["scores"]
        L = self.argued_round3("Reviewer: persuaded.\nSCORE[testability]: 9/10\nVERDICT: APPROVE")
        r = L.data()["rounds"][2]
        self.assertEqual(r["scores"], {"testability": 9.0})
        self.assertEqual(r["score"], 9.0)
        self.assertEqual(r["original_scores"], {"testability": 6.0})
        self.assertEqual(L.head(), "CHECKPOINT")

    def test_argue_note_plain_score_revises_every_touched_concern(self):
        # why: a plain SCORE line in a concern-banded ledger means "all touched concerns", as in `round` (S7).
        # proves: R3 (S7)
        # catches: an argue that updates r["score"] only when the note has a plain line
        L = self.argued_round3("Reviewer: persuaded.\nSCORE: 9/10")
        self.assertEqual(L.data()["rounds"][2]["scores"], {"testability": 9.0})
        self.assertEqual(L.head(), "CHECKPOINT")

    def test_argue_note_that_lowers_the_score_is_honored_and_unknown_concern_is_refused(self):
        # why: the reviewer may also dig in; and a typo'd concern must not silently drop the revision (S7, as `round` refuses it).
        # proves: R3 (S7)
        # catches: an argue that only ever raises scores, or ignores SCORE[bogus]
        L = ledger(self)
        L.two_below()
        L.rnd_ok("sha3", APPROVE_WITH_SHOULD, "fable", "sonnet", pending=True)
        code, _, err = L.call("argue", "--note", L.file("bad.txt", "Orchestrator: Which concern changed?\nReviewer: This concern.\nSCORE[bogus]: 9/10"))
        self.assertNotEqual(code, 0)
        self.assertIn("bogus", err)
        self.assertEqual(L.data()["rounds"][2].get("exchanges", []), [])  # nothing recorded
        L.argue(1)
        L.call("argue", "--note", L.file("low.txt", "Orchestrator: Does this still meet the bar?\nReviewer: No, I revise downward.\nSCORE: 5/10\nVERDICT: CHANGES"))
        r = L.data()["rounds"][2]
        self.assertEqual((r["score"], r["original_score"]), (5.0, 9.0))

    def test_completed_early_exchanges_and_pending_fable_exchanges(self):
        # why: completed early exchanges permit scheduling; every Fable reply still needs two exchanges.
        # proves: A4
        # catches: clean Fable approval bypassing the captured exchange requirement.
        L = ledger(self)
        L.rnd_ok("sha1", CHANGES, "sol", "sonnet")
        self.assertEqual(L.head(), "ROUND")
        L.run("outcome", "S1", "fixed")
        L.rnd_ok("sha2", OTHER_SHOULD, "opus", "sol")
        self.assertEqual(L.head(), "ROUND")
        L.run("outcome", "S2", "fixed")
        L.rnd_ok("sha3", "SCORE: 6/10\nVERDICT: CHANGES\nS1 resolved\nS2 resolved", "fable", "sonnet", pending=True)
        self.assertEqual(L.head(), "ARGUE")  # a CHANGES verdict alone makes round 3 non-clean ...
        M = ledger(self)
        M.two_below()
        M.rnd_ok("sha3", CLEAN_PASS, "fable", "sonnet", pending=True)
        self.assertEqual(M.head(), "ARGUE")  # clean Fable also requires two exchanges

    def test_round4_argues_and_exchanges_are_counted_per_round(self):
        # why: round 4 (first pivot round) also needs 2 exchanges, and round 3's do not count for it (A4, R3).
        # proves: A4, R3
        # catches: a single global exchange counter, so round 4 is never argued
        L = ledger(self)
        L.two_below()
        L.rnd_ok("sha3", CHANGES, "fable", "sonnet", pending=True)
        L.argue(2)
        L.run("outcome", "S1", "fixed")
        self.assertEqual(L.head(), "STEP-BACK")
        L.run("new-approach")
        L.rnd_ok("sha4", OTHER_SHOULD, "sol", "sonnet", pending=True)
        self.assertEqual(L.head(), "ARGUE")
        L.argue(1)
        self.assertEqual(L.head(), "ARGUE")
        L.argue(1)
        self.assertEqual(L.head(), "ROUND")


class Pass(unittest.TestCase):
    def passed_with_nits(self, reply=MIXED_NITS):
        L = ledger(self)
        L.two_below()
        L.rnd_ok("sha3", reply, "fable", "sonnet")
        self.assertEqual(L.head(), "CHECKPOINT")
        L.checkpoint()
        return L

    def test_passing_fable_round3_ends_without_tier2_unlike_a_legacy_sol_round3(self):
        # why: schema 2 skips tier 2 after a passing Fable round 3; legacy keeps it with Sol (A3, R1, R4, S15).
        # proves: A3, R4 (S15)
        # catches: an implementation that keeps the old "tier 1 passed -> tier 2 round" branch for round 3, or applies the new one to legacy
        L = ledger(self)
        L.two_below()
        L.rnd_ok("sha3", CLEAN_PASS, "fable", "sonnet")
        self.assertEqual(L.head(), "CHECKPOINT")
        L.checkpoint()
        self.assertEqual(L.head(), "STOP-AGREED")
        M = legacy(self)
        M.rnd_ok("sha1", BELOW, "sol", None)
        M.rnd_ok("sha2", BELOW, "sol", None)
        M.rnd_ok("sha3", CLEAN_PASS, "sol", None)
        M.checkpoint()
        self.assertIn("tier 2", M.nxt())

    def test_passing_fable_round_with_nits_goes_to_nit_cull_after_the_checkpoint(self):
        # why: nits left after Fable's pass are culled to at most 2 before STOP-AGREED (A3, A5, R4).
        # proves: A3, A5, R4
        # catches: next() that skips NIT-CULL, or returns it before the checkpoint
        L = ledger(self)
        L.two_below()
        L.rnd_ok("sha3", MIXED_NITS, "fable", "sonnet")
        self.assertEqual(L.head(), "CHECKPOINT")
        L.checkpoint()
        self.assertEqual(L.head(), "NIT-CULL")

    def test_passing_rounds_4_and_5_go_checkpoint_cull_stop(self):
        # why: a pass after the pivot ends like a Fable pass: checkpoint, cull, stop; no tier 2 (R4, S15).
        # proves: R4 (S15)
        # catches: a pass rule keyed on reviewer == fable or on round number == 3 only
        for passing_round in (4, 5):
            with self.subTest(passing_round=passing_round):
                L = ledger(self)
                L.two_below()
                L.rnd_ok("sha3", BELOW, "fable", "sonnet")
                L.run("new-approach")
                if passing_round == 4:
                    L.rnd_ok("sha4", MIXED_NITS, "sol", "sonnet")
                else:
                    L.rnd_ok("sha4", BELOW, "sol", "sonnet")
                    L.rnd_ok("sha5", MIXED_NITS, "opus", "sol")
                self.assertEqual(L.head(), "CHECKPOINT")
                L.checkpoint()
                self.assertEqual(L.head(), "NIT-CULL")
                code, _, err = L.call("cull", "--reply", L.file("c.txt", "KEEP: none"))
                self.assertEqual(code, 0, err)
                self.assertEqual(L.head(), "STOP-AGREED")

    def test_cull_brief_lists_each_item_with_its_text_and_asks_for_a_reason_per_kept_id(self):
        # why: the reviewer can only choose from what it sees: id and text for findings and stash items, a cap, a reason each (A5, R6, S17).
        # proves: A5, R6 (S17)
        # catches: a brief that lists ids only, omits stash items, never states the cap, or never asks for reasons
        L = self.passed_with_nits()
        brief = L.run("brief")
        self.assertRegex(brief, r"(?m)^.*\bS1\b.*rename x")
        self.assertRegex(brief, r"(?m)^.*\bS2\b.*reword y")
        self.assertRegex(brief, r"(?m)^.*\bN1\b.*stashed nit")
        self.assertRegex(brief, r"(?i)keep at most 2")
        self.assertRegex(brief, r"(?i)one line.*(reason|why)|(reason|why).*one line")
        self.assertIn("KEEP:", brief)
        self.assertRegex(brief, r"(?i)KEEP: in the first column, no markup")

    def test_cull_brief_for_findings_only_and_stash_only_fixtures(self):
        # why: each nit source works alone: findings with no stash, and a stash with no nit findings (S16).
        # proves: A5 (S16)
        # catches: a NIT-CULL trigger or brief that needs both sources, or lists a source that is empty
        L = self.passed_with_nits(FINDINGS_ONLY_NITS)
        self.assertEqual(L.head(), "NIT-CULL")
        brief = L.run("brief")
        self.assertRegex(brief, r"\bS1\b.*rename x")
        self.assertRegex(brief, r"\bS2\b.*reword y")
        self.assertNotRegex(brief, r"\bN1\b")
        M = self.passed_with_nits(STASH_ONLY_NITS)
        self.assertEqual(M.head(), "NIT-CULL")
        brief = M.run("brief")
        self.assertRegex(brief, r"\bN1\b.*stashed nit one")
        self.assertRegex(brief, r"\bN2\b.*stashed nit two")
        self.assertNotRegex(brief, r"\bS1\b")

    def test_cull_refuses_more_than_two_kept_and_leaves_the_ledger_byte_identical(self):
        # why: the cull exists to cut; KEEP of 3 is refused, not truncated, and nothing is written (A5, R5, S18).
        # proves: A5, R5 (S18)
        # catches: a cull that silently keeps the first two, or that discards some items before refusing
        L = self.passed_with_nits()
        before = Path(L.path).read_bytes()
        code, _, err = L.call("cull", "--reply", L.file("c.txt", "KEEP: S1, S2, N1\nS1 why"))
        self.assertEqual(code, 2, err)
        self.assertEqual(Path(L.path).read_bytes(), before)
        self.assertEqual(L.head(), "NIT-CULL")

    def test_cull_discards_the_rest_and_keeps_them_visible(self):
        # why: discarded is a closed outcome that stays listed so recurring nits show (A5).
        # proves: A5
        # catches: a cull that deletes the discarded items, or leaves them open
        L = self.passed_with_nits()
        code, _, err = L.call("cull", "--reply", L.file("c.txt", "KEEP: S1, N1\nS1: rename\nN1: real"))
        self.assertEqual(code, 0, err)
        self.assertEqual(L.data()["findings"]["S2"]["status"], "discarded")
        self.assertEqual(L.data()["findings"]["S1"]["status"], "open")
        self.assertRegex(L.run("status"), r"S2 .*=> discarded")

    def test_discarded_stash_item_stays_visible(self):
        # why: stash items are culled too and stay listed (A5).
        # proves: A5
        # catches: a cull that ignores N ids
        L = self.passed_with_nits()
        code, _, err = L.call("cull", "--reply", L.file("c.txt", "KEEP: S1, S2\nS1: a\nS2: b"))
        self.assertEqual(code, 0, err)
        self.assertRegex(L.run("stash"), r"N1.*discarded|discarded.*N1")

    def test_kept_stash_item_stays_pending_until_fixed_or_declined(self):
        # why: a kept N item is not closed by the cull; `next` asks for the fix, and `outcome N1` closes it (R5, S19, S20).
        # proves: R5 (S19, S20)
        # catches: a cull that marks kept N items closed, an outcome that only knows S ids, or a next() that jumps to STOP-AGREED
        for status, extra in (("fixed", []), ("declined", ["--evidence", "not worth it"])):
            with self.subTest(status):
                L = self.passed_with_nits(STASH_ONLY_NITS)
                code, _, err = L.call("cull", "--reply", L.file("c.txt", "KEEP: N2\nN2: real"))
                self.assertEqual(code, 0, err)
                self.assertEqual(L.nxt(), "FIX-KEPT: N2")
                self.assertRegex(L.run("stash"), r"N1.*discarded|discarded.*N1")
                code, _, err = L.call("outcome", "N2", status, *extra)
                self.assertEqual(code, 0, err)
                self.assertEqual(L.head(), "STOP-AGREED")

    def test_fix_kept_lists_every_open_kept_id_and_shrinks(self):
        # why: the orchestrator fixes kept items without a new review round; FIX-KEPT names what is still open (R5, S20).
        # proves: R5 (S20)
        # catches: a FIX-KEPT that lists all kept ids forever, or only the first, or that returns STOP-AGREED after one closes
        L = self.passed_with_nits()
        self.assertEqual(L.call("cull", "--reply", L.file("c.txt", "KEEP: S1, N1\nS1: a\nN1: b"))[0], 0)
        line = L.nxt()
        self.assertTrue(line.startswith("FIX-KEPT: "), line)
        self.assertEqual(set(re.findall(r"[SN]\d+", line)), {"S1", "N1"})
        self.assertEqual(L.call("outcome", "S1", "fixed")[0], 0)
        self.assertEqual(L.nxt(), "FIX-KEPT: N1")
        self.assertEqual(L.call("outcome", "N1", "declined", "--evidence", "ok")[0], 0)
        self.assertEqual(L.head(), "STOP-AGREED")

    def test_stop_agreed_after_all_kept_fixed_and_after_all_declined(self):
        # why: both closing outcomes end the loop (R5, S20).
        # proves: R5 (S20)
        # catches: a next() that treats only `fixed` (or only `declined`) as closed
        for status, extra in (("fixed", []), ("declined", ["--evidence", "ok"])):
            with self.subTest(status):
                L = self.passed_with_nits(FINDINGS_ONLY_NITS)
                self.assertEqual(L.call("cull", "--reply", L.file("c.txt", "KEEP: S1, S2\nS1: a\nS2: b"))[0], 0)
                self.assertTrue(L.nxt().startswith("FIX-KEPT"))
                self.assertEqual(L.call("outcome", "S1", status, *extra)[0], 0)
                self.assertEqual(L.call("outcome", "S2", status, *extra)[0], 0)
                self.assertEqual(L.head(), "STOP-AGREED")

    def test_keep_of_zero_ids_goes_straight_to_stop_agreed(self):
        # why: the reviewer may find no nit worth keeping; nothing is left to fix (R5, S20).
        # proves: R5 (S20)
        # catches: a next() that waits for kept items that do not exist, or a cull that errors on an empty KEEP
        for reply in ("KEEP: none", "KEEP:", "KEEP: none\nnothing here matters"):
            with self.subTest(reply=reply):
                L = self.passed_with_nits()
                code, _, err = L.call("cull", "--reply", L.file("c.txt", reply))
                self.assertEqual(code, 0, err)
                self.assertEqual(L.data()["findings"]["S1"]["status"], "discarded")
                self.assertEqual(L.data()["findings"]["S2"]["status"], "discarded")
                self.assertRegex(L.run("stash"), r"N1.*discarded|discarded.*N1")
                self.assertEqual(L.head(), "STOP-AGREED")


class StepBack(unittest.TestCase):
    def test_below_bar_fable_round3_asks_the_pivot_question(self):
        # why: the step-back continues the same Fable thread with a pivot question, not a new review (A6).
        # proves: A6
        # catches: reusing the old tier-1 step-back brief (full header, scoring format, findings request)
        L = ledger(self)
        L.two_below()
        L.rnd_ok("sha3", BELOW, "fable", "sonnet")
        self.assertEqual(L.head(), "STEP-BACK")
        brief = L.run("brief")
        self.assertIn("What should I pivot to instead", brief)
        self.assertIn("At most 15 lines", brief)
        self.assertNotIn("SCORE", brief)
        self.assertNotIn("Do not list more findings", brief)


class CommentFixups(unittest.TestCase):
    FIX = ("SCORE: 8/10\nVERDICT: APPROVE\nCOMMENT-FIXUPS:\n"
           "- lib/a.dart:12 reworded stale comment about null guard\n"
           "- lib/b.dart:9 removed a comment that restated the code\n")

    def test_header_states_the_full_comment_fixup_permission(self):
        # why: the permission must be complete: comment-only, no code, no docs, unslop loaded, and the listing format;
        #      and every other prohibition stays (A7, S22). Checked on the header block, in v2 and legacy briefs, round 1 and later.
        # proves: A7 (S22)
        # catches: dropping "Do not edit" without saying what is allowed, allowing code or docs edits, or losing the listing format
        for make in (ledger, legacy):
            L = make(self)
            if make is legacy:
                L.rnd_ok("sha1", BELOW, "sol", None)
            else:
                L.rnd_ok("sha1", BELOW, "sol", "sonnet")
            for brief in (make(self).run("brief"), L.run("brief")):
                block = brief.split("Repo:")[0]
                self.assertNotIn("Do not edit", block)
                self.assertRegex(block, r"(?i)review only")
                self.assertRegex(block, r"(?i)comment-only")
                self.assertRegex(block, r"(?i)\bno code\b")
                self.assertRegex(block, r"(?i)\bno docs?\b")
                self.assertRegex(block, r"(?i)unslop")
                self.assertIn("COMMENT-FIXUPS:", block)
                self.assertIn("- <file>:<line> <what changed>", block)
                self.assertRegex(block, r"(?i)do not[^\n]*commit[^\n]*push")
                # S22 r2: the subagent ban is part of the prohibition line, not a bare mention.
                self.assertRegex(block, r"(?i)do not[^\n]*\bstart subagents")
                self.assertNotRegex(block, r"(?im)^(?![^\n]*do not)[^\n]*\bstart subagents")

    def test_round_stores_comment_fixups_and_status_shows_them_with_descriptions(self):
        # why: the orchestrator must see which comments a reviewer changed, and what changed, before applying the patch (A7, S23).
        # proves: A7 (S23)
        # catches: parsing the section as findings/nits, dropping the description, or parsing it and never showing it
        L = ledger(self)
        code, _, err = L.rnd("sha1", self.FIX, "sol", "sonnet")
        self.assertEqual(code, 0, err)
        d = L.data()
        self.assertEqual(d["findings"], {})
        self.assertEqual(d.get("nit_stash", []), [])
        status = L.run("status")
        self.assertIn("COMMENT-FIXUPS", status)
        self.assertIn("lib/a.dart:12", status)
        self.assertIn("reworded stale comment about null guard", status)
        self.assertIn("lib/b.dart:9", status)
        self.assertIn("removed a comment that restated the code", status)
        raw = Path(L.path).read_text()
        self.assertIn("reworded stale comment about null guard", raw)
        self.assertIn("removed a comment that restated the code", raw)

    def test_fixups_next_to_stash_sections_parse_into_the_right_place(self):
        # why: reviewers end the reply with stash sections; a fixup bullet must not become a nit or hardening item, and a stash bullet not a fixup (A7, S23).
        # proves: A7 (S23)
        # catches: a stash parser that keeps the open stash across the COMMENT-FIXUPS header (the fixup lands in the stash)
        head = "SCORE: 9/10\nVERDICT: APPROVE\n"
        nit = "NIT-STASH:\n- c.py:3 a stashed nit\n"
        hard = "HARDENING-STASH:\n- d.py:4 a hardening item\n"
        fix = "COMMENT-FIXUPS:\n- lib/a.dart:12 reworded stale comment\n"
        orders = {"nit,fix,hard": nit + fix + hard, "fix,nit,hard": fix + nit + hard,
                  "nit,hard,fix": nit + hard + fix, "hard,nit,fix": hard + nit + fix}
        for label, tail in orders.items():
            with self.subTest(label):
                L = ledger(self)
                code, _, err = L.rnd("sha1", head + tail, "sol", "sonnet")
                self.assertEqual(code, 0, err)
                d = L.data()
                self.assertEqual([e["text"] for e in d.get("nit_stash", [])], ["c.py:3 a stashed nit"])
                self.assertEqual([e["text"] for e in d.get("hardening_stash", [])], ["d.py:4 a hardening item"])
                status = L.run("status")
                self.assertIn("COMMENT-FIXUPS", status)
                self.assertIn("lib/a.dart:12 reworded stale comment", status)
                self.assertNotIn("c.py:3", status.split("COMMENT-FIXUPS")[1].split("NEXT:")[0])

    def test_status_shows_no_fixups_section_when_none_were_reported(self):
        # why: positive control for the tests above: the line appears only when a reply had the section (A7).
        # proves: A7
        # catches: a status that always prints COMMENT-FIXUPS, or prints it for "none"
        L = ledger(self)
        L.rnd_ok("sha1", BELOW, "sol", "sonnet")
        self.assertNotIn("COMMENT-FIXUPS", L.run("status"))
        M = ledger(self)
        M.rnd_ok("sha1", BELOW + "\nCOMMENT-FIXUPS:\nnone", "sol", "sonnet")
        self.assertNotIn("COMMENT-FIXUPS", M.run("status"))




BOLD = ("Fuck me up, fam. Balls to the wall: say what you actually think, torch a wrong approach, "
        "and say ship it when it is good enough. No hedging, no asking permission.")


class FableBold(unittest.TestCase):
    """Owner 2026-11-13: briefs that go to Fable start with the BOLD line; Sol/Opus briefs never carry it."""

    def test_fable_briefs_start_with_the_bold_line(self):
        # why: round-3 review brief, STEP-BACK pivot brief (round 3 was Fable) and NIT-CULL brief all go to Fable.
        # catches: a bold line added to only one builder, or placed after the header
        L = ledger(self)
        L.two_below()
        self.assertIn("reviewer: fable", L.nxt())
        self.assertTrue(L.run("brief").startswith(BOLD + "\n"), L.run("brief")[:200])
        L.rnd_ok("sha3", BELOW, "fable", "sonnet")
        self.assertEqual(L.head(), "STEP-BACK")
        self.assertTrue(L.run("brief").startswith(BOLD + "\n"))
        self.assertIn("What should I pivot to instead", L.run("brief"))
        C = ledger(self)
        C.two_below()
        C.rnd_ok("sha3", MIXED_NITS, "fable", "sonnet")
        C.checkpoint()
        self.assertEqual(C.head(), "NIT-CULL")
        self.assertTrue(C.run("brief").startswith(BOLD + "\n"))

    def test_tier2_fable_brief_has_it_and_tier2_opus_brief_does_not(self):
        # why: tier 2 goes to Fable only when Opus wrote code; the line follows the reviewer, not the tier.
        # catches: a line keyed on tier, or on round number only
        F = ledger(self)
        F.rnd_ok("sha1", CLEAN_PASS, "sol", "opus")
        F.checkpoint()
        self.assertIn("reviewer: fable", F.nxt())
        self.assertTrue(F.run("brief").startswith(BOLD + "\n"))
        O = ledger(self)
        O.rnd_ok("sha1", CLEAN_PASS, "sol", "sonnet")
        O.checkpoint()
        self.assertIn("reviewer: opus", O.nxt())
        self.assertNotIn("Fuck me up, fam", O.run("brief"))

    def test_sol_opus_and_early_round_briefs_do_not_have_it(self):
        # why: only Fable gets the line (rounds 1, 2, 4, 5 go to Sol or Opus).
        # catches: a line added to every brief
        L = ledger(self)
        self.assertNotIn("Fuck me up, fam", L.run("brief"))  # round 1
        L.rnd_ok("sha1", BELOW, "sol", "sonnet")
        self.assertNotIn("Fuck me up, fam", L.run("brief"))  # round 2
        L.rnd_ok("sha2", BELOW, "opus", "sol")
        L.rnd_ok("sha3", BELOW, "fable", "sonnet")
        L.run("new-approach")
        self.assertNotIn("Fuck me up, fam", L.run("brief"))  # round 4

    def test_pivot_check_ignores_reviewer_case(self):
        # why: the author check lowercases; `--reviewer Fable` must still get the pivot brief (R1 nit).
        # catches: reviewer == "fable" compared case-sensitively
        L = ledger(self)
        L.two_below()
        L.rnd_ok("sha3", BELOW, "Fable", "sonnet")
        out = L.run("brief")
        self.assertIn("What should I pivot to instead", out)
        self.assertTrue(out.startswith(BOLD))


class BriefAndCheckpointText(unittest.TestCase):
    def test_brief_on_argue_and_fix_kept_is_one_line(self):
        # why: a full review brief on ARGUE or FIX-KEPT misleads the orchestrator (R1 nit).
        # catches: brief() falling through to the review brief on a non-ROUND step
        L = ledger(self)
        L.two_below()
        L.rnd_ok("sha3", CHANGES, "fable", "sonnet", pending=True)
        self.assertEqual(L.head(), "ARGUE")
        out = L.run("brief").strip()
        self.assertIn("Discuss round 3 with fable", out)
        self.assertIn("Review focus (weighting;", out)
        K = ledger(self)
        K.two_below()
        K.rnd_ok("sha3", MIXED_NITS, "fable", "sonnet")
        K.checkpoint()
        K.call("cull", "--reply", K.file("c.txt", "KEEP: S1"))
        self.assertEqual(K.head(), "FIX-KEPT")
        out = K.run("brief").strip()
        self.assertRegex(out, r"^No brief: next step is FIX-KEPT \(.+\)\.")
        self.assertIn("Review focus (weighting;", out)

    def test_checkpoint_at_round_3_says_the_cull_follows(self):
        # why: NIT-CULL handles the stash next, so "triage via `stash`" sends the orchestrator the wrong way.
        # catches: the legacy stash hint on a v2 round-3+ checkpoint; and losing it on rounds 1-2
        L = ledger(self)
        L.two_below()
        L.rnd_ok("sha3", MIXED_NITS, "fable", "sonnet")
        out = L.nxt()
        self.assertTrue(out.startswith("CHECKPOINT"), out)
        self.assertIn("the cull follows", out)
        self.assertNotIn("stashed nits to triage", out)
        E = ledger(self)
        E.rnd_ok("sha1", MIXED_NITS, "sol", "sonnet")
        out = E.nxt()
        self.assertTrue(out.startswith("CHECKPOINT"), out)
        self.assertIn("stashed nits to triage", out)
        self.assertNotIn("the cull follows", out)


if __name__ == "__main__":
    unittest.main()
