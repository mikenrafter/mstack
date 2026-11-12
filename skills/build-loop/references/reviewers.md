# Reviewer analysis (build-loop §2a)

Before you plan a contribution or PR to a project you do not own, learn how
its maintainers review. A PR shaped to the reviewer's stated and observed
preferences gets merged; one shaped to your own habits gets a split request.

## When

- Before the plan for any upstream contribution, and before splitting or
  re-scoping an open PR after review.
- Again when the reviewer changes, or the notes are older than the project's
  last contributor-guide change.

## Where it goes

`<project>.research/review/<reviewer>-review-preferences.md` (create
`research/review/` if missing), dated, every claim linked to its public
source. One file per reviewer; a project file (`<project>-contributing.md`)
for repository-wide rules. Reuse an existing file: update it, keep its dates.

## What to read

1. The target repo's contributor guide, PR template, CODEOWNERS, CI rules and
   any review policy docs. These outrank everything below.
2. The maintainer's public review comments, split requests, closing comments
   and their own PR descriptions in the target repo.
3. The same in other public projects where they review, to see whether a
   pattern holds across projects. A repository listing alone shows nothing:
   only comments, reviews and PR descriptions count.

Use public engineering material only. No personal data unrelated to their
review practice.

## How to record it

Keep four sections apart, and label every line with one of them:

| Kind | Meaning | Weight |
|---|---|---|
| Explicit requirement | Written rule (guide, template, CI) or a direct request on this PR | Must follow |
| Observed example | What they did or asked for in a linked case | Strong guidance, not a rule |
| Owner observation | What the user has noticed, dated, attributed to the user | Guidance; say it is the owner's |
| Uncertain inference | Your reading of a pattern | Say so; never act on it as policy |

Never turn an inferred number into a rule. A line count seen once (or an
owner's sense of a size limit) is a warning range, not a ceiling; record it
as such and do not pad a PR up to it.

## How it shapes the plan

- Split by coherent concern and dependency, not by size: one behavior per PR,
  merge order and dependencies stated.
- Correctness first; optional UI and uncertain product choices last or out.
- Diff against current main before planning: omit work already merged, drop
  review findings that main has made stale.
- Align the PR's evidence with its claims: tests sit with the behavior they
  prove, each regression test names the broken implementation it rejects,
  and hardware or platform limits that tests cannot settle are stated plainly
  (static inspection is not a device test).
- Put the reviewer notes' explicit requirements into the review brief (§6) as
  checklist lines, so tier-1 and tier-2 reviewers check them too.

Example: `/home/mini/Documents/repos/edge.research/review/abdul-review-preferences.md`
(OpenStrap/edge #669 and #620, OpenStrap/analytics #96, thesolvent/solvent #14
split into #104–#107).
