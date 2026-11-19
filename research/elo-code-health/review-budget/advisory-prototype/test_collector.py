"""CLI tests against the actual installed canonical policy, using synthetic Git objects."""
import copy
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import collector

HERE = Path(__file__).resolve().parent
COLLECTOR = HERE / 'collector.py'


class CollectorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=HERE)
        self.root = Path(self.tmp.name)
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        self.env = {**os.environ, 'GIT_AUTHOR_NAME': 'Synthetic', 'GIT_AUTHOR_EMAIL': 'synthetic@example.invalid',
                    'GIT_COMMITTER_NAME': 'Synthetic', 'GIT_COMMITTER_EMAIL': 'synthetic@example.invalid'}
        self.git('init', '-q')
        (self.repo / 'file.txt').write_text('initial\n')
        self.git('add', 'file.txt'); self.git('commit', '-qm', 'initial')
        self.first = self.git('rev-parse', 'HEAD').strip()
        (self.repo / 'file.txt').write_text('fixed\n')
        self.git('add', 'file.txt'); self.git('commit', '-qm', 'fix')
        self.head = self.git('rev-parse', 'HEAD').strip()
        self.ledger = self.root / 'review.ledger.json'
        self.data = {'schema': 2, 'repo': str(self.repo), 'base': self.first, 'bar': 8,
                     'phase': 0, 'approach': 1, 'checkpoint': True, 'findings': {},
                     'rounds': [{'n': i, 'tier': 1, 'approach': 1, 'reviewer': 'fable' if i == 3 else 'sol',
                                 'sha': self.head, 'score': 9, 'verdict': 'APPROVE',
                                 'exchange_minimum': 2 if i == 3 else 1,
                                 'exchanges': [f'Orchestrator: Synthetic challenge {j} on evidence coverage.\nReviewer: Synthetic answer {j} with a checked source and settled decision.'
                                               for j in range(2 if i == 3 else 1)]}
                                for i in (1, 2, 3)]}
        self.write_ledger()
        self.artifact = self.root / 'fix-report.txt'
        self.artifact.write_text('An accepted fix changes the cancellation transition.\n')
        self.fact_data = {'category': 'cancellation', 'accepted': True, 'fix_revision': self.head,
                          'diff_sha256': hashlib.sha256(self.diff()).hexdigest(),
                          'artifact_path': str(self.artifact),
                          'artifact_sha256': hashlib.sha256(self.artifact.read_bytes()).hexdigest()}
        self.fact = self.root / 'fact.json'
        self.fact.write_text(json.dumps(self.fact_data))

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.repo), *args], env=self.env, text=True)

    def diff(self):
        return subprocess.check_output(['git', '-c', 'core.fsmonitor=false', '-c', 'core.quotePath=true',
                                        '-c', 'diff.algorithm=myers', '-c', 'diff.mnemonicPrefix=false',
                                        '-C', str(self.repo), 'diff', '--binary', '--full-index', '--no-renames',
                                        '--no-ext-diff', '--no-textconv', self.first, self.head, '--'])

    def write_ledger(self):
        self.ledger.write_text(json.dumps(self.data))

    def capture(self, *extra, script=COLLECTOR):
        proc = subprocess.run([sys.executable, str(script), 'capture', '--source-root', str(self.root),
                               '--ledger', str(self.ledger), '--repo', str(self.repo),
                               '--revision', self.head, *map(str, extra)], capture_output=True, text=True)
        self.assertTrue(proc.stdout, f'collector must emit JSON, stderr={proc.stderr}')
        return proc, json.loads(proc.stdout)

    def test_actual_canonical_stop_and_verified_fact_are_shadow_only(self):
        # WHY: CLAIM(canonical-copy). Real policy output, not supplied verification, determines the boundary.
        before = self.ledger.read_bytes()
        proc, result = self.capture('--fact', self.fact)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(result['canonical']['step'], 'STOP-AGREED')
        self.assertEqual(result['status'], 'additional-review-recommended')
        self.assertFalse(result['execution_allowed'])
        self.assertEqual(result['scope'], 'git-object-only')
        self.assertEqual(result['ledger_sha256'], hashlib.sha256(before).hexdigest())
        self.assertEqual(result['canonical']['ledger_copy_sha256'], result['ledger_sha256'])
        self.assertEqual(self.ledger.read_bytes(), before)
        self.assertEqual(result['trigger']['accepted_basis'], 'supplied-assertion')

    def test_required_gate_cannot_become_optional(self):
        # WHY: CLAIM(mandatory-floor). A passing early round still needs fresh tier2.
        self.data['rounds'] = self.data['rounds'][:1]; self.write_ledger()
        proc, result = self.capture('--fact', self.fact)
        self.assertEqual(result['canonical']['step'], 'ROUND')
        self.assertEqual(result['status'], 'required-review-still-pending')
        self.assertFalse(result['boundary_observed'])

    def test_cap_never_creates_an_extra_review(self):
        # WHY: CLAIM(cap). Exhausted tier2 cannot become a synthetic optional slot.
        self.data['rounds'] = [{'n': i, 'tier': 2, 'approach': 1, 'reviewer': 'opus',
                                'sha': self.head, 'score': 6, 'verdict': 'CHANGES',
                                'exchange_minimum': 0} for i in (1, 2)]
        self.write_ledger()
        _, result = self.capture('--fact', self.fact)
        self.assertEqual(result['canonical']['step'], 'STOP-STUCK')
        self.assertEqual(result['status'], 'cap-reached-escalate')

    def test_mismatched_reviewed_commit_is_unknown_even_if_claimed_verified(self):
        # WHY: CLAIM(exact-object). Final dispositions cannot cover a different Git object.
        self.data['rounds'][-1]['sha'] = self.first
        self.data['capture_verified'] = True; self.write_ledger()
        _, result = self.capture('--fact', self.fact)
        self.assertEqual(result['status'], 'insufficient-evidence')
        self.assertFalse(result['boundary_observed'])
        self.assertIn('stale-review-coverage', result['reasons'])

    def test_no_trigger_never_means_early_stop(self):
        # WHY: CLAIM(no-learned-stop). No supported rule is not evidence of a clean change.
        _, result = self.capture()
        self.assertEqual(result['status'], 'insufficient-evidence')
        self.assertTrue(result['boundary_observed'])
        self.assertEqual(result['outcome'], 'unobserved')

    def test_wrong_fact_diff_or_artifact_hash_is_rejected(self):
        # WHY: CLAIM(trigger-evidence). A supplied accepted flag cannot authenticate a fix.
        for key in ('diff_sha256', 'artifact_sha256'):
            changed = copy.deepcopy(self.fact_data); changed[key] = '0' * 64
            self.fact.write_text(json.dumps(changed))
            proc, result = self.capture('--fact', self.fact)
            self.assertEqual(proc.returncode, 2)
            self.assertEqual(result['status'], 'insufficient-evidence')

    def test_symlink_and_outside_root_are_rejected(self):
        # WHY: CLAIM(confined-read). Being explicitly named does not authorize a neighboring file.
        with tempfile.TemporaryDirectory(dir=HERE) as other:
            outside = Path(other) / 'report.txt'; outside.write_text(self.artifact.read_text())
            self.fact_data['artifact_path'] = str(outside)
            self.fact.write_text(json.dumps(self.fact_data))
            proc, result = self.capture('--fact', self.fact)
            self.assertEqual(proc.returncode, 2)
            self.assertIn('outside-source-root', ' '.join(result['reasons']))
            link = self.root / 'linked-report.txt'; link.symlink_to(outside)
            self.fact_data['artifact_path'] = str(link)
            self.fact.write_text(json.dumps(self.fact_data))
            proc, result = self.capture('--fact', self.fact)
            self.assertEqual(proc.returncode, 2)

    def test_malformed_ledger_never_reaches_a_clean_outcome(self):
        # WHY: CLAIM(malformed-unknown). Parse failure and absent rounds cannot become a negative.
        for value in ('{', json.dumps({'schema': 2, 'rounds': 'wrong'})):
            self.ledger.write_text(value)
            proc, result = self.capture()
            self.assertEqual(proc.returncode, 2)
            self.assertEqual(result['outcome'], 'unobserved')
            self.assertFalse(result['execution_allowed'])

    def test_duplicate_reordered_or_impossible_round_history_is_rejected(self):
        # WHY: CLAIM(round-history). Repeated exports cannot masquerade as three distinct passing rounds.
        original = copy.deepcopy(self.data)
        variants = []
        for numbers in ([1, 1, 1], [3, 1, 2], [0, 2, 3]):
            changed = copy.deepcopy(original)
            for row, number in zip(changed['rounds'], numbers): row['n'] = number
            variants.append(changed)
        backward = copy.deepcopy(original); backward['phase'] = 1
        for row, phase in zip(backward['rounds'], [0, 1, 0]): row['phase'] = phase
        variants.append(backward)
        future = copy.deepcopy(original); future['rounds'][-1]['phase'] = 1
        variants.append(future)
        for index, changed in enumerate(variants):
            with self.subTest(variant=index):
                self.data = changed; self.write_ledger()
                proc, result = self.capture('--fact', self.fact)
                self.assertEqual(proc.returncode, 2)
                self.assertEqual(result['status'], 'insufficient-evidence')
                self.assertFalse(result['boundary_observed'])

    def test_immutable_storage_and_separate_unknown_outcome(self):
        # WHY: CLAIM(append-only). Duplicate captures are idempotent; outcomes do not rewrite observations.
        store = self.root / 'store'
        _, first = self.capture('--store', store)
        record = Path(first['stored_path']); original = record.read_bytes()
        outcome = self.root / 'outcome.json'
        outcome.write_text(json.dumps({'state': 'unobserved', 'reason': 'No additional review performed.'}))
        proc = subprocess.run([sys.executable, str(COLLECTOR), 'record-outcome', '--observation', str(record),
                               '--outcome', str(outcome), '--store', str(store)], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        appended = json.loads(proc.stdout)
        self.assertNotEqual(appended['stored_path'], str(record))
        self.assertEqual(record.read_bytes(), original)
        self.assertEqual(json.loads(Path(appended['stored_path']).read_text())['outcome']['state'], 'unobserved')
        value = json.loads(original)
        same = collector.store_record(value, store, 'observation')
        self.assertEqual(same, record)
        record.chmod(0o644); record.write_text('tampered')
        with self.assertRaisesRegex(collector.Refusal, 'tampering'):
            collector.store_record(value, store, 'observation')

    def test_descendant_fix_is_not_an_ancestor_of_target(self):
        # WHY: CLAIM(ancestry). A valid hash for a real later fix cannot justify an earlier snapshot.
        (self.repo / 'file.txt').write_text('later fix\n')
        self.git('add', 'file.txt'); self.git('commit', '-qm', 'later')
        self.fact_data['fix_revision'] = self.git('rev-parse', 'HEAD').strip()
        self.fact.write_text(json.dumps(self.fact_data))
        proc, result = self.capture('--fact', self.fact)
        self.assertEqual(proc.returncode, 2)
        self.assertIn('fix-not-ancestor-of-object', result['reasons'])

    def test_git_replacement_cannot_change_named_object_snapshot(self):
        # WHY: CLAIM(raw-git-object). Git replacement refs must not substitute code behind a pinned commit ID.
        original_tree = self.git('rev-parse', self.head + '^{tree}').strip()
        (self.repo / 'file.txt').write_text('replacement code\n')
        self.git('add', 'file.txt'); self.git('commit', '-qm', 'replacement')
        replacement = self.git('rev-parse', 'HEAD').strip()
        self.git('replace', self.head, replacement)
        substituted_tree = self.git('rev-parse', self.head + '^{tree}').strip()
        self.assertNotEqual(substituted_tree, original_tree)  # Positive control: replacement is active for ordinary Git.
        proc, result = self.capture()
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(result['git_tree'], original_tree)
        self.assertEqual(result['revision'], self.head)

    def test_unsupported_installed_policy_hash_refuses_before_execution(self):
        # WHY: CLAIM(policy-pin). Updating executable bytes needs an explicit adapter review.
        with mock.patch.object(collector, 'EXPECTED_POLICY_SHA', '0' * 64), mock.patch.object(collector, 'run_bounded') as run:
            with self.assertRaisesRegex(collector.Refusal, 'unsupported-policy-hash'):
                collector.canonical_next(self.ledger.read_bytes())
            run.assert_not_called()

    def test_source_change_during_real_canonical_call_invalidates_capture(self):
        # WHY: CLAIM(source-pin). Happy-path hash equality does not exercise a racing ledger edit.
        actual = collector.run_bounded
        def changing(argv, *args, **kwargs):
            output = actual(argv, *args, **kwargs)
            if str(collector.POLICY) in argv:
                self.ledger.write_bytes(self.ledger.read_bytes() + b' ')
            return output
        args = argparse.Namespace(source_root=str(self.root), ledger=str(self.ledger), repo=str(self.repo),
                                  revision=self.head, fact=None, store=None)
        with mock.patch.object(collector, 'run_bounded', changing):
            with self.assertRaisesRegex(collector.Refusal, 'source-'):
                collector.capture(args)

    def test_unknown_canonical_stdout_is_not_a_gate(self):
        # WHY: CLAIM(gate-token). No arbitrary output token may become a stopping boundary.
        with mock.patch.object(collector, 'run_bounded', return_value=b'STOP-SAFE: invented\n'):
            with self.assertRaisesRegex(collector.Refusal, 'unknown-canonical-output'):
                collector.canonical_next(self.ledger.read_bytes())

    def test_changed_policy_after_canonical_call_invalidates_capture(self):
        # WHY: CLAIM(policy-after-pin). A source replacement during invocation must not keep a valid capture.
        actual = collector.read_source
        policy_reads = 0
        def changed(root, path, limit):
            nonlocal policy_reads
            data = actual(root, path, limit)
            if path == collector.POLICY:
                policy_reads += 1
                if policy_reads == 2:
                    return data + b' '
            return data
        with mock.patch.object(collector, 'read_source', changed):
            with self.assertRaisesRegex(collector.Refusal, 'policy-changed-during-capture'):
                collector.canonical_next(self.ledger.read_bytes())
        self.assertEqual(policy_reads, 2)


if __name__ == '__main__':
    unittest.main()
