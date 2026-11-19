---
name: ratchets
description: >-
  Use when a review comment or retro finding should never recur, when adding a
  lint rule to a codebase with many existing violations, when rolling out a
  new tool, skill or habit, or when the owner says ratchet.
---

# ratchets

A ratchet is a limit that moves one way. Code that already breaks a new rule
may stay for now; new breaks may not; every fix lowers the limit for good.
That lets a rule land on day one in a repo with thousands of violations.

## 1. Ratchets in code

1. **Pick the deterministic form.** A linter rule, clippy
   `disallowed_methods` / `disallowed_types`, an import or dependency fence
   (dependency-cruiser, import-linter, depguard, ArchUnit), a grep with an
   allowlist, a size or complexity limit, a coverage or mutation-score floor.
   Prefer an allowlist ("use only these") to a ban ("never use that"); agents
   follow a short list of permitted forms more reliably than a nuance.
2. **Record the baseline as occurrences, not a count.** Commit a file listing
   each existing violation by a stable key (path plus symbol, or path plus
   rule plus a hash of the line). A bare count lets someone fix one and add
   another elsewhere.
3. **The check:** fail on any occurrence not in the baseline. When an
   occurrence disappears, rewrite the baseline without it in the same change.
   The baseline only shrinks.
4. **The error names the alternative:** "`as` casts are fenced outside
   `src/shared/`; use `parseUser()`". An error that only says no gets
   worked around.
5. **Raising the baseline needs the owner**, with a written reason next to
   the entry. An agent never adds to it.
6. **Shrink it on purpose.** A periodic task takes the oldest few entries off
   the list and fixes them, under `adaptive-hardening`'s budget. Without that,
   a baseline only shrinks when someone happens to touch the code.
7. **Fix the examples first.** If docs or existing code teach the banned
   pattern, agents copy it. Clean the docs before the code (`retro` §4).

Existing tools: `betterer` (TypeScript), `eslint --max-warnings`, ruff
per-file ignores, `cargo-deny`, `cargo clippy` with `#[expect]` lists. A
small script with a committed baseline file works anywhere.

## 2. Ratchets in workflow

The same shape governs practices. Examples in mstack: build-loop's review
stage only rises (bars.md B10); the PR size limit only falls (`pr-stacks`
§3); a directory's comment limit only falls (`comment-audit` §4).

## 3. Getting the operator to adopt a new tool

A new tool loses to the habit it replaces unless using it is easier and
skipping it is visible. In order:

1. **Default on.** The new path runs unless someone opts out. Opting out is
   one command with a reason, and it is logged (`pr-size override`).
2. **Show the count.** Print skips and overrides where the operator looks
   anyway: at session start, in a hook message, in the retro. Counts, not
   lectures.
3. **Meet the moment of need.** Offer the tool when the old habit starts: a
   PreToolUse hint, a vigil advisory, a reminder scoped to the project. A rule
   in a document read once a month does not change behaviour.
4. **Stage it.** Suggest, then warn, then block. Move up a stage after a
   stretch of clean use, never down without the owner's written reason.
   Record the stage where the check can read it.
5. **Make the first use cheap.** One command, sensible defaults, output that
   fits in a glance. If the tool needs setup, the setup is the tool's job.
6. **Measure adoption.** The retro counts uses against skips from
   transcripts and logs. A tool nobody uses after its stage reached "warn" is
   a finding against the tool, not the operator.
7. **Retire the old path** once adoption holds: delete it, or keep it as a
   named backup that says when to use it (`manual-keepalive` behind vigil).

Never hide a skip, and never make the operator's override silently stick:
each one is logged and counted again next session.
