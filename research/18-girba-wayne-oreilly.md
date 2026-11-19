# 18. Gîrba, Wayne and O'Reilly: ideas worth adopting in an agent-heavy practice

Written 2026-11-18 on nixed. Read only: nothing was posted, followed, starred
or opened. This report adds to [03](03-moldable-development.md) (moldable
development basics, the Rewilding chapter 6 inventory numbers),
[10](10-residual-integration.md) (what residual does) and
[17](17-pocock-video-and-skills.md) (glossaries, ADRs). It does not repeat them.

Sources read: the full feenk Medium feed (10 items) and Hillel Wayne's
Buttondown feed (30 items, 2025-12-10 to 2026-11-03) as RSS bodies; a clone
of `feenkcom/gt4llm` at `0c846c7` (latest commit 2026-11-19); residual at
`/home/mini/Documents/repos/residual-cli` (head `32c0836`, metadata branch
`origin/residual/metadata`). The brief and an earlier task said
`/home/mini/Documents/repos/residual`, which does not exist. Also read: four
O'Reilly papers via Crossref/OpenAlex abstracts (ScienceDirect returned 403
for the full text), an InfoQ write-up, a book summary, and auto-captions of
four O'Reilly talks and one podcast, pulled with yt-dlp.

## Top findings

1. **Gîrba's rule for agents: have the LLM write the tool, then trust the
   tool's answer.** feenk now practises this in code. In `gt4llm`, a
   `<gtLlmView>` pragma marks which object views the model may read (92
   files). Every object an agent touches is stored with an id and a *reason*.
   Running an example returns its status, the result's views, an object id
   and a notebook page. Grade C: working code, no outcome data.
   [gt4llm][gt4llm]
2. **gt4llm became a front end for Claude Code and Codex in November 2026.**
   The `Gt4Llm-ACP` package (earliest commit 2026-11-05) reads
   `~/.claude` transcripts and Codex rollouts, drives both agents over the
   Agent Client Protocol (ACP), and shows tool calls, bash output and
   "needs input" states as views. Since April 2026, summarizers have turned
   an agent session into views of what code changed and which
   examples and tests ran. This is the closest outside match to paneweft.
   Grade C. [gt4llm][gt4llm]
3. **LLM-written properties are mostly tautologies.** Wayne took apart a public
   AI-written Alloy and TLA+ project. Its Alloy spec did not compile, and its
   assertions restated `canImport == P || Q`. With a client, he could not get
   Claude to write a liveness or action property even when told to. Grade C
   (one repo plus client anecdotes, model unnamed, "as of March 2026").
   [Wayne 2026-03-10][w-vibing]
4. **A conditional property passes vacuously when its trigger never happens.**
   Wayne's check: a property such as "a worker in Retry eventually leaves
   Retry" also needs a separate test that Retry is reachable. test-quality
   checks empty inputs for vacuity (§5) but not conditional properties. Grade
   C (reproducible reasoning). [Wayne 2026-02-11][w-possible]
5. **Refinement mappings are a checkable way to review migrations.** Wayne's
   database example maps each new schema back to the old one. Moving to
   event sourcing broke the "activated stays activated" rule even though all
   reads still worked. Index finding 3 puts stored data and migration at 47 of
   164 late review findings, so this targets your largest family. Grade C for
   the example, D for the transfer. [Wayne 2026-01-20][w-refine],
   [00](00-index.md)
6. **O'Reilly's test is held-out stressors, and residual can run it, mostly
   by hand** (corrected 2026-11-19; see
   `residual-cli.research/archaeology-ranking.md`). "Architectures should be
   trained, not designed": derive the architecture from one set of
   stressors, then count survivals on a second set that was never used.
   Ri = (Y − X) / S, where X and Y are the test stressors the naive and
   residual architectures survive and S is the size of the test set. In
   residual, record the two designs as architecture sets (`add component
   --architecture-set naive|residual-1`). Keep the test stressors out of
   training sessions on a forked metadata branch (`branch_mode = true`,
   `residual branch init`) or in a file outside the ledger. Judge survival
   per stressor by hand or with a fresh subagent, then run `residual matrix
   ri --stressors S --naive-survived X --residual-survived Y` and store the
   result with `add iteration --ri-score`. Residual does not mark test
   stressors, store per-stressor survival, or compute Ri from the ledger;
   `matrix ri` takes three typed numbers and does not reject S = 0. Checked
   against the older checkout (`32c0836`); newer code may differ. No
   published Ri results from his PhD experiments, and the owner's own ledger
   records none. Grade D for efficacy. [InfoQ 2025-10-07][infoq],
   [Lebrero 2025-08-20][lebrero], [Jfokus 2022 slides][jfokus]
7. **O'Reilly's position on agents (2026-07-13): an LLM is "determined by its
   training set".** Asking it for stressors gives you patterns found by
   statistics, and "the walk around the problem is the point." On
   2026-11-10 he described agentic and harness engineering as "an attempt to
   automate architecture." Residual's design (agent as Socratic partner,
   human approves every write) already fits this. Grade D. [Root Cause
   podcast][rootcause], [Zurich lecture][zurich]
8. **O'Reilly has no blog, Substack, GitHub or YouTube channel of his own
   that I could confirm.** His talks land on conference channels (NDC, GOTO,
   DDD Europe). His company's two Squarespace RSS feeds are almost empty, and
   LinkedIn is his main outlet. Two traps: `barryoreilly.com` belongs to a
   different Barry O'Reilly (*Lean Enterprise*, *Unlearn*), and "Residual
   Thoughts" on Substack belongs to Joe Hovde. Grade: verified with curl
   2026-11-18.

---

## 1. Tudor Gîrba (feenk, Glamorous Toolkit)

### The method in one paragraph

Gîrba treats engineering as decision-making about a system too large to
read, which makes "reading code" the bottleneck. Developers spend more than
half their time figuring out systems ([ch. 2, 2025-02-06][rw2]). Instead of
reading, you ask a question and build a *contextual micro tool* that answers
it from the system itself. You then fold the answer into a live model of the
system and ask the next question. He compares these tools to surveying
theodolites. "Explainable" means the answer keeps a path back to the code and
data that produced it, so you can check it instead of believing it ([ch.
2][rw2]; [ch. 4, 2025-03-12][rw4]). Report 03 covers ttA/ttQ (time to answer,
time to question), example-driven development and the patterns paper.

### What he said about LLMs, 2025 to 2026

- **"The suggestions that come out of an LLM are in fact questions to explore
  disguised as answers."** He tested a stuck-cursor bug against leading chat
  assistants. They suggested Stack Overflow searches that led nowhere. "Use
  LLMs to build deterministic tools that you can use to produce explainable
  summaries." ([ch. 4, 2025-03-12][rw4]). Grade D. He counters the "eventually
  the LLM will build the tool" objection with "it's tools all the way down":
  you still need a way to understand the tool.
- **A table of when to use AI** ([ch. 5, 2025-05-22][rw5]). If you are at the
  right level and can see the problem, generate code and evaluate it. If
  you are at the right level but have no tool, have the AI generate the tool
  or view. If you don't know where to look, ask it for possible questions.
  "Prompts are not a deterministic language." The architectural question he
  names is "at what point do I value human decision making?" Grade D.
- **"LLMs are not truth engines but coherence engines"** ([ch. 6,
  2026-01-16][rw6]). The inventory experiment (194 components and 396
  dependencies, with roughly 5–30% missing plus some hallucinated) is in report
  03. His new claim here: with many agents, "one agent creates the tool and
  another reads it" removes "any human path to understanding." He also mocks
  spec-driven development as "Wish Driven Development." Grade C for the
  experiment, D for the rest. The model name and version are not given.
- Talk and podcast: "Beyond AI Code Assistants: how moldable development
  answers questions AI can't" (Scrum Master Toolbox, 2025-10 [unverified
  date]) [smt]. I found no 2026 talk.

### What gt4llm actually does (read 2026-11-18)

`feenkcom/gt4llm`: MIT licence, created 2024-01-31, 17 stars, 2,910 commits.
The top committer since 2026-01-01 is Gîrba (553 commits), then Andrei Chiș
(490 under two spellings) and Juraj Kubelka (231). It is an LLM library
inside GT, written in Pharo and ported to GemStone. Its main parts:

| Area | What the code does | Path |
|---|---|---|
| Clients | OpenAI (Responses API), Anthropic, Gemini, Ollama, LM Studio; chat model with compaction strategies (prompt, API, OpenAI server-side) | `src/Gt4Llm-*`, `Gt4LlmCore/GtL*CompactionStrategy` |
| Agent tools | About 40 Magritte-described function tools: class and method lookup, references, implementors, compile and remove methods, refactoring preview and apply, file grep and read, git changes, Smalltalk evaluation, run examples and SUnit tests, Lepiter page edit, world screenshot, start a sub-agent | `Gt4LlmCore/GtLMagritteToolFor*`, `GtLToolFor*` |
| **Views for the model** | `<gtLlmView>` / `<gtLlmMessageView>` pragmas (`GtLSettings messageViewPragmaNames`) mark which inspector views an LLM may read. `getClassViews` lists a class's `<gtView>` methods. `getViewContent(objectId, viewSelector)` returns a view of a stored object together with the view method's source | `GtLToolForClassViews`, `GtLToolForObjectView`, `GtLObjectPhlowViewExtractor` |
| **Object storage with reasons** | Each object the agent produces gets a UUID and a reason (from an example run, a code execution, a tool call, or free text), and later calls refer to it by id. A human sees the same store as an inspector table | `GtLObjectStorage`, `GtLStoredObject*Reason` |
| **Examples as tools** | `exampleMethodRun` returns status (success, error, failure, skipped), the result as JSON or image views, an object id and a "playground page reference" for object-specific notes. Exceptions come back with stack, class and views | `GtLToolForExampleMethodRun` |
| Session summarizers | Views over a chat's tool calls: code changes made, example and SUnit runs, calls by type (added 2026-04-15 to 05-07) | `GtLCodeChangesToolCallsSummarizer`, `GtLOverall*ExecutionsSummarizer` |
| MCP server | GT exposes its tools, resources and prompts over MCP, via stdio or HTTP (added 2025-07-12) | `GtLMcpServer*` |
| **ACP front end** | Starts Claude Code and Codex sessions over ACP and reads stored sessions from `~/.claude` (or `CLAUDE_CONFIG_DIR`) and Codex rollouts. Shows tool calls with bash and input views, inter-session messages, and "attention" (input-needed) notifications tested by `<gtExample>`s. Lepiter pages can serve as system instructions (2026-11-18) | `src/Gt4Llm-ACP` |
| Domain editing | Wardley-map edits, SmaCC rewrite rules, Lepiter snippets, refactorings, each as a typed "transformation specification" the model fills in and a human previews | `Gt4Llm-WardleyMap`, `Gt4Llm-SmaCC-Transformations`, `Gt4LlmCore/GtL*Specification` |

Reading it: the model is never asked to summarize the system. It receives
views that someone already wrote and tested. Changes come back as typed
specifications with a preview. Its default models were "gpt-5-3-codex and
opus-4-5" from 2026-02-27 (commit log). Grade C: the code exists. I found no
published data on whether it improves outcomes.

### Adoptable ideas

| # | Idea | Source, date | Grade | Suggested change |
|---|---|---|---|---|
| G1 | Never act on a structural answer that has no tool behind it. Counts of callers, dependencies or affected modules come from a command or view, never from model prose. | [ch. 6, 2026-01-16][rw6] | C | `technical-excellence` §7: a finding that asserts structure must cite the command output or view id it came from. build-loop `references/review.md`: reviewers attach the grep, `cargo tree`, or similar output. |
| G2 | Treat an LLM suggestion as a question to investigate. | [ch. 4, 2025-03-12][rw4] | D | build-loop §6d already asks for "failing test first". Extend it to claims that are not tests: an unsourced reviewer claim enters the ledger as `hypothesis`, not `finding`. |
| G3 | When you don't know where to look, ask the agent for questions, not answers. | [ch. 5, 2025-05-22][rw5] | D | `question-everything` §2: add "if the code area is unfamiliar, first ask a subagent for ten questions it would ask, then answer them with tools." |
| G4 | Opt in, view by view, to what the model reads. | gt4llm `<gtLlmView>` | C | paneweft: add an `audience: human \| agent \| both` field to each view declaration. Agent discovery lists only views marked for agents by default, so humans can keep richer views without padding the context. |
| G5 | Every stored observation carries a *reason* (which tool call or question produced it). | gt4llm `GtLStoredObject` | C | paneweft object records: add `reason` next to the existing provenance stamp (`host_collected` / `agent_submitted`, report 12 §5). build-loop ledger: findings refer to evidence by id. |
| G6 | Running an example is an agent tool that returns status, views of the result, an id and a notes page. | `GtLToolForExampleMethodRun` | C | paneweft `view_result` (report 12 §6) already returns bounded text. Add the notes-page link, and have `rg-implement` hand-backs list the run ids. |
| G7 | Build the session report from tool calls, not from prose. | gt4llm summarizers (2026-04/05) | C | build-loop §12 hand-off: generate "files changed, tests run, results" from the transcript or `git diff --stat` plus test logs. The agent's prose then explains only. This addresses index finding 1 (a checklist line answered "done" that was false). |
| G8 | A moldable front end over Claude Code and Codex transcripts. | `Gt4Llm-ACP` (from 2026-11-05) | C | paneweft: add a transcript adapter (Claude `~/.claude/projects/*.jsonl`, Codex rollouts) so the one-off usage analyses in reports 06 and 07 become reusable views. Read feenk's session-store classes for the file formats first. |

---

## 2. Hillel Wayne

Context for 2026: *Logic for Programmers* reached 1.0 in print on 2026-07-29
after five years ([w-lfp-done]). It has eleven chapters: logic, rewrite
rules, property testing, contracts, Dafny, database theory, decision tables,
Alloy, TLA+, SMT solving and Prolog/ASP ([lfp]). He now works at Antithesis,
a testing company, on property-based testing for web apps. He argues that
randomized testing becomes accessible through "state-based system
invariants as opposed to algebraic laws and roundtrip properties" ([w-nyc,
2026-10-22][w-nyc]).

### What he says about LLMs and specs

- **2025-06-05, "AI is a gamechanger for TLA+ users."** Agents were good at
  syntax-fix loops with the SANY checker, at summarizing error traces of 20+
  steps, and at boilerplate. They were poor at finding properties
  ("trivial, uninteresting, or tied to implementation details"), at
  abstraction, and at running the checker instead of hallucinating commands.
  Grade C. Measured on Claude 3.7 in Copilot, now obsolete. [w-gamechanger]
- **2026-03-10, "LLMs are bad at vibing specifications."** 4% of public
  GitHub TLA+ specs mention "Claude." AI-written properties are "obvious"
  rather than "subtle": they catch a missing guard, not concurrency or
  multi-step bugs. "If you need to know formal methods to get the LLM to do
  formal methods, is that really helping?" Grade C. [w-vibing]
- **2026-09-30, "What TLA+ can and can't check."** He wrote this after Boris
  Cherny reported Opus finding race conditions with TLA+. TLA+ cannot natively
  express possibility ("P can happen"), properties spanning two or more steps
  (undo restores the state), hyperproperties (power-saving mode always uses
  less power; percentile latency) or real-time and floating-point
  properties. The workarounds (auxiliary variables, self-composition,
  `REACHABLE`) are clever hacks with costs. Grade D. [w-tla]
- **2026-09-16, "The LLMs yearn for the spines."** PR titles containing
  "spine" grew 20x from 2025 to 2026-09-01, against about 1.5x for all PRs.
  "Gate" appears in 1 of 300 PR titles. "Lane", "seam", "truth" and "proof" are
  also up. He attributes the change to several models, not one. Grade C
  (GitHub search counts, gist published). [w-spines]

### Adoptable ideas

| # | Idea | Source, date | Grade | Suggested change |
|---|---|---|---|---|
| W1 | **Reachability before conditional properties.** A passing `A(x ⇒ E(y))` is vacuous if `x` never happens. Check `P(x)` by asserting that `A(¬x)` fails. | [2026-02-11][w-possible] | C | `test-quality` §3 State machines: "for every property of the form *when X, then Y*, count how often X occurred in the generated runs (proptest/fast-check `classify` or a counter) and fail if it is zero." Add a matching row to the §5 tautology hunt. |
| W2 | **A property that restates the definition is a tautology.** Agents write "obvious" properties, while the value is in multi-step and concurrent ones. | [2026-03-10][w-vibing], [2025-06-05][w-gamechanger] | C | `question-everything` §4: the spec reviewer marks each red property as *restates the code* or *could catch a subtle bug*. For stateful features, require at least one property over a sequence of two or more steps, written or approved by the designer. Agents may write the harness; the designer picks the properties. |
| W3 | **Refinement mapping for every schema or format migration.** Write `old = f(new)`, then check that each rule about how a value may change (for example, "once true, stays true") survives. | [2026-01-20][w-refine] | C (worked example), D (transfer) | `question-everything` §1.3 Lifecycle: add "for each stored-data change, write the mapping from new to old and list the rules each field must keep across updates; one red test per rule." This targets the stored data and migration family (index finding 3). |
| W4 | **Illegal vs unwanted states.** Many states you would make unrepresentable are only unwanted (double booking, overbooking, a network partition). They must be representable and detectable, and they need an "eventually leaves" rule (P's *hot states*). | [2026-04-28][w-unwanted] | D | `technical-excellence` §5: add a caveat under "make invalid states unrepresentable": first ask whether the state is illegal or only unwanted. `question-everything` §1.1 States: label each state legal, unwanted (who leaves it, and by when) or illegal. |
| W5 | **Assumptions weaken properties.** `Prop ⇒ (ASSUME ⇒ Prop)`, and a mock adds the assumption "the mock matches the API." Checking assumptions is a separate job. | [2026-05-20][w-assume] | D | `technical-excellence` §2 CLAIM format: allow `assumes: <x>, checked by <test or tool>`. `test-quality` over-mocking row (mode 2): name the assumption each mock adds and the contract test that checks it. |
| W6 | **Decision tables, checked for completeness and soundness.** Rows = the product of the input domains; no input combination may appear twice with different outputs. | [2020-09-09][w-dt], LfP ch. 7 | C | `question-everything` §1.4 Precedence: when two or more sources disagree, the spec contains a decision table. The spec reviewer counts rows against the input space, and each row becomes one red test. |
| W7 | **Nondeterministic differential testing.** One divergent observation does not prove a difference. You need to see both `(x, y)` and `(y, x)`, and rates matter. | [2026-10-22][w-nyc] | D | `test-quality` parity section: for agent-made ports (polara-port, mentioned in report 06), compare the *set* of outcomes per input over N runs. Neither one mismatch nor one match settles anything. |
| W8 | **Write a NameOfProblem.md before a conceptually complex change.** Current state, problems, dead ends, proposed fix, what it does *not* solve. This prevents "you're the expert, I trust you." | [2026-02-18][w-socdd] | D | build-loop round 3 step-back and `references/dialogue.md`: when Fable or a reviewer proposes a redesign, the proposer writes this file and the owner or orchestrator agrees to it before any edit. |
| W9 | **Choose boring technology and innovative practices.** Practices are cheap to drop, and tools are cheaper to drop than "material" (anything production depends on). | [2026-03-24][w-boring] | D | `practice-watch`: give each adopted practice a trial date and an exit criterion. Keep `residual` and `paneweft` as tools; don't let shipped code depend on them. |
| W10 | **LLM vocabulary is measurable.** "Gate", "seam", "spine" and "lane" are rising in agent-written PRs. | [2026-09-16][w-spines] | C | `unslop`: add these words to the list of tells for copy. mstack's own skills use "gate" 31 times and "seam" 4 times. That is fine as defined jargon inside skills but a tell in PR bodies. |

Older foundations that still apply: strong and weak tests (`STRONG ⇒ WEAK`;
lift example tests into properties, remove mocks to strengthen)
([2023-06-14][w-strong]). The empirical software engineering talk: code
review has "a detectable positive impact," TDD results are mixed
([2019-04-28][w-wwk], grade B to C depending on the cited study). The
crossover interviews: traditional engineers' main lesson was upfront failure
analysis, "where is this thing gonna fail?" ([2021-01-22][w-crossover], grade
C, small interview set).

---

## 3. Barry O'Reilly (residuality theory)

### The method, beyond what residual already holds

Report 10 and residual's `research/nkp-residuality-theory.md` cover stressors,
attractors, residues, the force × component incidence matrix (NKP),
hyperliminal coupling, fusion and fission, and K/N criticality. New material
read for this report:

- **Train and test.** Derive the residual architecture from one set of
  stressors, then test it against a second set that was never used, and
  compare survivals with the naive design. "Residuality theory ultimately
  states that architectures should be trained, not designed" ([InfoQ,
  2025-10-07][infoq]; Ri defined in the [2020 paper][or2020]). He says this
  takes "a few hundred" stressors from many people, generated with PESTLE,
  the Business Model Canvas and Porter's five forces. Columns that no
  stressor touches mean components "haven't been stressed enough"
  ([Lebrero's notes on *Residues*, 2025-08-20][lebrero]).
- **Papers** (Procedia Computer Science): [2020][or2020] introduction;
  [2021][or2021] philosophy; [2022][or2022] Kauffman networks, random
  simulation and "the use of matrices for encouraging emergent component
  decomposition"; [2023][or2023] "Residuality and Representation", which
  argues for representing architecture as a stack of residues (processuality,
  criticality, difference) rather than static diagrams. **I found no
  O'Reilly paper on arXiv** (searched the arXiv API for "residuality",
  "residuality theory" and author O'Reilly). Others have started publishing
  on it: Fellah 2024 ([CCIS][fellah]) and an urban-design chapter (2026).
- **"Contagion analysis"** is O'Reilly's own term (corrected 2026-11-19). His
  Jfokus 2022 slides split residual analysis into "Stressor analysis (Random
  simulation)" and "Contagion analysis (Network analysis)"; the second uses
  component-by-component adjacency matrices and stressor-by-flow incidence
  matrices, "based on Kauffman networks" ([jfokus]).
  **[unverified]**
- **Talks, 2025 to 2026:** "Model Drift and Software Attractors" (DDD Europe
  2025, uploaded 2026-01-12): code freezes a model of the problem, the world
  drifts away from it, and fixing modularity early limits which attractors
  the system can reach. "LLM coding" is "injecting pure cholesterol" into an
  already clogged practice ([P_bWLYbjeLM][drift]). "Architecture as Science"
  (NDC Oslo 2025, uploaded 2026-02-04): case studies cannot generalize
  because each project is unique ("idiographic"), and he warns against
  scientism. He says his PhD experiments were "extremely expensive" but gives
  no numbers ([hUNuHQdMG2Y][science]). Also a Code BEAM Lite Stockholm 2026
  keynote ([z3LzgbYBOAU][codebeam]) and "Why loose coupling is just
  guesswork" (SAG 2025, [sJL_-Btrvz4][sag]).
- **On AI** ([Root Cause podcast, 2026-07-13, 1:07:04 to 1:20:40][rootcause]):
  he doubts code is cheaper ("if that had gotten cheaper, we would see
  margins rising… we're not seeing that"; he has heard "two to three percent
  productivity" "on the grapevine" [unverified]). On agents generating
  stressors: "it's determined by its training set… it can only look back in
  time and say what's the average result," so LLM architecture "is basically
  restating the case for patterns." "Show us scientifically." He expects that
  if AI ever does architecture, "it will be reduced to stress in the
  environment." The host and guest agree "the walk around the problem is the
  point." Zurich, 2026-11-10: "Agentic and harness engineering are an attempt
  to automate architecture" ([abstract][zurich]; no recording found). Grade D
  throughout.

### Residual: implemented vs missing

| O'Reilly concept | residual today | Gap |
|---|---|---|
| Stressors, attractors (± states), residues, incidence matrix | Yes. v4 CSVs; `residues.csv` is the sole coupling source | none |
| Row and column totals, hyperliminal pairs, fusion, fission | Yes. `src/nkp/matrix.rs` (`row_totals`, `col_totals`, `hyperliminal_pairs`, `fusion_candidates`, `fission_candidates`) | no warning for **untouched columns** |
| N, K, criticality | Yes. `src/nkp/criticality.rs`, but its 0.5 ≤ K/N ≤ 3.0 band is residual's own heuristic, not O'Reilly's (he cites Kauffman's K≈2) | label the band as residual's heuristic |
| Ri | Runnable by hand: architecture sets, a forked metadata branch to hide the test set, `matrix ri` for the arithmetic, `add iteration --ri-score` to record it | no test-set flag, no per-stressor survival record, `matrix ri` does not read the ledger or check S = 0; no Ri trend across iterations |
| Volume (hundreds of stressors) | Own ledger: 62 stressors, 34 purposes, 37 components, 21 attractors, 94 residues (`origin/residual/metadata`) | no breadth lenses (PESTLE, BMC, Porter) in `stressor-walk`; no record of which stressors came from people and which from the agent |
| FMEA, ATAM | Yes, as optional lenses | none |
| Contagion analysis | No | component adjacency matrices per the Jfokus 2022 slides; not implemented |
| Model drift | Iteration snapshots, tag scan | no view comparing the authored component model with the actual code modules |
| Walks by a human, agent as partner | Yes. Socratic skills, writes only on approval, isolated persona subagents | matches his AI position |

### Adoptable ideas

| # | Idea | Source, date | Grade | Suggested change |
|---|---|---|---|---|
| O1 | **Held-out stressors and a real Ri.** | [InfoQ 2025-10-07][infoq], [2020][or2020] | D (efficacy) | residual: add `holdout = true` on stressors, or a separate `test-stressors.csv`. `skill data` must leave them out of every walk's context. Add `residual eval --iteration n` to record survive/fail per held-out stressor for the naive and residual designs, compute Ri, and save it to `iterations/<n>.md`. A fresh subagent that never saw the walk judges survival, the same pattern as hold-out tests. |
| O2 | **Record where each stressor came from.** | [Root Cause 2026-07-13][rootcause] | D | residual: add `origin = human \| agent \| persona:<name>` per force. After a few iterations you can check his claim directly: do agent stressors ever lead to a *new* attractor? |
| O3 | **Breadth lenses and a target count.** | [Lebrero 2025-08-20][lebrero] | D | `stressor-walk` SKILL: offer PESTLE, BMC and Porter as prompts, show the count against "a few hundred", and have the human write first with the agent adding a labelled batch afterwards. |
| O4 | **Untouched-column warning.** | [Lebrero 2025-08-20][lebrero] | C (trivial, testable) | `residual matrix show` / `verify`: list components whose column total is 0 as "not stressed yet". One small function using `col_totals`. |
| O5 | **Model your agent practice as a residual system.** Harness engineering is architecture. | [Zurich 2026-11-10][zurich] | D | Run `residual init` on mstack. Index finding 4 (rules lost in compaction), usage-limit resets, model deprecation and reviewer drift are stressors with real evidence, and build-loop, vigil and qex are components. Hyperliminal pairs will show which skills one stressor breaks together. |
| O6 | **Model drift view.** | [DDD Europe 2025][drift] | D | paneweft view (Gîrba's move applied to residual): authored `components.csv` next to modules extracted from code, with separate provenance. Report 10 warned against relabeling coupling as calls, so keep the two relations distinct. |
| O7 | **No case-study evidence.** | [NDC Oslo 2025][science] | D | Already matches BRIEF's grading. `practice-watch`: rank a source's single-project success stories as D however vivid they are. |

### Pollable feeds for O'Reilly (verified 2026-11-18)

```toml
[[person]]
name = "Barry M. O'Reilly"
slug = "barry-oreilly"
why = "Creator of residuality theory (stressors, attractors, residues, NKP matrix); residual implements his method; sceptical of LLM-made architecture and frames harness engineering as automated architecture."
sources = [
  { kind = "page", url = "https://www.blacktulip.se/", notes = "Black Tulip Technology, his company. NOT barryoreilly.com (different person: Lean Enterprise/Unlearn)." },
  { kind = "feed", url = "https://www.blacktulip.se/news?format=rss", notes = "Squarespace RSS, 200 application/rss+xml; one item (2024-04-14, 'Little Book' released). Very low volume." },
  { kind = "feed", url = "https://www.blacktulip.se/new-blog?format=rss", notes = "'Notes' blog RSS, 200 but empty (lastBuildDate 2024-05-17). Cheap to keep." },
  { kind = "page", url = "https://leanpub.com/residuality", notes = "Residues book; Leanpub updates and bundles." },
  { kind = "page", url = "https://leanpub.com/architectsparadox", notes = "The Architect's Paradox, second book." },
  { kind = "youtube", url = "https://www.youtube.com/feeds/videos.xml?channel_id=UCTdw38Cw6jcm0atBPA39a0Q", notes = "NDC Conferences (verified 200). No personal channel exists; filter titles for 'O'Reilly'. 6 of his talks 2023-2026." },
  { kind = "youtube", url = "https://www.youtube.com/feeds/videos.xml?channel_id=UC3PGn-hQdbtRiqxZK9XBGqQ", notes = "DDD Europe (verified 200); 'Model Drift and Software Attractors' 2025. Filter titles." },
  { kind = "youtube", url = "https://www.youtube.com/feeds/videos.xml?channel_id=UCs_tLP3AiwYKwdUHpltJPuA", notes = "GOTO Conferences (verified 200); 'Residues' GOTO 2025. High volume; filter titles." },
  { kind = "page", url = "https://api.crossref.org/works?query.author=Barry+O%27Reilly&query.bibliographic=residuality&sort=published&order=desc&rows=10", notes = "JSON; new papers (Procedia CS 2020-2023 so far). No arXiv papers found." },
  { kind = "social", url = "https://www.linkedin.com/in/barry-o-reilly-b924657/", notes = "His main outlet (linked from podcast notes); not pollable without login." },
]
# Not his / not found: barryoreilly.com (other Barry O'Reilly), residualthoughts.substack.com (Joe Hovde),
# github.com/barryoreilly (0 repos, no name or bio; identity unconfirmed), no Substack found.
```

---

## Where your setup differs

- **technical-excellence §5** says make invalid states unrepresentable,
  without exception. Wayne's illegal/unwanted split (W4) is the missing
  caveat: some states must stay representable and need an exit rule instead.
- **test-quality §3 and §5** covers model-based state machines and empty-input
  vacuity. It lacks a reachability check for conditional properties (W1),
  multi-step and hyperproperty awareness (W2, [w-tla]), and set-based
  comparison for nondeterministic parity (W7). Its monoid and round-trip
  emphasis is the "algebraic laws" style that Wayne now argues is less
  accessible than system invariants for application code ([w-nyc]).
- **question-everything §1** asks about states, lifecycle and precedence in
  prose. Wayne gives each a checkable form: state classes (W4), refinement
  mappings for migrations (W3), decision tables for precedence (W6).
- **build-loop review** scores reviewer findings but does not separate a
  sourced finding from an LLM hypothesis (G1, G2). The §12 hand-off is
  written by the agent rather than generated from tool calls (G7).
- **paneweft** already shares gt4llm's core decisions: views computed beside
  the code, bounded text for agents, examples that publish views, provenance
  stamps. It adds immutable records where GT keeps live objects. gt4llm goes
  further on three points: per-view agent opt-in (G4), a reason on every
  stored object (G5), and views over agent sessions (G7, G8).
- **residual** follows O'Reilly closely on structure and is stricter about
  human control than he asks for. It misses the one empirical step he insists
  on, held-out stressors (O1). The criticality band it prints is its own
  heuristic.
- **Gîrba and O'Reilly agree from different sides** that an agent's output is
  a hypothesis about a model. Gîrba wants the model extracted from the system
  by tools; O'Reilly wants it stressed by the environment. Your stack has one
  tool for each: paneweft for extraction, residual for stress. Neither feeds
  the other yet (O6).

## Candidate actions

Ranked by expected value over cost.

1. **Add the reachability check to test-quality §3 and §5 (W1).** One
   paragraph plus a mutation hint. It catches a silent class of passing
   property tests that agents write often.
2. **Add the untouched-column warning to residual (O4).** About 20 lines with
   a test. It is the cheapest piece of O'Reilly's method that is still
   missing.
3. **Require refinement mappings for stored-data changes in
   question-everything §1.3 (W3).** It targets the largest late-finding
   family (index finding 3) with a mechanical check.
4. **Make structural findings cite a tool (G1, G2) in technical-excellence §7
   and the build-loop review brief.** Low cost, and it raises the bar on
   unsourced reviewer claims.
5. **Hold out stressors and record survivals in residual (O1, O2).** Medium
   cost: a schema field, a context filter, an `eval` command and an isolated
   judge. It is the only way to get evidence either way on residuality, and
   on his "LLM stressors are averages" claim.
6. **Add state classes and decision tables to question-everything (W4, W6).**
   Low cost. They make the designer interview checkable.
7. **Generate the build-loop hand-off from tool calls (G7).** Medium cost. It
   closes the false "done" gap from index finding 1.
8. **Add `audience` and `reason` fields to paneweft's v1 records (G4, G5).**
   Cheap now while the design is unbuilt, and expensive after records exist.
9. **Pilot a residual ledger for mstack itself (O5).** Half a day of walking.
   You already have measured stressors from reports 06 and 07.
10. **Add a paneweft transcript adapter (G8).** Higher cost. Do it only if the
    06/07 analyses need to recur; read feenk's `GtLACP*SessionStore` first.

## Sources

Gîrba / feenk
- [rw2]: https://medium.com/feenk/rewilding-software-engineering-083b86c81c43 Gîrba and Wardley, ch. 2 "How we make decisions", 2025-02-06
- [rw4]: https://medium.com/feenk/rewilding-software-engineering-a3601a066e50 ch. 4 "Flexing those thinking muscles", 2025-03-12
- [rw5]: https://medium.com/feenk/chapter-5-different-folks-for-different-strokes-70d24a750dff ch. 5, 2025-05-22
- [rw6]: https://medium.com/feenk/rewilding-software-engineering-ca3ad1e612d8 ch. 6 "Myths we tell ourselves", 2026-01-16
- [gt4llm]: https://github.com/feenkcom/gt4llm cloned 2026-11-18 at 0c846c7; created 2024-01-31, MIT; files cited by path above
- [smt]: https://scrummastertoolbox.libsyn.com/beyond-ai-code-assistants-how-moldable-development-answers-questions-ai-cant-tudor-girba podcast, 2025-10 [unverified date]
- Feed: https://medium.com/feed/feenk (verified 200)

Wayne
- [w-spines]: https://buttondown.com/hillelwayne/archive/the-llms-yearn-for-the-spines/ 2026-09-16
- [w-tla]: https://buttondown.com/hillelwayne/archive/what-tla-can-and-cant-check/ 2026-09-30
- [w-nyc]: https://buttondown.com/hillelwayne/archive/nyc-new-webinar-differential-testing/ 2026-10-22
- [w-vibing]: https://buttondown.com/hillelwayne/archive/llms-are-bad-at-vibing-specifications/ 2026-03-10
- [w-spec]: https://buttondown.com/hillelwayne/archive/a-sufficiently-comprehensive-spec-is-not/ 2026-04-15 (a spec is a set of implementations; refinement narrows it)
- [w-unwanted]: https://buttondown.com/hillelwayne/archive/illegal-vs-unwanted-states/ 2026-04-28
- [w-assume]: https://buttondown.com/hillelwayne/archive/assumptions-weaken-properties/ 2026-05-20
- [w-refine]: https://buttondown.com/hillelwayne/archive/refinement-without-specification/ 2026-01-20
- [w-possible]: https://buttondown.com/hillelwayne/archive/proving-whats-possible/ 2026-02-11
- [w-socdd]: https://buttondown.com/hillelwayne/archive/stream-of-consciousness-driven-development/ 2026-02-18
- [w-boring]: https://buttondown.com/hillelwayne/archive/choose-boring-technology-and-innovative-practices/ 2026-03-24
- [w-lfp-done]: https://buttondown.com/hillelwayne/archive/logic-for-programmers-is-done/ 2026-07-29
- [w-gamechanger]: https://buttondown.com/hillelwayne/archive/ai-is-a-gamechanger-for-tla-users/ 2025-06-05
- [w-strong]: https://buttondown.com/hillelwayne/archive/some-tests-are-stronger-than-others/ 2023-06-14
- [w-dt]: https://www.hillelwayne.com/post/decision-table-patterns/ 2020-09-09
- [w-wwk]: https://www.hillelwayne.com/talks/what-we-know-we-dont-know/ 2019-04-28
- [w-crossover]: https://www.hillelwayne.com/post/what-we-can-learn/ 2021-01-22
- [lfp]: https://logicforprogrammers.com (contents; © 2026)
- Feed: https://buttondown.com/hillelwayne/rss (verified 200, 30 items)

O'Reilly
- [or2020]: https://doi.org/10.1016/j.procs.2020.03.120 "An Introduction to Residuality Theory", Procedia CS 2020
- [or2021]: https://doi.org/10.1016/j.procs.2021.03.101 "The Philosophy of Residuality Theory", 2021
- [or2022]: https://doi.org/10.1016/j.procs.2022.03.084 "Residuality Theory, random simulation, and attractor networks", 2022
- [or2023]: https://doi.org/10.1016/j.procs.2023.09.015 "Residuality and Representation", 2023 (abstract via OpenAlex)
- [fellah]: https://doi.org/10.1007/978-3-031-75201-8_3 Fellah, CCIS, 2024-10-19
- [infoq]: https://www.infoq.com/news/2025/10/architectures-residuality-theory/ Ben Linders, 2025-10-07
- [lebrero]: https://danlebrero.com/2025/08/20/residues-time-uncertainty-change-software-architecture-summary/ 2025-08-20
- [jfokus]: https://www.jfokus.se/jfokus22-preso/Residuality-Theory.pdf O'Reilly, "An Introduction to Residuality Theory", Jfokus 2022 slides
- [rootcause]: https://www.youtube.com/watch?v=EGwcEQPX-lM Root Cause (Nune Isabekyan), 2026-07-13; captions read 1:07–1:21
- [science]: https://www.youtube.com/watch?v=hUNuHQdMG2Y "Architecture as Science", NDC Oslo 2025, uploaded 2026-02-04
- [drift]: https://www.youtube.com/watch?v=P_bWLYbjeLM "Model Drift and Software Attractors", DDD Europe 2025, uploaded 2026-01-12
- [codebeam]: https://www.youtube.com/watch?v=z3LzgbYBOAU Code BEAM Lite Stockholm 2026 keynote, uploaded 2026-05-25
- [sag]: https://www.youtube.com/watch?v=sJL_-Btrvz4 SAG 2025, uploaded 2026-05-11
- [zurich]: https://content.software-leader.com/barry-november2026 lecture listing, 2026-11-10
- https://www.blacktulip.se/ (company site)

Local
- `/home/mini/Documents/repos/residual-cli`: `README.md`, `ARCHITECTURE.md`, `src/nkp/{matrix,criticality,residual_index}.rs`, `src/skills/definitions/stressor_walk/SKILL.md`, ledger at `origin/residual/metadata` (line counts minus one header line, read 2026-11-18)
- `/home/mini/Documents/repos/mstack/skills/{question-everything,technical-excellence,test-quality,build-loop}/SKILL.md`
