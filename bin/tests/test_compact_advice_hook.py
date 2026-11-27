"""bin/compact-advice-hook against synthetic transcripts."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

HOOK = Path(__file__).resolve().parent.parent / "compact-advice-hook"


def line(kind, tokens, sidechain=False):
    usage = {"input_tokens": 2, "cache_creation_input_tokens": 1000,
             "cache_read_input_tokens": tokens - 1002, "output_tokens": 50}
    return json.dumps({"type": kind, "isSidechain": sidechain, "message": {"usage": usage}})


class CompactAdvice(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.root = Path(self.dir.name)
        self.env = dict(os.environ, XDG_STATE_HOME=str(self.root / "state"))
        self.env.pop("T3CODE_THREAD_ID", None)

    def tearDown(self):
        self.dir.cleanup()

    def run_hook(self, lines, session="s1"):
        transcript = self.root / f"{session}.jsonl"
        transcript.write_text("\n".join(lines) + "\n")
        payload = {"hook_event_name": "PostToolUse", "session_id": session,
                   "transcript_path": str(transcript)}
        result = subprocess.run([str(HOOK)], input=json.dumps(payload), text=True,
                                capture_output=True, env=self.env, check=True)
        return result.stdout.strip()

    def test_silent_below_threshold(self):
        self.assertEqual(self.run_hook([line("assistant", 499_000)]), "")

    def test_advises_once_per_band_with_the_session_id(self):
        # WHY: the advice must repeat as context grows, but not on every tool call.
        first = self.run_hook([line("assistant", 520_000)])
        self.assertIn("uw-agent compact ask s1", first)
        self.assertEqual(self.run_hook([line("assistant", 560_000)]), "")
        self.assertIn("about 610k", self.run_hook([line("assistant", 610_000)]))

    def test_inside_t3_advises_the_native_self_message(self):
        # WHY: in T3 Code `/compact` sent to the session's own thread runs at the
        # end of the turn; the usagewindow queue waits for a policy pass.
        # catches: advice still naming uw-agent when a thread id is known.
        self.env["T3CODE_THREAD_ID"] = "thread-9"
        out = self.run_hook([line("assistant", 520_000)])
        self.assertIn("t3_thread_send` (threadId thread-9", out)
        # catches: advice that queues only /compact, which leaves the session idle.
        self.assertIn("/compact next:", out)
        self.assertIn("resume message", out)
        # catches: a resume a later, already-resumed session cannot tell is its own and stale.
        self.assertIn("[self-resume <id>", out)
        # catches: leaving the summary to the summarizer, or to the broken babeltele CLI.
        self.assertIn("BabelTele summary by hand", out)
        self.assertNotIn("uw-agent", out)

    def test_subagent_messages_do_not_count(self):
        # WHY: CLAIM(context-size); a sidechain's large context is not the main session's.
        # catches: taking the last assistant line regardless of isSidechain.
        out = self.run_hook([line("assistant", 200_000), line("assistant", 900_000, sidechain=True)])
        self.assertEqual(out, "")

    def test_bad_input_is_silent(self):
        result = subprocess.run([str(HOOK)], input="not json", text=True,
                                capture_output=True, env=self.env)
        self.assertEqual((result.returncode, result.stdout), (0, ""))


if __name__ == "__main__":
    unittest.main()
