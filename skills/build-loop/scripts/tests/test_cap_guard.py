"""W49 pilot: G6 launch decisions, using synthetic Claude transcripts and a fake vigil."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

GUARD = Path(__file__).resolve().parents[4] / "bin" / "cap-guard"
DELEGATE = "mcp__t3-code__delegate_task"


def launch(name="Agent", label="first worker", reviewer=False, provider="claudeAgent"):
    if name == DELEGATE:
        return {"title": label, "role": "review" if reviewer else "implementation",
                "target": {"providerInstanceId": provider}, "task": "Check the patch."}
    return {"description": label, "prompt": "Review the patch." if reviewer else "Implement the patch.",
            "run_in_background": True}


def tool(name, inp, tid="first"):
    return {"type": "assistant", "message": {"role": "assistant", "content": [
        {"type": "tool_use", "id": tid, "name": name, "input": inp}]}}


def running(name="Agent", label="first worker", reviewer=False):
    rows = [{"type": "user", "message": {"role": "user", "content": "Implement this."}},
            tool(name, launch(name, label, reviewer))]
    if name != DELEGATE:
        rows.append({"type": "user", "toolUseResult": {"isAsync": True, "agentId": "agent1"},
                     "message": {"role": "user", "content": [
                         {"type": "tool_result", "tool_use_id": "first",
                          "content": "Async agent launched successfully. agentId: agent1"}]}})
    return rows


class CapGuard(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.transcript = self.root / "transcript.jsonl"
        self.mode = self.root / ".config" / "build-loop" / "cap-guard-mode"
        self.log = self.root / "vigil-args.jsonl"
        self.fake_vigil()

    def fake_vigil(self, work=1, review=1, code=0):
        script = self.bin / "vigil"
        script.write_text(f"#!{sys.executable}\nimport json, sys\n"
                          f"with open({str(self.log)!r}, 'a') as log:\n"
                          "    log.write(json.dumps(sys.argv[1:]) + '\\n')\n"
                          f"print({json.dumps({'work': work, 'review': review})!r})\n"
                          f"sys.exit({code})\n")
        script.chmod(0o755)

    def run_guard(self, rows, name="Agent", inp=None, mode=None, raw=None, pending=False):
        if mode is not None:
            self.mode.parent.mkdir(parents=True, exist_ok=True)
            self.mode.write_text(mode + "\n")
        payload = {"tool_name": name, "tool_input": inp if inp is not None else launch(name, "next"),
                   "transcript_path": str(self.transcript), "tool_use_id": "pending"}
        rows = list(rows)
        if pending:
            rows.append(tool(name, payload["tool_input"], "pending"))
        self.transcript.write_text(raw if raw is not None else "".join(json.dumps(r) + "\n" for r in rows))
        return subprocess.run([sys.executable, "-I", str(GUARD)], input=json.dumps(payload),
                              env={"PATH": str(self.bin), "HOME": str(self.root)},
                              capture_output=True, text=True, timeout=8)

    def assert_silent(self, result):
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, "", ""))

    def assert_advice(self, result, count=1, cap=1, reviewer=False, deny=False):
        self.assertEqual((result.returncode, result.stderr), (0, ""))
        self.assertTrue(result.stdout, "an over-cap launch must produce hook advice")
        output = json.loads(result.stdout)["hookSpecificOutput"]
        self.assertEqual(output["hookEventName"], "PreToolUse")
        text = output["additionalContext"]
        who = "Claude reviewer(s)" if reviewer else "working Claude agent(s)"
        self.assertTrue(text.startswith(f"cap-guard: {count} {who} unfinished (cap {cap}):"), text)
        self.assertIn("first reviewer" if reviewer else "first worker", text)
        self.assertIn("build-loop §2", text)
        self.assertIn("wait for one to finish", text)
        self.assertIn("vigil cap set", text)
        self.assertIn("--review N" if reviewer else "--work N", text)
        if deny:
            self.assertEqual(output.get("permissionDecision"), "deny")
            self.assertEqual(output["permissionDecisionReason"], text)
        else:
            self.assertIn(output.get("permissionDecision"), (None, "allow"))

    def test_codex_launch_is_silent_even_with_a_claude_unfinished(self):
        """WHY: G6 leaves Codex/Sol outside the Claude cap.
        catches: applying the Claude counter to every delegated provider."""
        for provider in ("codex", "unknown-provider"):
            with self.subTest(provider=provider):
                self.assert_silent(self.run_guard(running(), DELEGATE,
                                                 launch(DELEGATE, provider=provider), mode="block"))
        self.assertFalse(self.log.exists(), "unclassified launches need no vigil call")

    def test_first_claude_launch_is_silent(self):
        """WHY: G6 admits the first launch, including after a previous worker finished.
        catches: off-by-one admission, counting the pending call, or counting completed launches."""
        for name in ("Agent", "Task", DELEGATE):
            for pending in (False, True):
                with self.subTest(name=name, pending=pending):
                    self.assert_silent(self.run_guard([], name, pending=pending))
        rows = running()
        rows.append({"type": "user", "message": {"role": "user", "content":
                     "<task-notification><task-id>agent1</task-id><status>completed</status></task-notification>"}})
        self.assert_silent(self.run_guard(rows))

    def test_second_working_claude_warns_by_default(self):
        """WHY: G6 warns when an asynchronous worker still owns the only work slot.
        catches: treating an async tool result as completion or failing open when vigil is unavailable."""
        for name in ("Agent", "Task", DELEGATE):
            with self.subTest(name=name):
                self.assert_advice(self.run_guard(running(name), name))
        (self.bin / "vigil").unlink()
        self.assert_advice(self.run_guard(running()))
        self.fake_vigil(work=2, code=1)
        self.assert_advice(self.run_guard(running()))

    def test_second_working_claude_is_denied_in_block_mode(self):
        """WHY: G6 makes blocking opt-in at the owner's mode file.
        catches: emitting only advice in block mode, or omitting the denial reason."""
        self.assert_advice(self.run_guard(running(), mode="block"), deny=True)

    def test_reviewer_uses_its_own_cap(self):
        """WHY: G6 permits one worker alongside a reviewer but caps further reviewers separately.
        catches: combining both pools, ignoring reviewers, or using the work limit for reviews."""
        self.assert_silent(self.run_guard(running(), inp=launch(reviewer=True)))
        rows = running(label="first reviewer", reviewer=True)
        self.assert_silent(self.run_guard(rows))
        self.fake_vigil(work=2, review=1)
        self.assert_advice(self.run_guard(rows, inp=launch(reviewer=True)), reviewer=True)
        self.assert_advice(self.run_guard(rows, DELEGATE, launch(DELEGATE, reviewer=True), mode="block"),
                           reviewer=True, deny=True)

    def test_raised_vigil_work_cap_allows_the_second(self):
        """WHY: G6 honors the owner's effective cap from vigil rather than hardcoding one.
        catches: ignoring vigil's work limit, reading review instead, or invoking the wrong command."""
        self.fake_vigil(work=2, review=1)
        self.assert_silent(self.run_guard(running(), mode="block"))
        self.assertEqual([json.loads(line) for line in self.log.read_text().splitlines()], [["cap"]])

    def test_broken_transcript_fails_open(self):
        """WHY: G6 never blocks a launch because the transcript cannot be scanned.
        catches: uncaught scan errors or advising from a partially scanned broken transcript."""
        for raw in ("not json\n", json.dumps({"type": "user", "message": 42}) + "\n"):
            with self.subTest(raw=raw):
                self.assert_silent(self.run_guard([], mode="block", raw=raw))


if __name__ == "__main__":
    unittest.main()
