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
