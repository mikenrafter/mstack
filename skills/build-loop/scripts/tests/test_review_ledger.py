"""Tests for scripts/review-ledger. Run: python3 -I -m unittest discover -s scripts/tests"""
import contextlib
import importlib.machinery
import importlib.util
import io
import json
import os
import re
import subprocess
import tempfile
import unittest
from collections import Counter
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "review-ledger"
_loader = importlib.machinery.SourceFileLoader("review_ledger", str(SCRIPT))
_spec = importlib.util.spec_from_loader("review_ledger", _loader)
rl = importlib.util.module_from_spec(_spec)
_loader.exec_module(rl)


UM = "one agent calls it, one request at a time; input comes from the same user"


class Ledger:
    """Drives the CLI against a temp ledger, as an agent would."""

    def __init__(self, test, bar=8, extra=()):
        self.dir = tempfile.TemporaryDirectory()
        test.addCleanup(self.dir.cleanup)
        self.path = str(Path(self.dir.name) / "ledger.json")
        bar_args = ["--bar", str(bar)] if bar is not None else []
        if "--category" not in extra:
            bar_args += ["--category", "test"]  # testability is 8 at explore-first prototype; the default `logic` is 9
        model = [] if any(x in extra for x in ("--threat-model", "--project-kind")) else ["--usage-model", UM]
        self.run("init", "--repo", "r", "--base", "base0", *bar_args, "--intent", "fix x", *model, *extra)

    def run(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rl.main(["-l", self.path, *args])
        return out.getvalue()

    def round(self, tier, sha, reply):
        p = Path(self.dir.name) / f"reply-{sha}.txt"
        p.write_text(reply)
        return self.run("round", "--tier", str(tier), "--reviewer", "sol" if tier == 1 else "opus",
                        "--sha", sha, "--reply", str(p))

    def next(self):
        return self.run("next").split(":")[0]

    def data(self):
        return json.loads(Path(self.path).read_text())


BUG = "S1 [should] [needed for bar: yes] [class: null deref] lib/a.dart:12, lib/b.dart:9 user may be null. Fix: guard"


class ParseReply(unittest.TestCase):
    def test_full_finding_line(self):
        score, verdict, fs, res = rl.parse_reply(f"SCORE: 6/10 (fix S1)\nVERDICT: CHANGES\n{BUG}\n")
        self.assertEqual((score, verdict, res), (6.0, "CHANGES", []))
        f = fs[0]
        self.assertEqual(f["severity"], "should")
        self.assertEqual(f["needed"], "yes")
        self.assertEqual(f["class"], "null deref")
        self.assertEqual(f["where"], ["lib/a.dart:12", "lib/b.dart:9"])
        self.assertEqual(f["claim"], "user may be null.")
        self.assertEqual(f["fix"], "guard")
        self.assertFalse(f["pre_existing"])

    def test_minimal_finding_and_pre_existing_tag(self):
        _, _, fs, _ = rl.parse_reply("S2 [nit] [pre-existing] wording is odd")
        self.assertEqual(fs[0]["where"], [])
        self.assertEqual(fs[0]["claim"], "wording is odd")
        self.assertTrue(fs[0]["pre_existing"])
        self.assertIsNone(fs[0]["needed"])

    def test_resolutions_are_not_findings(self):
        _, _, fs, res = rl.parse_reply("SCORE: 9/10\nS1 resolved\nS2 still open: guard misses b.dart")
        self.assertEqual(fs, [])
        self.assertEqual(res, [("S1", "resolved", ""), ("S2", "still open", "guard misses b.dart")])

    def test_missing_score(self):
        self.assertIsNone(rl.parse_reply("looks fine")[0])

    def test_prose_mentioning_ids_is_ignored(self):
        _, _, fs, res = rl.parse_reply("As in S1, the code is fine.\nSee S3 above.")
        self.assertEqual((fs, res), ([], []))


class Flow(unittest.TestCase):
    def test_happy_path_through_both_tiers(self):
        L = Ledger(self)
        self.assertEqual(L.next(), "ROUND")
        L.round(1, "sha1", f"SCORE: 6/10\nVERDICT: CHANGES\n{BUG}")
        self.assertEqual(L.next(), "ROUND")
        self.assertIn("See ONLY: git diff sha1", L.run("brief"))
        L.run("outcome", "S1", "fixed")
        L.round(1, "sha2", "SCORE: 8/10\nVERDICT: APPROVE\nS1 resolved")
        self.assertEqual(L.next(), "CHECKPOINT")
        self.assertIn("No brief", L.run("brief"))
        L.run("checkpoint")
        brief = L.run("brief")
        self.assertIn("See: git diff base0", brief)
        self.assertIn("Do not re-raise ledger items", brief)
        L.round(2, "sha2", "SCORE: 9/10\nVERDICT: APPROVE")
        self.assertEqual(L.next(), "STOP-AGREED")

    def test_score_at_bar_with_open_blocker_does_not_pass(self):
        L = Ledger(self)
        L.round(1, "sha1", f"SCORE: 8/10\n{BUG}")
        self.assertEqual(L.next(), "ROUND")

    def test_open_nit_does_not_block(self):
        L = Ledger(self)
        L.round(1, "sha1", "SCORE: 8/10\nS1 [nit] [needed for bar: no] a.dart:1 rename")
        self.assertEqual(L.next(), "CHECKPOINT")

    def test_still_open_reopens_a_fixed_finding(self):
        L = Ledger(self)
        L.round(1, "sha1", f"SCORE: 6/10\n{BUG}")
        L.run("outcome", "S1", "fixed")
        L.round(1, "sha2", "SCORE: 8/10\nS1 still open: b.dart:9 unguarded")
        self.assertEqual(L.data()["findings"]["S1"]["status"], "open")
        self.assertEqual(L.next(), "ROUND")

    def test_three_rounds_below_bar_step_back_then_new_approach(self):
        L = Ledger(self)
        for i in range(3):
            L.round(1, f"sha{i}", "SCORE: 6/10")
        self.assertEqual(L.next(), "STEP-BACK")
        self.assertIn("Do not list more findings", L.run("brief"))
        L.run("new-approach")
        self.assertEqual(L.next(), "ROUND")
        L.round(1, "sha3", "SCORE: 6/10")
        self.assertEqual(L.next(), "ROUND")
        L.round(1, "sha4", "SCORE: 6/10")
        self.assertEqual(L.next(), "STOP-STUCK")  # 5 tier-1 rounds in total

    def test_tier2_below_bar_gets_one_re_review(self):
        L = Ledger(self)
        L.round(1, "sha1", "SCORE: 9/10")
        L.run("checkpoint")
        L.round(2, "sha1", f"SCORE: 6/10\n{BUG}")
        self.assertEqual(L.next(), "ROUND")
        L.run("outcome", "S1", "fixed")
        L.round(2, "sha2", "SCORE: 7/10\nS1 resolved")
        self.assertEqual(L.next(), "STOP-STUCK")

    def test_dispute_cap(self):
        L = Ledger(self)
        L.round(1, "sha1", f"SCORE: 6/10\n{BUG}")
        L.run("outcome", "S1", "disagree", "--evidence", "caller checks null")
        L.round(1, "sha2", "SCORE: 7/10\nS1 still open: other caller does not")
        self.assertEqual(L.next(), "ROUND")
        L.round(1, "sha3", "SCORE: 7/10\nS1 still open: still")
        self.assertEqual(L.next(), "STOP-STUCK")

    def test_round_without_score_is_rejected(self):
        L = Ledger(self)
        with self.assertRaises(SystemExit):
            L.round(1, "sha1", "no score here")
        self.assertEqual(L.data()["rounds"], [])


class Repeats(unittest.TestCase):
    def test_re_raising_a_declined_finding_is_closed_as_repeat(self):
        L = Ledger(self)
        L.round(1, "sha1", f"SCORE: 6/10\n{BUG}")
        L.run("outcome", "S1", "declined", "--evidence", "out of scope")
        out = L.round(1, "sha2", "SCORE: 7/10\n" + BUG.replace("S1", "S2"))
        self.assertIn("S2 repeats S1", out)
        self.assertEqual(L.data()["findings"]["S2"]["status"], "repeat")
        self.assertEqual(L.next(), "ROUND")  # 7 < bar

    def test_new_instance_of_a_fixed_class_stays_open(self):
        L = Ledger(self)
        L.round(1, "sha1", f"SCORE: 6/10\n{BUG}")
        L.run("outcome", "S1", "fixed")
        L.round(1, "sha2", "SCORE: 8/10\nS1 resolved\n"
                "S2 [should] [class: null deref] lib/c.dart:4 missed instance. Fix: guard")
        f = L.data()["findings"]["S2"]
        self.assertEqual(f["status"], "open")
        self.assertIn("S1", f["evidence"])
        self.assertEqual(L.next(), "ROUND")

    def test_reused_id_gets_a_fresh_id(self):
        L = Ledger(self)
        L.round(1, "sha1", f"SCORE: 6/10\n{BUG}")
        L.round(1, "sha2", "SCORE: 6/10\nS1 [nit] other.dart:1 different thing")
        self.assertEqual(sorted(L.data()["findings"]), ["S1", "S2"])
        self.assertEqual(L.data()["findings"]["S1"]["severity"], "should")


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@t", "-c", "user.name=t", *args],
                   check=True, capture_output=True)


class RepoCase(unittest.TestCase):
    """A temp git repo with a sibling research dir; init() drives `review-ledger init`."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.repo = self.root / "proj"
        self.repo.mkdir()
        git(self.repo, "init", "-q")
        (self.repo / "keep.txt").write_text("x")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-qm", "base")
        self.base = subprocess.run(["git", "-C", str(self.repo), "rev-parse", "HEAD"],
                                   capture_output=True, text=True).stdout.strip()
        self.research = self.root / "proj.research"
        self.research.mkdir()
        self.n = 0

    def touch(self, rel):
        f = self.repo / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("changed")

    def init(self, *args, ledger=None, model=True):
        self.n += 1
        path = ledger or str(self.root / f"new{self.n}.json")
        has_model = any(a in ("--threat-model", "--usage-model", "--project-kind") for a in args)
        given = ["--usage-model", UM] if model and not has_model else []
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rl.main(["-l", path, "init", "--repo", str(self.repo), "--base", self.base,
                     "--intent", "x", *given, *args])
        return out.getvalue(), json.loads(Path(path).read_text())

    def old_ledger(self, name, findings, age=0):
        f = self.research / "review" / f"{name}.ledger.json"
        f.parent.mkdir(exist_ok=True)
        f.write_text(json.dumps({"findings": findings}))
        os.utime(f, (1_000_000 - age, 1_000_000 - age))

    @staticmethod
    def finding(cls, where="lib/a.dart:1", status="fixed"):
        return {"class": cls, "where": [where], "status": status, "claim": "c"}


class Bars(RepoCase):
    """init suggests a bar from categories, recurring classes, owner floors and residual."""

    def test_slug_is_stored_and_free_text_warns_but_is_kept(self):
        """WHY: reviewers get a vocabulary, yet a reply with prose must never be rejected."""
        L = Ledger(self)
        out = L.round(1, "s1", "SCORE: 6/10\nS1 [should] [class: Fail Open Read] a.py:1 x\n"
                      "S2 [should] [class: null deref] b.py:1 y")
        f = L.data()["findings"]
        self.assertEqual(f["S1"]["class"], "fail-open-read")
        self.assertNotIn("class_canonical", f["S1"])
        self.assertEqual((f["S2"]["class"], f["S2"]["class_canonical"]), ("null deref", False))
        self.assertIn("warning: S2", out)
        self.assertIn("ordering-stale-write", out)
        self.assertNotIn("warning: S1", out)
        self.assertIn("fail-open-read", L.run("brief"))

    def test_old_free_text_ledger_still_loads(self):
        """WHY: ledgers written before CLASSES existed must keep working."""
        L = Ledger(self)
        old = L.data()
        old.pop("bar_suggested", None)
        old["findings"] = {"S1": {"id": "S1", "severity": "should", "needed": "yes", "class": "null deref",
                                  "pre_existing": False, "where": ["a.py:1"], "claim": "c", "fix": "",
                                  "round": 1, "tier": 1, "status": "open", "evidence": None}}
        old["rounds"] = [{"n": 1, "tier": 1, "approach": 1, "reviewer": "sol", "sha": "abcdef12345",
                          "score": 6.0, "verdict": None}]
        Path(L.path).write_text(json.dumps(old))
        self.assertIn("bar 8/10", L.run("status"))
        self.assertIn("null deref", L.run("brief"))
        self.assertEqual(L.next(), "ROUND")

    def test_escaped_outcome_closes_the_finding(self):
        """WHY: a shipped defect is history, not an open blocker for the next round."""
        L = Ledger(self)
        L.round(1, "s1", f"SCORE: 9/10\n{BUG}")
        L.run("outcome", "S1", "escaped", "--evidence", "seen in prod")
        self.assertEqual(L.data()["findings"]["S1"]["status"], "escaped")
        self.assertEqual(L.next(), "CHECKPOINT")

    def test_category_base_bars(self):
        """WHY: the bar must follow the riskiest category; the default (logic) is legibility-led at explore-first prototype."""
        self.touch("a.txt")
        for cats, want in [([], 9), (["docs"], 7), (["docs", "logic"], 9), (["logic", "consent"], 9)]:
            args = [x for c in cats for x in ("--category", c)]
            out, led = self.init(*args)
            self.assertEqual((led["bar"], led["bar_suggested"], led["categories"]), (want, want, cats))
            self.assertIn(f"Suggested bar: {want}", out)

    def test_recurrence_hot_via_two_findings(self):
        """WHY: the same class twice in files this diff touches predicts a third miss."""
        self.touch("lib/a.dart")
        self.old_ledger("one", {"S1": self.finding("fail-open-read")})
        self.old_ledger("two", {"S1": self.finding("fail-open-read")}, age=10)
        self.old_ledger("cold", {"S1": self.finding("lifecycle-leak")}, age=20)
        out, led = self.init("--category", "test")
        self.assertEqual(led["bar_suggested"], 9)
        self.assertIn("hot class fail-open-read: 2", out)
        self.assertIn("one.ledger.json", out)
        self.assertNotIn("lifecycle-leak", out)

    def test_single_finding_or_untouched_file_is_not_hot(self):
        """WHY: one finding, or findings in files this diff does not touch, is not a pattern."""
        self.touch("lib/a.dart")
        self.old_ledger("one", {"S1": self.finding("fail-open-read"),
                                "S2": self.finding("hidden-state", "lib/zzz.dart:3"),
                                "S3": self.finding("hidden-state", "lib/zzz.dart:4")})
        self.assertEqual(self.init("--category", "test")[1]["bar_suggested"], 8)

    def test_recurrence_hot_via_one_escaped(self):
        """WHY: a defect that shipped weighs more than two caught in review."""
        self.touch("lib/a.dart")
        self.old_ledger("one", {"S1": self.finding("consent-bypass", status="escaped")})
        out, led = self.init("--category", "test")
        self.assertEqual(led["bar_suggested"], 9)
        self.assertIn("one escaped", out)

    def test_hot_is_capped_at_9_and_only_three_newest_ledgers_count(self):
        """WHY: only an owner may demand 10; stale ledgers must not keep a class hot."""
        self.touch("lib/a.dart")
        for i in range(3):
            self.old_ledger(f"n{i}", {"S1": self.finding("hidden-state", status="escaped")}, age=i)
        out, led = self.init("--category", "pii")
        self.assertEqual(led["bar_suggested"], 9)
        self.assertIn("n0.ledger.json", out)
        self.old_ledger("ancient", {"S1": self.finding("data-exposure", status="escaped")}, age=99)
        self.assertNotIn("data-exposure", self.init()[0])

    def test_untracked_and_paths_scope(self):
        """WHY: new files count as changed, and --paths narrows what counts."""
        self.touch("lib/a.dart")
        self.old_ledger("one", {"S1": self.finding("hidden-state", status="escaped")})
        self.assertEqual(self.init("--category", "test")[1]["bar_suggested"], 9)
        self.assertEqual(self.init("--paths", "other", "--category", "test")[1]["bar_suggested"], 8)

    def test_owner_floor_10_is_allowed(self):
        """WHY: the owner can pin a path to 10, and then --bar 10 needs no reason."""
        self.touch("lib/secure/k.dart")
        (self.research / "review").mkdir()
        (self.research / "review" / "bars.json").write_text(json.dumps(
            {"keep": 1, "owner": [{"paths": ["lib/secure/*"], "bar": 10, "reason": "keys", "date": "d"}]}))
        out, led = self.init("--bar", "10")
        self.assertEqual((led["bar"], led["bar_suggested"]), (10, 10))
        self.assertIn("owner floor 10", out)
        hist = json.loads((self.research / "review" / "bars.json").read_text())
        self.assertEqual(hist["keep"], 1)
        self.assertEqual(hist["history"][0]["chosen"], 10)
        self.assertEqual(hist["history"][0]["suggested"], 10)

    def test_bar_below_suggestion_or_10_needs_a_reason(self):
        """WHY: lowering the bar, or asking for 10 unprompted, must leave a written reason."""
        self.touch("a.txt")
        for bar in ("7", "10"):
            err = io.StringIO()
            with contextlib.redirect_stderr(err), self.assertRaises(SystemExit) as cm:
                self.init("--category", "consent", "--bar", bar) if bar == "7" else self.init("--bar", bar)
            self.assertEqual(cm.exception.code, 2)
            self.assertIn("--bar-reason", err.getvalue())
        _, led = self.init("--category", "consent", "--bar", "7", "--bar-reason", "docs only")
        self.assertEqual((led["bar"], led["bar_suggested"], led["bar_reason"]), (7, 9, "docs only"))

    def test_no_ledger_is_written_when_refused(self):
        """WHY: a refused init must not leave a half-configured ledger behind."""
        path = str(self.root / "refused.json")
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            self.init("--category", "consent", "--bar", "5", ledger=path)
        self.assertFalse(Path(path).exists())

    def test_history_is_appended_per_init(self):
        """WHY: the owner audits bar choices later from bars.json."""
        self.touch("a.txt")
        self.init("--category", "docs")
        self.init("--category", "logic")
        hist = json.loads((self.research / "review" / "bars.json").read_text())["history"]
        self.assertEqual([h["chosen"] for h in hist], [7, 9])
        self.assertEqual((hist[0]["shape"], hist[0]["stage"]), ("explore-first", "prototype"))
        self.assertEqual(hist[0]["categories"], ["docs"])

    def test_residual_absent(self):
        """WHY: no residual dir is normal and must be said, not guessed at."""
        self.assertIn("residual: not set up (bar from paths and ledgers)", self.init()[0])

    def test_residual_present_reports_forces_without_changing_bar(self):
        """WHY: residual is evidence for the owner, never an automatic bar change."""
        self.touch("src/auth/login.kt")
        res = self.repo / "residual"
        res.mkdir()
        (res / "components.csv").write_text(
            "name,description,status,architecture_set\napp::Auth,d,actual,b\nbilling,d,actual,b\n")
        (res / "residues.csv").write_text("id,shortname,app::Auth,billing\nS-01,a,1,\nS-02,b,1,1\nS-03,c,,1\n")
        out, led = self.init("--category", "test")
        self.assertIn("residual: app::Auth carries 2 forces", out)
        self.assertNotIn("billing", out)
        self.assertEqual(led["bar"], 8)

    def test_residual_unreadable_residues_does_not_crash(self):
        """WHY: a half-set-up residual dir must not break init."""
        self.touch("src/auth.kt")
        res = self.repo / "residual"
        res.mkdir()
        (res / "components.csv").write_text("name\nauth\n")
        self.assertIn("residual: unreadable", self.init()[0])


SKILL_DIR = Path(__file__).resolve().parents[2]
SECURITY_CATEGORIES = ("permissions", "consent", "pii", "signing", "egress")
TM_TRIVIAL = "Reach: local single user\nUntrusted: none\nHolds: nothing\nOne developer runs it by hand."
TM_LOCAL_DATA = "Reach: local single user\nUntrusted: local files or captured data\nHolds: nothing"
TM_NETWORK_SECRETS = "Reach: network\nUntrusted: network input\nHolds: secrets"
STASH_REPLY = (
    "SCORE: 6/10 (fix S1)\nVERDICT: CHANGES\n" + BUG + "\n"
    "NIT-STASH:\n- lib/a.dart:3 rename x to count\n- S7 [nit] lib/b.dart:2 trailing space\n\n"
    "HARDENING-STASH:\n- lib/a.dart:20 two writers with one id in the same millisecond\n")


def refuses(test, fn, *needles):
    """fn must exit 2 and say every needle on stderr."""
    err = io.StringIO()
    with contextlib.redirect_stderr(err), test.assertRaises(SystemExit) as cm:
        fn()
    test.assertEqual(cm.exception.code, 2, err.getvalue())
    for n in needles:
        test.assertIn(n, err.getvalue())


class BarTables(unittest.TestCase):
    """B1, B2, B4: the shape x stage tables keep their range, caps and per-shape claims."""

    def cells(self):
        for shape in rl.SHAPES:
            for stage in rl.STAGES:
                for concern, bar in rl.bars_for(shape, stage).items():
                    yield shape, stage, concern, bar

    def test_b1_every_shape_and_stage_rates_every_concern_from_6_to_10(self):
        """WHY: a missing concern would silently fall back to no bar; B1 fixes the range."""
        self.assertEqual(len(rl.SHAPES), 9)
        self.assertEqual(rl.STAGES, ("prototype", "beta", "production"))
        for shape in rl.SHAPES:
            for stage in rl.STAGES:
                table = rl.bars_for(shape, stage)
                self.assertEqual(set(table), set(rl.CONCERNS) - {"security"}, (shape, stage))
                for concern, bar in table.items():
                    self.assertIsInstance(bar, int, (shape, stage, concern))
                    self.assertTrue(6 <= bar <= 10, (shape, stage, concern, bar))

    def test_b1_most_bars_are_7_or_8_and_10_is_rare(self):
        """WHY: B1 says 7 and 8 dominate, 6 is a floor and 10 is rare; a table of 9s would burn rounds."""
        n = Counter(bar for *_, bar in self.cells())
        self.assertGreater(n[7] + n[8], n[6] + n[9] + n[10])
        self.assertLessEqual(n[10], len(rl.SHAPES))

    # (shape, concern, stage) cells that may be 6 outside a spike. Owner rule: 6 is rare; the taper only
    # reaches 6 (glue architecture at production); research may be low on code quality (spec B4 shape 8).
    ALLOWED_6 = frozenset(
        {("glue", "architecture", "production")}
        | {("research", c, st) for c, sts in {
            "architecture": ("prototype", "beta", "production"), "concurrency": ("prototype", "beta"),
            "durability": ("prototype",), "performance": ("prototype", "beta"),
            "compatibility": ("prototype", "beta"), "observability": ("prototype",),
            "error-paths": ("prototype",), "wiring": ("prototype",), "docs": ("prototype",),
        }.items() for st in sts})

    def test_b1_six_is_rare_outside_a_spike_and_only_in_named_cells(self):
        """WHY: owner rule. 6 is the spike shape, a tapered peak, or a concern the spec names low for a shape;
        every other not-yet-ramped concern starts at 7."""
        cells = [c for c in self.cells() if c[0] != "spike"]
        sixes = [(sh, co, st) for sh, st, co, bar in cells if bar == 6]
        self.assertLessEqual(len(sixes) / len(cells), 0.10, len(sixes))
        self.assertEqual(set(sixes) - self.ALLOWED_6, set())

    def test_b1_the_only_non_spike_6_outside_research_is_a_taper_from_7(self):
        """WHY: the taper only reaches 6, from a higher stage; it is not a starting bar."""
        for sh, co, st in self.ALLOWED_6:
            if sh != "research":
                prev = rl.STAGES[rl.RANK[st] - 1]
                self.assertEqual(rl.bars_for(sh, prev)[co], 7, (sh, co))

    def test_b4_exploration_shapes_put_legibility_9_8_7_above_early_architecture(self):
        """WHY: while direction is unknown, readable code is what lets the next move be cheap."""
        for shape in ("explore-first", "pivot"):
            self.assertEqual([rl.bars_for(shape, st)["legibility"] for st in rl.STAGES], [9, 8, 7], shape)
            p = rl.bars_for(shape, "prototype")
            self.assertGreater(p["legibility"], p["architecture"], shape)

    def test_b2_only_architecture_reaches_10_and_only_at_one_stage_per_shape(self):
        """WHY: B2 ramp cap. A rising concern stops at 9; architecture alone has a peak that may be 10."""
        for shape, stage, concern, bar in self.cells():
            if bar == 10:
                self.assertEqual(concern, "architecture", (shape, stage))
        for shape in rl.SHAPES:
            peaks = [s for s in rl.STAGES if rl.bars_for(shape, s)["architecture"] == 10]
            self.assertLessEqual(len(peaks), 1, shape)

    def test_b12_security_is_not_a_shape_by_stage_cell(self):
        """WHY: amendment A1. The security bar comes from the threat model, not from a fixed floor per shape."""
        for shape in rl.SHAPES:
            for stage in rl.STAGES:
                self.assertNotIn("security", rl.bars_for(shape, stage), (shape, stage))

    def test_b4_explore_first_puts_legibility_first_then_peaks_architecture_late(self):
        """WHY: while direction is unknown, legibility beats architecture; architecture peaks at beta, then tapers."""
        t = {st: rl.bars_for("explore-first", st) for st in rl.STAGES}
        self.assertGreater(t["prototype"]["legibility"], t["prototype"]["architecture"])
        self.assertEqual(t["beta"]["architecture"], 10)
        self.assertLess(t["production"]["architecture"], 10)

    def test_b4_port_peaks_architecture_at_prototype(self):
        """WHY: direction is borrowed, so the structure is the only open question from day one."""
        self.assertEqual(rl.bars_for("port", "prototype")["architecture"], 10)
        self.assertLess(rl.bars_for("port", "beta")["architecture"], 10)

    def test_b4_rewrite_is_high_on_architecture_and_compat_and_robust_a_stage_earlier(self):
        """WHY: a replacement inherits the old system's users, so robustness rises one stage before explore-first."""
        rw0 = rl.bars_for("rewrite", "prototype")
        self.assertGreaterEqual(rw0["architecture"], 9)
        self.assertGreaterEqual(rw0["compatibility"], 9)
        for concern in ("concurrency", "durability", "error-paths", "performance", "observability"):
            for i in (0, 1):
                self.assertEqual(rl.bars_for("rewrite", rl.STAGES[i])[concern],
                                 rl.bars_for("explore-first", rl.STAGES[i + 1])[concern], (concern, i))

    def test_b4_spike_is_all_6(self):
        """WHY: a spike's output is knowledge. A1 removed its security 8: security follows the threat model."""
        for stage in rl.STAGES:
            for concern, bar in rl.bars_for("spike", stage).items():
                self.assertEqual(bar, 6, (stage, concern))

    def test_b4_glue_keeps_architecture_low_and_wiring_rollback_blast_radius_high(self):
        """WHY: in integration work the wiring, rollback and blast radius are what breaks."""
        for stage in rl.STAGES:
            t = rl.bars_for("glue", stage)
            self.assertLessEqual(t["architecture"], 7)
        beta = rl.bars_for("glue", "beta")
        for concern in ("wiring", "durability", "compatibility"):
            self.assertIn(beta[concern], (8, 9), concern)

    def test_b4_research_rates_measurement_9_early_and_code_quality_6_to_7(self):
        """WHY: a benchmark that measures the wrong thing is worth nothing; its code is throwaway-grade."""
        self.assertEqual(rl.bars_for("research", "prototype")["measurement"], 9)
        for stage in rl.STAGES:
            for concern, bar in rl.bars_for("research", stage).items():
                if concern not in ("measurement", "security"):
                    self.assertLessEqual(bar, 7, (stage, concern))

    def test_b4_library_compatibility_steps_to_9_at_the_first_outside_user(self):
        """WHY: the first outside user (stage beta) is what makes the API hard to change."""
        self.assertLess(rl.bars_for("library", "prototype")["compatibility"], 9)
        self.assertEqual(rl.bars_for("library", "beta")["compatibility"], 9)
        self.assertEqual(rl.bars_for("library", "production")["compatibility"], 9)

    def test_b4_accretion_and_pivot_run_the_explore_first_curve(self):
        """WHY: a new region (or a reset one) starts exploring again; only its stage differs from the repo's."""
        for stage in rl.STAGES:
            for shape in ("accretion", "pivot"):
                self.assertEqual(rl.bars_for(shape, stage)["architecture"],
                                 rl.bars_for("explore-first", stage)["architecture"])

    def test_bars_md_table_matches_the_script_tables(self):
        """WHY: parity. The doc a person reads and the table the script applies must be the same numbers."""
        rows = {}
        for line in (SKILL_DIR / "references" / "bars.md").read_text().splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cells and cells[0] in rl.CONCERNS and len(cells) == len(rl.SHAPES) + 1:
                rows[cells[0]] = cells[1:]
        self.assertEqual(set(rows), set(rl.CONCERNS) - {"security"})
        for concern, cells in rows.items():
            for shape, cell in zip(rl.SHAPES, cells):
                want = "/".join(str(rl.bars_for(shape, st)[concern]) for st in rl.STAGES)
                self.assertEqual(cell, want, (concern, shape))


class ShapeInputs(RepoCase):
    """B3, B11: shape and stage come from flags, from declared facts, or from the printed default."""

    def test_b3_each_shape_and_stage_is_stored_in_the_ledger(self):
        """WHY: later loops reuse the shape and stage from the ledger (B10)."""
        self.touch("a.txt")
        for shape in rl.SHAPES:
            if shape == "pivot":
                continue  # needs an owner entry; see Ratchet
            for stage in rl.STAGES:
                _, led = self.init("--shape", shape, "--stage", stage, "--region", f"{shape}-{stage}")
                self.assertEqual((led["shape"], led["stage"]), (shape, stage))
                self.assertEqual(led["region"], f"{shape}-{stage}")

    def test_b3_unknown_shape_or_stage_is_rejected(self):
        """WHY: a typo must not fall back to some other table."""
        for flag, bad in (("--shape", "greenfield"), ("--stage", "alpha")):
            refuses(self, lambda: self.init(flag, bad))

    def test_b3_shape_is_derived_from_the_declared_facts(self):
        """WHY: the owner declares facts about the project; the script picks the table."""
        cases = [
            (["--throwaway"], "spike"),
            (["--lifespan", "short"], "spike"),
            (["--lifespan", "short", "--users-at-start", "yes"], "explore-first"),
            (["--direction-known", "no"], "explore-first"),
            (["--users-at-start", "yes"], "explore-first"),
            (["--direction-known", "yes"], "port"),
            (["--direction-known", "yes", "--users-at-start", "yes", "--outside-consumers", "no"], "rewrite"),
            (["--direction-known", "no", "--users-at-start", "yes", "--formats", "costly"], "library"),
        ]
        for i, (facts, want) in enumerate(cases):
            out, led = self.init(*facts, "--region", f"case{i}")
            self.assertEqual(led["shape"], want, facts)
            self.assertIn(f"Shape: {want} (derived from", out)

    def test_b3_shape_and_facts_together_are_refused(self):
        """WHY: two sources of one answer; the script must not pick silently."""
        refuses(self, lambda: self.init("--shape", "port", "--throwaway"), "--shape", "facts")

    def test_b3_category_keeps_selecting_the_touched_concerns(self):
        """WHY: --category stays; it picks which table rows the diff touches."""
        _, led = self.init("--shape", "glue", "--stage", "beta", "--category", "egress", "--category", "docs")
        self.assertEqual(set(led["concerns"]), {"security", "docs"})

    def test_b11_default_is_explore_first_prototype_and_says_so(self):
        """WHY: B11. Old command lines keep working, and the output says what was assumed."""
        out, led = self.init()
        self.assertEqual((led["shape"], led["stage"], led["region"]), ("explore-first", "prototype", "."))
        self.assertIn("Shape: explore-first (default", out)
        self.assertIn("Stage: prototype (default", out)


class DiffBar(RepoCase):
    """B2, B4, B5: the diff's bar is the max over touched concerns, then recurrence, then owner floors."""

    def test_b5_init_prints_shape_stage_and_each_touched_concern(self):
        """WHY: the reader must see why the bar is what it is (B5)."""
        self.touch("a.txt")
        out, led = self.init("--shape", "glue", "--stage", "beta", "--category", "logic")
        for line in ("Shape: glue", "Stage: beta", "legibility: 7", "error-paths: 8", "Suggested bar: 8"):
            self.assertIn(line, out)
        self.assertEqual((led["bar"], led["concerns"]), (8, {"legibility": 7, "error-paths": 8}))

    def test_b5_categories_take_the_highest_touched_concern(self):
        """WHY: a mixed diff pays for its riskiest part."""
        self.touch("a.txt")
        _, led = self.init("--shape", "explore-first", "--stage", "production",
                           "--category", "docs", "--category", "concurrency")
        self.assertEqual(led["bar"], 9)

    def test_b2_architecture_10_is_automatic_at_its_peak_and_needs_no_reason(self):
        """WHY: owner rule. The peak is 10 without extra approval; anywhere else 10 needs an owner floor."""
        self.touch("a.txt")
        _, led = self.init("--shape", "explore-first", "--stage", "beta", "--category", "architecture", "--bar", "10")
        self.assertEqual((led["bar"], led["bar_suggested"]), (10, 10))
        refuses(self, lambda: self.init("--shape", "explore-first", "--stage", "prototype", "--region", "early",
                                        "--category", "architecture", "--bar", "10"), "--bar-reason")

    def test_b2_recurrence_adds_one_up_to_9_and_never_lowers_a_10(self):
        """WHY: the +1 is capped at 9; an architecture peak of 10 must not be pulled down to 9."""
        self.touch("lib/a.dart")
        self.old_ledger("one", {"S1": self.finding("fail-open-read")})
        self.old_ledger("two", {"S1": self.finding("fail-open-read")}, age=10)
        for shape, stage, cat, want in [("explore-first", "prototype", "architecture", 8),
                                        ("explore-first", "production", "concurrency", 9),
                                        ("explore-first", "beta", "architecture", 10)]:
            _, led = self.init("--shape", shape, "--stage", stage, "--category", cat, "--region", f"{stage}{cat}")
            self.assertEqual(led["bar_suggested"], want, (stage, cat))

    def test_b2_owner_floor_may_reach_10_on_any_concern(self):
        """WHY: B2 exception (b): an owner floor in bars.json may demand 10."""
        self.touch("lib/secure/k.dart")
        (self.research / "review").mkdir()
        (self.research / "review" / "bars.json").write_text(json.dumps(
            {"owner": [{"paths": ["lib/secure/*"], "bar": 10, "reason": "keys", "date": "d"}]}))
        out, led = self.init("--shape", "explore-first", "--stage", "prototype", "--category", "docs")
        self.assertEqual(led["bar"], 10)
        self.assertIn("owner floor 10", out)

    def test_b12_security_categories_follow_the_threat_model_not_the_shape(self):
        """WHY: A1. A local single-user tool holding nothing is 7 in every shape; there is no floor of 8."""
        self.touch("a.txt")
        for shape in ("glue", "research", "explore-first", "library"):
            for cat in SECURITY_CATEGORIES:
                _, led = self.init("--shape", shape, "--stage", "prototype", "--category", cat,
                                   "--threat-model", TM_TRIVIAL, "--region", f"{shape}-{cat}")
                self.assertEqual(led["bar"], 7, (shape, cat))
                self.assertEqual(led["concerns"], {"security": 7})

    def test_b12_spike_security_is_6_for_a_trivial_threat_model_and_follows_it_otherwise(self):
        """WHY: A1. The spike's security 8 is gone; a spike that holds secrets still needs a real bar."""
        self.touch("a.txt")
        out, led = self.init("--shape", "spike", "--category", "logic")
        self.assertEqual(led["bar"], 6)
        self.assertIn("no review needed", led["note"])
        self.assertIn("no review needed", out)
        _, led = self.init("--shape", "spike", "--category", "egress", "--threat-model", TM_TRIVIAL, "--region", "s2")
        self.assertEqual(led["bar"], 6)
        self.assertNotIn("no review needed", led.get("note", ""))
        _, led = self.init("--shape", "spike", "--category", "egress", "--threat-model", TM_NETWORK_SECRETS,
                           "--region", "s3")
        self.assertEqual(led["bar"], 9)

    def test_b4_new_region_uses_its_own_stage_even_when_the_repo_is_production(self):
        """WHY: accretion. A new region starts at prototype however mature the rest is."""
        self.init("--stage", "production")
        out, led = self.init("--shape", "accretion", "--region", "new-mod")
        self.assertEqual((led["stage"], led["region"]), ("prototype", "new-mod"))
        self.assertIn("Stage: prototype (default", out)
        regions = json.loads((self.research / "review" / "bars.json").read_text())["regions"]
        self.assertEqual((regions["."]["stage"], regions["new-mod"]["stage"]), ("production", "prototype"))


class UsageModel(unittest.TestCase):
    """B6, B14: the threat model (usage included) is required, `--usage-model` stays as an alias, the brief prints it."""

    def run_init(self, path, *args):
        rl.main(["-l", path, "init", "--repo", "r", "--base", "b0", "--intent", "x", *args])

    def test_b6_missing_empty_or_dash_threat_model_is_refused(self):
        """WHY: the v1 ledger had "Threat model: -" and reviewers assumed hostile multi-writer use."""
        with tempfile.TemporaryDirectory() as d:
            path = str(Path(d) / "l.json")
            refuses(self, lambda: self.run_init(path), "--threat-model", "--project-kind")
            for flag in ("--threat-model", "--usage-model"):
                for bad in ("", "-", "   "):
                    refuses(self, lambda: self.run_init(path, flag, bad), flag)
            self.assertFalse(Path(path).exists())

    def test_b14_usage_model_is_an_accepted_alias_of_threat_model(self):
        """WHY: command lines written before A1 keep working."""
        with tempfile.TemporaryDirectory() as d:
            a, b = str(Path(d) / "a.json"), str(Path(d) / "b.json")
            with contextlib.redirect_stdout(io.StringIO()):
                self.run_init(a, "--usage-model", TM_TRIVIAL)
                self.run_init(b, "--threat-model", TM_TRIVIAL)
            la, lb = json.loads(Path(a).read_text()), json.loads(Path(b).read_text())
            for k in ("threat_model", "threat_model_status", "threat_facts"):
                self.assertEqual(la[k], lb[k], k)
            refuses(self, lambda: self.run_init(str(Path(d) / "c.json"), "--usage-model", "x", "--threat-model", "y"),
                    "not both")

    def test_b6_brief_prints_the_threat_model_and_the_bar_context(self):
        """WHY: the reviewer needs who calls it, how many at once, and what is untrusted."""
        L = Ledger(self, extra=("--shape", "glue", "--stage", "beta"))
        brief = L.run("brief")
        self.assertIn(f"Threat model (confirmed): {UM}", brief)
        self.assertIn("glue", brief)
        self.assertIn("beta", brief)
        self.assertEqual(L.data()["threat_model"], UM)


class Stashes(unittest.TestCase):
    """B7, B8: reviewers put nits and unreproducible findings in stashes the brief never shows."""

    def test_b8_stash_sections_are_parsed_and_kept_out_of_findings(self):
        """WHY: a stashed line shaped like a finding must not become one."""
        nits, hard = rl.parse_stashes(STASH_REPLY)
        self.assertEqual(nits, ["lib/a.dart:3 rename x to count", "S7 [nit] lib/b.dart:2 trailing space"])
        self.assertEqual(hard, ["lib/a.dart:20 two writers with one id in the same millisecond"])
        score, _, fs, res = rl.parse_reply(STASH_REPLY)
        self.assertEqual((score, [f["id"] for f in fs], res), (6.0, ["S1"], []))

    def test_b8_stash_formats_none_inline_numbered_and_ending_at_a_non_bullet(self):
        """WHY: reviewers write the sections in slightly different shapes; none may eat a real finding."""
        self.assertEqual(rl.parse_stashes("NIT-STASH: none\nHARDENING-STASH: -\n"), ([], []))
        nits, hard = rl.parse_stashes("nit-stash: a.py:1 inline\n1. a.py:2 numbered\n* a.py:3 star\n"
                                      "S2 resolved\nHARDENING-STASH:\n- h.py:1 x\n")
        self.assertEqual(nits, ["a.py:1 inline", "a.py:2 numbered", "a.py:3 star"])
        self.assertEqual(hard, ["h.py:1 x"])
        _, _, fs, res = rl.parse_reply("NIT-STASH:\n- a.py:2 n\nS2 resolved\nS3 [should] a.py:5 real\n")
        self.assertEqual((res, [f["id"] for f in fs]), ([("S2", "resolved", "")], ["S3"]))

    def test_b8_round_stores_both_stashes_and_brief_hides_them(self):
        """WHY: the orchestrator must not see nits or hardening items before their phase (like holdout tests)."""
        L = Ledger(self)
        out = L.round(1, "sha1", STASH_REPLY)
        led = L.data()
        self.assertEqual(sorted(led["findings"]), ["S1"])
        self.assertEqual([e["text"] for e in led["nit_stash"]][0], "lib/a.dart:3 rename x to count")
        self.assertEqual(len(led["nit_stash"]), 2)
        self.assertEqual(led["hardening_stash"][0]["round"], 1)
        self.assertIn("2 nits", out)
        self.assertIn("1 hardening", out)
        for hidden in ("rename x to count", "trailing space", "same millisecond"):
            self.assertNotIn(hidden, L.run("brief"))
            self.assertNotIn(hidden, L.run("status"))

    def test_b8_nit_stash_opens_at_the_checkpoint_and_hardening_stays_closed(self):
        """WHY: nits open when tier 1 passes; hardening opens only in its own phase (B9)."""
        L = Ledger(self)
        L.round(1, "sha1", STASH_REPLY)
        before = L.run("stash")
        self.assertNotIn("rename x to count", before)
        self.assertIn("closed", before)
        L.run("outcome", "S1", "fixed")
        L.round(1, "sha2", "SCORE: 8/10\nS1 resolved")
        self.assertEqual(L.next(), "CHECKPOINT")
        self.assertIn("2 stashed nits", L.run("next"))
        opened = L.run("stash")
        self.assertIn("rename x to count", opened)
        self.assertIn("ONE central change", opened)
        self.assertNotIn("same millisecond", opened)
        L.run("checkpoint")
        self.assertIn("rename x to count", L.run("stash"))
        self.assertNotIn("same millisecond", L.run("stash"))

    def test_b7_b8_brief_asks_for_a_realistic_reproduction_and_the_stash_sections(self):
        """WHY: the reviewer is told how to file; findings without a reproduction go to the hardening stash."""
        brief = Ledger(self).run("brief")
        for needle in ("realistic reproduction", "threat model", "who does what", "how often",
                       "HARDENING-STASH:", "NIT-STASH:"):
            self.assertIn(needle, brief)

    def test_b8_review_md_and_bars_md_carry_the_same_wording(self):
        """WHY: the docs the orchestrator reads must name the same sections the script asks for."""
        for name in ("review.md", "bars.md"):
            text = (SKILL_DIR / "references" / name).read_text()
            for needle in ("NIT-STASH", "HARDENING-STASH", "realistic reproduction"):
                self.assertIn(needle, text, name)


class Hardening(unittest.TestCase):
    """B9: the hardening stash opens only in its own phase, and that phase uses the next stage's bars."""

    def test_b9_hardening_opens_the_stash_and_uses_the_next_stage_bars(self):
        """WHY: items deferred at prototype are judged at the bar of the stage the region is entering."""
        L = Ledger(self, bar=None, extra=("--shape", "explore-first", "--stage", "prototype",
                                          "--category", "architecture"))
        self.assertEqual(L.data()["bar"], 7)
        L.round(1, "sha1", STASH_REPLY)
        out = L.run("hardening")
        self.assertIn("same millisecond", out)
        self.assertIn("beta", out)
        self.assertEqual((L.data()["hardening"]["stage"], L.data()["hardening"]["bar"], L.data()["bar"]), ("beta", 10, 10))
        self.assertIn("same millisecond", L.run("stash"))
        self.assertIn("same millisecond", L.run("brief"))
        self.assertIn("Hardening phase", L.run("brief"))

    def test_b9_production_has_no_next_stage(self):
        """WHY: the last stage hardens against its own bars."""
        L = Ledger(self, bar=None, extra=("--stage", "production", "--category", "architecture"))
        L.round(1, "sha1", STASH_REPLY)
        L.run("hardening")
        self.assertEqual((L.data()["hardening"]["stage"], L.data()["hardening"]["bar"]), ("production", 8))

    def test_b9_hardening_pulls_items_from_earlier_ledgers(self):
        """WHY: at a stage change the stash lives in the earlier loops' ledgers."""
        old = Ledger(self, extra=("--stage", "prototype"))
        old.round(1, "sha1", STASH_REPLY)
        new = Ledger(self, bar=None, extra=("--stage", "beta", "--category", "architecture"))
        out = new.run("hardening", "--from", old.path)
        self.assertIn("same millisecond", out)
        led = new.data()
        self.assertEqual(led["hardening"]["stage"], "beta")
        self.assertEqual(led["hardening_stash"][0]["source"], old.path)
        new.run("hardening", "--from", old.path)
        self.assertEqual(len(new.data()["hardening_stash"]), 1)

    def test_b9_a_round_never_opens_the_hardening_stash(self):
        """WHY: hardening is never part of an ordinary quality round."""
        L = Ledger(self)
        L.round(1, "sha1", STASH_REPLY)
        L.round(1, "sha2", "SCORE: 6/10\nS1 still open: x")
        self.assertNotIn("hardening", L.data())
        self.assertNotIn("same millisecond", L.run("next") + L.run("brief") + L.run("stash"))


class Ratchet(RepoCase):
    """B10: a region's stage only rises on its own; the owner lowers it in bars.json."""

    def bars_json(self):
        return json.loads((self.research / "review" / "bars.json").read_text())

    def pin(self, **entry):
        f = self.research / "review" / "bars.json"
        data = json.loads(f.read_text()) if f.exists() else {}
        data.setdefault("stages", []).append({"region": ".", "reason": "owner", "date": "2026-11-11", **entry})
        f.parent.mkdir(exist_ok=True)
        f.write_text(json.dumps(data))

    def test_b10_stage_and_shape_are_recorded_and_reused_by_later_loops(self):
        """WHY: the next loop must not have to repeat, or contradict, the last one."""
        self.init("--shape", "port", "--stage", "beta")
        self.assertEqual(self.bars_json()["regions"]["."]["stage"], "beta")
        out, led = self.init()
        self.assertEqual((led["shape"], led["stage"]), ("port", "beta"))
        self.assertIn("reused", out)

    def test_b10_a_rising_stage_is_accepted_and_schedules_hardening(self):
        """WHY: stage entry is when the hardening phase is due."""
        self.init("--stage", "prototype")
        out, led = self.init("--stage", "beta")
        self.assertEqual(led["stage"], "beta")
        self.assertEqual(led["stage_change"], {"from": "prototype", "to": "beta"})
        self.assertIn("hardening", out)
        self.assertEqual(self.bars_json()["regions"]["."]["stage"], "beta")

    def test_b10_an_automatic_downgrade_is_refused_and_writes_nothing(self):
        """WHY: a lower stage means lower bars; only the owner may decide that."""
        self.init("--stage", "beta")
        path = str(self.root / "down.json")
        refuses(self, lambda: self.init("--stage", "prototype", ledger=path), "beta", "bars.json")
        self.assertFalse(Path(path).exists())
        self.assertEqual(self.bars_json()["regions"]["."]["stage"], "beta")
        self.assertEqual(len(self.bars_json()["history"]), 1)

    def test_b10_an_owner_entry_lowers_the_stage_once_then_the_ratchet_resumes(self):
        """WHY: the owner's word is final, applied once; after that the stage rises on its own again."""
        self.init("--stage", "beta")
        self.pin(stage="prototype")
        _, led = self.init("--stage", "prototype")
        self.assertEqual(led["stage"], "prototype")
        self.assertEqual(self.bars_json()["regions"]["."]["stage"], "prototype")
        _, led = self.init("--stage", "beta")
        self.assertEqual(led["stage"], "beta")
        refuses(self, lambda: self.init("--stage", "prototype"), "bars.json")

    def test_b10_changing_the_recorded_shape_needs_the_owner(self):
        """WHY: switching to spike would be a silent downgrade of every bar."""
        self.init("--shape", "port")
        refuses(self, lambda: self.init("--shape", "spike"), "port", "bars.json")
        self.pin(stage="prototype", shape="spike")
        _, led = self.init("--shape", "spike")
        self.assertEqual(led["shape"], "spike")

    def test_b10_pivot_is_an_owner_declared_reset_to_prototype(self):
        """WHY: exploration resurges only when the owner says the region pivoted."""
        self.init("--shape", "explore-first", "--stage", "production")
        refuses(self, lambda: self.init("--shape", "pivot"), "pivot", "bars.json")
        refuses(self, lambda: self.init("--shape", "pivot", "--region", "fresh"), "owner-declared reset")
        self.pin(stage="prototype")
        out, led = self.init("--shape", "pivot")
        self.assertEqual((led["shape"], led["stage"]), ("pivot", "prototype"))
        self.assertIn("owner", out)

    def test_b10_without_a_research_dir_the_ratchet_is_unchecked_not_fatal(self):
        """WHY: a repo with no sibling research dir still gets bars, with the gap said aloud."""
        L = Ledger(self, extra=("--stage", "beta"))
        self.assertEqual(L.data()["stage"], "beta")
        self.assertIn("ratchet unchecked", " ".join(L.data()["bar_reasons"]))


class OldLedger(unittest.TestCase):
    """B11: ledgers written before shapes, stages and stashes still load and run."""

    def old(self):
        L = Ledger(self)
        led = L.data()
        for k in ("shape", "stage", "region", "usage_model", "concerns", "nit_stash", "hardening_stash",
                  "note", "stage_change", "owner_floor", "hardening", "shape_source", "stage_source",
                  "threat_model_status", "threat_facts", "threat_model_path", "concern_bars", "bar_table"):
            led.pop(k, None)
        led["threat_model"] = ""  # before A1 the default was empty
        Path(L.path).write_text(json.dumps(led))
        return L

    def test_b11_every_command_runs_on_a_ledger_without_the_new_fields(self):
        """WHY: loops in flight, and old ledgers read for recurrence, must not crash."""
        L = self.old()
        self.assertIn("bar 8/10", L.run("status"))
        self.assertIn("Threat model: -", L.run("brief"))
        self.assertEqual(L.next(), "ROUND")
        self.assertIn("empty", L.run("stash"))
        L.round(1, "sha1", STASH_REPLY)
        self.assertEqual(len(L.data()["nit_stash"]), 2)
        L.run("outcome", "S1", "fixed")
        self.assertIn("same millisecond", L.run("hardening"))
        self.assertEqual(L.data()["hardening"]["stage"], "beta")  # old ledgers count as explore-first prototype


class BarValidation(RepoCase):
    """HARDENING-STASH from review r1: explicit bars are integers 6..10, with or without a reason."""

    def test_explicit_bar_must_be_an_integer_from_6_to_10(self):
        """WHY: --bar-reason used to let 5, 11 and 8.5 through; a bar outside B1 means nothing."""
        for bad in ("8.5", "5", "11", "0", "abc"):
            for reason in ((), ("--bar-reason", "because")):
                path = str(self.root / "bad.json")
                refuses(self, lambda: self.init("--bar", bad, *reason, ledger=path), "--bar", "6..10")
                self.assertFalse(Path(path).exists(), bad)
        _, led = self.init("--bar", "9", "--bar-reason", "owner asked")
        self.assertEqual(led["bar"], 9)

    def test_owner_floor_outside_6_to_10_is_ignored_with_a_warning(self):
        """WHY: a typo in bars.json must not raise a bar to 11 or 8.5 silently."""
        self.touch("lib/k.dart")
        (self.research / "review").mkdir()
        for bad in (11, 8.5, "9", 5):
            (self.research / "review" / "bars.json").write_text(json.dumps(
                {"owner": [{"paths": ["lib/*"], "bar": bad, "reason": "typo"}]}))
            out, led = self.init("--category", "docs")
            self.assertEqual(led["bar_suggested"], 7, bad)
            self.assertIn("warning", out)
            self.assertIn("6..10", out)


class ShapeFacts(RepoCase):
    """Review r1 S4: facts that cannot tell a replacement from a library need --shape or --outside-consumers."""

    def test_s4_ambiguous_facts_require_an_explicit_shape(self):
        """WHY: direction known + existing users fits both a rewrite and a library with consumers."""
        for facts in (["--direction-known", "yes", "--users-at-start", "yes"],
                      ["--direction-known", "yes", "--users-at-start", "yes", "--outside-consumers", "yes"]):
            path = str(self.root / "amb.json")
            refuses(self, lambda: self.init(*facts, ledger=path), "--shape", "rewrite", "library")
            self.assertFalse(Path(path).exists())
        _, led = self.init("--shape", "library", "--region", "explicit")
        self.assertEqual(led["shape"], "library")

    def test_s4_outside_consumers_tells_a_replacement_from_a_library(self):
        """WHY: a replacement has users it must keep; a library has consumers outside the repo."""
        cases = [
            (["--direction-known", "yes", "--users-at-start", "yes", "--outside-consumers", "no"], "rewrite"),
            (["--outside-consumers", "yes"], "library"),
            (["--direction-known", "no", "--users-at-start", "yes", "--outside-consumers", "yes"], "library"),
            (["--direction-known", "yes", "--outside-consumers", "yes"], "library"),
            (["--users-at-start", "yes", "--outside-consumers", "no", "--formats", "costly"], "explore-first"),
            (["--lifespan", "short", "--formats", "reversible", "--outside-consumers", "yes"], "library"),
            (["--throwaway", "--outside-consumers", "yes"], "spike"),
        ]
        for i, (facts, want) in enumerate(cases):
            _, led = self.init(*facts, "--region", f"c{i}")
            self.assertEqual(led["shape"], want, facts)

    def test_s4_outside_consumers_is_a_declared_fact_not_a_shape_companion(self):
        """WHY: B3 says give the shape or the facts, not both."""
        refuses(self, lambda: self.init("--shape", "port", "--outside-consumers", "yes"), "--shape", "facts")


class RatchetShape(RepoCase):
    """Review r1 S2: an owner stage reset does not unlock a shape change; a pivot needs a prototype reset."""

    bars_json = Ratchet.bars_json
    pin = Ratchet.pin

    def test_s2_stage_only_owner_entry_keeps_the_recorded_shape(self):
        """WHY: lowering port/beta to prototype must not let --shape spike lower every bar as well."""
        self.init("--shape", "port", "--stage", "beta")
        self.pin(stage="prototype")
        refuses(self, lambda: self.init("--shape", "spike", "--stage", "prototype"), "port", "bars.json")
        out, led = self.init("--stage", "prototype")
        self.assertEqual((led["shape"], led["stage"]), ("port", "prototype"))
        _, led = self.init("--shape", "port")
        self.assertEqual(led["shape"], "port")

    def test_s2_an_entry_naming_a_shape_authorizes_that_shape_only(self):
        """WHY: the owner decides the shape change; anything else stays refused."""
        self.init("--shape", "port", "--stage", "beta")
        self.pin(stage="prototype", shape="rewrite")
        refuses(self, lambda: self.init("--shape", "spike"), "port", "bars.json")
        _, led = self.init("--shape", "rewrite")
        self.assertEqual((led["shape"], led["stage"]), ("rewrite", "prototype"))

    def test_s2_a_new_pivot_needs_an_entry_that_resets_to_prototype(self):
        """WHY: a production entry must not pass as a pivot (a pivot is a reset to prototype)."""
        self.init("--shape", "explore-first", "--stage", "production")
        self.pin(stage="production")
        refuses(self, lambda: self.init("--shape", "pivot"), "pivot", "prototype")
        self.assertEqual(self.bars_json()["regions"]["."]["shape"], "explore-first")
        refuses(self, lambda: self.init("--shape", "pivot", "--region", "fresh"), "owner-declared reset")

    def test_s2_a_recorded_pivot_can_be_named_again_without_a_new_entry(self):
        """WHY: the owner's entry applies once, but later loops of the pivoted region may repeat --shape pivot."""
        self.init("--shape", "explore-first", "--stage", "production")
        self.pin(stage="prototype")
        self.init("--shape", "pivot")
        _, led = self.init("--shape", "pivot")
        self.assertEqual(led["shape"], "pivot")


class StashFormat(unittest.TestCase):
    """Review r1 S3: stash items may wrap, and an unbulleted finding-shaped line under a header stays a stash item."""

    def test_s3_indented_continuation_lines_extend_the_item_and_later_bullets_survive(self):
        """WHY: a wrapped bullet used to end the section and drop every later item."""
        text = ("NIT-STASH:\n- a.py:1 first nit\n    that wraps here\n- a.py:2 second\n\n"
                "HARDENING-STASH:\n- h.py:1 long\n  wrapped\n  twice\n- h.py:2 next\n")
        nits, hard = rl.parse_stashes(text)
        self.assertEqual(nits, ["a.py:1 first nit that wraps here", "a.py:2 second"])
        self.assertEqual(hard, ["h.py:1 long wrapped twice", "h.py:2 next"])

    def test_s3_a_finding_shaped_line_directly_under_a_stash_header_is_a_stash_item(self):
        """WHY: it must not become a blocking round finding that shows in the brief."""
        text = "SCORE: 8/10\nHARDENING-STASH:\nS2 [should] lib/a.py:3 two writers race\nNIT-STASH:\nS3 [nit] a.py:1 x\n"
        self.assertEqual(rl.parse_stashes(text), (["S3 [nit] a.py:1 x"], ["S2 [should] lib/a.py:3 two writers race"]))
        self.assertEqual(rl.parse_reply(text)[2], [])

    def test_s3_round_keeps_such_a_line_out_of_findings_and_the_brief(self):
        """WHY: end to end, the stash item stays hidden and does not block."""
        L = Ledger(self)
        L.round(1, "sha1", "SCORE: 8/10\nVERDICT: APPROVE\nHARDENING-STASH:\nS2 [should] lib/a.py:3 two writers race\n")
        self.assertEqual(L.data()["findings"], {})
        self.assertEqual(len(L.data()["hardening_stash"]), 1)
        self.assertNotIn("two writers race", L.run("brief"))
        self.assertEqual(L.next(), "CHECKPOINT")

    def test_s3_none_bullets_are_not_items(self):
        """WHY: "- none" is how the brief tells a reviewer to write an empty stash."""
        self.assertEqual(rl.parse_stashes("NIT-STASH:\n- none\nHARDENING-STASH:\n- n/a\n"), ([], []))

    def test_s3_a_finding_after_a_bulleted_stash_is_still_a_finding(self):
        """WHY: the unbulleted rule must not swallow real findings that follow a stash."""
        _, _, fs, _ = rl.parse_reply("HARDENING-STASH:\n- h.py:1 x\nS3 [should] a.py:5 real\n")
        self.assertEqual([f["id"] for f in fs], ["S3"])


class ThreatModel(RepoCase):
    """Amendment A1 (B12-B14): security follows the threat model; it is stored, reused and marked inferred."""

    ladder = [
        # (reach, untrusted, holds, bar)
        ("local single user", "none", "nothing", 7),
        ("local single user", "none", "owner data", 8),
        ("local single user", "local files or captured data", "nothing", 8),
        ("other local users", "none", "nothing", 8),
        ("local single user", "none", "secrets", 9),
        ("local single user", "none", "others data", 9),
        ("network", "none", "nothing", 9),
        ("public", "none", "nothing", 9),
        ("local single user", "network input", "nothing", 9),
        ("local single user", "third-party code", "nothing", 9),
        ("network", "network input", "secrets", 9),
    ]

    def facts(self, reach, untrusted, holds):
        return rl.parse_threat_model(f"Reach: {reach}\nUntrusted: {untrusted}\nHolds: {holds}")[0]

    def test_b12_security_bar_ladder(self):
        """WHY: B12. 7 with nothing reachable or held; 8 for local untrusted data; 9 for network, secrets, others' data."""
        for reach, untrusted, holds, want in self.ladder:
            self.assertEqual(rl.security_bar(self.facts(reach, untrusted, holds)), want, (reach, untrusted, holds))

    def test_b12_a_spike_gets_6_only_where_the_ladder_says_7(self):
        """WHY: B12 "(6 in a spike)": the taper applies to the trivial case, not to real exposure."""
        for reach, untrusted, holds, want in self.ladder:
            f = self.facts(reach, untrusted, holds)
            self.assertEqual(rl.security_bar(f, spike=True), 6 if want == 7 else want, (reach, untrusted, holds))

    def test_b12_never_10_from_facts_and_unstated_facts_never_lower_the_bar(self):
        """WHY: B12 "10 only by owner floor"; a model that states nothing proves nothing, so it stays at 9."""
        for r in ("local single user", "other local users", "network", "public"):
            for u in ("none", "local files", "network input", "third-party code"):
                for h in ("nothing", "owner data", "secrets", "others data"):
                    self.assertLessEqual(rl.security_bar(self.facts(r, u, h)), 9)
        self.assertEqual(rl.security_bar(rl.parse_threat_model("one agent calls it")[0]), 9)
        self.assertEqual(rl.security_bar(rl.parse_threat_model("Reach: local single user")[0]), 9)

    def test_b12_value_synonyms_and_lists_are_read(self):
        """WHY: owners write prose; a list takes its worst value, a typo is refused, not guessed."""
        f, status = rl.parse_threat_model("reach: Network / public\nUntrusted inputs: files, captured data\n"
                                          "Holds: the owner's data\nStatus: inferred")
        self.assertEqual(f, {"reach": "public", "untrusted": "local-data", "holds": "owner-data"})
        self.assertEqual(status, "inferred")
        with self.assertRaises(ValueError) as cm:
            rl.parse_threat_model("Reach: galaxy")
        self.assertIn("local-single-user", str(cm.exception))

    def test_b12_init_prints_the_security_bar_and_its_reason(self):
        """WHY: B5/B12. The reader sees where the security bar comes from."""
        out, led = self.init("--category", "pii", "--threat-model", TM_NETWORK_SECRETS)
        self.assertEqual((led["bar"], led["concerns"]), (9, {"security": 9}))
        self.assertIn("security: 9", out)
        self.assertIn("threat model", out)
        self.assertEqual(led["threat_facts"], {"reach": "network", "untrusted": "network-input", "holds": "secrets"})
        out, led = self.init("--category", "pii", "--threat-model", "one agent calls it", "--region", "u")
        self.assertEqual(led["bar"], 9)
        self.assertIn("states no", out)
        self.assertIn("Reach:", out)

    def test_b12_bad_fact_value_is_refused_and_writes_nothing(self):
        """WHY: a typo in a labelled line must not fall through to a lower bar."""
        path = str(self.root / "bad.json")
        refuses(self, lambda: self.init("--threat-model", "Reach: galaxy", ledger=path), "Reach", "network")
        self.assertFalse(Path(path).exists())

    def test_b13_threat_model_may_be_a_file(self):
        """WHY: B13 `--threat-model FILE|TEXT`; the owner keeps the model in a file."""
        f = self.root / "tm.md"
        f.write_text(TM_LOCAL_DATA)
        _, led = self.init("--threat-model", str(f), "--category", "permissions")
        self.assertEqual(led["bar"], 8)
        self.assertIn("Untrusted: local files", led["threat_model"])

    def test_b13_it_is_stored_in_the_research_dir_and_reused_when_the_flag_is_absent(self):
        """WHY: B13. Every loop and brief reuses the owner's model without being told again."""
        self.init("--threat-model", TM_LOCAL_DATA)
        stored = self.research / "review" / "threat-model.md"
        self.assertIn("Untrusted: local files", stored.read_text())
        out, led = self.init("--category", "egress", model=False)
        self.assertEqual((led["bar"], led["threat_model_status"]), (8, "confirmed"))
        self.assertIn("threat-model.md", out)
        self.assertEqual(led["threat_model_path"], str(stored))

    def test_b13_residual_project_data_is_the_home_when_residual_is_set_up(self):
        """WHY: B13. The model lives with the project's residual data; the research dir is the fallback."""
        res = self.repo / "residual"
        res.mkdir()
        (res / "config.toml").write_text('format_version = "v4"\n[storage]\ngit_sidecar_enabled = false\n')
        self.init("--threat-model", TM_LOCAL_DATA)
        self.assertIn("Untrusted: local files", (res / "threat-model.md").read_text())
        self.assertFalse((self.research / "review" / "threat-model.md").exists())
        _, led = self.init("--category", "egress", model=False)
        self.assertEqual(led["bar"], 8)
        self.assertEqual(led["threat_model_path"], str(res / "threat-model.md"))

    def test_b13_a_git_sidecar_residual_falls_back_to_the_research_dir(self):
        """WHY: with the sidecar on, residual's metadata lives on a branch this script must not write to."""
        res = self.repo / "residual"
        res.mkdir()
        (res / "config.toml").write_text('[storage]\ngit_sidecar_enabled = true\n')
        self.init("--threat-model", TM_LOCAL_DATA)
        self.assertFalse((res / "threat-model.md").exists())
        self.assertTrue((self.research / "review" / "threat-model.md").exists())

    def test_b13_an_explicit_model_replaces_the_stored_one(self):
        """WHY: the owner may change their mind; the newest word wins and is what later loops reuse."""
        self.init("--threat-model", TM_LOCAL_DATA)
        self.init("--threat-model", TM_NETWORK_SECRETS)
        _, led = self.init("--category", "egress", model=False)
        self.assertEqual(led["bar"], 9)

    def test_b13_no_model_anywhere_is_refused_and_a_project_kind_is_the_way_out(self):
        """WHY: B6/B13. A reviewer must never assume a hostile multi-writer world because nobody said."""
        path = str(self.root / "none.json")
        refuses(self, lambda: self.init(model=False, ledger=path), "--threat-model", "--project-kind")
        self.assertFalse(Path(path).exists())

    def test_b13_a_model_derived_from_the_project_kind_is_marked_inferred(self):
        """WHY: B13. The agent may guess from the kind, but the ledger and the brief say it is a guess."""
        for kind in rl.KIND_THREAT:
            out, led = self.init("--project-kind", kind, "--category", "egress", "--region", kind, model=False)
            self.assertEqual(led["threat_model_status"], "inferred", kind)
            self.assertEqual(led["threat_facts"], rl.parse_threat_model("\n".join(
                f"{k}: {v}" for k, v in rl.KIND_THREAT[kind].items()))[0], kind)
            self.assertIn(led["bar"], (8, 9), kind)
            self.assertIn("inferred", out)
        self.assertIn("status: inferred", (self.research / "review" / "threat-model.network-service.md").read_text().lower())

    def test_b13_the_brief_marks_an_inferred_model_until_the_owner_confirms(self):
        """WHY: reviewers must treat a guessed model as provisional."""
        L = Ledger(self, extra=("--project-kind", "network-service"))
        self.assertIn("Threat model (inferred", L.run("brief"))
        out = L.run("threat-model")
        self.assertIn("inferred", out)
        L.run("threat-model", "--confirm")
        self.assertEqual(L.data()["threat_model_status"], "confirmed")
        brief = L.run("brief")
        self.assertIn("Threat model (confirmed)", brief)
        self.assertNotIn("inferred", brief)

    def test_b13_confirm_also_marks_the_stored_model_so_later_loops_inherit_it(self):
        """WHY: confirming once must be enough."""
        self.init("--project-kind", "cli-tool", model=False)
        stored = self.research / "review" / "threat-model.md"
        self.assertIn("inferred", stored.read_text().lower())
        led_path = str(self.root / "c.json")
        self.init("--project-kind", "cli-tool", model=False, ledger=led_path)
        with contextlib.redirect_stdout(io.StringIO()):
            rl.main(["-l", led_path, "threat-model", "--confirm"])
        self.assertNotIn("inferred", stored.read_text().lower())
        _, led = self.init(model=False)
        self.assertEqual(led["threat_model_status"], "confirmed")

    def test_b13_an_inferred_stored_model_is_reused_still_inferred(self):
        """WHY: reusing a guess must not launder it into the owner's word."""
        self.init("--project-kind", "local-service", model=False)
        _, led = self.init(model=False)
        self.assertEqual(led["threat_model_status"], "inferred")

    def test_b13_confirm_on_a_ledger_without_a_model_is_refused(self):
        """WHY: old ledgers have nothing to confirm."""
        L = Ledger(self)
        d = L.data()
        for k in ("threat_model_status", "threat_facts"):
            d.pop(k, None)
        Path(L.path).write_text(json.dumps(d))
        refuses(self, lambda: L.run("threat-model", "--confirm"), "no threat model")

    def test_b14_the_brief_scopes_security_findings_to_the_threat_model(self):
        """WHY: B14. A security finding needs an attacker the model includes; the rest is hardening."""
        brief = Ledger(self, extra=("--threat-model", TM_LOCAL_DATA)).run("brief")
        for needle in ("attacker", "threat model includes", "HARDENING-STASH"):
            self.assertIn(needle, brief)
        self.assertIn("Reach: local single user", brief)

    def test_b12_hardening_recomputes_security_with_the_stored_facts(self):
        """WHY: the hardening phase must not lose the threat model's bar for security."""
        L = Ledger(self, bar=None, extra=("--category", "pii", "--threat-model", TM_LOCAL_DATA))
        L.round(1, "sha1", STASH_REPLY)
        L.run("hardening")
        self.assertEqual(L.data()["concerns"], {"security": 8})
        self.assertEqual(L.data()["bar"], 8)


class PerConcern(RepoCase):
    """Per-concern bars: each concern is judged against its own bar; the max is only the summary."""

    def ledger(self, cats=("docs", "concurrency"), stage="production"):
        extra = ["--shape", "explore-first", "--stage", stage]
        for c in cats:
            extra += ["--category", c]
        return Ledger(self, bar=None, extra=extra)

    def test_scores_are_parsed_per_concern_and_a_plain_score_is_kept(self):
        """WHY: old ledgers and old replies use one SCORE line; new replies give one per concern."""
        per, plain = rl.parse_scores("SCORE[docs]: 8/10 (x)\nSCORE[concurrency]: 7.5/10\nSCORE: 9/10")
        self.assertEqual((per, plain), ({"docs": 8.0, "concurrency": 7.5}, 9.0))
        self.assertEqual(rl.parse_scores("SCORE: 9/10"), ({}, 9.0))
        self.assertEqual(rl.parse_scores("nothing"), ({}, None))
        self.assertEqual(rl.parse_reply("SCORE[docs]: 8/10\nSCORE[wiring]: 6/10")[0], 6.0)

    def test_init_stores_each_touched_concerns_own_bar_and_the_max_as_the_summary(self):
        """WHY: the summary line stays; the per-concern bars are what a round is judged by."""
        L = self.ledger()
        d = L.data()
        self.assertEqual(d["concerns"], {"docs": 8, "concurrency": 9})
        self.assertEqual(d["bar"], 9)
        self.assertIn("docs 8", L.run("brief"))
        self.assertIn("SCORE[", L.run("brief"))
        self.assertIn("docs: 8", L.run("status"))

    def test_a_round_passes_when_every_touched_concern_meets_its_own_bar(self):
        """WHY: docs at 8 is enough for docs even though concurrency needs 9; one SCORE line at 8 would fail it."""
        L = self.ledger()
        L.round(1, "s1", "SCORE[docs]: 8/10\nSCORE[concurrency]: 8/10")
        self.assertEqual(L.next(), "ROUND")
        L.round(1, "s2", "SCORE[docs]: 8/10\nSCORE[concurrency]: 9/10")
        self.assertEqual(L.next(), "CHECKPOINT")
        self.assertEqual(L.data()["rounds"][-1]["scores"], {"docs": 8.0, "concurrency": 9.0})
        self.assertEqual(L.data()["rounds"][-1]["score"], 8.0)

    def test_a_plain_score_applies_to_every_concern(self):
        """WHY: old replies must keep working; one number is held to the highest bar."""
        L = self.ledger()
        L.round(1, "s1", "SCORE: 8/10")
        self.assertEqual(L.next(), "ROUND")
        L.round(1, "s2", "SCORE: 9/10")
        self.assertEqual(L.next(), "CHECKPOINT")

    def test_a_missing_concern_score_or_a_typo_is_sent_back(self):
        """WHY: a reply that skips a touched concern says nothing about it."""
        L = self.ledger()
        with contextlib.redirect_stderr(io.StringIO()) as err, self.assertRaises(SystemExit):
            L.round(1, "s1", "SCORE[docs]: 9/10")
        self.assertIn("concurrency", err.getvalue())
        with contextlib.redirect_stderr(io.StringIO()) as err, self.assertRaises(SystemExit):
            L.round(1, "s2", "SCORE[docs]: 9/10\nSCORE[concurency]: 9/10")
        self.assertIn("legibility", err.getvalue())
        self.assertEqual(L.data()["rounds"], [])

    def test_a_volunteered_low_score_for_another_concern_counts_against_its_own_bar(self):
        """WHY: a reviewer who scores wiring 6 says wiring is below the 8 its table gives."""
        L = self.ledger()
        L.round(1, "s1", "SCORE[docs]: 9/10\nSCORE[concurrency]: 9/10\nSCORE[wiring]: 6/10")
        self.assertEqual(L.next(), "ROUND")
        L.round(1, "s2", "SCORE[docs]: 9/10\nSCORE[concurrency]: 9/10\nSCORE[wiring]: 8/10")
        self.assertEqual(L.next(), "CHECKPOINT")

    def test_an_open_blocker_still_blocks_whatever_the_scores(self):
        """WHY: scores are the reviewer's claim, not a pass."""
        L = self.ledger()
        L.round(1, "s1", "SCORE[docs]: 10/10\nSCORE[concurrency]: 10/10\n" + BUG)
        self.assertEqual(L.next(), "ROUND")

    def test_tier_two_uses_the_same_rule(self):
        """WHY: the final pass is judged per concern too."""
        L = self.ledger()
        L.round(1, "s1", "SCORE: 9/10")
        L.run("checkpoint")
        L.round(2, "s2", "SCORE[docs]: 9/10\nSCORE[concurrency]: 8/10")
        self.assertEqual(L.next(), "ROUND")
        L.round(2, "s3", "SCORE[docs]: 9/10\nSCORE[concurrency]: 9/10")
        self.assertEqual(L.next(), "STOP-AGREED")

    def test_explicit_bar_applies_to_every_touched_concern(self):
        """WHY: --bar N is the owner's one number; it must not leave stale per-concern bars behind."""
        L = Ledger(self, bar=9, extra=("--shape", "explore-first", "--stage", "production",
                                       "--category", "docs", "--category", "concurrency"))
        self.assertEqual(L.data()["concerns"], {"docs": 9, "concurrency": 9})

    def test_finding_concern_comes_from_its_class_or_from_the_reviewer(self):
        """WHY: the reply format gains the concern; the class slug maps to one, and the reviewer may name it."""
        _, _, fs, _ = rl.parse_reply(
            "S1 [should] [class: fail-open-read] a.py:1 x\n"
            "S2 [should] [class: fail-open-read] [concern: concurrency] a.py:2 y\n"
            "S3 [nit] [class: other] a.py:3 z")
        self.assertEqual([f["concern"] for f in fs], ["error-paths", "concurrency", None])
        for cls, concern in rl.CLASS_CONCERN.items():
            self.assertIn(cls, rl.CLASSES)
            self.assertIn(concern, rl.CONCERNS)
        self.assertEqual(set(rl.CLASS_CONCERN), set(rl.CLASSES) - {"other"})

    def test_an_unknown_concern_tag_warns_and_falls_back_to_the_class(self):
        """WHY: like class slugs, a free-text concern is kept visible but never rejects the reply."""
        L = self.ledger(cats=("docs",))
        out = L.round(1, "s1", "SCORE: 9/10\nS1 [should] [class: hidden-state] [concern: vibes] a.py:1 x")
        self.assertIn("warning: S1 concern", out)
        self.assertEqual(L.data()["findings"]["S1"]["concern"], "legibility")
        self.assertIn("legibility", L.run("status"))

    def test_the_brief_asks_for_the_concern_and_one_score_per_concern(self):
        """WHY: the reply format is stated in the brief and in review.md."""
        brief = self.ledger().run("brief")
        self.assertIn("[concern: <name>]", brief)
        self.assertIn("SCORE[docs]: n/10", brief)
        self.assertIn("SCORE[concurrency]: n/10", brief)

    def test_docs_carry_the_per_concern_format_and_the_threat_model_rules(self):
        """WHY: the docs the orchestrator reads must match the script."""
        for name, needles in (("review.md", ("SCORE[", "[concern:", "--threat-model", "threat-model --confirm", "inferred")),
                              ("bars.md", ("SCORE[", "own bar", "--threat-model", "--outside-consumers",
                                           "threat-model.md", "inferred", "--confirm") + tuple(rl.KIND_THREAT))):
            text = (SKILL_DIR / "references" / name).read_text()
            for n in needles:
                self.assertIn(n, text, (name, n))
        self.assertNotIn("Security stays at 8", (SKILL_DIR / "references" / "bars.md").read_text())
        self.assertIn("SCORE[", (SKILL_DIR / "SKILL.md").read_text())


class HardeningPhase(unittest.TestCase):
    """Review r1 S1: hardening is a separate phase: fresh rounds, checkpoint and a full first brief; history kept."""

    def finished_quality_phase(self):
        L = Ledger(self)
        for i in range(3):
            L.round(1, f"q{i}", "SCORE: 6/10")
        L.run("new-approach")
        L.round(1, "q3", "SCORE: 9/10")
        L.run("checkpoint")
        L.round(2, "q4", "SCORE: 9/10")
        self.assertEqual(L.next(), "STOP-AGREED")
        return L

    def test_s1_hardening_after_a_finished_phase_starts_a_new_one(self):
        """WHY: the ledger used to say STOP-AGREED and "No brief" after `hardening`."""
        L = self.finished_quality_phase()
        out = L.run("hardening")
        self.assertIn("hardening phase", out)
        self.assertTrue(L.run("next").startswith("ROUND: tier 1 round 1"))
        brief = L.run("brief")
        self.assertIn("See: git diff base0", brief)
        self.assertIn("Hardening phase", brief)
        self.assertNotIn("No brief", brief)
        d = L.data()
        self.assertFalse(d["checkpoint"])
        self.assertEqual(len(d["rounds"]), 5)
        self.assertEqual([r["n"] for r in d["rounds"]], [1, 2, 3, 4, 5])

    def test_s1_round_caps_and_the_checkpoint_start_fresh(self):
        """WHY: four tier-1 rounds in the quality phase must not push the hardening phase into STOP-STUCK."""
        L = self.finished_quality_phase()
        L.run("hardening")
        L.round(1, "h1", "SCORE: 6/10")
        self.assertEqual(L.next(), "ROUND")
        L.round(1, "h2", "SCORE: 6/10")
        L.round(1, "h3", "SCORE: 6/10")
        self.assertEqual(L.next(), "STEP-BACK")
        L.run("new-approach")
        L.round(1, "h4", "SCORE: 9/10")
        self.assertEqual(L.next(), "CHECKPOINT")
        L.run("checkpoint")
        self.assertIn("tier 2 round 1", L.run("next"))
        L.round(2, "h5", "SCORE: 9/10")
        self.assertEqual(L.next(), "STOP-AGREED")

    def test_s1_earlier_history_is_kept_and_the_second_call_does_not_restart(self):
        """WHY: findings and rounds of the quality phase stay readable; repeating `hardening` only merges items."""
        L = Ledger(self)
        L.round(1, "q1", STASH_REPLY)
        L.run("hardening")
        L.round(1, "h1", "SCORE: 6/10")
        L.run("hardening")
        d = L.data()
        self.assertEqual(len(d["rounds"]), 2)
        self.assertEqual([r.get("phase", 0) for r in d["rounds"]], [0, 1])
        self.assertIn("S1", d["findings"])
        self.assertEqual(L.next(), "ROUND")
        self.assertIn("See ONLY: git diff h1", L.run("brief"))


class Round3(RepoCase):
    """Review r2 S3, S5, S6, S7 and the confirm item, each from the reviewer's reproduction."""

    LOCAL = "Reach: local-single-user\nUntrusted: none\nHolds: nothing"
    NETWORK = "Reach: network\nUntrusted: network-input\nHolds: secrets"

    def test_s3_every_unbulleted_entry_under_a_stash_header_is_a_stash_item(self):
        """WHY: a reviewer reply with two entries turned the second into a blocking round finding."""
        text = ("SCORE: 9/10\nHARDENING-STASH:\nS1 [should] a.py:1 second-writer race\n"
                "S2 [should] a.py:2 second-process race\nNIT-STASH:\nS3 [nit] a.py:3 x\nS4 [nit] a.py:4 y\n")
        nits, hard = rl.parse_stashes(text)
        self.assertEqual(len(hard), 2)
        self.assertEqual(len(nits), 2)
        self.assertEqual(rl.parse_reply(text)[2], [])

    def test_s3_a_round_with_two_unbulleted_entries_records_no_finding(self):
        """WHY: end to end, the ledger gets two stash items and no finding, so the loop can stop."""
        L = Ledger(self)
        L.round(1, "s1", "SCORE: 9/10\nHARDENING-STASH:\nS1 [should] a.py:1 one\nS2 [should] a.py:2 two\n")
        self.assertEqual(L.data()["findings"], {})
        self.assertEqual(len(L.data()["hardening_stash"]), 2)
        self.assertEqual(L.next(), "CHECKPOINT")

    def test_s3_a_score_line_or_a_non_finding_line_ends_the_unbulleted_section(self):
        """WHY: keeping the section open must not swallow what follows it."""
        _, _, fs, _ = rl.parse_reply("HARDENING-STASH:\nS1 [should] a.py:1 one\nSCORE: 8/10\nS2 [should] b.py:2 real\n")
        self.assertEqual([f["id"] for f in fs], ["S2"])
        _, _, fs, _ = rl.parse_reply("HARDENING-STASH:\nS1 [should] a.py:1 one\n- b.py:2 bullet\nS3 [should] c.py:3 real\n")
        self.assertEqual([f["id"] for f in fs], ["S3"])

    def init_region(self, name, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rl.main(["-l", str(self.root / f"{name}.json"), "init", "--repo", str(self.repo), "--base", self.base,
                     "--intent", "review", "--category", "security", "--research", str(self.research), *args])
        return json.loads((self.root / f"{name}.json").read_text())

    def test_s5_threat_models_are_kept_per_region(self):
        """WHY: reviewing a local tool overwrote the server region's model; a later server loop got the tool's."""
        self.init_region("server1", "--region", "server", "--threat-model", self.NETWORK)
        self.init_region("tool", "--region", "tool", "--threat-model", self.LOCAL)
        led = self.init_region("server2", "--region", "server")
        self.assertEqual((led["threat_facts"]["reach"], led["threat_model_status"]), ("network", "confirmed"))
        self.assertEqual(led["concerns"]["security"], 9)

    def test_s5_the_default_region_keeps_the_old_path_and_does_not_leak_into_named_regions(self):
        """WHY: existing projects keep their stored model; a named region never silently inherits another's."""
        self.init_region("d", "--threat-model", self.LOCAL)
        self.assertTrue((self.research / "review" / "threat-model.md").is_file())
        refuses(self, lambda: self.init_region("n", "--region", "server"), "--threat-model")

    def test_s6_a_fresh_project_stores_its_model_in_a_new_research_dir(self):
        """WHY: with no residual and no research dir the first model was dropped and the next loop was refused."""
        fresh, research = self.root / "fresh", self.root / "fresh.research"
        fresh.mkdir()
        args = ["--repo", str(fresh), "--research", str(research), "--base", "HEAD", "--intent", "first"]
        with contextlib.redirect_stdout(io.StringIO()):
            rl.main(["-l", str(self.root / "f1.json"), "init", *args, "--threat-model", self.NETWORK])
            self.assertTrue((research / "review" / "threat-model.md").is_file())
            rl.main(["-l", str(self.root / "f2.json"), "init", *args])
        led = json.loads((self.root / "f2.json").read_text())
        self.assertEqual(led["threat_facts"]["reach"], "network")

    def test_s6_without_a_flag_an_existing_repo_gets_its_sibling_research_dir(self):
        """WHY: the next loop discovers the sibling `<repo>.research` by convention."""
        fresh = self.root / "fresh2"
        fresh.mkdir()
        args = ["--repo", str(fresh), "--base", "HEAD", "--intent", "first"]
        with contextlib.redirect_stdout(io.StringIO()):
            rl.main(["-l", str(self.root / "g1.json"), "init", *args, "--threat-model", self.LOCAL])
            rl.main(["-l", str(self.root / "g2.json"), "init", *args])
        self.assertEqual(json.loads((self.root / "g2.json").read_text())["threat_facts"]["reach"], "local-single-user")

    def test_s7_bar_10_is_granted_per_concern_not_by_the_architecture_peak(self):
        """WHY: --bar 10 gave security and docs a 10 nobody authorised because architecture peaks at 10."""
        led = self.init_region("mixed", "--region", "mixed", "--shape", "port", "--category", "architecture",
                               "--category", "docs", "--threat-model", self.LOCAL, "--bar", "10")
        self.assertEqual(led["concerns"]["architecture"], 10)
        self.assertEqual(led["concerns"]["security"], 9)
        self.assertEqual(led["concerns"]["docs"], 9)
        self.assertEqual(led.get("owner_floor", 0), 0)

    def test_s7_bar_10_with_no_authorised_concern_is_refused(self):
        """WHY: B2. Nothing is at a peak or owner floor, so 10 needs a written reason."""
        refuses(self, lambda: self.init_region("none", "--region", "early", "--shape", "explore-first",
                                               "--category", "docs", "--threat-model", self.LOCAL, "--bar", "10"),
                "--bar-reason")

    def test_s7_a_written_reason_still_sets_every_concern(self):
        """WHY: --bar-reason is the owner's documented override."""
        led = self.init_region("why", "--region", "why", "--shape", "port", "--category", "architecture",
                               "--category", "docs", "--threat-model", self.LOCAL, "--bar", "10",
                               "--bar-reason", "owner asked")
        self.assertEqual(set(led["concerns"].values()), {10})

    def test_confirm_does_not_bless_a_different_stored_model(self):
        """WHY: a later loop replaced the guess; confirming the older ledger marked the newer guess confirmed."""
        g = self.research / "guesses"
        g.mkdir()
        for name, kind in (("guess1", "cli-tool"), ("guess2", "network-service")):
            with contextlib.redirect_stdout(io.StringIO()):
                rl.main(["-l", str(self.root / f"{name}.json"), "init", "--repo", str(self.repo), "--base", self.base,
                         "--intent", "x", "--research", str(g), "--project-kind", kind])
        with contextlib.redirect_stdout(io.StringIO()):
            rl.main(["-l", str(self.root / "guess1.json"), "threat-model", "--confirm"])
        self.assertIn("inferred", (g / "review" / "threat-model.md").read_text().lower())


if __name__ == "__main__":
    unittest.main()
