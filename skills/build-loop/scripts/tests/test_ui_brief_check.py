import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "ui-brief-check"

GOOD = """# Brief
## UI inheritance
| Source | Path or SHA | Take from it |
|---|---|---|
| Mock-up (signed off) | mockups/alarms-v22.html | layout, copy |
| Original screen | lib/ui2/profile/alarm.dart | toggles, rows |
| Prior pilot / landed feature | pilot/day-timeline @ c6b764aae | annotations |

## Fidelity check
Screenshot pairs (mock-up | build) in shots/.
"""


def run(text):
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write(text)
    r = subprocess.run([sys.executable, "-I", str(SCRIPT), f.name], capture_output=True, text=True)
    return r.returncode, r.stdout


class UiBriefCheck(unittest.TestCase):
    def test_complete_brief_passes(self):
        self.assertEqual(run(GOOD), (0, "ui-brief-check: ok\n"))

    def test_mockup_only_brief_fails(self):
        code, out = run("# Brief\nMatch mockups/alarms-v22.html.\n")
        self.assertEqual(code, 1)
        self.assertIn("UI inheritance", out)
        self.assertIn("Fidelity check", out)

    def test_missing_prior_pilot_row_fails(self):
        code, out = run(GOOD.replace("| Prior pilot / landed feature | pilot/day-timeline @ c6b764aae | annotations |\n", ""))
        self.assertEqual(code, 1)
        self.assertIn("prior pilot", out)

    def test_none_found_with_search_passes(self):
        text = GOOD.replace("pilot/day-timeline @ c6b764aae", "none found: git branch -a | grep -i pilot")
        self.assertEqual(run(text)[0], 0)

    def test_row_without_reference_fails(self):
        code, out = run(GOOD.replace("lib/ui2/profile/alarm.dart", "the old screen"))
        self.assertEqual(code, 1)
        self.assertIn("original screen", out)

    def test_fidelity_without_screenshots_fails(self):
        code, out = run(GOOD.replace("Screenshot pairs (mock-up | build) in shots/.", "Look at it."))
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
