---
name: legible-cores
description: >-
  Use when an agent or the owner keeps guessing at something a program could
  measure (time, cost, cache state, layout, architecture, what happens next),
  when a retro or the Friday practice digest runs, and when a problem in the work looks big
  enough for one independent founder to build a company on.
---

# Legible cores (owner, 2026-11-21)

## The model

Agent work that goes well has four layers:

1. **Core.** A deterministic, non-inference piece: a clock, a ledger, a
   measurement, a search index, a test. Fast and exact, and it can't adapt.
2. **Comprehension.** The agent or person reads the core and acts on it.
   Today's intelligence, human or model, does well once it can see.
3. **Mushy edge.** Judgement the core can't make: intent, taste, trade-offs.
   Inference belongs here. It adapts, but it is slower and less precise.
4. **Chaos.** Reality outside both. Nothing runs on chaos alone.

Code alone is fast and brittle. Inference alone is adaptable, slow and
vague. The winning tools are cores that make the edge smaller: search,
legibility, measurement. This is a twist on the bitter lesson. More compute
keeps making models better, but a person or model that can't see the state
of things still guesses, the same as before. A core that shows the state
keeps paying off however smart the reader gets.

The owner's own run of these:

| Blind spot | Core |
|---|---|
| Agents misjudge time and cache expiry | keepalive → vigil → agentpace |
| What a change will do next | residual |
| Code architecture beyond hand-drawn mock-ups | paneweft |
| UI stability, otherwise judged by eye | Edge's CLS (layout shift) measurement |
| What a push publishes | publish-scan |
| Whether prose reads as machine-made | unslop's fixed catalogue of patterns (owner, 2026-11-21) |
| What survives compaction | The BabelTele compaction hook and the skill-reread hooks: they fire every time, so the rules don't depend on memory |

## Spot one in the work

Signals that an inference loop wants a core:

- An agent estimates, recalls or eyeballs something a program could read
  (elapsed time, token spend, file size, pixel offsets, call graphs).
- The same mistake comes back across sessions or models: the blindness is
  structural, not a slip.
- The owner explains the same state of the world twice.
- A prose rule keeps failing and a check would hold it (`retro` §4).

The test for bitter-lesson resistance: **would a model ten times smarter
still need this?** If it would still need the measurement (it can't see the
clock, the cache or the screen without one), the core lasts. If it would
just reason its way past it, the core is a crutch: skip it.

## Raise the opportunity

When a signal shows up and the problem is also big outside this work
(enough buyers to support one independent founder), raise it with the owner.

- **When:** at a natural break (a phase boundary, a handoff, the end of a
  turn), not in the middle of a fix. At most one per session unless the owner
  asks for more. Skip the ones already in the ledger unless there is new
  evidence.
- **How (it's a visual thing):** cards shown with `html_preview` then
  `html_render`, HTML kept in `~/Documents/repos/mstack.research/opportunities/`.
  The owner prefers cards for any idea brief (2026-11-21): one card per idea
  or part, in a grid, each short enough to take in at a glance. An
  opportunity's cards cover:
  - the problem, and who has it (people, agents, both);
  - the core, and what it leaves to the edge;
  - evidence from our work (session, commit, file);
  - market: who pays, a rough size with a source and date, what exists today
    and why it falls short (`standard` web search; mark guesses
    `[unverified]`);
  - the smallest first build (about two weeks of one person with agents), and
    which of the owner's tools already cover part of it;
  - the ten-times-smarter test result, and the biggest risk.
- **Ledger:** append one entry per card to
  `~/Documents/repos/mstack.research/opportunities/ledger.md` (date, title,
  evidence, status `raised | exploring | dropped | building`, the owner's
  reply). It is private; never copy it into a public repo.
- **Tools to build it:** if the owner wants to pursue one, propose a pilot
  the `build-loop` way (§1 scope, a `pilot/<topic>` branch or a new repo
  with a `.research` directory) and a one-page plan: first users, the
  core's interface, what to measure, what would make us drop it. Creating a
  public repo or anything outward still needs the owner
  (`no-unsolicited-upstream`).

## Cores show their state as HTML

A core is only as good as how fast someone can read it. A tool that holds
state (vigil, agentpace, residual, paneweft) offers `--html <path>`: one
self-contained page (inline CSS, no server or network), coloured with the host
theme's CSS variables plus fallbacks, with the same snapshot as `--json`
embedded in a `<script type="application/json">` block for agents. Put the
overview on the first screen as cards and the detail below it. Leave about 6rem
of space under the last card so it clears T3's mobile navigation. Budgets and
limits show when they reset. residual's
static export is the reference (research/23).

## Cores part (retro and practice digest)

`retro` and `practice-watch` each end with a **Cores** part:

- inference loops from this week that a core would have shortened, with
  evidence;
- ledger entries that gained or lost evidence;
- outside work (from the digest) that builds a core we lack or shows one of
  ours is a crutch;
- at most one new card, shown as above.
