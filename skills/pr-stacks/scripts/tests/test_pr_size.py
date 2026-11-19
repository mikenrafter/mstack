"""pr-size against a throwaway git repo."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parent.parent / "pr-size"


class PrSize(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.repo = Path(self.dir.name)
        self.env = dict(os.environ, XDG_STATE_HOME=str(self.repo / ".state"),
                        GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                        GIT_COMMITTER_EMAIL="t@t")
        self.git("init", "-q", "-b", "main")
        (self.repo / "a.txt").write_text("x\n")
        self.git("add", ".")
        self.git("commit", "-qm", "base")

    def tearDown(self):
        self.dir.cleanup()

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.repo, env=self.env, check=True)

    def commit(self, name, lines):
        (self.repo / name).write_text("y\n" * lines)
        self.git("add", ".")
        self.git("commit", "-qm", name)

    def check(self, *extra):
        return subprocess.run(["python3", "-I", str(SCRIPT), "check", "--base", "main~1", *extra],
                              cwd=self.repo, env=self.env, capture_output=True, text=True)

    def test_lockfiles_do_not_count(self):
        # WHY: CLAIM(size-count); a dependency bump must not force a stack.
        # catches: summing every numstat row.
        self.commit("Cargo.lock", 9000)
        self.assertEqual(self.check().returncode, 0)

    def test_over_limit_fails_unless_a_stack_plan_is_given(self):
        self.commit("big.rs", 4001)
        self.assertEqual(self.check().returncode, 1)
        spec = self.repo / "spec.md"
        spec.write_text("# Spec\n\n## Stack\n1. [two-way] x\n")
        self.assertEqual(self.check("--plan", str(spec)).returncode, 0)

    def test_exactly_at_limit_passes(self):
        self.commit("edge.rs", 4000)
        self.assertEqual(self.check().returncode, 0)


if __name__ == "__main__":
    unittest.main()
