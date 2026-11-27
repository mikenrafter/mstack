"""Every mstack skill's frontmatter loads in the harness. Run: python3 -I -m unittest discover -s scripts/tests

WHY: a SKILL.md whose frontmatter is not strict YAML, or whose description is missing, too long or
holds angle brackets, is skipped or truncated by the harness without an error, so the skill silently
stops triggering (practice-watch 2026-11-20, carried over 2026-11-27).
"""
import os
import unittest
from pathlib import Path

import yaml

SKILLS = Path(os.environ.get("MSTACK_SKILLS_DIR") or Path(__file__).resolve().parents[3])
DESCRIPTION_CHARS = 1024


def frontmatter(path):
    text = path.read_text()
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    return None if end < 0 else text[4:end]


class SkillFrontmatter(unittest.TestCase):
    def test_every_skill_has_loadable_frontmatter(self):
        paths = sorted(SKILLS.glob("*/SKILL.md"))
        self.assertGreater(len(paths), 10, f"found {len(paths)} skills under {SKILLS}; is the path right?")
        problems = []
        for path in paths:
            name = path.parent.name
            raw = frontmatter(path)
            if raw is None:
                problems.append(f"{name}: no frontmatter block between '---' lines")
                continue
            try:
                meta = yaml.safe_load(raw)
            except yaml.YAMLError as error:
                problems.append(f"{name}: frontmatter is not strict YAML ({error.__class__.__name__})")
                continue
            if not isinstance(meta, dict):
                problems.append(f"{name}: frontmatter is not a mapping")
                continue
            if not isinstance(meta.get("name"), str) or not meta["name"].strip():
                problems.append(f"{name}: name missing or empty")
            description = meta.get("description")
            if not isinstance(description, str) or not description.strip():
                problems.append(f"{name}: description missing or empty")
                continue
            if "<" in description or ">" in description:
                problems.append(f"{name}: description contains '<' or '>'")
            if len(description) > DESCRIPTION_CHARS:
                problems.append(f"{name}: description is {len(description)} characters (max {DESCRIPTION_CHARS})")
        self.assertEqual(problems, [], "\n" + "\n".join(problems))


if __name__ == "__main__":
    unittest.main()
