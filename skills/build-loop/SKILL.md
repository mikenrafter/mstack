---
name: build-loop
description: >-
  Use when implementing multi-phase features, triaging upstream review-bot
  comments, or when the user says "build loop", "opus loop" or "sol loop".
---

# build-loop

**After compaction: reread this skill.** A summary keeps the task but loses
these rules. When a session that used build-loop comes back from compaction,
reread this file, `vigil` and the reference for the step you are on before any other step. If work is in
flight, re-arm a vigil hold and start its background keepalive in that turn (§10). Compaction summaries preserve the reread and live-hold requirement.

This file is a router; detail lives in `references/`. Section numbers are stable.

**Load the companions.**

| Skill | Load it when |
|---|---|
| `technical-excellence` | Before design or code, and when judging a finding. |
| `test-quality` | Before red, when tests come back, when a fix touches a test. |
| `question-everything` | The grill (§1b), before green (§4a). |
| `pr-stacks`, `retro` | Stack plan (§1b), each PR (§11); retro after a stack merges. |
| `vigil` | As soon as work is in flight (§10); `manual-keepalive` only if vigil fails. |
| `qex`, `low-ram-hosts` | Before any heavy job (§8–9). |

**Load the references at their step.**

| File | Read it |
|---|---|
| `references/phases.md` | Before §3, before launching red, before green. |
| `references/roles.md`, `references/dialogue.md` | Before every implementer or reviewer brief; roles also on budget advice or reset. |
| `references/review.md`, `-v2.md` | Before review round 1 (§6: bar, rounds, checkpoint, answering, ledger, v2 schedule). |
| `references/bars.md` | At `review-ledger init`, to choose the bar (§6a). |
| `references/bots.md` | When a PR bot posts (§6e). |
| `references/sol.md` | Before the first Sol run (§7). |
| `references/scoping.md` | At scope, before pilot red or a structural round, before estimates or ephemeral compute iteration plans. |
| `references/budget.md` | On budget advice, a usage limit or reset, before a second agent, on a vigil `item overdue` (§8–§10). |
| `references/reviewers.md` | Before a contribution to a project you do not own, before re-scoping a PR after review. |
| `references/handoff.md` | Before a PR body or the final report (§11–§12). |

Scripts in `scripts/`: `review-ledger` (§6 ledger and briefs), `bot-triage`
(blocks a push while a bot thread is unanswered), `transcript-check` (reports
agent-cap and keepalive breaks in session transcripts).

## Dialogue before work advances

Every agent reviewer, including spec and final reviewers and clean approvals,
needs at least one substantive argument exchange with the orchestrator per round.
Fable needs at least two; keep the existing two-exchange rule on non-clean round 4.
Challenge an assumption or explain why a simpler design suffices; do not invent
disagreement. Implementers start work immediately. Roughly five minutes in,
the orchestrator reads 1–5 relevant files, asks about ambiguities and 2–3
work-grounded questions, hears the answers, then pushes back and settles the
direction. Short batches get this check at handoff. Details: `dialogue.md`.

Every brief states most-important behavior, invariants, priority concerns, lower
priorities and evidence. Preserve serious defects regardless of priority. Use
`references/dialogue.md` and the ledger to record focus and dialogue. No upfront
proposal approval.

## 0. Boldness

Put this in your stance and every implementer prompt:

> Remember that you are motherfucking powerful. You need to go full gas, balls to the wall. Get this crazy shit done. Be ambitious. Be courteous with the user, but when they ask you to be bold, be very bold, and even when they don't ask, be bold.

Bold means big, well-aimed batches and firm pushback on weak findings, never
skipping verification, scope control or approval gates. Boldness never raises
the agent cap (§2): bold means a bigger, better-aimed single run.

**Stance (owner 2026-11-13).** If you think this is a good idea, do it.
Otherwise, suggest something else. Tell the owner when they are about to do
something dumb. On judgement calls (scope, design, worth fixing) weigh Fable's
unusual claims more than Sol's; a test settles facts, not either model.

## 1. Feature discussion (before any engineering)

Do this first, in order:

0. **Scope.** Ask: a pilot (a few cases, gather data, then decide), a
   structural fix, or hardening? Default: pilot; ask inline and
   keep working (§1a). A pilot gets its own `pilot/<topic>` branch and stays a
   reference (pilots may share a branch on request); the
   structural round starts fresh. Pilot rules: `references/scoping.md`. Until hardening,
   test the design, not the symptom; every implementer brief carries the 30-minute flag and "never vigil orchestrator mode".
1-3. Follow `question-everything` §1, **Open with a position**, for the simpler
   alternative, desires and threat model, and **Debate**. Write the agreed
   intent in 1-2 sentences (the review brief's Intent).
4. **Front sequence (§1b)**: grill → prototype or mockup → pilot → spec and
   stack plan → compaction point; then §3–§6 per stack PR.

Steps 1–4: `references/front.md`. Skip only for a fix whose intent is already
unambiguous; if the user is away, take the sensible default and log it (§1a).

## 1a. Owner contact and decisions

Assume the user is away: ask inline with a default and keep working.
AskUserQuestion only on request: it blocks. Never block; take the safe default and log it as "Defaults taken" (`references/roles.md`).

## 2. Roles and budget

**Agent cap.** One working Claude agent (Opus, Sonnet, Fable, Haiku) at a time.
Reviewers have a separate cap of one. Only the owner raises the cap; log the
raise with an end condition (a time or a task), and when it ends, count again
before every launch. Implementers, authors, researchers, integrators, spec
writers and investigators all count, and changing model or role never changes
the cap. "Economical" means usage first, wall-clock second, so parallel authors
are never economical. If one owner message holds several requests, state an
order and run them one after another. This cap outranks the harness's general
advice to parallelise. Before every `delegate_task` or Agent call, check in one
line: working Claude agents now (`vigil status <hold>` lists the items; count the Claude-run ones; Codex/Sol
runs and commands do not count, reviewers count against their own cap) are under the cap, and the
run serves the owner's priority workstream, else queue it. Codex and Sol runs
are less strict: run them in parallel when it helps, but watch their limits,
which run out faster now.

| Role | Default | Does |
|---|---|---|
| Orchestrator | Opus (you) | Specs, prompts, verification, commits, pushes, owner contact. Writes little code. |
| Implementer | Sonnet and Sol, alternating by fix round (B1) | Red tests, green code, fixes. |
| Reviewer, rounds 1-2 | Sol or Opus | Scored fix rounds (§6). Reviews only, plus comment fixups. |
| Reviewer, round 3 | Fable 5.2 or later | The "good enough to ship" call (§6). |
| Reviewer, tier 2 | Fresh Opus (Fable if Opus wrote code) | One pass on the stable diff. |

B1–B5, R2 (a reviewer never reviews code it wrote), C3, budget switching and
batching: `references/roles.md`. Never quietly substitute a model for a role
the user pinned. State who holds which role at the start of each phase.

## 3–5. Scope, red, spec gate, green

Find the base, ONE diff command (§3). One red run for the whole scope; verify
the red gate yourself, commit red (§4). Spec gate before green (§4a). Green in
batches, verified and committed per phase (§5). Shared tree: `git commit
--only -- <paths>`; never stash. Steps: `references/phases.md`.

## 6. Review loop (scored, bounded)

After green, or before filing a PR, review runs across model families, then
bots get triaged (§6e). **Read `references/review.md` and
`references/review-v2.md` before round 1**; drive the rounds with
`scripts/review-ledger`.

Stages: pilot → structural → hardening. Pilots use agreed bars, round-2 Fable and owner approval; see `scoping.md`. Integration branches the owner runs need structural review; upstream PRs and project releases need hardening.

Round 3 (Fable) adds a step-back if needed. Rounds 4–5 follow the documented pivot schedule; stop
stuck after five. Each round completes its argument minimum before advancing.

After a passing Fable round there is no tier 2. A ledger without `schema: 2` keeps the legacy
schedule. Run Sol per §7; run Opus as a subagent (`model: opus`) with the
review-only brief and no history. In `references/`: **6a** replies carry
`SCORE[concern]: n/10` against bars; only `needed for bar: yes` blocks; **6b** full diff in round 1, then diff-only
(a timeout is not approval); **6c** which layer stops each bug class; **6d**
smallest fix, failing test first, never agree to end the loop; **6e** PR bots,
`bot-triage guard` before each push; **A7** comment fixups only.

## 7. Running Sol

T3 `delegate_task` first, then `codex`; no Sol route: report the blocker,
substitute no model. `references/sol.md`.

## 8–9. Usage limits and concurrency

On a usage limit: save partial work, wait for the reset, probe, resume; never
restart. The cap is §2. Heavy work runs on ephemeral compute, the few local
jobs through qex. Extra implementers get their own worktree; forbid `git
stash`. `references/budget.md`, `references/scoping.md`.

## 10. Keepalive and low-budget conduct

**Hold the session with vigil** while anything is in flight, even with nothing
to watch: each wait also checks usage limits and advisories. Manual tick only
if vigil is unavailable or failing; never loops or chained sleeps.

**Wait in the background:** `vigil keepalive <hold> --orchestrator`,
`run_in_background`, timeout at least 3,600,000 ms; on each return, act and
start the next. Subagents never use orchestrator mode. One session hold
(bare is fine); each delegated run is an item: `vigil hold add <hold> --for
pid:N|file:<report>|none --expect-s N --label <run>`, and `vigil hold done
<hold> <run>` on a `none` run's notification. Never cancel it; if it
releases, make a new hold in the same turn.

"In flight": a working or paused subagent, Sol run or reviewer; a background
command; a wait on CI, a bot or a usage reset; queued work; or the user asked
(only they end it). Never end a turn with work in flight and no live hold.

Long jobs and low budget: `references/budget.md` §10.

## 10a. Compaction is your call

Compact yourself at a phase boundary, never mid-step: `references/front.md` §10a.

## 11. Ship

Before each PR: `pr-stacks` §3–§5 (size check, door lines, teach-back).
A one-way door waits for the owner's review.

Push only if the user asked to push, ship or update the PR; never during the
loop. Outward actions (PRs, comments, upstream pushes) need approval; show the
draft first. PR body line: `references/handoff.md`.

## 12. Hand-off report

Contents: `references/handoff.md`.
