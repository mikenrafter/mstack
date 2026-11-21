"""Hook framing and fail-open behavior with deterministic CLI reports."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

HOOK = Path(__file__).resolve().parents[1] / "vigil-advice-hook"


class VigilAdviceHookTests(unittest.TestCase):
    def invoke(self, report):
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / "vigil"
            executable.write_text("#!/usr/bin/env python3\nprint(" + repr(report) + ")\n")
            executable.chmod(0o755)
            return subprocess.run(["bash", str(HOOK)], input=json.dumps({"tool_input":{"command":"cargo test"}}),
                                  text=True, capture_output=True, check=True,
                                  env={**os.environ, "PATH": directory + os.pathsep + os.environ["PATH"]}).stdout

    def test_advisory_rules_and_project_reminders_have_distinct_headers(self):
        # WHY: D1: a release reminder is not an operator rule for the heavy job.
        output = self.invoke(json.dumps({"advice":[{"id":"budget", "message":"Use Boat"}],
                                        "reminders":[{"id":"release", "message":"Ship when ready"}]}))
        context = json.loads(output)["hookSpecificOutput"]["additionalContext"]
        self.assertEqual(context, "vigil advice (operator rules; follow them for this heavy job):\nbudget: Use Boat\n\nvigil project reminders:\nrelease: Ship when ready")

    def test_reminder_unavailability_preserves_operator_advice(self):
        # WHY: a missing/expired reminder cache must not drop the hook's advice.
        output = self.invoke(json.dumps({"advice":[{"id":"budget", "message":"Use Boat"}],
                                        "reminders":[{"id":"release", "message":"Refresh pending"}]}))
        self.assertIn("budget: Use Boat", json.loads(output)["hookSpecificOutput"]["additionalContext"])

    def test_empty_and_malformed_reports_fail_open(self):
        # WHY: hook errors and empty reports must not block or inject garbage.
        self.assertEqual(self.invoke('{"advice":[],"reminders":[]}'), "")
        self.assertEqual(self.invoke("broken"), "")


if __name__ == "__main__":
    unittest.main()
