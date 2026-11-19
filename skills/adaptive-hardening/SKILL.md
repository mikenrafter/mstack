---
name: adaptive-hardening
description: Choose and run bounded periodic code or test audits using risk, audit history, and an explicit spend budget. Use when the owner asks for periodic hardening or to spend spare capacity on audit work; do not add audits to every ordinary coding task.
---

# Adaptive hardening

Choose the next useful audit within the owner's budget. Separate optional
maintenance from verification required for the current change. A low budget
can defer optional audits; it cannot turn missing required proof into approval.

## Budget and selection

Use the project's audit history and actual provider headroom if available.
Unknown budget is unknown. Without a spend grant, propose a plan rather than
starting unattended paid work. An interactive audit request authorizes a
bounded audit of its stated scope; choose one lens when no larger budget is set.

Offer these controls without pretending token costs are predictable:

| Mode | Optional work allowance |
|---|---|
| off | Record candidates only; run required checks as usual. |
| lean | One component, one lens, one pass. |
| balanced | One component, two complementary lenses, one pass each. |
| deep | Owner-selected components and lenses with explicit run/spend ceilings. |

At a phase boundary or an already-authorized maintenance wake, rank candidates
by concrete risk: escaped defects, changed trust/data boundaries, repeated
findings, recent churn since audit, and stale or missing evidence. Include an
occasional neglected component so selection does not only follow churn.
Choose the highest-value candidate that fits the remaining allowance. A skip
with a recorded reason is valid. Resume unfinished work before creating copies.

Time makes an audit eligible; capacity and risk select what runs. Scheduling
future execution requires a user request. If one is requested, use the available
scheduler and its real budget/control interface. Do not claim a schedule exists
because a skill describes one. A scheduler without a budget check cannot enforce
this policy autonomously. Re-read budget before each optional run; stop optional
launches when its reserve or cap is reached. Never silently switch providers,
spend API credits, or raise effort to exhaust a subscription.

## Lenses

Give each pass a concrete question and relevant artifacts. Independent passes
can omit each other's conclusions. All passes retain the real requirements.

| Lens | Evidence to seek |
|---|---|
| Test effectiveness | Does the test execute and reject a realistic broken implementation? Check skips, assertion reachability, swallowed failures, mocks, independent oracles. |
| Simplification | Which branch, wrapper, fallback, or duplicate has no supported requirement? Verify consumers before recommending deletion. |
| End-to-end behavior | Can a real caller complete the intended workflow through actual wiring? |
| State and durability | Trace interruptions, replay, restart, cancellation, ordering, and data ownership where the component promises them. |
| Trust boundaries | Trace reachable untrusted inputs to sensitive effects under the current threat model. |

Use `test-quality` for test audits. A surviving mutation is a candidate for
investigation, not automatic evidence that a test is useless. Check equivalent
mutations, uncovered requirements, runner failures, and selection mistakes.
Make mutations in an isolated disposable copy and restore it after the run.
Do not delete tests or broadly refactor as a side effect of an audit request.

## Effort and findings

Declare requested model, harness, effort, scope, lens, and stopping condition.
Record effective settings only when exposed. For a substantial review, high
is a starting experiment where supported; use a cheaper supported setting for
mechanical triage. Higher effort requires a specific unresolved reasoning need
and room in the budget. Effort labels are not equivalent across providers.
Follow pinned roles, existing review rules, agent caps, and delegation permissions.
This skill does not authorize additional agents by itself.

Use the finding criteria in
[deliberate-changes/references/review-scope.md](../deliberate-changes/references/review-scope.md).
Audit findings go into the project's existing ledger or follow-up file. Record
revision, component, lens, settings, evidence, disposition, remaining uncertainty,
and actual usage if exposed. Deduplicate existing items. Reopen only with new
evidence. Stop at the allowance; report unresolved important findings clearly.

Judge the policy by confirmed defects, escaped bugs, review-induced regressions,
and cost per useful finding. Increasing scores or finding counts alone do not
show that hardening helped.

## Vigil project reminders

The owner has requested per-project reminders. A project means a product or
shared body of work, with one or more repositories. Every project rotates the
same five technical concerns above, using its own completion history. Current
priorities guide inspection within the selected concern; they do not replace
the rotation. User acceptance remains part of normal implementation review.

On first use in a project, run `scripts/review-maintenance ensure --project ABS`.
This discovers a single-repository project without a preselected project list;
repeating it is cheap and does not add duplicate reminders. Repository
subdirectories and linked worktrees share the main checkout's identity. Separate
clones or related repositories join a logical project through explicit membership:

```sh
scripts/review-maintenance group --id product --title Product --project /path/app --repo /path/library --repo /path/firmware
scripts/review-maintenance ensure --project /path/app
```

`group` adds members to an existing id and preserves completion evidence from
previous independent histories. A repository belongs to one logical project.
Membership lives in `projects/registry.json` under the maintenance state directory;
repositories need no configuration files or purpose comments. Separate clones
must be added explicitly; matching names or remotes do not establish membership.
Each project gets a `review-<key>` reminder and a `comment-audit-<key>` reminder
across the same member repositories, research directories and worktrees. Scopes
split after 16 entries with matching `-2` and later ids for both kinds. Rerun
`ensure` after membership or worktree changes to refresh both kinds and retire
obsolete reminders. Grouping also retires the members' independent reminders.
Reminders never wake an idle session. Seven days since a completed technical
audit makes the next concern eligible. Budget controls
inspection depth and whether optional work runs, rather than skipping concerns.

Comment audits are weekly on Saturday or Sunday, 09:00-21:00 in America/Denver,
the technical review reminder's timezone. Load `comment-audit` for changed files
since the last audit and a whole-repo pass once a month. Report only; edits need
the owner. Check headroom first; the reminder authorizes at most lean work.
Vigil tracks done state per reminder id, so comment audits need no probe.

Copy the current implementation round's focus to maintenance state:

```sh
scripts/review-maintenance context --project ABS --file focus.json
scripts/review-maintenance due --project ABS
```

`focus.json` has the same five fields as build-loop's `references/dialogue.md`.
The reminder names its selected concern. Establish missing focus from current
requirements before assigning reviewers. Give every reviewer most-important
behavior, invariants, priority concerns, lower priorities and evidence. Check
current context rather than treating an old record as a new acceptance contract.
Use the existing spend allowance, or ask for one when none is granted.

After an actual technical audit, record the evidence and suppress this period's
reminder:

```sh
scripts/review-maintenance complete --project ABS --concern CONCERN --evidence REPORT
vigil remind done REMINDER_ID
```

Snooze with `vigil remind snooze REMINDER_ID 2h` if busy. Do not mark an audit
complete because a reminder was delivered. State defaults to
`$XDG_STATE_HOME/vigil/review-maintenance`; use `--state-dir` before the command
for isolated tests. A probe exits 0 due, 1 successfully not due, 2 unavailable.
