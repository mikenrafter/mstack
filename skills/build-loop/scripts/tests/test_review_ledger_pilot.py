"""Owner pilot decisions, 2026-11-15. Exercise the ledger CLI and persisted state."""
import json
import unittest
from pathlib import Path

from test_review_ledger_v2 import V2


class Pilot(unittest.TestCase):
    def ledger(self, *extra, pilot=True):
        flags = ("--pilot",) if pilot else ()
        return V2(self, bar=None, extra=flags + extra)

    def test_default_bars_and_data_exception(self):
        # why: CLAIM(pilot-bars): defaults are 6, durability 7; data writes need 9.
        for extra, durability in (((), 7), (("--touches-data",), 9),
                                  (("--category", "migration"), 9)):
            with self.subTest(extra=extra):
                L = self.ledger("--category", "legibility", "--category", "durability",
                                "--category", "security", *extra)
                self.assertEqual(L.data()["concerns"]["legibility"], 6)
                self.assertEqual(L.data()["concerns"]["security"], 6)
                self.assertEqual(L.data()["concerns"]["durability"], durability)
                self.assertIn("default", " ".join(L.data()["bar_reasons"]))
                self.assertTrue(L.data()["pilot"])

    def test_data_flag_adds_durability_to_default_concerns(self):
        # why: data safety must be scored even if the caller omitted its category.
        L = self.ledger("--touches-data")
        self.assertEqual(L.data()["concerns"], {"testability": 6, "durability": 9})

    def test_agreed_bars_are_the_scored_set_and_ignore_other_scores(self):
        # why: CLAIM(pilot-bars): the owner's feature agreement names the bars and scope.
        L = self.ledger("--bar", "durability=9", "--bar", "wiring=7",
                        "--bars-agreed", "Owner: protect data at 9, wiring at 7")
        self.assertEqual(L.data()["concerns"], {"durability": 9, "wiring": 7})
        self.assertEqual(L.data()["bars_agreed"], "Owner: protect data at 9, wiring at 7")
        L.run("owner-ok", "Owner: pilot build looks good")
        L.rnd_ok("s1", "SCORE[durability]: 9/10\nSCORE[wiring]: 6/10", "sol")
        self.assertEqual(L.head(), "ROUND")
        L.rnd_ok("s2", "SCORE[durability]: 9/10\nSCORE[wiring]: 7/10\nSCORE[docs]: 2/10", "fable")
        self.assertEqual(L.head(), "CHECKPOINT")

    def test_named_bars_require_agreement_and_reject_mixed_forms(self):
        # why: an unrecorded or ambiguous agreement must not silently select bars.
        L = self.ledger()
        before = Path(L.path).read_bytes()
        for flags in (("--bar", "wiring=7"), ("--bar", "6", "--bar", "wiring=7"),
                      ("--bar", "wiring=7", "--bars-agreed", " ")):
            code, _, _ = L.call("init", "--pilot", "--repo", "r", "--base", "b",
                                "--intent", "pilot", "--project-kind", "cli-tool", *flags)
            self.assertEqual(code, 2)
            self.assertEqual(Path(L.path).read_bytes(), before)

    def test_pilot_init_does_not_create_or_change_region_bars(self):
        # why: CLAIM(pilot-region): pilots cannot lock shape/stage or consume owner resets.
        L = self.ledger()
        research = Path(L.dir.name) / "research"
        research.mkdir()
        bars = research / "review" / "bars.json"
        flags = ("init", "--pilot", "--repo", "r", "--research", str(research),
                 "--base", "b", "--intent", "pilot", "--project-kind", "cli-tool")
        L.run(*flags)
        self.assertFalse(bars.exists())
        bars.write_text('{"regions": {".": {"shape": "library", "stage": "production"}}, '
                        '"stages": [{"region": ".", "stage": "prototype", "shape": "pivot"}]}\n')
        before = bars.read_bytes()
        L.run(*flags, "--shape", "glue", "--stage", "prototype")
        self.assertEqual(bars.read_bytes(), before)
        self.assertNotIn("stage_change", L.data())

    def test_round_two_fable_and_non_pilot_schedule(self):
        # why: CLAIM(pilot-schedule): Fable moves to round 2 only in pilot mode.
        for pilot in (True, False):
            L = self.ledger(pilot=pilot)
            L.rnd_ok("s1", "SCORE: 4/10", "sol")
            self.assertIn("reviewer: fable" if pilot else "reviewer: sol, opus or neon", L.nxt())
            before = Path(L.path).read_bytes()
            code, _, _ = L.rnd("s2", "SCORE: 4/10", "sol" if pilot else "fable")
            self.assertEqual(code, 2)
            self.assertEqual(Path(L.path).read_bytes(), before)
            L.rnd_ok("s2", "SCORE: 4/10", "fable" if pilot else "opus")
            if pilot:
                self.assertEqual(L.head(), "STEP-BACK")
            else:
                self.assertIn("reviewer: fable", L.nxt())

    def test_passing_first_round_still_schedules_fable(self):
        # why: a passing Sol round cannot divert the pilot's second review to tier-2 Opus.
        L = self.ledger()
        L.run("owner-ok", "Owner: pilot build approved")
        L.rnd_ok("s1", "SCORE: 6/10", "sol")
        self.assertIn("tier 1 round 2", L.nxt())
        self.assertIn("reviewer: fable", L.nxt())
        self.assertEqual(L.rnd("bypass", "SCORE: 6/10", "opus", tier=2)[0], 2)
        L.rnd_ok("s2", "SCORE: 6/10", "fable")
        self.assertEqual(L.head(), "CHECKPOINT")

    def test_after_pilot_pivot_normal_rounds_and_caps_resume(self):
        # why: moving Fable to round 2 must not reduce the total cap or repeat Fable at 3.
        L = self.ledger()
        L.rnd_ok("s1", "SCORE: 4/10", "sol")
        L.rnd_ok("s2", "SCORE: 4/10", "fable")
        L.run("new-approach")
        for number, reviewer in ((3, "sol"), (4, "opus"), (5, "sol")):
            self.assertIn("reviewer: sol, opus or neon", L.nxt())
            L.rnd_ok(f"s{number}", "SCORE: 4/10", reviewer)
        self.assertEqual(L.head(), "STOP-STUCK")

    def test_scored_safety_finding_still_blocks_with_owner_ok(self):
        # why: owner approval never waives a data-safety finding needed for its bar.
        L = self.ledger("--touches-data")
        L.run("owner-ok", "Owner: pilot looks good")
        L.rnd_ok("s1", "SCORE: 9/10\nS1 [should] [needed for bar: yes] "
                 "[concern: durability] db.py:1 lost write. Fix: transaction", "sol")
        L.rnd_ok("s2", "SCORE: 9/10", "fable", pending=True)
        self.assertEqual(L.head(), "ARGUE")
        L.argue(2)
        self.assertEqual(L.head(), "STEP-BACK")
        self.assertEqual(L.data()["findings"]["S1"]["status"], "open")

    def test_owner_gate_rejects_checkpoint_and_blocks_stop(self):
        # why: CLAIM(pilot-owner): passing scores never substitute for a pilot-build thumbs-up.
        L = self.ledger()
        L.rnd_ok("s1", "SCORE: 4/10", "sol")
        L.rnd_ok("s2", "SCORE: 6/10", "fable")
        self.assertEqual(L.head(), "OWNER-OK")
        before = Path(L.path).read_bytes()
        self.assertEqual(L.call("checkpoint")[0], 2)
        self.assertEqual(L.call("owner-ok", " ")[0], 2)
        self.assertEqual(Path(L.path).read_bytes(), before)
        quote = "Owner: tried the pilot build, thumbs up"
        L.run("owner-ok", quote)
        self.assertEqual(L.data()["owner_ok"]["quote"], quote)
        self.assertIn(quote, L.run("status"))
        self.assertEqual(L.head(), "CHECKPOINT")
        L.checkpoint()
        self.assertEqual(L.head(), "STOP-AGREED")
        data = L.data()
        data.pop("owner_ok")
        Path(L.path).write_text(json.dumps(data))
        self.assertEqual(L.head(), "OWNER-OK")

    def test_round_two_argue_then_cull_and_fix_kept(self):
        # why: CLAIM(pilot-schedule): the whole Fable machinery moves, including captured ARGUE.
        L = self.ledger()
        L.run("owner-ok", "Owner: yes to the build")
        L.rnd_ok("s1", "SCORE: 4/10", "sol")
        L.rnd_ok("s2", "SCORE: 4/10\nVERDICT: CHANGES\nNIT-STASH:\n- x.py:1 old nit", "fable", pending=True)
        self.assertEqual(L.head(), "ARGUE")
        L.argue()
        self.assertEqual(L.head(), "ARGUE")
        L.call("argue", "--note", L.file("revision", "Orchestrator: Does the revised score permit checkpoint?\nReviewer: Yes, the score reaches the bar.\nSCORE: 6/10\nVERDICT: APPROVE"))
        self.assertEqual(L.head(), "CHECKPOINT")
        L.checkpoint()
        self.assertEqual(L.head(), "NIT-CULL")
        self.assertEqual(L.call("cull", "--reply", L.file("keep", "KEEP: N1"))[0], 0)
        self.assertEqual(L.nxt(), "FIX-KEPT: N1")
        L.run("outcome", "N1", "fixed")
        self.assertEqual(L.head(), "STOP-AGREED")

    def test_nonblocking_and_unagreed_findings_use_existing_hardening_stash(self):
        # why: CLAIM(pilot-stash): off-bar work is deferred, even when labelled should/blocker.
        L = self.ledger("--bar", "wiring=7", "--bars-agreed", "Owner: wiring is the pilot goal")
        self.assertIn("not needed", L.run("brief"))
        L.rnd_ok("s1", "SCORE[wiring]: 7/10\n"
                 "S1 [should] [needed for bar: no] [concern: wiring] a.py:1 tidy helper. Fix: tidy\n"
                 "S2 [blocker] [needed for bar: yes] [concern: docs] b.md:2 translate copy. Fix: translate\n"
                 "HARDENING-STASH:\n- x.py:3 pixel sweeps", "sol")
        self.assertEqual(L.data()["findings"], {})
        self.assertEqual(len(L.data()["hardening_stash"]), 3)
        self.assertEqual(L.data()["nit_stash"], [])
        self.assertIn("reviewer: fable", L.nxt())
        L.rnd_ok("s2", "SCORE[wiring]: 7/10", "fable")
        self.assertEqual(L.head(), "OWNER-OK")
        self.assertIn("closed until a hardening phase", L.run("stash"))
        L.run("hardening")
        self.assertIn("tidy helper", L.run("brief"))
        L.rnd_ok("h1", "SCORE: 4/10", "sol")
        self.assertIn("reviewer: sol, opus or neon", L.nxt())
        self.assertEqual(L.data()["concerns"], {"wiring": 8})

    def test_structural_nonblocking_findings_also_wait_for_hardening(self):
        # why: current-stage scope applies to structural reviews too; no added triage phase.
        L = self.ledger(pilot=False)
        L.rnd_ok("s1", "SCORE: 9/10\n"
                 "S1 [should] [needed for bar: no] a.py:1 stricter measurement. Fix: harness", "sol")
        self.assertEqual(L.data()["findings"], {})
        self.assertEqual(len(L.data()["hardening_stash"]), 1)
        self.assertEqual(L.head(), "CHECKPOINT")

