"""Hook scripts in agent-integration/bin/ must parse, and the build-loop compaction
reminder must behave, before a deploy finds out. Lives here because this is the
module's only test suite. 2026-11-13: an apostrophe inside the hook's
single-quoted jq argument (then inline in flake.nix) failed the nixed deploy."""
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

BIN = Path(__file__).resolve().parents[4] / "bin"
REMINDER = BIN / "build-loop-compact-reminder"


def bash_scripts():
    return [p for p in sorted(BIN.iterdir())
            if p.is_file() and p.read_text(errors="replace").startswith(("#!/usr/bin/env bash", "#!/bin/bash"))]


class HookScriptsParse(unittest.TestCase):
    def test_every_bash_script_in_bin_parses(self):
        """WHY: a syntax error in a hook only showed up at deploy time.
        catches: a quote slip in any bin/ shell script."""
        scripts = bash_scripts()
        self.assertIn(REMINDER, scripts, "the compaction reminder must be a bin/ script so this check covers it")
        for script in scripts:
            r = subprocess.run(["bash", "-n", str(script)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, f"{script.name}: {r.stderr}")


@unittest.skipUnless(shutil.which("jq") and shutil.which("grep"), "needs jq and grep on PATH")
class CompactReminder(unittest.TestCase):
    def run_hook(self, transcript_text):
        with tempfile.TemporaryDirectory() as d:
            t = Path(d) / "t.jsonl"
            t.write_text(transcript_text)
            r = subprocess.run(["bash", str(REMINDER)], input=json.dumps({"transcript_path": str(t)}),
                               capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def test_a_build_loop_session_gets_the_reread_reminder(self):
        """WHY: after compaction the summary drops build-loop's rules.
        catches: a message lost in quoting (empty or truncated additionalContext)."""
        out = json.loads(self.run_hook('{"skill": "build-loop"}\n'))
        ctx = out["hookSpecificOutput"]["additionalContext"]
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "SessionStart")
        self.assertTrue(ctx.startswith("REREAD build-loop §2 (agent cap) and §10, and vigil"), ctx[:80])
        self.assertIn("vigil hold done <session-hold> <run>", ctx)

    def test_other_sessions_stay_silent(self):
        """WHY: the reminder is noise for sessions that never used build-loop.
        catches: a grep that matches everything."""
        self.assertEqual(self.run_hook('{"skill": "qex"}\n'), "")


if __name__ == "__main__":
    unittest.main()
