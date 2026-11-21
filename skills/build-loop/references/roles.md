# build-loop reference: roles, defaults, budget switching (§1a, §2)

The agent cap and the role table stay in SKILL.md §2. This file holds the rest.

## 1a. Owner contact and decisions

- When the workq hook asks, file the owner's requests.
- **Asking.** Assume the user is away. Ask inline with a proposed default and
  keep working. AskUserQuestion only on request: it blocks.
- **Never block on a decision.** Pick the safe default (reversible, least
  harm, closest to the spec), apply it, and log it in a "Defaults taken" list
  (id, choice, reason). Raise each at the next check-in; if it touches reviewed
  code, ask the reviewer to judge it.
- **Genuinely blocked.** Do other planned work, or stay in cache (§10).

## 2. Role rules

- **B1 Alternate.** Outside low budget, implementers alternate by fix round:
  if Sonnet wrote the first build, Sol writes the round-1 fixes and Sonnet the
  round-2 fixes. Green may also alternate from red. Pass `--author` to the ledger.
- **B2 Poor scope.** Ask for detail first. Occasionally an Opus agent on high
  effort implements instead of Sonnet; say why.
- **B3 Fable.** A T3 delegate (`orchestrator_capabilities` lists the version;
  the Agent tool's `fable` alias returns 404 here), effort high. Never swap
  versions silently; tell the owner.
- **R2 Authors.** A reviewer never reviews code it wrote.
- **B5 Back to default.** On a usage reset, on `claude-budget` or
  `codex-budget` advice that budget is fine, or on `credit_state_changed` with
  `on_credits` false, return to the default roles at the next phase boundary,
  not mid-run (`references/budget.md`).
- **Copy (C3).** Subagents do not load `unslop` or `plain-writing` unless they
  write copy; briefs to implementers say so.

## 2b. Capability and coherency (owner, 2026-11-20)

Judge every model on six sub-axes in two groups. Benchmarks mostly measure the last one.

**Coherency.** Can you follow it and work with it?
- **Copy:** text a person reads easily. Plans, PR bodies and replies have no slop and no stumbles.
- **Task juggling:** it stays on task over hours, keeps parallel threads straight, finishes the work
  and does not stop halfway. Failure looks like "slop for days" or dropped threads.
- **HITL comms:** it understands what the owner meant, asks the right question at the right time,
  reports what it did and what it needs, and answers the ask instead of a side question.

**Capability.** What can it do, and what does it cost when it goes wrong?
- **Safeguard aggression:** how readily safety filters stop legitimate work. Current ranking, most
  aggressive first: Opus 5+, Sonnet 5+, Sol (every version), Opus 4.8. Other models are unknown.
  Before giving a model security, firmware or reverse-engineering work, check this ranking, and
  `handling-ambiguous-work` for recovery.
- **Mistake gravity:** how bad its errors are when they happen. A wrong comment is cheap. A silent
  data change, a destructive command or a confident false claim is expensive.
- **Capability ceiling:** the hardest problem it can solve.

**Evidence and its weight.** Score each sub-axis from two sources, recorded separately:
1. The owner's own use: review ledgers, retro findings, trials (§2c). This weighs most.
2. The collective temperature: practitioners' write-ups and videos (`practice-watch`, Theo's
   council, people the owner follows), with the source and date.

AI companies' own announcements, press releases and launch benchmarks count for almost nothing.
They are notoriously unreliable. Never let one raise a score on its own.

Where the axes decide the role:
- **Release hardening and final reviews:** task juggling and HITL comms first, then low mistake
  gravity. Use a capable model that is weak on these only for bounded subtasks, with ~30-minute
  check-ins.
- **Pilots with a deadline:** task juggling over the capability ceiling. A model that stays on task
  beats a stronger one that drifts. Hard, isolated subproblems go to the strongest model.
- **Copy, press releases, PR bodies:** copy first.
- **Open-ended research:** the capability ceiling matters most, but every claim is marked verified
  or unverified. High mistake gravity in analysis (Neon: 10 of 72 claims wrong in one review) means
  claims are checked before anyone acts on them.

## 2c. A new model arrives

A new model gets no pinned role (round-3 reviewer, hardening, press release) until it is scored.

1. **Access and cost first.** How do we run it here (T3 provider, CLI)? What does it cost or what
   subscription subsidises it (`budget.md` §8a)? Tell the owner if it needs a login or a paid plan.
2. **Trial as a pilot.** About an hour on real work, scored on both axes:
   - a coherency probe: a long, bounded task with a mid-run steer, and a "why is this slow / what is
     wrong" diagnosis on a thread another model got lost in;
   - a capability probe: a hard, verifiable task from the current backlog.
   Record a profile entry in `reviewer-profiles.json` (strengths, failure modes, both scores, date,
   source) and tell the owner the result before giving it a role.
3. **Its quirks go into `references/quirks.md`**: what it does, how to detect it, and the
   defined response, in the brief and in the orchestrator.
4. **Re-check on version bumps.** A new version of a profiled model is re-trialled briefly, never
   assumed equal (B3).

**Gemini 4 Neon** (Google, medium model, 2026-11). Available here since 2026-11-20: T3 provider
`antigravity`, model `gemini-4-neon` (always name it; the provider default is Gemini 3.8 Flash), on a
Google AI Pro account. Untrialled. Reported: high coherency and capability, the best plan and
press-release copy the reviewer had seen, weak at 3D, analysis hallucinations as above. Until the
trial (§2c) scores it, its roles fall back as listed (press release: Opus).

**Switch by budget.** Claude usage low: Sol implements, Opus reviews and
verifies. Sol low or at its limit: Sonnet implements, Opus reviews or waits
for Sol (§8). Never quietly substitute a model for a role the user pinned.
State who holds which role at the start of each phase.

**Batching.** Both budgets low and Sol available now and then: red for the
whole scope, then one big green run per batch. Else 1-2 phases per run.

## 2a. Reviewer analysis

Before planning a PR to a project you do not own, study how its maintainers
review and plan from it. Full rules: `references/reviewers.md`.

## Implementation check-in

Implementers begin work without a proposal approval gate. Roughly five minutes
into each implementation batch, including red-test work, the orchestrator reads
1–5 relevant files and asks 2–3 concrete questions about the work, including what
remains ambiguous. The implementer explains its choices and uncertainties; the
orchestrator pushes back and settles the ambiguity. Ground the questions in
observed code, tests and the round priorities. Do not ask the agent to repeat the
orchestrator's planning process. For a batch finishing sooner, check at handoff.

This applies especially to Sonnet and cheaper implementers, which should expose
assumptions before extending the design further. Do not wait five minutes to
raise a known blocker. Use `dialogue.md` for timing and the exchange record.
