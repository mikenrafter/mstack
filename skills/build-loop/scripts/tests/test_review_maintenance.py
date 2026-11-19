"""Adaptive review maintenance CLI contract, using isolated state and a fake vigil.

Spec: phoe-nix.research/review-behavior/dialogue-spec.md, Adaptive maintenance CLI.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from test_review_dialogue import FOCUS

SCRIPT = Path(__file__).resolve().parents[3] / "adaptive-hardening" / "scripts" / "review-maintenance"
CONCERNS = ("test-effectiveness", "simplification", "end-to-end", "state-durability", "trust-boundaries")
START = "2026-11-16T12:00:00Z"
BEFORE = "2026-11-23T11:59:59Z"
BOUNDARY = "2026-11-23T12:00:00Z"


class Maintenance(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.project = self.root / "project"
        self.project.mkdir()
        self.state = self.root / "state"
        self.env = dict(os.environ)

    def call(self, *args, now=START, project=None):
        return subprocess.run([sys.executable, "-I", str(SCRIPT), "--state-dir", str(self.state),
            "--now", now, *args, "--project", str(project or self.project)],
            capture_output=True, text=True, env=self.env)

    def ok(self, result, code=0):
        self.assertEqual(result.returncode, code, f"stdout={result.stdout}\nstderr={result.stderr}")
        return result.stdout

    def due(self, now=START, code=0, project=None):
        return json.loads(self.ok(self.call("due", now=now, project=project), code))

    def test_rotation_cooldown_and_boundary_use_completion_evidence(self):
        # why: CLAIM(maintenance-rotation) reviews rotate after seven days, not on every tool call.
        # catches: rotating on reads, treating six days as a week, or ignoring the exact boundary.
        first = self.due()
        self.assertEqual({key: first[key] for key in ("due", "concern", "context")},
                         {"due": True, "concern": "test-effectiveness", "context": None})
        self.assertEqual(self.due(), first)
        self.ok(self.call("complete", "--concern", "test-effectiveness", "--evidence", "Reviewed real test oracles."))
        self.assertFalse(self.due(now=BEFORE, code=1)["due"])
        next_review = self.due(now=BOUNDARY)
        self.assertTrue(next_review["due"])
        self.assertEqual(next_review["concern"], "simplification")
        other = self.root / "another-project"
        other.mkdir()
        self.assertEqual(self.due(project=other)["concern"], "test-effectiveness")

    def test_all_named_concerns_rotate_then_oldest_completion_returns(self):
        # why: CLAIM(maintenance-rotation) a concern cannot disappear from long-lived maintenance.
        # catches: always selecting the first item or never revisiting completed concerns.
        for index, concern in enumerate(CONCERNS):
            self.assertEqual(self.due(now=BOUNDARY)["concern"], concern)
            self.ok(self.call("complete", "--concern", concern, "--evidence", f"Review {index} completed."))
        # All equal timestamps tie-break in the documented concern order.
        self.assertEqual(self.due(now=BOUNDARY)["concern"], "test-effectiveness")

    def test_invalid_completion_never_suppresses_due_work(self):
        # why: CLAIM(maintenance-evidence) empty evidence cannot stand in for an actual review.
        # catches: complete marking work done before validating its evidence or concern.
        self.ok(self.call("complete", "--concern", "test-effectiveness", "--evidence", "  "), code=2)
        self.assertTrue(self.due()["due"])
        self.ok(self.call("complete", "--concern", "made-up", "--evidence", "reviewed"), code=2)
        self.assertTrue(self.due()["due"])

    def test_unrepresentable_utc_time_is_unavailable_not_not_due(self):
        # WHY CLAIM(maintenance-state): probe exceptions must not use successful-false exit 1.
        # catches: returning not-due when a stored timestamp cannot be represented in UTC.
        self.ok(self.call("complete", "--concern", "test-effectiveness", "--evidence", "Checked time."))
        state_file = next(self.state.glob("*.json"))
        state = json.loads(state_file.read_text())
        state["completed"]["test-effectiveness"]["at"] = "0001-01-01T00:00:00+01:00"
        state_file.write_text(json.dumps(state))
        self.ok(self.call("due"), code=2)

    def test_context_is_persistent_and_project_identity_resolves_symlinks(self):
        # why: CLAIM(maintenance-context) reminders need explicit focus and must share state across aliases.
        # catches: deriving context from a project name or keying state on the unnormalized CLI path.
        focus_file = self.root / "focus.json"
        focus_file.write_text(json.dumps(FOCUS))
        self.ok(self.call("context", "--file", str(focus_file)))
        alias = self.root / "alias"
        alias.symlink_to(self.project, target_is_directory=True)
        self.assertEqual(self.due(project=alias)["context"], FOCUS)
        self.ok(self.call("complete", "--concern", "test-effectiveness", "--evidence", "Reviewed aliases.", project=alias))
        self.assertFalse(self.due(code=1)["due"])
        self.assertEqual(self.due(code=1)["context"], FOCUS)
        self.assertEqual(list(self.project.iterdir()), [])

    def test_current_priorities_focus_inspection_without_replacing_shared_rotation(self):
        # why: CLAIM(maintenance-priority) current security work informs the selected audit's focus.
        # catches: skipping the shared rotation whenever a current priority names another concern.
        focus_file = self.root / "priority.json"
        current_focus = {**FOCUS, "priority_concerns": ["security"]}
        focus_file.write_text(json.dumps(current_focus))
        self.ok(self.call("context", "--file", str(focus_file)))
        self.assertEqual(self.due()["concern"], "test-effectiveness")
        self.assertEqual(self.due()["context"], current_focus)
        self.ok(self.call("complete", "--concern", "test-effectiveness", "--evidence", "Checked security-test oracles."))
        self.assertEqual(self.due(now=BOUNDARY)["concern"], "simplification")
        self.ok(self.call("complete", "--concern", "user-fit", "--evidence", "Acceptance check."), code=2)

    def test_corrupt_state_is_unavailable_instead_of_fresh_due(self):
        # why: CLAIM(maintenance-state) corruption must not silently reset the maintenance record.
        # catches: catching JSON errors as if the project had no saved state.
        self.ok(self.call("complete", "--concern", "test-effectiveness", "--evidence", "Reviewed persistence."))
        state_files = list(self.state.glob("*.json"))
        self.assertEqual(len(state_files), 1, "one project has one persistent state record")
        state_file = state_files[0]
        state_file.write_text("{broken")
        result = self.call("due")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertNotEqual(result.stderr.strip(), "")
        self.assertEqual(state_file.read_text(), "{broken")

    def test_parallel_context_and_completions_preserve_each_update(self):
        # why: CLAIM(maintenance-state) separate agents may complete different review lenses together.
        # catches: unlocked read-modify-write losing one completed concern or its context.
        focus_file = self.root / "focus.json"
        focus_file.write_text(json.dumps(FOCUS))
        actions = [("context", "--file", str(focus_file))] + [
            ("complete", "--concern", concern, "--evidence", f"Reviewed {concern}.") for concern in CONCERNS[:3]]
        with ThreadPoolExecutor(max_workers=4) as pool:
            for result in pool.map(lambda action: self.call(*action), actions):
                self.ok(result)
        query = self.due(now=BOUNDARY)
        self.assertEqual(query["concern"], "state-durability")
        self.assertEqual(query["context"], FOCUS)

    def init_git(self, root):
        for command in (["git", "init", "-q", str(root)],
            ["git", "-C", str(root), "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
             "commit", "--allow-empty", "-qm", "fixture"]):
            result = subprocess.run(command, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    def fake_vigil(self):
        capture = self.root / "vigil-calls.jsonl"
        fake = self.root / "fake-vigil"
        fake.write_text("#!/usr/bin/env python3\nimport json, os, sys\nfrom pathlib import Path\n"
                        "with Path(os.environ['ARGV_CAPTURE']).open('a') as output:\n"
                        "    output.write(json.dumps(sys.argv[1:]) + '\\n')\n"
                        "path = Path(os.environ['REMINDERS_STATE'])\n"
                        "state = json.loads(path.read_text()) if path.exists() else {}\n"
                        "action, ident = sys.argv[2:4]\n"
                        "failure = path.with_suffix('.failed')\n"
                        "if action == 'rm' and ident == os.environ.get('FAIL_REMOVAL') and not failure.exists():\n"
                        "    failure.touch()\n"
                        "    print('temporary removal failure', file=sys.stderr)\n    sys.exit(1)\n"
                        "if action == 'add':\n"
                        "    if ident in state:\n"
                        "        print('already exists', file=sys.stderr)\n        sys.exit(1)\n"
                        "    state[ident] = sys.argv[1:]\n"
                        "elif action == 'rm':\n"
                        "    if ident not in state:\n"
                        "        print('no reminder named ' + ident, file=sys.stderr)\n        sys.exit(1)\n"
                        "    del state[ident]\n"
                        "path.write_text(json.dumps(state))\nprint('fixture-reminder')\n")
        fake.chmod(0o755)
        self.env.update(VIGIL_BIN=str(fake), ARGV_CAPTURE=str(capture),
                        REMINDERS_STATE=str(self.root / "reminders.json"))
        return capture

    def reminders(self):
        return json.loads(Path(self.env["REMINDERS_STATE"]).read_text())

    def reminder_scopes(self, args):
        start = args.index("--scope") + 1
        end = next(index for index in range(start, len(args)) if args[index].startswith("--"))
        return args[start:end]

    def test_logical_project_members_share_completion_context_and_rotation(self):
        # why: CLAIM(maintenance-membership) a product's repositories have one audit history.
        # catches: resolving membership only during registration, or merging unrelated projects.
        companion = self.root / "firmware"
        other = self.root / "unrelated"
        companion.mkdir()
        other.mkdir()
        self.ok(self.call("group", "--id", "edge", "--title", "Edge", "--repo", str(companion)))
        self.assertTrue((self.state / "projects" / "registry.json").is_file())
        focus_file = self.root / "focus.json"
        focus_file.write_text(json.dumps(FOCUS))
        self.ok(self.call("context", "--file", str(focus_file), project=companion))
        self.ok(self.call("complete", "--concern", "test-effectiveness", "--evidence", "Reviewed app and firmware paths."))
        self.assertFalse(self.due(project=companion, code=1)["due"])
        self.assertEqual(self.due(now=BOUNDARY, project=companion)["concern"], "simplification")
        self.assertEqual(self.due(now=BOUNDARY, project=companion)["context"], FOCUS)
        self.assertEqual(self.due(project=other)["concern"], "test-effectiveness")

    def test_group_merges_existing_evidence_using_latest_per_concern(self):
        # why: CLAIM(maintenance-migration) grouping repositories must retain completed audit evidence.
        # catches: resetting history, dropping one member, or letting older evidence overwrite newer.
        companion = self.root / "firmware"
        companion.mkdir()
        self.ok(self.call("complete", "--concern", "test-effectiveness", "--evidence", "Older app oracle review."))
        self.ok(self.call("complete", "--concern", "test-effectiveness", "--evidence", "Newer firmware oracle review.",
                          project=companion, now=BOUNDARY))
        self.ok(self.call("complete", "--concern", "simplification", "--evidence", "App simplification review."))
        self.ok(self.call("group", "--id", "edge", "--title", "Edge", "--repo", str(companion)))
        self.assertFalse(self.due(project=companion, now=BOUNDARY, code=1)["due"])
        merged = json.loads(self.ok(self.call("complete", "--concern", "end-to-end", "--evidence", "Checked complete flow.",
                                             project=companion, now=BOUNDARY)))
        self.assertEqual(merged["completed"]["test-effectiveness"]["evidence"], "Newer firmware oracle review.")
        self.assertEqual(merged["completed"]["simplification"]["evidence"], "App simplification review.")
        self.assertEqual(self.due(project=self.project, now=BOUNDARY, code=1)["concern"], "state-durability")

    def test_a_repository_cannot_belong_to_two_logical_projects(self):
        # why: CLAIM(maintenance-membership) overlapping groups would make completion ownership ambiguous.
        # catches: last-write-wins registry edits silently stealing a product's repository.
        companion = self.root / "firmware"
        other = self.root / "unrelated"
        companion.mkdir()
        other.mkdir()
        self.ok(self.call("group", "--id", "edge", "--title", "Edge", "--repo", str(companion)))
        self.ok(self.call("group", "--id", "other", "--title", "Other", "--repo", str(companion), project=other), code=2)
        self.ok(self.call("complete", "--concern", "test-effectiveness", "--evidence", "Checked original membership."))
        self.assertFalse(self.due(project=companion, code=1)["due"])
        self.assertTrue(self.due(project=other)["due"])

    def test_git_worktree_and_subdirectory_share_repository_identity(self):
        # why: CLAIM(maintenance-membership) worktrees and subdirectory sessions belong to the same project.
        # catches: using checkout paths as independent audit histories.
        self.init_git(self.project)
        nested = self.project / "src"
        nested.mkdir()
        linked = self.root / "linked"
        result = subprocess.run(["git", "-C", str(self.project), "worktree", "add", "-q", "-b", "fixture", str(linked)],
                                capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.ok(self.call("complete", "--concern", "test-effectiveness", "--evidence", "Reviewed shared implementation.", project=nested))
        self.assertFalse(self.due(project=linked, code=1)["due"])
        self.assertFalse(self.due(code=1)["due"])
        self.assertEqual(self.due(project=linked, now=BOUNDARY)["concern"], "simplification")

    def test_ensure_discovers_once_and_group_registration_includes_each_repository(self):
        # why: CLAIM(maintenance-discovery) ordinary project use initializes reminders without duplicate adds.
        # catches: requiring a pre-enumerated project list, or re-registering on every session check.
        capture = self.fake_vigil()
        first = json.loads(self.ok(self.call("ensure")))
        self.ok(self.call("ensure"))
        calls = [json.loads(line) for line in capture.read_text().splitlines()]
        additions = [args for args in calls if args[:2] == ["remind", "add"]]
        self.assertEqual(len(additions), 2)
        self.assertIn(first["id"], additions[0])
        key = hashlib.sha256(str(self.project).encode()).hexdigest()[:24]
        self.assertEqual(set(self.reminders()), {"review-" + key, "comment-audit-" + key})
        for args in additions:
            self.assertEqual(self.reminder_scopes(args), [str(self.project)])
            self.assertEqual(args[args.index("--tz") + 1], "America/Denver")
            self.assertEqual(args[args.index("--period") + 1], "week")
        comment = self.reminders()["comment-audit-" + key]
        review = self.reminders()["review-" + key]
        self.assertEqual(review[review.index("--days") + 1], "mon,tue,wed,thu,fri,sat,sun")
        self.assertEqual(review[review.index("--cache-s") + 1], "3600")
        self.assertEqual(review[review.index("--timeout-s") + 1], "4")
        self.assertNotIn("--window", review)
        self.assertEqual(comment[comment.index("--days") + 1], "sat,sun")
        self.assertEqual(comment[comment.index("--window") + 1], "09:00-21:00")
        self.assertNotIn("--probe", comment)
        self.assertEqual(comment[comment.index("--message") + 1],
                         "A comment audit is due for this project. Load the comment-audit skill: "
                         "files changed since the last audit (whole repo once a month). Report only; "
                         "edits need the owner. Check headroom with adaptive-hardening; this reminder "
                         "does not authorize paid work beyond lean. Then vigil remind done "
                         "comment-audit-" + key + ". Snooze if busy.")
        companion = self.root / "firmware"
        companion.mkdir()
        self.ok(self.call("group", "--id", "edge", "--title", "Edge", "--repo", str(companion)))
        self.ok(self.call("register", "--title", "Edge"))
        calls = [json.loads(line) for line in capture.read_text().splitlines()]
        registrations = [args for args in calls if args[:2] == ["remind", "add"]][-2:]
        for registration in registrations:
            self.assertEqual(self.reminder_scopes(registration), [str(self.project), str(companion)])
        # Grouping an already discovered repo must retire its former reminder,
        # after the replacement exists, so one product does not get two nudges.
        for kind in ("review", "comment-audit"):
            old_id = kind + "-" + key
            old_removal = ["remind", "rm", old_id]
            self.assertIn(old_removal, calls)
            self.assertGreater(calls.index(old_removal), max(calls.index(args) for args in registrations))
            self.assertNotIn(old_id, self.reminders())
        self.assertEqual(len(self.reminders()), 2)
        self.ok(self.call("ensure", project=companion))
        repeated = [json.loads(line) for line in capture.read_text().splitlines()]
        self.assertEqual(len([args for args in repeated if args[:2] == ["remind", "add"]]), 4)

    def test_refresh_migrates_old_receipt_and_keeps_both_ids_without_duplicates(self):
        # WHY: CLAIM(maintenance-discovery) existing projects gain comment audits and keep stable ids.
        # catches: accepting a review-only receipt, duplicating on refresh, or failing to refresh both scopes.
        capture = self.fake_vigil()
        first = json.loads(self.ok(self.call("ensure")))
        receipt_path = next((self.state / "projects").glob("*.registration.json"))
        receipt = json.loads(receipt_path.read_text())
        receipt.pop("kinds", None)
        receipt["version"] = 2
        receipt_path.write_text(json.dumps(receipt))
        comment_id = first["id"].replace("review-", "comment-audit-", 1)
        path = Path(self.env["REMINDERS_STATE"])
        path.write_text(json.dumps({first["id"]: self.reminders()[first["id"]]}))
        self.ok(self.call("ensure"))
        self.assertEqual(set(self.reminders()), {first["id"], comment_id})
        research = self.root / "project.research"
        research.mkdir()
        self.ok(self.call("ensure"))
        self.assertEqual(set(self.reminders()), {first["id"], comment_id})
        for args in self.reminders().values():
            self.assertEqual(self.reminder_scopes(args), [str(self.project), str(research)])
        before = capture.read_text()
        self.assertTrue(json.loads(self.ok(self.call("ensure")))["unchanged"])
        self.assertEqual(capture.read_text(), before)

    def test_split_scopes_match_for_both_kinds_and_retire_on_regroup(self):
        # WHY: CLAIM(maintenance-scope) every session scope needs both reminders, including split ids.
        # catches: dropping scopes above 16, using different suffixes, or leaving split member reminders.
        self.fake_vigil()
        self.init_git(self.project)
        linked = []
        for index in range(16):
            worktree = self.root / f"linked-{index:02d}"
            result = subprocess.run(["git", "-C", str(self.project), "worktree", "add", "-q",
                                     "--detach", str(worktree)], capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            linked.append(str(worktree))
        first = json.loads(self.ok(self.call("ensure")))
        key = first["id"].removeprefix("review-")
        expected = {kind + "-" + key + suffix for kind in ("review", "comment-audit") for suffix in ("", "-2")}
        self.assertEqual(set(self.reminders()), expected)
        for kind in ("review", "comment-audit"):
            base = kind + "-" + key
            self.assertEqual(self.reminder_scopes(self.reminders()[base]), [str(self.project), *linked[:15]])
            self.assertEqual(self.reminder_scopes(self.reminders()[base + "-2"]), linked[15:])
            if kind == "comment-audit":
                self.assertIn("vigil remind done " + base + "-2.", self.reminders()[base + "-2"][-1])
        self.ok(self.call("group", "--id", "edge", "--title", "Edge"))
        self.ok(self.call("ensure"))
        group_key = hashlib.sha256(b"project:edge").hexdigest()[:24]
        self.assertEqual(set(self.reminders()),
                         {kind + "-" + group_key + suffix for kind in ("review", "comment-audit") for suffix in ("", "-2")})
        # Removing a linked checkout must retire both obsolete second chunks on refresh.
        result = subprocess.run(["git", "-C", str(self.project), "worktree", "remove", linked[-1]], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.ok(self.call("ensure"))
        self.assertEqual(set(self.reminders()), {kind + "-" + group_key for kind in ("review", "comment-audit")})

    def test_retirement_retry_tolerates_an_already_removed_reminder(self):
        # why: CLAIM(maintenance-discovery) interrupted cleanup can leave a receipt after removal.
        # catches: treating a removed review as fatal, or skipping comment cleanup when the group is unchanged.
        capture = self.fake_vigil()
        first = json.loads(self.ok(self.call("ensure")))
        comment_id = first["id"].replace("review-", "comment-audit-", 1)
        receipt = next((self.state / "projects").glob("*.registration.json"))
        self.ok(self.call("group", "--id", "edge", "--title", "Edge"))
        self.env["FAIL_REMOVAL"] = comment_id
        self.ok(self.call("ensure"), code=2)
        self.assertTrue(receipt.exists())
        self.assertNotIn(first["id"], self.reminders())
        self.assertIn(comment_id, self.reminders())
        before = [json.loads(line) for line in capture.read_text().splitlines()]
        self.assertTrue(json.loads(self.ok(self.call("ensure")))["unchanged"])
        self.assertFalse(receipt.exists())
        self.assertNotIn(comment_id, self.reminders())
        self.assertEqual(len(self.reminders()), 2)
        after = [json.loads(line) for line in capture.read_text().splitlines()]
        self.assertEqual([args for args in after if args[:2] == ["remind", "add"]],
                         [args for args in before if args[:2] == ["remind", "add"]])

    def test_register_scopes_project_research_and_worktrees_without_repo_writes(self):
        # why: CLAIM(maintenance-scope) reminders follow the project into research and worktree sessions.
        # catches: broad parent-directory scope, missing linked worktree, or invoking the real vigil.
        for command in (["git", "init", "-q", str(self.project)],
            ["git", "-C", str(self.project), "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
             "commit", "--allow-empty", "-qm", "fixture"]):
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
        research = self.root / "project.research"
        worktrees = self.root / "project.worktrees"
        unrelated = self.root / "unrelated"
        for directory in (research, worktrees, unrelated):
            directory.mkdir()
        linked = self.root / "separate-worktree"
        self.assertEqual(subprocess.run(["git", "-C", str(self.project), "worktree", "add", "-q", "-b", "fixture", str(linked)],
            capture_output=True).returncode, 0)
        capture = self.fake_vigil()
        before = subprocess.run(["git", "-C", str(self.project), "status", "--porcelain"], capture_output=True).stdout
        self.ok(self.call("register", "--title", "Project review"))
        args, comment = [json.loads(line) for line in capture.read_text().splitlines()]
        self.assertEqual(self.reminder_scopes(args), self.reminder_scopes(comment))
        self.assertEqual(args[:2], ["remind", "add"])
        scopes = []
        reading_scopes = False
        for value in args:
            if value == "--scope":
                reading_scopes = True
            elif value.startswith("--"):
                reading_scopes = False
            elif reading_scopes:
                scopes.append(value)
        self.assertEqual(set(scopes), {str(self.project.resolve()), str(research.resolve()), str(worktrees.resolve()), str(linked.resolve())})
        probe = json.loads(args[args.index("--probe") + 1])
        self.assertIn("due", probe)
        self.assertIn(str(self.project.resolve()), probe)
        self.assertNotIn(str(unrelated), " ".join(args))
        after = subprocess.run(["git", "-C", str(self.project), "status", "--porcelain"], capture_output=True).stdout
        self.assertEqual(after, before)
        self.assertEqual(list(research.iterdir()), [])
        self.assertEqual(list(worktrees.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
