"""Guards the size of the build-loop skill text. Run: python3 -I -m unittest discover -s scripts/tests"""
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[2]
SKILL_WORDS = 2700
REFERENCE_WORDS = 1700


def words(path):
    return len(path.read_text().split())


class SkillSize(unittest.TestCase):
    def test_skill_md_stays_small(self):
        """WHY: SKILL.md is loaded whole every time; growth costs every run."""
        n = words(SKILL_DIR / "SKILL.md")
        self.assertLessEqual(n, SKILL_WORDS, f"SKILL.md has {n} words (max {SKILL_WORDS}): cut elsewhere before adding")

    def test_references_stay_small(self):
        """WHY: references are read on demand, but each still has to fit one read."""
        refs = sorted((SKILL_DIR / "references").glob("*.md"))
        self.assertTrue(refs, "no references/*.md found; is the path right?")
        for ref in refs:
            n = words(ref)
            self.assertLessEqual(n, REFERENCE_WORDS,
                                 f"references/{ref.name} has {n} words (max {REFERENCE_WORDS}): cut elsewhere before adding")


if __name__ == "__main__":
    unittest.main()
