---
name: pr-stacks
description: >-
  Use when writing tickets or a stack plan, before filing any PR, when a diff
  passes the owner's PR size limit, or when reviewing a PR in a stack.
---

# pr-stacks

Plan the stack before the code exists. A stack cut from finished code gives
PRs nobody deployed or tested on their own (research/17). The plan is
provisional: fix the door labels and where the flags go up front; PR
boundaries may move when implementation shows a better seam. Pilots skip
the plan (they live on their own branch and never merge); write it at the
start of the structural round, when the pilot has shown where the seams
are.

## 1. Doors

- **Two-way door**: merge it, revert it, nothing is lost. Prefactors, renames,
  glossary and ADR docs, tests, additive code behind a flag that is off,
  additive schema that nothing writes yet.
- **One-way door**: hard to walk back. Migrations that transform or drop data,
  writes to stored or exported data, external API or file-format contracts,
  turning a flag on for users, new exposure to untrusted input, anything sent
  outward (notifications, emails, uploads).

When unsure, call it one-way.

## 2. The stack plan

Written at the end of the grill (`question-everything` §6), inside the spec:

```
## Stack
1. [two-way] Extract shared editor (prefactor) — ~300 lines — blocked by: none
2. [two-way] Glossary: thumbnail diagram; ADR-0012 — ~40 lines — blocked by: none
3. [two-way] Thumbnail diagram behind `thumbnailDiagram` flag (off) — ~1,800 lines — blocked by: 1, 2
4. [one-way] Migration: thumbnail_diagram column, backfill — ~200 lines — blocked by: 3
5. [one-way] Flag on — ~5 lines — blocked by: 4
```

Rules:
- Each PR is reviewable and verifiable alone: its own tests pass and, for
  two-way doors, it can ship to the default branch without changing what
  users see.
- Keep structure changes and behaviour changes in separate PRs (Kent Beck,
  *Tidy First?*).
- One-way doors go last. More than one is allowed only when each depends on
  the one before; say why each cannot be made two-way.
- A feature flag turns one large behaviour PR into two-way doors plus a flip.
  Default to one for any new behaviour; it is the cheapest way to make a
  door two-way. See build-loop `references/scoping.md` for where the flag
  lives (in the product, at start-up, or at build time).
- Each line in the plan is one ticket and one implementer brief.

Tooling: plain git branches with `gh pr create --base <previous branch>`.
research/16 proposed a one-week jj trial; a stack is a good place to run it.

## 3. Size limit

**Limit: 4,000 changed lines per PR without a stack plan (owner, 2026-11-18).**
The limit only goes down. Raising it needs the owner's written reason in
`limit.json`.

Before filing any PR run:

```sh
python3 -I <this skill>/scripts/pr-size check --base origin/main
```

It counts added plus deleted lines, excluding lockfiles, snapshots and
generated files, and exits 1 when the PR is over the limit and its body or
spec has no `## Stack` section. Over the limit: split it, or ask the owner.
If the owner waves it through, record it:

```sh
python3 -I <this skill>/scripts/pr-size override --reason "<owner's words>"
```

`pr-size report` shows overrides in the last 30 days. build-loop prints it at
session start, so the owner sees how often the limit was skipped.

## 4. Two kinds of questioning

Two words, two jobs. Do not mix them up.

- **Grill**: before code, for alignment. The agent asks; the owner decides.
  Lives in `question-everything`.
- **Teach-back**: per PR, for comprehension. The agent asks the owner to
  explain the change back in their own words, then checks the answers
  against the code.

Teach-back depth follows the door:

| PR | Teach-back | Owner review |
|---|---|---|
| Two-way door | 3 questions, answered in one batch | Optional |
| One-way door | Up to 10 questions, one at a time on any wrong answer | Required before merge |
| The stack plan itself | Grill it once, before the first PR | Required |

Good teach-back questions ask what the code does in a case the PR changes,
what breaks if a named line is removed, which invariant a test proves, and
how to undo the PR. A wrong answer is a finding against the code or the
PR description before it is a gap in the owner's knowledge: unclear code,
a missing test name, or a PR body that hid the point. Fix those, then
explain.

## 5. PR body

Every PR body carries two lines (from Matt Pocock's `pr` skill):

```
Door: two-way | one-way (why)
Blast radius: <one word: none, ui, data, api, auth, build>
```

Plus the stack position: `Stack: 3 of 5, after #41`.
