"""bin/skill-watch-hook against synthetic transcripts and skill directories."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest

HOOK = Path(__file__).resolve().parent.parent / "skill-watch-hook"


class SkillWatch(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.root = Path(self.dir.name)
        self.skill = self.root / "installed" / "skills" / "demo"
        (self.skill / "references").mkdir(parents=True)
        (self.skill / "SKILL.md").write_text("v1\n")
        (self.skill / "references" / "step.md").write_text("r1\n")
        self.source = self.root / "mstack" / "skills"
        self.env = dict(os.environ, XDG_STATE_HOME=str(self.root / "state"),
                        MSTACK_SKILLS=str(self.source), INSTALLED_SKILLS=str(self.root / "no-install"))
        self.transcript = self.root / "t.jsonl"
        # Loaded "a minute from now" so files written in setUp predate the load.
        stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + 60))
        load = {"type": "user", "isSidechain": False, "timestamp": stamp, "message": {
            "role": "user", "content": [{"type": "text", "text": f"Base directory for this skill: {self.skill}\n\n# Demo"}]}}
        self.transcript.write_text(json.dumps(load) + "\n")

    def tearDown(self):
        self.dir.cleanup()

    def run_hook(self, event="PostToolUse", **extra):
        payload = {"hook_event_name": event, "session_id": "s1",
                   "transcript_path": str(self.transcript), **extra}
        out = subprocess.run([str(HOOK)], input=json.dumps(payload), text=True,
                             capture_output=True, env=self.env, check=True).stdout.strip()
        return json.loads(out)["hookSpecificOutput"]["additionalContext"] if out else ""

    def test_reports_a_changed_reference_once(self):
        # WHY: CLAIM(baseline-at-load); the alert must name the file and not repeat.
        self.assertEqual(self.run_hook(), "")
        (self.skill / "references" / "step.md").write_text("r2\n")
        alert = self.run_hook()
        self.assertIn("references/step.md", alert)
        self.assertNotIn("SKILL.md", alert)
        self.assertEqual(self.run_hook(), "")

    def test_the_sessions_own_edit_is_not_reported(self):
        # catches: alerting on every Edit the agent makes to a skill it is improving.
        self.run_hook()
        (self.skill / "SKILL.md").write_text("v2\n")
        self.assertEqual(self.run_hook(tool_name="Edit", tool_input={"file_path": str(self.skill / "SKILL.md")}), "")
        self.assertEqual(self.run_hook(), "")

    def test_mstack_source_edit_is_reported_as_not_installed(self):
        (self.source / "demo").mkdir(parents=True)
        (self.source / "demo" / "SKILL.md").write_text("v1\n")
        self.run_hook()
        (self.source / "demo" / "SKILL.md").write_text("v2\n")
        self.assertIn("mstack source (not yet installed)", self.run_hook())

    def test_installed_source_change_says_follow_it_now(self):
        # WHY: a source change that the install already copied is live; the old wording
        # ("not yet installed", "only if the owner asked") let an agent discount it.
        # catches: labelling every mstack-source change as uninstalled
        (self.source / "demo").mkdir(parents=True)
        (self.source / "demo" / "SKILL.md").write_text("v1\n")
        self.run_hook()
        (self.source / "demo" / "SKILL.md").write_text("v2\n")
        (self.skill / "SKILL.md").write_text("v2\n")
        alert = self.run_hook()
        self.assertIn("mstack source, installed", alert)
        self.assertIn("follow them now", alert)
        self.assertNotIn("not yet installed", alert)
        self.assertNotIn("only if the owner asked", alert)

    def test_a_directory_is_reported_once(self):
        # WHY: loading the mstack copy directly and the installed copy made one directory
        # appear twice, under two contradictory labels.
        # catches: walking the mstack source once per loaded skill directory
        (self.source / "demo").mkdir(parents=True)
        (self.source / "demo" / "SKILL.md").write_text("v1\n")
        load = json.loads(self.transcript.read_text().splitlines()[0])
        load["message"]["content"][0]["text"] = f"Base directory for this skill: {self.source / 'demo'}\n\n# Demo"
        with open(self.transcript, "a") as handle:
            handle.write(json.dumps(load) + "\n")
        self.run_hook()
        (self.source / "demo" / "SKILL.md").write_text("v2\n")
        alert = self.run_hook()
        self.assertEqual(alert.count(str(self.source / "demo")), 1, alert)
        self.assertIn("mstack source (not yet installed)", alert)

    def test_dotted_cache_directories_are_ignored(self):
        # catches: reporting .pytest_cache/README.md as a skill change
        cache = self.skill / ".pytest_cache"
        cache.mkdir()
        (cache / "README.md").write_text("c1\n")
        self.run_hook()
        (cache / "README.md").write_text("c2\n")
        self.assertEqual(self.run_hook(), "")

    def test_compaction_lists_loaded_skills(self):
        self.run_hook()
        alert = self.run_hook("SessionStart", source="compact")
        self.assertIn(f"demo ({self.skill}/SKILL.md)", alert)
        self.assertEqual(self.run_hook("SessionStart", source="startup"), "")

    def test_change_before_first_hook_run_is_reported(self):
        # WHY: a skill updated between the load and the hook's first look must not
        # become the silent baseline.
        load = json.loads(self.transcript.read_text())
        load["timestamp"] = "2020-01-01T00:00:00Z"
        self.transcript.write_text(json.dumps(load) + "\n")
        self.assertIn("SKILL.md", self.run_hook())

    def test_sidechain_loads_are_ignored(self):
        load = json.loads(self.transcript.read_text())
        load["isSidechain"] = True
        self.transcript.write_text(json.dumps(load) + "\n")
        self.run_hook()
        self.assertEqual(self.run_hook("SessionStart", source="compact"), "")

    def test_bash_reads_with_home_and_relative_paths_count_as_loads(self):
        # catches: matching only absolute paths, which missed `cat ~/.claude/skills/x/SKILL.md`
        # and `cat skills/x/SKILL.md` run from the repo.
        home_skill = Path.home() / ".claude" / "skills"
        rel_root = self.root / "repo"
        (rel_root / "skills" / "rel").mkdir(parents=True)
        (rel_root / "skills" / "rel" / "SKILL.md").write_text("x\n")
        lines = [json.dumps({"type": "assistant", "cwd": str(rel_root), "message": {"content": [
            {"type": "tool_use", "name": "Bash", "input": {"command": "sed -n 1,9p skills/rel/SKILL.md"}}]}})]
        if (home_skill / "unslop").is_dir():
            lines.append(json.dumps({"type": "assistant", "cwd": "/", "message": {"content": [
                {"type": "tool_use", "name": "Bash", "input": {"command": "cat ~/.claude/skills/unslop/SKILL.md | head"}}]}}))
        with self.transcript.open("a") as handle:
            handle.write("\n".join(lines) + "\n")
        alert = self.run_hook("SessionStart", source="compact")
        self.assertIn(f"rel ({rel_root}/skills/rel/SKILL.md)", alert)
        if (home_skill / "unslop").is_dir():
            self.assertIn("unslop (", alert)


if __name__ == "__main__":
    unittest.main()
