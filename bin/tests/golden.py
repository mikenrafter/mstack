"""Golden files for hook output: the whole text an agent reads, compared exactly.

A hook's output is prose an agent follows, so the full wording is the contract; a
handful of substring checks lets every other sentence drift unreviewed.

Regenerate with `UPDATE_GOLDENS=1 python3 -I -m unittest discover -s bin/tests`. That
is a deliberate act: read `git diff bin/tests/goldens`, and name each regenerated file
and why it changed in the commit message. Ask the owner first unless the change that
moved the golden is one the owner asked for (test-quality techniques.md, "Goldens").
"""
import os
from pathlib import Path
import sys

GOLDENS = Path(__file__).resolve().parent / "goldens"


def check(case, name, text, paths=()):
    """Compare text against goldens/<name>.txt after replacing each (path, token) pair."""
    for path, token in paths:
        text = text.replace(str(path), token)
    golden = GOLDENS / f"{name}.txt"
    if os.environ.get("UPDATE_GOLDENS") == "1":
        GOLDENS.mkdir(exist_ok=True)
        golden.write_text(text + "\n")
        print(f"golden updated: {golden}", file=sys.stderr)
        return
    if not golden.exists():
        case.fail(f"no golden {golden}; run with UPDATE_GOLDENS=1 and review it")
    case.assertEqual(text + "\n", golden.read_text(), f"golden {name} differs")
