"""Evaluator checks with independently specified outcomes; no subject builds."""
import unittest
import subprocess
import tempfile
from pathlib import Path

from replay import Commit, eligible_source, fix_label, history, metrics, replay_scores, selection, tree_files


class ReplayTests(unittest.TestCase):
    def test_fractional_ties_do_not_reward_filename_order(self):
        # WHY/CLAIM(tie-budget): five equal files, one place => 1/5 each.
        self.assertEqual(selection(dict.fromkeys('abcde', 1500)), dict.fromkeys('abcde', 0.2))

    def test_budget_and_event_recall_have_independent_oracle(self):
        # WHY/CLAIM(event-recall): one inspected file catches 2 of 3 fix touches.
        scores = dict(a=5, b=4, c=3, d=2, e=1)
        future = [Commit('f', '', 'fix: a', ('a',)), Commit('g', '', 'fix: a b', ('a', 'b'))]
        result = metrics(scores, future, 'broad')
        self.assertAlmostEqual(result['event_recall'], 2 / 3)
        self.assertEqual(result['unique_recall'], 0.5)
        self.assertEqual(result['precision'], 1)
        self.assertEqual(result['selected_files'], 1)

    def test_cold_start_is_reported_outside_evaluable_denominator(self):
        # WHY/CLAIM(cold-start): new files must not vanish from limitations.
        result = metrics(dict(a=1), [Commit('f', '', 'fix: both', ('a', 'new'))], 'broad')
        self.assertEqual(result['cold_start_touches'], 1)
        self.assertEqual(result['eligible_fix_touches'], 1)
        self.assertEqual(result['event_recall'], 1)

    def test_future_labels_cannot_change_frozen_training_scores(self):
        # WHY/CLAIM(no-future): the cutoff must slice before any training statistic.
        history = [Commit('a', '', 'feature', ('a', 'b')), Commit('b', '', 'fix: a', ('a',))]
        future = [Commit('c', '', 'fix: b', ('b',))]
        one = replay_scores(history + future, 2, {'a', 'b'})
        two = replay_scores(history + [Commit('x', '', 'feature', ('a',))], 2, {'a', 'b'})
        self.assertEqual(one, two)
        self.assertEqual(one['fix_count'], {'a': 1, 'b': 0})

    def test_elo_win_has_correct_direction_and_zero_sum(self):
        # WHY/CLAIM(elo-update): equal ratings => expected 1/2, K32 => +/-16.
        scores = replay_scores([Commit('a', '', 'fix: a', ('a',)),
                                Commit('b', '', 'feature', ('b',))], 2, {'a', 'b'})
        self.assertEqual(scores['elo'], {'a': 1516, 'b': 1484})

    def test_source_and_labels_reject_misleading_inputs(self):
        # WHY: test/generated/docs files and the noun 'prefix' must not create labels.
        for path in ['test/a.dart', 'lib/a_test.dart', 'lib/a.g.dart', 'src/foo.test.ts',
                     'crates/core/tests/a.rs', 'docs/example.py', 'tool/check.dart']:
            self.assertFalse(eligible_source(path), path)
        for path in ['lib/a.dart', 'src/a.rs', 'crates/core/src/a.rs', 'src/a.ts']:
            self.assertTrue(eligible_source(path), path)
        self.assertFalse(fix_label('feat: prefix display', 'broad'))
        self.assertFalse(fix_label('feat: improve handling', 'strict'))
        self.assertTrue(fix_label('Merge pull request #4 from x/fix/time', 'strict'))
        self.assertTrue(fix_label('fix(db): commit before ack', 'strict'))

    def test_constant_control_matches_budget_including_tied_boundary(self):
        # WHY: a constant rating must have exactly random expected recall.
        result = metrics(dict.fromkeys('abcdef', 1500),
                         [Commit('f', '', 'fix: a', ('a',))], 'broad')
        self.assertAlmostEqual(result['event_recall'], 2 / 6)
        self.assertAlmostEqual(result['selected_files'], 2)

    def test_sparse_window_remains_missing_not_zero_or_perfect(self):
        # WHY: no positive observations cannot be reported as measured failure/success.
        result = metrics(dict(a=1), [Commit('f', '', 'feat: a', ('a',))], 'broad')
        self.assertIsNone(result['event_recall'])
        self.assertIsNone(result['precision'])

    def test_real_git_merge_is_one_event_and_eligibility_uses_old_tree(self):
        # WHY/CLAIM(merge-once): branch commits must not duplicate their merge's fixes.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def git(*args):
                return subprocess.check_output(['git', '-C', directory, *args], text=True,
                                               stderr=subprocess.DEVNULL).strip()
            git('init', '-b', 'main')
            git('config', 'user.name', 'Experiment fixture')
            git('config', 'user.email', 'fixture@example.invalid')
            (root / 'src').mkdir()
            (root / 'src/a.rs').write_text('fn a() {}\n')
            git('add', '.')
            git('commit', '-m', 'initial')
            initial = git('rev-parse', 'HEAD')
            git('checkout', '-b', 'fix/branch')
            (root / 'src/b.rs').write_text('fn b() {}\n')
            git('add', '.')
            git('commit', '-m', 'fix: add b')
            git('checkout', 'main')
            git('merge', '--no-ff', 'fix/branch', '-m', 'Merge pull request #1 from x/fix/branch')
            commits = history(root, 'HEAD')
            self.assertEqual(len(commits), 2)
            self.assertEqual(commits[1].files, ('src/b.rs',))
            self.assertEqual(tree_files(root, initial), {'src/a.rs'})


if __name__ == '__main__':
    unittest.main()
