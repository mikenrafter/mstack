# mstack for agents and contributors

The human overview is [README.md](README.md). This file is for an agent or a person changing this repository.

## What lives where

| Path | Holds |
|---|---|
| `skills/<name>/SKILL.md` | One skill: frontmatter (`name`, `description`), the rules, and pointers to its `references/` |
| `skills/build-loop/scripts/` | Helper scripts (`review-ledger`, `bot-triage`, `ui-brief-check`) and the tests for the skill text |
| `bin/` | Workflow helpers and hooks, including `publish-scan` |
| `global-instructions.md` | The instructions installed into `~/.claude/CLAUDE.md` and Codex |
| `research/` | Dated research; follow [research/BRIEF.md](research/BRIEF.md) |

## Editing and installing

- Edit skills here, never an installed copy (`~/.claude/skills`, `~/.codex/skills`); the next install overwrites those.
- phoe-nix consumes a locked `mstack` input and installs these files through its agent-integration scout module. There is no second editable copy there.
- To try an unpublished change, build the consumer with `--override-input mstack path:/absolute/path/to/mstack`. After publishing, update the `mstack` lock and run `nix-scout switch agent-integration` without the override.
- A skill that documents a tool and must change in step with it lives in that tool's repository: `qex` (qex), `usagewindow-status` (usagewindow), `babeltele` (babeltele).
- `file-pr`, `babysit-pr` and `leaving-pr-comments` come from Theo Browne's [tstack](https://github.com/t3dotgg/tstack); install them from there. To change how one behaves, write the change into an mstack skill, not a copy of theirs.

## Writing a skill

- Every skill is model-invocable; do not set `disable-model-invocation`.
- Write the description as conditions saying when to invoke it; the model reads it as a prose hook. It must be strict YAML, at most 1,024 characters, with no `<` or `>` (`test_skill_frontmatter.py` checks this).
- `build-loop/SKILL.md` stays under 1,800 words and each of its references under 1,700 (`test_skill_size.py`).
- Before installing an edit that changes a rule, try a read-back: give three fresh agents only the changed text and a concrete situation, ask what they would do, and fix the wording wherever one misreads it. Log it in `mstack.research/skill-readback.md`. This is a pilot over ten edits.
- A skill change the owner asked for may move a golden in `bin/tests/goldens/`; regenerate it with `UPDATE_GOLDENS=1` and say so. Otherwise a golden change needs the owner.

## Helper scripts

They need Python 3 and its standard library; ledger work needs Git, and live bot triage needs an authenticated `gh`. Some hook tests also need Bash, jq and grep. Run from the repository root:

```sh
python3 skills/build-loop/scripts/review-ledger --help          # review state and briefs
python3 skills/build-loop/scripts/bot-triage --help             # review-bot findings
python3 -I -m unittest discover -s skills/build-loop/scripts/tests
python3 -I -m unittest discover -s bin/tests
```

The tests check the helpers and the skill text, not whether the workflow improves software.

## Environment assumptions

`build-loop` assumes specific model roles and T3 Code orchestration tools. `boat`, `low-ram-hosts`, `vigil`, `manual-keepalive` and `uw-agent` describe the owner's environment. The `boat-run` wrapper, qex, NixOS hooks and the usagewindow service are not bundled.

## Rules

- Never open issues, forks, pull requests, discussions or other outreach without the owner's explicit request ([no-unsolicited-upstream](skills/no-unsolicited-upstream/SKILL.md)).
- Before pushing, run `bin/publish-scan`; [publishing-scrub](skills/publishing-scrub/SKILL.md) says what to scrub without asking.
- Keep transcripts, credentials, personal highlights and session handoffs out of this repository.
- Keep changes focused and report the checks you actually ran.
