"""WHY: masks must not silently transfer assumptions across roles or new weights."""
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'review-profile'


class Profiles(unittest.TestCase):
    def setUp(self):
        loader = importlib.machinery.SourceFileLoader('review_profile', str(SCRIPT))
        spec = importlib.util.spec_from_loader('review_profile', loader)
        self.module = importlib.util.module_from_spec(spec)
        loader.exec_module(self.module)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'profiles.json'
        unknown = {'pattern': 'Not established', 'status': 'unknown', 'evidence': []}
        def entry(model, role, nickname):
            return {'model': model, 'family': 'example', 'role': role, 'aliases': [],
                    'archetype': nickname, 'status': 'provisional',
                    'strengths': [unknown] * 3, 'weaknesses': [unknown] * 3,
                    'mask': ['Check supported callers.']}
        self.path.write_text(json.dumps({'schema': 1, 'updated_at': '2026-11-16',
            'archetypes': [{'id': 'finder', 'nickname': 'Finder'}],
            'models': [entry('example-v1', 'reviewer', 'finder'),
                       entry('example-v1', 'implementation', 'builder'),
                       entry('family:example', 'reviewer', 'finder')]}))

    def test_role_does_not_inherit_another_roles_observations(self):
        # CLAIM(profile-role): implementation assumptions cannot become reviewer facts.
        result = self.module.select_profile('example-v1', 'implementation', None, self.path)
        self.assertEqual(result['profile']['archetype'], 'builder')
        self.assertEqual(result['match'], 'exact')
        self.assertEqual(self.module.select_profile('example-v1', 'reviewer', None, self.path)['profile']['archetype'], 'finder')

    def test_new_weights_remain_unknown_without_explicit_family_request(self):
        # CLAIM(profile-no-inheritance): family similarity is not evidence for new weights.
        result = self.module.select_profile('example-v2', 'reviewer', None, self.path)
        self.assertEqual(result['match'], 'unknown')
        self.assertEqual(result['profile']['mask'], [])
        self.assertEqual(len(result['profile']['strengths']), 3)
        fallback = self.module.select_profile('example-v2', 'reviewer', 'example', self.path)
        self.assertEqual(fallback['match'], 'family-aggregate')
        self.assertEqual(fallback['requested_model'], 'example-v2')
        self.assertEqual(fallback['profile']['model'], 'family:example')

    def test_renderer_keeps_uncertainty_and_core_findings_visible(self):
        # CLAIM(profile-nonblocking): optional masks never suppress important defects.
        text = self.module.render_profile('example-v1', profiles_path=self.path)
        self.assertIn('unknown', text.lower())
        self.assertIn('Check supported callers.', text)
        self.assertIn('security', text.lower())
        self.assertIn('2026-11-16', text)

    def test_invalid_profile_is_not_a_silent_success(self):
        # CLAIM(profile-fail-visible): corrupt observations must not look like a healthy empty profile.
        self.path.write_text('{broken')
        with self.assertRaises(ValueError):
            self.module.select_profile('example-v1', 'reviewer', None, self.path)
