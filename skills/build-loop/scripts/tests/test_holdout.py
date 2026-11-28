import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "holdout"


@unittest.skipUnless(shutil.which("age") and shutil.which("age-keygen"), "age is not installed")
class Holdout(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)
        self.env = dict(os.environ,
                        MSTACK_HOLDOUT_KEY=str(self.root / "key.txt"),
                        MSTACK_HOLDOUT_RECIPIENTS=str(self.root / "recipients.txt"))
        self.project = self.root / "proj"
        self.project.mkdir()

    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-I", str(SCRIPT), *args],
                              capture_output=True, text=True, env=self.env)

    def backup_identity(self):
        path = self.root / "backup.txt"
        subprocess.run(["age-keygen", "-o", str(path)], check=True, capture_output=True)
        public = subprocess.run(["age-keygen", "-y", str(path)], check=True,
                                capture_output=True, text=True).stdout.strip()
        return path, public

    def test_seal_then_extract_with_either_key(self):
        backup, public = self.backup_identity()
        self.assertEqual(self.run_cli("key", "--backup", public).returncode, 0)
        source = self.root / "held"
        (source / "sub").mkdir(parents=True)
        (source / "sub" / "test_x.py").write_text("assert True\n")

        sealed = self.run_cli("seal", str(source), "--project", str(self.project),
                              "--feature", "feat", "--slice", "01")
        self.assertEqual(sealed.returncode, 0, sealed.stderr)
        self.assertFalse(source.exists())
        target = self.root / "proj.research" / "holdouts" / "feat" / "01.tar.age"
        self.assertNotIn(b"assert True", target.read_bytes())

        for identity in ([], ["--identity", str(backup)]):
            out = self.root / f"out{len(identity)}"
            result = self.run_cli("extract", "--sealed", str(target), "--into", str(out), *identity)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((out / "sub" / "test_x.py").read_text(), "assert True\n")

    def test_seal_refuses_to_overwrite(self):
        self.run_cli("key")
        for _ in range(2):
            source = self.root / "held"
            source.mkdir(exist_ok=True)
            (source / "t.py").write_text("x\n")
            result = self.run_cli("seal", str(source), "--project", str(self.project),
                                  "--feature", "f", "--slice", "02")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--replace", result.stderr)


if __name__ == "__main__":
    unittest.main()
