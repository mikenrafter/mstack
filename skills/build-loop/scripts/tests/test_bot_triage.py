"""Tests for scripts/bot-triage. Run: python3 -I -m unittest discover -s scripts/tests"""
import contextlib
import importlib.machinery
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "bot-triage"
_loader = importlib.machinery.SourceFileLoader("bot_triage", str(SCRIPT))
_spec = importlib.util.spec_from_loader("bot_triage", _loader)
bt = importlib.util.module_from_spec(_spec)
_loader.exec_module(bt)

CR = "coderabbitai[bot]"
LABEL = ('**<picture><img src="x.svg" alt=""></picture> {sev}** · **Functional Correctness** · **Quick win**\n\n'
         '<details>\n<summary>Supported by static analysis</summary>\n'
         '<details><summary>nested</summary>' + "script output " * 300 + '</details>\n</details>\n\n'
         '**{title}**\n\nBody text.\n\n<!-- fingerprint -->\n')


def comment(id_, user, created, body, commit="c1", reply_to=None, path="lib/a.dart", line=10):
    c = {"id": id_, "user": {"login": user, "type": "Bot" if user.endswith("[bot]") else "User"},
         "created_at": created, "body": body, "original_commit_id": commit, "path": path,
         "original_line": line, "line": None, "html_url": f"https://x/{id_}"}
    if reply_to:
        c["in_reply_to_id"] = reply_to
    return c


COMMENTS = [
    comment(1, CR, "2026-01-01T00:00:01Z", LABEL.format(sev="Minor", title="Guard the null user.")),
    comment(2, CR, "2026-01-01T00:00:02Z", LABEL.format(sev="Major", title="Re-arm the alarm.")),
    comment(3, CR, "2026-01-01T00:00:03Z", LABEL.format(sev="Minor", title="Rename the field.")),
    comment(4, "me", "2026-01-01T01:00:00Z", "Fixed in abc123. Test: x.", reply_to=1),
    comment(5, "me", "2026-01-01T01:00:01Z", "Not changing this: out of scope.", reply_to=2),
    comment(6, CR, "2026-01-01T01:00:02Z", "Understood. <!-- <review_comment_withdrawn> -->", reply_to=2),
    comment(7, CR, "2026-01-02T00:00:00Z", LABEL.format(sev="Minor", title="Second pass finding."), commit="c2"),
    comment(8, "sourcery-ai[bot]", "2026-01-02T00:00:01Z", "**Issue:** plain bot text", commit="c2"),
    comment(9, "me", "2026-01-01T01:00:03Z", "Good catch, it now uses the reader.", reply_to=3),
]


class Base(unittest.TestCase):
    def setUp(self):
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        self.file = Path(d.name) / "c.json"
        self.file.write_text(json.dumps(COMMENTS))

    def run_cli(self, *args):
        out = io.StringIO()
        code = 0
        with contextlib.redirect_stdout(out):
            try:
                bt.main(["--comments", str(self.file), *args])
            except SystemExit as e:
                code = e.code
        return code, out.getvalue()


class Threads(unittest.TestCase):
    def setUp(self):
        self.ts = {t["id"]: t for t in bt.threads(COMMENTS)}

    def test_only_top_level_bot_comments(self):
        self.assertEqual(sorted(self.ts), [1, 2, 3, 7, 8])

    def test_strip_removes_nested_details_and_html_comments(self):
        t = self.ts[1]
        self.assertNotIn("script output", t["body"])
        self.assertNotIn("fingerprint", t["body"])
        self.assertIn("Guard the null user.", t["body"])
        self.assertLess(t["stripped_chars"] * 10, t["chars"])

    def test_coderabbit_label_and_title(self):
        t = self.ts[2]
        self.assertEqual((t["severity"], t["category"], t["effort"]), ("Major", "Functional Correctness", "Quick win"))
        self.assertEqual(t["title"], "Re-arm the alarm.")
        self.assertEqual(t["where"], "lib/a.dart:10")

    def test_other_bot_has_no_label(self):
        t = self.ts[8]
        self.assertIsNone(t["severity"])
        self.assertEqual(t["title"], "**Issue:** plain bot text")

    def test_passes_per_bot_and_commit(self):
        self.assertEqual([self.ts[i]["pass"] for i in (1, 2, 3, 7, 8)], [1, 1, 1, 2, 3])

    def test_outcomes(self):
        self.assertEqual(self.ts[1]["outcome"], "fixed")
        self.assertEqual(self.ts[2]["outcome"], "declined")
        self.assertTrue(self.ts[2]["closed_by_bot"])
        self.assertEqual(self.ts[3]["outcome"], "replied")
        self.assertEqual(self.ts[7]["outcome"], "unanswered")


class Cli(Base):
    def test_list_latest_pass(self):
        code, out = self.run_cli("list", "o/r#1")
        self.assertEqual(code, 0)
        self.assertEqual([l.split()[0] for l in out.splitlines()], ["8"])

    def test_list_unanswered_exits_1(self):
        code, out = self.run_cli("list", "o/r#1", "--pass", "all", "--unanswered")
        self.assertEqual(code, 1)
        self.assertEqual([l.split()[0] for l in out.splitlines()], ["7", "8"])

    def test_guard_blocks_push_with_unanswered_threads(self):
        code, out = self.run_cli("guard", "o/r#1")
        self.assertIn("unanswered", str(code))
        self.assertIn("Second pass finding.", out)

    def test_guard_passes_when_all_answered(self):
        self.file.write_text(json.dumps(COMMENTS[:6] + COMMENTS[8:]))
        code, out = self.run_cli("guard", "o/r#1")
        self.assertEqual(code, 0)
        self.assertIn("no unanswered", out)

    def test_stats(self):
        _, out = self.run_cli("stats", "o/r#1")
        self.assertIn("5 findings in 3 passes", out)
        self.assertIn("fixed 1, declined 1, other replies 1, unanswered 2", out)

    def test_show(self):
        code, out = self.run_cli("show", "o/r#1", "2")
        self.assertEqual(code, 0)
        self.assertIn("Re-arm the alarm.", out)
        self.assertNotIn("script output", out)

    def test_bad_pr_ref(self):
        with self.assertRaises(SystemExit):
            bt.fetch("not-a-ref")


if __name__ == "__main__":
    unittest.main()
