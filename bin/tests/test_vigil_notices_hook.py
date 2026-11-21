"""vigil-notices-hook: framing, event name, fail-open."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

HOOK = Path(__file__).resolve().parents[1] / "vigil-notices-hook"


class VigilNoticesHookTests(unittest.TestCase):
    def invoke(self, payload, vigil_script):
        with tempfile.TemporaryDirectory() as directory:
            vigil = Path(directory) / "vigil"
            vigil.write_text(vigil_script)
            vigil.chmod(0o755)
            completed = subprocess.run(
                ["bash", str(HOOK)], input=payload, text=True, capture_output=True,
                env={**os.environ, "PATH": directory + os.pathsep + os.environ["PATH"]}, timeout=10)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return completed.stdout

    def test_pending_notice_becomes_context_for_the_event(self):
        # catches: a hook that drops the notice text or names the wrong event
        out = self.invoke(json.dumps({"hook_event_name": "SessionStart", "session_id": "s1"}),
                          '#!/bin/sh\ncat >/dev/null\necho "neon: Gemini Neon is available"\n')
        hook = json.loads(out)["hookSpecificOutput"]
        self.assertEqual(hook["hookEventName"], "SessionStart")
        self.assertIn("Gemini Neon is available", hook["additionalContext"])

    def test_nothing_pending_prints_nothing(self):
        self.assertEqual(self.invoke('{"hook_event_name":"UserPromptSubmit"}', '#!/bin/sh\ncat >/dev/null\n'), "")

    def test_failing_vigil_and_garbage_input_fail_open(self):
        # catches: a non-zero exit or partial JSON that could break the harness
        self.assertEqual(self.invoke("not json", '#!/bin/sh\nexit 3\n'), "")


if __name__ == "__main__":
    unittest.main()
