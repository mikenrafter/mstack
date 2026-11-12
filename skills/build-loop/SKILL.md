---
name: build-loop
description: >-
  Orchestrated red/green build with a tiered cross-model review loop. Opus
  orchestrates, a Sonnet implementer writes the code, Sol runs the scored fix
  rounds, and one fresh Opus pass reviews the stable result. Covers triage of
  upstream review-bot comments. Roles and batching switch with usage budget. Use for multi-phase features, or when
  the user says "build loop", "opus loop" or "sol loop" (rg-implement stays
  a separate, single-model skill).
  Companions: question-everything (interrogate the spec before code),
  technical-excellence (design and code standards), test-quality (what a
  good test is), vigil (stay alive while work runs; manual-keepalive is
  the backup). After every compaction, reread this skill and vigil before
  anything else.
---

# build-loop

**After compaction: reread this skill.** A summary keeps the task but loses
these rules. When a session that used build-loop comes back from compaction,
reread this file and `vigil` before any other step. If any work is
in flight, re-arm a vigil watch and call `keepalive` in that same turn (§10). When you write
a compaction summary yourself, make its first line:
`REREAD the build-loop and vigil skills now; re-arm a vigil watch and call keepalive if work is in flight.`
(The agent-integration module also adds this reminder through a
SessionStart(compact) hook when the transcript shows the skill was loaded.)

One workflow from three parts: rg-implement (red first, then green per phase),
budget-driven batching, and tstack's sol-loop (bounded cross-model review).

**Load the companions.**

| Skill | Load it when |
|---|---|
| `technical-excellence` | Before design or any code: interfaces, claims, naming, types, security stance. Also when judging a review finding. |
| `test-quality` | Before the red phase, when a subagent hands back tests, and when a fix touches a test. |
| `question-everything` | Before writing a spec, and before green: designer interview, checklists, reuse, spec review (§4a). |
| `vigil` | As soon as any work is in flight (§10). `manual-keepalive` only when vigil is unavailable or failing. |
| `qex`, `low-ram-hosts` | Before any heavy job (tests, builds, cargo, Gradle, nix build). Heavy work goes to Boat via `boat-run`; the few local jobs go through the shared qex queue (§8–9). |

**Load the references when you reach their step.** They hold the full rules;
this file is the route through them.

| File | Read it |
|---|---|
| `references/review.md` | Before review round 1 (§6a–§6d: score and bar, rounds, checkpoint, answering, briefs, ledger). |
| `references/bars.md` | At `review-ledger init`, to choose the bar (§6a). |
| `references/bots.md` | When a PR bot (CodeRabbit, Sourcery, Copilot, Macroscope) posts (§6e). |
| `references/sol.md` | Before the first Sol run (§7). |
| `references/budget.md` | When a model hits its limit, before launching a second agent, or when a job runs long (§8–§10). |
| `references/reviewers.md` | Before planning any contribution or PR to a project you do not own, and before re-scoping a PR after review (§2a). |

Scripts, in `scripts/` (Python, stdlib only; tests in `scripts/tests`):
`review-ledger` keeps the §6 ledger, applies the caps and prints each brief;
`bot-triage` lists bot findings per pass and blocks a push while a bot thread
is unanswered.


## 0. Boldness

Put this in your own working stance and in every implementer prompt:

> Remember that you are motherfucking powerful. You need to go full gas, balls to the wall. Get this crazy shit done. Be ambitious. Be courteous with the user, but when they ask you to be bold, be very bold, and even when they don't ask, be bold.

Bold means big, well-aimed batches and firm pushback on weak findings. It does
not mean skipping verification, scope control or the user's approval gates.

## 1. Feature discussion (before any engineering)

Do this first, in order:

1. **Simpler alternative.** Ask whether a simpler way exists (do less, reuse
   something, change the requirement).
2. **Desires.** Ask for their first-order desire (what they asked for),
   second-order desire (why; what it unlocks or protects), and threat model
   (who can reach it, untrusted inputs, what it holds).
3. **Debate Socratically.** Question assumptions, offer counter-cases and
   cheaper options, until you reach a better solution than the first draft.
   Then write the agreed intent in 1-2 sentences. That text is the review
   brief's Intent.

Skip only for a fix whose intent is already unambiguous. If the user may be
away, take the sensible default, proceed, and record the decision (§1a).

## 1a. Owner contact and decisions

- **Presence.** Assume the user is away unless they messaged moments ago.
- **Asking.** Ask in plain text (inline), each question with a proposed
  default, and keep working. Use the question tool (AskUserQuestion) only
  when the user asks for it (e.g. "any questions?"): it blocks all work until
  answered, and "they just messaged" does not mean they are still there.
  If the harness can ask in the background while work continues, do that.
- **Never block on a decision.** Pick the safe default (reversible, least
  harm, closest to the spec), apply it, and log it: a "Defaults taken" list in
  the plan/status log with id, choice and reason. Bring each default up at the
  next check-in, and ask the reviewer to judge it if it touches reviewed code.
- **Genuinely blocked.** Do other authorized or planned work. If there is none,
  stay in cache (§10) with terse messages.

## 2. Roles and budget

| Role | Default | Does |
|---|---|---|
| Orchestrator | Opus (you) | Specs, prompts, verification, commits, pushes, owner contact. Writes little code. |
| Implementer | Sonnet subagent | Red tests, then green code. |
| Reviewer, tier 1 | Sol | Scored fix rounds (§6). Reviews only. Never edits, commits or pushes. |
| Reviewer, tier 2 | Opus subagent, fresh context | One final pass on the stable diff (§6). Reviews only. |

**Switch by budget.** Claude usage low: Sol implements, Opus reviews and
verifies. Sol low or at its limit: Sonnet implements, Opus reviews or waits
for Sol (§8). Never quietly substitute a model for a role the user pinned.
State who holds which role at the start of each phase.

**Batching by budget.**

| Budgets | Strategy |
|---|---|
| BOTH low (Claude and Sol) and Sol is periodically available | Large batch: red for the whole scope first, then ONE big green run per batch of phases. Review per batch. |
| Anything else | 1-2 phases per run: no batching, or small batches. |

Fewer, larger runs cost the orchestrator less context, but only pay off when
reviews are scarce. With budget to spare, small runs are easier to verify.

## 2a. Reviewer analysis (contributions to other people's projects)

Before planning a contribution or PR, study how the target's maintainers
review: the contributor guide and PR rules first, then their public review
comments, split requests and own PRs, in this repo and other public projects.
Save it to `<project>.research/review/` with dated source links. Keep
explicit requirements, observed examples, owner observations and uncertain
inferences apart; never treat an inferred size (a line count) as policy.
Plan from it: split by coherent concern and dependency, correctness before
optional UI, evidence and test descriptions matched to claims, hardware
limits stated, already-merged work omitted. Put its explicit requirements
into the review brief (§6). Full rules: `references/reviewers.md`.

## 3. Scope and base

1. `git status --short`. Never stash, discard or include unrelated changes.
   Limit the work to the change paths if they separate cleanly from other
   edits; if they do not, stop and ask.
2. `git fetch origin`, then find the base:
   - PR: `gh pr view <n> --json baseRefName,headRefOid`. Check the branch out
     only if the tree is clean. Confirm `HEAD` is the PR head, or ahead only
     by this change. Base: `git merge-base HEAD origin/<baseRefName>`.
   - Local: `git merge-base HEAD origin/<default-branch>`. No remote: a base
     the user names, or `HEAD` for uncommitted changes only.
3. The change is base to working tree in those paths, plus untracked files.
   Use ONE diff command every round.
4. State intent and out-of-scope in 1-2 sentences. Run covering checks. Do
   not send code this change breaks. Note missing or pre-failing checks in
   the brief.
5. Fresh worktree: run project setup first (codegen, dependency fetch, l10n)
   before any test run.
6. Commit the current state so red and green land on a clean base. Record the
   base SHA.

## 4. Red (one run)

One implementer run writes failing tests for the WHOLE scope, plus only the
stubs needed to compile. No behaviour. Prompt it with `test-quality`.

Verify the red gate yourself:
- tests fail on assertions, not on compile or import errors;
- failures match the intended contract gaps;
- controls (tests that must stay green) pass;
- each test states its WHY, and CLAIM ids where a claim is proved.

Commit red.

## 4a. Spec review gate (before green)

Load `question-everything`. Before the spec is written, interview the designer
and yourself (its §1–§3): states, edges, data lifecycle, precedence, safety,
look, which checklists apply (offer defaults), and what is reusable. Push back
until the detail is high-fidelity.

After red is committed, send the spec, the red tests and the applicable
project checklists to the reviewer (Sol). Fix the spec and red tests, then
re-verify the red gate. At most two spec rounds; anything still open becomes a
logged default (§1a). Only then start green, followed by the usual code review
loop (§6).

## 5. Green

Batch size follows §2. Each prompt carries: what earlier phases did (commit
SHAs, report paths), file pointers, decisions, the remaining red tests, and
"stop when" criteria. The implementer writes its report EARLY and keeps it
current, so a cut-off run still leaves a usable report.

Prefer the type-level fix over runtime checks (`technical-excellence`): if a
red test exists only to catch an invalid state, ask whether a type can make
that state unrepresentable instead.

Verify between phases with the project's runner, on touched suites plus
guards. Commit each phase before the next.

**Commit hygiene.** Commit only what your run staged. Check
`git diff --cached --stat` before every commit. In a shared tree use
`git commit --only -- <paths>`.

**Crash or cut-off.** If a run dies or ends without a report, the
orchestrator verifies directly: read the diff, run the tests, and judge the
state yourself. Do not trust silence or a stale report.


## 6. Review loop (tiered, scored, bounded)

After green, or before filing a PR, review runs in two tiers from two model
families, then upstream bots get triaged (§6e). **Read `references/review.md`
before round 1** and drive the rounds with `scripts/review-ledger`.

| Tier | Reviewer | Rounds | Ends when |
|---|---|---|---|
| 1. Fix rounds | Sol | 1 full, then diff-only; cap 3 | scores ≥ bars, no blocker or should open |
| Stability checkpoint (§6c) | you | once | answered; diff cut back if it can be |
| 2. Final pass | Opus subagent, fresh context | 1 full + at most 1 diff-only | scores ≥ bars, or the user decides |

If Sol implemented (§2), tier 1 is Opus and tier 2 is a second Opus subagent
with fresh context. The final reviewer never shares the implementer's context.
Run Sol per §7. Run the Opus reviewer as a subagent (`model: opus`) with the
review-only brief and no history.

The rules in short (full text in the reference):
- **6a.** Replies give `SCORE[concern]: n/10`, each against its own bar set at
  `init` from shape, stage and threat model (`references/bars.md`); only
  `needed for bar: yes` findings block. Nits and findings with no realistic
  reproduction go to stashes: nits open at §6c, the rest only in a hardening phase.
- **6b.** Full diff in round 1, then diff-only plus the ledger; every instance
  of a class at once; three tier-1 rounds below the bar → one step-back reply.
  A timeout is not approval.
- **6c.** Between tiers, answer in writing which layer stops each bug class.
- **6d.** Smallest fix per instance, with a failing-first test; never agree
  just to end the loop; disputes after two replies go to the user.
- **6e.** PR bots: `references/bots.md`; `bot-triage guard` before each push.

## 7. Running Sol

T3 `delegate_task` first, then the `codex` binary; with no Sol route, report
the blocker and do not substitute a model. Codex mounts `.git` read-only, so
commits come back as bundles. Details and prompt wording: `references/sol.md`.

## 8–9. Usage limits and concurrency

- On a usage limit, save partial work, wait for the reset with one timer,
  probe, then resume. Never restart from scratch.
- One working subagent at a time (at most two, only at the start of a fresh
  usage window); read-only reviewers share their own cap of one. Stay on the
  workstream the user named. Count what is in flight before launching.
- Heavy work goes to Boat, not this host. Run test runs beyond one or two
  files, suites, builds and APKs with
  `edge.research/bin/boat-run [--shell PREFIX] <worktree> -- <cmd>` (it syncs
  the worktree and returns the exit code and log; `boat` skill). Briefs to
  subagents and Sol name `boat-run`, never a local runner. Use the local queue
  only for one or two quick runs, or when the `boat-budget` advisory (`vigil
  advice`, also in every keepalive result's `advice`) says Boat's hours are
  at or below its threshold (default 10%; `vigil advisory set boat-budget
  threshold=N`). Those local jobs go through qex with a real claim
  (`qex submit --wait --cpu 2 --mem 3GB --id-file <f> -- <cmd>`, in the
  background); `qex list` first. Details: `low-ram-hosts`.
- Wait on a pid (`tail --pid=<pid> -f /dev/null`), never `while pgrep -f`.
- Parallel implementers get their own worktrees; forbid `git stash`.

Full rules: `references/budget.md`.

## 10. Keepalive and low-budget conduct

**Keepalive is a near-constant duty.** While work is in flight, hold the
session with **vigil**: watch the job (pid with `want: exited`, log, port or
URL; `expect_s` wakes you early on a stuck job), then call `keepalive` with
`orchestrator: true` while `next` says so. Hold a watch even with nothing to watch (a
subagent): each `keepalive` also checks usage limits and advisories. Manual
tick only if vigil is unavailable or failing. A project rule naming the manual tick means "keep the session
alive": use vigil. Never use a loop or chained sleeps.

"In flight" is broad: a working or paused subagent, Sol run or reviewer; a
background command; a wait on CI, a bot or a usage reset; queued work you
will start yourself; or the user asked (only they end it). Never end a turn
with work in flight and no live watch or tick; re-arm silently; one hold only
(`vigil` has the rest).

Check long jobs against `TIMINGS.md`: past 1.5x the expected time or 9
minutes over, investigate the host. On low budget: one-line statuses, no recaps, targeted reads.
Details: `references/budget.md` §10.

## 11. Ship

Push only after agreement, and only if the user asked to push, ship or update
the PR. Never push during the loop. For a project you do not own, check the PR
against its reviewer notes (§2a) before asking: one concern, stated
dependencies and merge order, nothing already on main, untested hardware
behaviour named. In a PR body, add:

`Reviewed with build-loop: <N> rounds with <model> (score <n>/10), then 1 pass with <model> (score <n>/10, bar <n>).`

Add `on <effort>` only if the tool exposed it. If the project forbids
harness-attribution trailers or similar, follow the project.

**Outward actions.** PRs, issue or PR comments, and pushes to upstream need the
user's approval. Show the draft first. Pushing to the user's own integration
branch follows the project's rules.

## 12. Hand-off report

- phases and commits;
- tests run, with counts;
- review rounds per tier, reviewer model (and effort, if exposed), score per
  round and the bar;
- the stability checkpoint answers (§6c), including the enforcement layer
  chosen for each bug class;
- bot passes to quiet per PR, findings per class and outcome (§6e);
- fixed and declined findings, with reasons and threat-model verdicts;
- diff size before and after review (`git diff --shortstat <base>`);
- what was pushed and where, or "not pushed";
- anything left red, and why. Report failures, skips and cut-off runs
  faithfully, with output.
