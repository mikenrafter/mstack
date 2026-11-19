---
name: comment-audit
description: Audit code comments as smells. Delete narration and agent session notes, turn workaround excuses into code fixes, move decisions to ADRs and timing rules to test names, and keep sourced claims and interface contracts. Use when a vigil comment-audit reminder fires, when a retro hands over comment findings, or when the owner asks to audit or cut comments. Companions: technical-excellence (CLAIM convention), retro, adaptive-hardening.
---

# comment-audit

Comments cost upkeep: agents must keep them true, and a stale one misleads.
Some carry what code cannot. This audit keeps those and gives each a check,
and removes the rest. A comment that excuses a workaround usually marks code
that should have been designed differently (Lauren Tan's `comment-sicko`,
research/17).

## 1. Scope

Default: files changed since the last audit (`<project>.research/comment-audit/`
records it). Monthly, or when the owner asks: the whole repo, under
`adaptive-hardening`'s budget. Report only; edits go in a separate change the
owner approves.

Adaptive-hardening's `scripts/review-maintenance ensure --project ABS` creates
one `comment-audit-<key>` reminder per project, sharing the technical review's
repository, research and worktree scopes. Projects with more than 16 scopes
get matching `-2` and later reminder ids. Delivery is weekly on Saturday or
Sunday, 09:00-21:00 in America/Denver, the review reminder's timezone. Each id
has its own done state in vigil; no audit probe is needed. Check headroom with
`adaptive-hardening` before starting. The reminder authorizes at most lean work.

## 2. Classify every comment

| Class | Action |
|---|---|
| Narration: restates the code | Delete |
| Agent session note ("added for ticket 4", "now we", "as requested", "new:") | Delete |
| Commented-out code | Delete; git has it |
| Workaround excuse in our own code | Mark the symbol `MUST-FIX` with the reshape that makes the comment unnecessary: rename, extract, type, adapter. The comment goes when the fix lands |
| Constraint from a vendor, platform or protocol we cannot change | Keep, with a link. Prefer moving it into an adapter that owns the quirk |
| Why behind a decision spanning modules | Move to an ADR; leave `ADR-NNNN` at the site |
| Ordering, race or timing rule | Becomes a test whose name states the rule, plus a CLAIM id if one exists |
| Verifiable claim with a source (`CLAIM(id)`) | Keep. Check the source still holds and a test names the id |
| Public interface contract (what callers may rely on) | Keep (Ousterhout: the interface comment is part of the design) |
| Lint or type suppression | Keep only if the rule is wrong for this line; otherwise `MUST-FIX` |
| Legal or license header | Keep |

When unsure between keep and delete, read the code it governs. If the claim
is obvious there, delete.

## 3. Staleness

Flag a comment as possibly stale when `git blame` shows it older than the
lines it sits above (the code changed, the comment did not). Read each
flagged pair and say whether the comment still holds.

## 4. Numbers and limits

Report comment lines as a share of code lines per directory, excluding CLAIM
lines, license headers and interface doc comments, against the previous
audit. A directory can opt into a no-comment limit in
`<project>.research/comment-audit/limits.json` (`{"src/ui": 0.02}`). The
number for an opted-in directory only goes down; raising it needs the owner.

## 5. Output

`<project>.research/comment-audit/<date>.md`: counts per class, every
`MUST-FIX` with one line on the reshape, the ADRs to write, the tests to
rename or add, stale pairs, and the per-directory ratios. Then
`vigil remind done <id>` if a reminder started it.
