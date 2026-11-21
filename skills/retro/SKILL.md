---
name: retro
description: >-
  Use when a vigil retro reminder fires, after a large piece of work or a
  merged stack, or when the owner asks to look back over agent sessions and
  review findings.
---

# retro

Every review comment is a hypothesis about what in the agent's environment
let the problem through. A retro tests those hypotheses and fixes the
environment, not the one instance.

## 1. Scope and budget

Default scope: sessions and PRs in the current project since the last retro
(`<project>.research/retro/` holds earlier ones). Check headroom with
`adaptive-hardening`. Without a spend grant, run `lean`: one project, one
pass, transcripts sampled. Read raw transcripts with subagents that have a
fresh context; never pull them into the main session whole.

## 2. Inputs

- Claude Code transcripts: `~/.claude/projects/<dir>/*.jsonl` for the project
  and its worktrees. Codex: `~/.codex/sessions/`.
- `skills/build-loop/scripts/transcript-check` for agent-cap and keepalive
  breaks.
- Review ledgers (`review-ledger`) and `HARDENING-STASH` entries.
- The owner's PR review comments: `gh api repos/<o>/<r>/pulls/<n>/comments`
  and `.../reviews` for PRs merged in scope.
- Teach-back misses from `pr-stacks` §4.

## 3. Find causes

Group findings by family, not by file. For each family, find the cause: a
missing check, a rule nobody reads at the right moment, a doc or existing
code that teaches the rejected pattern, a skill step that is missing or
wrong, or context loss at compaction. Count instances in the codebase as well
as in the sessions; a pattern with thousands of existing instances needs a
baseline, not a rule.

### Reviewer noise per model

Sum `review-ledger status` across the period's ledgers. For each reviewer model, report the share
of findings that ended fixed against disagreed, declined or discarded, and the mean rounds to
pass. Compare with the outside references: Anthropic's review telemetry (mean 1.32 rounds to pass
after round caps and step-backs, heard through Theo) and Theo's council (scores move from ~7.5 to
~9 after two or more rounds). A model whose noise share stands out loses reviewer weight in
`reviewer-profiles.json`. It feeds the mistake-gravity and HITL-comms scores (`build-loop`
`roles.md` §2b).

## 4. Route each cause

Checks first. Prose rules did not survive compaction in the owner's own data
(research/00-index item 4).

| Cause | Fix |
|---|---|
| Mechanical: a banned API, an import shape, a file location, a syntax pattern | A deterministic check: a linter rule, clippy `disallowed_methods`, a pre-commit hook, or a CI job. Existing violations go in a baseline that only shrinks. The error message names what to use instead. |
| Judgement call | One line in the project's review standards, read by the reviewer, not the implementer. |
| Docs or examples teach the wrong pattern | Fix the docs and examples first. Agents copy what is there. |
| Skill gap or skill defect | A proposed edit to the mstack skill, shown to the owner. |
| Lost at compaction | Move the rule into a hook or the file the hook re-reads. |
| Comments hiding workarounds | Hand to `comment-audit`. |

A repo with no check covering a repeated family is itself a finding.

## 5. Output

Write `<project>.research/retro/<date>.md`: families ranked by cost (rounds,
tokens, owner time), each with evidence (session ids, PR comment links,
counts), cause, and the proposed fix. Propose; do not apply. The owner picks
what to do. Issues, PRs and upstream reports need approval
(`no-unsolicited-upstream`). After the owner decides, record the outcome and
run `vigil remind done <id>` if a reminder started the retro.
