# 23. Legible cores: what others have said, and where we differ

Date: 2026-11-21. The owner's observation, in short: agent work goes well when a deterministic
core (a clock, ledger, measurement, index or check) lets the agent see its situation, inference
handles a mushy edge of judgement, and reality is the chaos outside both. Code alone is fast and
brittle; inference alone adapts but is slow and imprecise. More compute makes models better, yet a
reader who can't see the state still guesses. The skill that applies it is
[legible-cores](../skills/legible-cores/SKILL.md). Grades follow [BRIEF.md](BRIEF.md). Several
sources were read only through search summaries, and those are marked.

## The owner's own cores

| Blind spot | Core | Status |
|---|---|---|
| Time and cache expiry | keepalive → vigil → agentpace | In daily use; vigil caught a harness's 180 s MCP cutoff (vigil 1aede03) |
| What happens next | residual | Static HTML export of a snapshot |
| Architecture beyond hand-drawn mock-ups | paneweft | In-code views, viewer server |
| UI stability judged by eye | Edge layout-shift (CLS) measurement | Used in Edge UI work |
| What a push publishes | publish-scan | mstack 090297b |

## What others have said

- **Sutton, "The Bitter Lesson"** (2019-03-13): general methods that use more computation beat
  built-in human knowledge in the long run. Grade C (historical argument).
- **Rodney Brooks, "A Better Lesson"**
  ([2019-03-19](https://rodneybrooks.com/a-better-lesson/)): every one of Sutton's wins needed human
  design (convolutions build in translation invariance). Count the *total* cost of a solution,
  human ingenuity included. Grade C. The nearest classic statement of the owner's view.
- **Scaffolding decays.** Boris Cherny (Claude Code) is reported to say harness scaffolding buys
  10–20% on a task and "the gain is wiped out with the next model"; Vercel reportedly cut 80% of an
  agent's tools and got fewer steps and tokens
  ([Schmid, 2026](https://www.philschmid.de/agent-harness-2026)). Traversal argues hand-built
  controllers and fixed task splits make agents worse
  ([Traversal](https://www.traversal.com/blog/ai-agent-architecture-mistakes)). Lee Hanchung asks
  which parts of a harness are load-bearing and which only prop up today's capability
  ([2026-05-08](https://leehanchung.github.io/blogs/2026/05/08/hidden-technical-debt-agent-harness/)).
  O'Reilly and Addy Osmani on harness engineering
  ([O'Reilly](https://www.oreilly.com/radar/agent-harness-engineering/),
  [Osmani](https://addyosmani.com/blog/agent-harness-engineering/)). Grade D, read through
  summaries; `[unverified]` quotes.
- **The interface changes results with the same model.** SWE-agent's agent-computer interface
  ablations (Yang et al. 2024, [01](01-research-literature.md) S10). Grade A on older models.
- **Visual views speed up verification.** Karpathy's "Software 3.0" talk (YC AI Startup School,
  June 2025): the human checker is the bottleneck in the generate-and-verify loop, and GUIs make
  checking faster because seeing is cheaper than reading
  ([Latent Space write-up](https://www.latent.space/p/s3)). Grade D, read through summaries.
- **Moldable development** (Gîrba; [03](03-moldable-development.md), [18](18-girba-wayne-oreilly.md)):
  build a small view for each question about the system. The same idea, aimed at people.
- **Residuality** (O'Reilly, [18](18-girba-wayne-oreilly.md) O5): harness engineering is
  architecture. residual is built on his method.
- **James C. Scott, *Seeing Like a State*** (1998): legibility imposed from the top flattens the local
  knowledge it can't see. Grade C. It warns against a core that hides the edge instead of
  informing it.

## Where we differ, and the test that settles it

The harness-deletion writers and the owner agree more than it seems. What decays is scaffolding for
*reasoning*: controllers, fixed task splits, "think carefully" prompts, summariser steps. A smarter
model does those itself. What lasts is a core that gives the model *information it cannot get by
thinking*: the time, a cache TTL, a quota, a pixel offset, what a push contains. Hence the test in
legible-cores: would a model ten times smarter still need it? Brooks's point applies too: count the
whole cost, including the human design that made the core possible.

Applied to mstack: sensors (vigil, agentpace, publish-scan, CLS) stay. Prose rules that tell the
model how to think are candidates for deletion with each model release. A pass over the skills to
sort them into these two kinds is open work.

## State as HTML (owner, 2026-11-21)

The owner wants the tools to show their state as HTML an agent can place in a preview, starting
with vigil and agentpace. residual already does this: its static export splices rendered fragments
into a shell template and embeds the snapshot as JSON in
`<script type="application/json" id="residual-snapshot">`. One page serves two readers: a person
looks at it, and an agent parses the embedded JSON instead of scraping. Karpathy's point about
verification argues for it. The proposed contract:

- `<tool> … --html <path>` writes one self-contained file: no server, no network, inline CSS.
- Colours come from the host theme's CSS variables (T3's `--card`, `--border`, `--chart-n`), with
  fallbacks, so it renders inside `html_render` and on its own.
- The same snapshot is embedded as JSON, matching the tool's `--json` output.
- One screen first: cards, an overview a person can take in at a glance, detail below.

## Open

- vigil and agentpace `--html` (proposed pilot; owner to confirm).
- A pass over the skills sorting sensors from reasoning scaffolds.
- T3's preview browser lacks system libraries on nixed, so `html_preview` fails there.
- Measurement of cross-model style influence ([22](22-agent-cadence.md)).
