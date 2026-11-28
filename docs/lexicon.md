# Lexicon

Terms used across mstack whose meaning an agent cannot guess from the word. When two terms are easy to confuse, the entry says how they differ.

## Rituals

**Retro.** A look back over agent sessions, review ledgers and the owner's PR comments since the last retro, to find what in the environment let problems through (`skills/retro`). Two a week per project, from vigil reminders: one on Tuesday or Wednesday, one on Friday or Saturday. It proposes fixes and applies none.

**Practice digest (the Friday check-in).** The weekly `practice-watch` run on Fridays. It reads what the engineers the owner follows have published, compares it with mstack, and proposes changes. It also holds the *claim to test*: one widely repeated claim and the cheapest check that could change our mind. It is not a retro. A retro looks at our own sessions; the digest looks at outside work. A Friday retro and the digest are separate runs, even on the same day.

**Practice questions.** Four questions about a finished run: where it diverged, how to name the mistake, what drill would help, what practitioners and papers offer (`skills/retro`, "Practice questions"). They are asked in every retro, and after a run when the `practice-questions` reminder is due.

**Going cold.** Ending a session whose work is done: cancel the holds (`vigil cold`), queue one `/compact` carrying a BabelTele summary, end the turn. A final message alone is not going cold (`skills/vigil`).

## Build loop

**Orchestrator, implementer, reviewer.** The build-loop roles (`skills/build-loop`). The orchestrator writes specs, prompts and mock-ups, verifies, commits and talks to the owner; it writes little code. Implementers write red tests and green code. Reviewers score fix rounds.

**Opus, Sonnet, Sol, Neon.** Agents by model: Opus is the Claude orchestrator; Sonnet is a Claude implementer; Sol is the Codex (OpenAI) agent, used as implementer and reviewer; Neon is Gemini through Antigravity, used as a reviewer and for legibility reads.

**Red and green.** In a slice, red writes failing tests from the agreed behavior, and green writes the code that makes them pass.

**Holdout.** A test red writes but green cannot see during the implementation round. Holdouts are sealed with age in the research sidecar and run from outside the implementer's checkout. They join the checkout as ordinary tests when the slice moves to review, whatever the concern bar (`skills/build-loop/references/holdouts.md`).

**Concern bar.** The quality bar for one concern (durability, security, UX and so on) in a feature, an integer from 6 to 10, usually 7 or 8 (`skills/build-loop/references/bars.md`). At 9 or above the orchestrator steps in on every slice and holdouts are never shown during implementation.

**Quirks ledger.** The table of repeatable model behaviors that cost time or quality, each with a detection signal and a defined response (`skills/build-loop/references/quirks.md`). An entry needs two sightings, or one written report from someone the owner follows.

## Ideas

**Legible core.** A deterministic program (a measurement, ledger, index or check) that shows agents and people the state of things, so inference handles only the edge (`skills/legible-cores`).

**Attractor.** From residuality theory: a state a system tends to settle into under stress. In the backlog, the attractor work asks whether failures cluster near particular states or transitions, and how to measure that (`docs/influences.md`).

**Temporary backlog.** The private backlog in the research sidecar (`mstack.research/readwise/<date>/backlog.md`), not in this repository and not in `/tmp`. "Temporary" means it will move to a permanent home later.

**Research sidecar.** `<project>.research/`, the private directory beside a repository for research, retros, mock-ups and sealed holdouts. It is never pushed with the repository.
