import subprocess
import tempfile
import unittest
from pathlib import Path

from snapshots import snapshot_features, summarize_numstat


class SnapshotTests(unittest.TestCase):
    def test_counts_separate_source_tests_binary_and_state_paths(self):
        # WHY: a large fixture or image must not inflate measured source-fix size.
        result = summarize_numstat('4\t2\tsrc/session.rs\n8\t1\ttests/lease.rs\n-\t-\tdocs/image.png\n')
        self.assertEqual(result['changed_files'], 3)
        self.assertEqual(result['changed_lines'], 15)
        self.assertEqual(result['source_changed_lines'], 6)
        self.assertEqual(result['test_changed_lines'], 9)
        self.assertEqual(result['binary_files'], 1)
        self.assertEqual(result['state_path_files'], 2)

    def test_only_pinned_revisions_enter_features(self):
        # WHY: later source edits and the actual checkout cannot leak into old decisions.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def git(*args):
                return subprocess.check_output(['git', '-C', directory, *args], text=True,
                                               stderr=subprocess.DEVNULL).strip()
            git('init', '-b', 'main')
            git('config', 'user.name', 'Fixture')
            git('config', 'user.email', 'fixture@example.invalid')
            (root / 'a.rs').write_text('fn a() {}\n')
            git('add', '.')
            git('commit', '-m', 'base')
            base = git('rev-parse', 'HEAD')
            (root / 'a.rs').write_text('fn b() {}\n')
            git('add', '.')
            git('commit', '-m', 'target')
            target = git('rev-parse', 'HEAD')
            before = snapshot_features(root, base, target)
            self.assertEqual(before['changed_lines'], 2)
            (root / 'a.rs').write_text('future\n' * 100)
            self.assertEqual(snapshot_features(root, base, target), before)
            self.assertTrue(snapshot_features(root, target, target)['same_snapshot'])

    def test_missing_object_is_unknown_not_zero(self):
        # WHY: missing evidence must not make a change appear small or safe.
        self.assertEqual(snapshot_features(Path('/unavailable'), None, 'abc')['status'], 'unknown')

    def test_kotlin_source_is_not_mistaken_for_no_fix(self):
        # WHY: Fauxx uses Kotlin; dropping its language creates false zero-change evidence.
        result = summarize_numstat('5\t3\tapp/src/main/java/Owner.kt\n')
        self.assertEqual(result['source_changed_lines'], 8)
        self.assertEqual(result['source_files'], 1)


if __name__ == '__main__':
    unittest.main()
