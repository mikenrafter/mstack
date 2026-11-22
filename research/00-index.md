# Agentic practice research, November 2026

Start here. Written 2026-11-10 on nixed from [BRIEF.md](BRIEF.md), sections
01 to 09, the skills in `scout-modules/agent-integration/skills/` and the
installed `~/.claude/skills/build-loop/SKILL.md`. Where a section and
[09](09-cross-check.md) disagree, this file follows 09.

## 1. What this is

Nine sections compare how you work with coding agents against published
research, well-known practitioners and the classic software literature, and
measure your own Claude Code and Codex usage. The usage data comes from nixed
only: 504 Claude Code transcripts and 449 Codex sessions between 2026-10-17 and
2026-11-10, with edge and polara-port making up 98.8% of estimated Claude cost
([06](06-usage-claude.md), [07](07-usage-codex.md)). Void was offline, so its
transcripts, most of your Nix work and the newest diff-core and residual-cli
drafts are missing; sonic was not analyzed, and the diff-core and residual-cli
directories on nixed contain no files ([03](03-moldable-development.md),
[04](04-code-review-and-diff-core.md)). No result here measures your escaped
defects, production impact or learning ([09](09-cross-check.md)).

Grades follow the brief: **A** controlled study or benchmark, **B** large
observational data with n stated, **C** practitioner report with numbers,
**D** opinion or untested proposal.

## 2. Ten things to know

1. **Check what a test proves before buying more review.** Meta's
   mutation-guided generator killed 12% or 15% of targeted mutants against
   2.0% or 2.4% for a coverage filter. TDFlow resolved 94.3% of issues with
   valid human reproduction tests and 68.0% with tests it wrote itself. In
   your data, 06 found a checklist line answered "done" that was false and a
   tautological test; 07 counts 43 test-quality finding lines in scored Codex
   replies. A externally, B/C locally. [01](01-research-literature.md),
   [09](09-cross-check.md)
2. **Extra review can make code worse.** In one controlled study, Claude
   reviewing Codex raised accuracy from 71.6% to 89.7%; Codex reviewing Claude
   lowered it from 91.4% to 82.8%. Developers rejected 56.3% of 31,073
   CodeRabbit comment/feedback pairs. Your ledgers cannot show marginal yield
   yet: 10 of 35 findings in six build-loop ledgers are still open, and nothing
   isolates the round cap. A externally, C locally.
   [01](01-research-literature.md), [04](04-code-review-and-diff-core.md),
   [06](06-usage-claude.md)
3. **Late findings cluster in stored data and contracts.** Across 9 wake-pr
   changes, findings per round fell 81, 52, 19, 12. Stored data, migration and
   export was the largest family, 47 of 164 overall and 28 of 83 in round 2 or
   later. Codex replies repeat lifecycle and wiring concerns. Feedback aimed
   at known defect categories cut targeted warnings 11.1% in an A-grade
   intervention. C locally. [06](06-usage-claude.md),
   [07](07-usage-codex.md), [01](01-research-literature.md)
4. **Rules written as prose did not survive compaction.** None of 44
   compaction summaries carried the REREAD line. build-loop was re-read after
   2 of 44, and the keepalive chain was still dead 60 tool calls after 7 of
   44. A controlled study found the first summary dropped about a third of
   anticheating rules while benchmark scores held. B locally, A externally.
   [06](06-usage-claude.md), [01](01-research-literature.md)
5. **Keepalive ticks start turns carrying a quarter of Claude spend.** 5,178
   main-session ticks led to 10,656 API calls, 24.9% of the estimated $3,207,
   about $798. Main-session cache writes are almost all 1-hour: 20.36 M tokens
   against 0.036 M at 5 minutes. An hour of ticking costs $2.05; one full
   rebuild costs $2.70. B for the attribution. The modeled 22.6% saving from
   50-minute ticks is D, because nobody measured what ticks do for liveness and
   recovery. [06](06-usage-claude.md), [09](09-cross-check.md)
6. **Subagents are half the cost, and idle resumes are the expensive part.**
   562 subagent cache rebuilds after 5 to 60 minute gaps cost 11.0%. 297 of
   them, 6.4% of cost, were parent messages to an idle child. In Codex, 67 of
   68 native children re-read files their parent had read. B. Whether a fresh
   brief costs less than a resume is untested. [06](06-usage-claude.md),
   [07](07-usage-codex.md), [09](09-cross-check.md)
7. **Three prompt lines would address a quarter of Claude tool errors.**
   Sonnet 5.5 subagents called a tool named `bash` 59 times and Monitor
   without `description` 47 times, 9.0% of 1,175 errors. Blocked
   `sleep N; cat` waits add 182 more, 15.5%. Codex's largest nonzero cluster
   is missing paths or commands: 608 events, 26.3%. B.
   [06](06-usage-claude.md), [07](07-usage-codex.md)
8. **More instruction text cost more and did not raise success.** Generated
   AGENTS.md files added 20% and 23% to cost with no significant gain;
   human-written guidance moved resolution 2.4 points at p=0.21. The study
   tested repository context files. Your Nix host rules answer failures no
   benchmark covers; the growing workflow package is what needs measuring. A.
   [01](01-research-literature.md), [05](05-classic-engineering.md)
9. **A plausible explanation can raise confidence and lower accuracy.** In an
   86-programmer experiment, people judged correct assertions 74% accurately
   and incorrect ones 49%; poor explanations increased confidence and hurt
   judgment. Across 330,343 PRs, files shown later correlate with more later
   bug fixes. For diff-core, explanation fidelity and file order are things to
   test. A and B. [04](04-code-review-and-diff-core.md)
10. **Delegating unfamiliar work costs learning.** A randomized study of 52
    developers learning a new library found quiz scores of 50% with AI and 67%
    without, with no significant speed gain. METR's maintainers took 19% longer
    with early-2025 tools while believing they were faster. A.
    [01](01-research-literature.md), [02](02-practitioners.md)

## 3. Where you differ from the popular approach

| Your practice | Popular practice | Evidence for yours | Evidence for theirs | Verdict |
|---|---|---|---|---|
| 270 s keepalive tick whenever anything is in flight (manual-keepalive, build-loop §10) | Native completion notifications, no idle ticks (Claude Code docs, Cursor's file-backed context) | Keeps the turn open; you asked for it in 46 prompts, 6.4% [06]; vigil woke early on real events in this run (§5) | Tick turns carry 24.9% of cost; the 1-hour cache refreshes on every hit [06]; a tick's usefulness is unmeasured [09] | **Test** cadence. Drop the "keeps the cache" reason from the skill text |
| Sol fix rounds capped at 3, then one fresh Opus pass | Theo's council: three providers, repeat until satisfied. Claude Code team: one fresh-context reviewer plus CI | The cap bounds churn; findings fell 81, 52, 19, 12 by round [06] | Cross-model review moved accuracy +18.1 or −8.6 points by direction [01]; neither recipe has a comparison [02], [04] | **Keep** the cap. **Test** one review against the full loop at equal cost |
| Score bar 8/10, 9/10 for risky changes, as the stop gate | Scores as a summary; Bugbot tracks resolution | None for the numbers 8 and 9 [01], [02] | Model judges were perturbation-sensitive across 26 models [01] | **Adjust**: scores advisory; blocking needs a reproducible failure, affected caller or broken invariant |
| Tier-2 reviewer receives tier 1's score and ledger | Independent read before seeing earlier verdicts | Stops re-raising settled items | Biased metadata changed automated review outcomes [04]; D on both sides [02] | **Test**: verdict first, then reconcile with the ledger |
| Red tests for the whole scope before any green (rg-implement, build-loop §4) | Small red/green cycles (Willison, Beck, Superpowers) | Valid reproduction tests: 94.3% vs 68.0% [01] | No comparison of granularity; Beck keeps each transition testable [02] | **Adjust**: whole-scope tests for stable contracts, phase-local red where interfaces are still forming |
| 3 to 5 manual mutations on every change (test-quality §4) | Coverage filters (TestGen-LLM) | Mutation-guided tests: 12%/15% kills vs 2.0%/2.4% [01] | No evidence for a fixed count [01], [02] | **Keep** mutation checks, scale the count to risk |
| CLAIM ids and a WHY on every claim and test | Sparse comments (Tan's Comment Sicko); interface comments only (Ousterhout) | Ties comments to tests, which answers "comments rot" [05] | D on both sides [02] | **Adjust**: keep for protocol facts, durability order, external constraints, surprising fixtures |
| One working agent; heavy jobs through qex | 20 to 30 agents (Yegge); planner/worker swarms (Cursor) | Multi-agent effects ran +80.8% to −70.0% by task [01]; your ~8 GB hosts | Cursor's 1.38× kernel result does not isolate agent count [02] | **Keep** |
| Large skill package, reread after compaction | Short instructions; hard rules in hooks and permissions (Claude Code docs); evaluate skills (Tan, Ronacher) | Encodes failures specific to your hosts [02] | 0 of 44 summaries kept the REREAD line [06]; context files +20%/+23% cost [01] | **Adjust**: hard rules into hooks; small eval set |
| Implementer answers each checklist line | Reviewer verifies answers; verification maps (Tan) | Recurring families do recur: 28 of 83 late findings [06] | A false "done" reached round 3 [06] | **Adjust**: reviewer checks each answer |
| Implementer can see and edit all acceptance tests | Holdout tests outside the editable scope (Karpathy's autoresearch, StrongDM) | Independent fixtures already resist shared mistakes [02] | TDFlow found 7 test-hacking cases in 800 runs [01] | **Test** on the next parser or migration |
| Resume an idle child with SendMessage | Fresh bounded brief (Superpowers, Horthy) | The child keeps its context | 297 resumes cost 6.4% [06]; 67 of 68 Codex children re-read parent files [07] | **Test** |
| No owner walkthrough step | Willison's linear walkthroughs | None | 50% vs 67% learning result [01] | **Adjust**: add for unfamiliar, consequential changes |
| No explicit preserve/change decision for consumed outputs | Feathers' characterization tests; Hyrum's law | Goldens and parity tests cover part of it [09] | C/D practitioner evidence [05] | **Adjust**: label which existing behavior must survive |

Bracketed numbers are section files: [01](01-research-literature.md),
[02](02-practitioners.md), [04](04-code-review-and-diff-core.md),
[05](05-classic-engineering.md), [06](06-usage-claude.md),
[07](07-usage-codex.md), [09](09-cross-check.md).

## 4. Upgrade backlog

One list, deduplicated across sections, ranked by expected value over cost
inside each tier. Effects marked "modeled" are addressable buckets from 06 or
07; they overlap, do not add up and are not measured savings
([09](09-cross-check.md)). Confidence is 09's triangulation label where 09
rated the action. **BL** marks work that should go through build-loop when
built.

### (a) Tool injections and skill edits, a day or less

| # | Action | Target | Expected effect | Cost | Confidence | Sources |
|---|---|---|---|---|---|---|
| 1 | Subagent brief lines: the tool is `Bash`; Monitor needs `description`; no foreground wait past 270 s, use qex or a background command. The updated build-loop §8–9 has the qex rule but not the tool-name lines | skill: build-loop brief, rg-implement template | 106 errors, 9.0%; 182 blocked waits, 15.5%; modeled 4.1% of cost | minutes | High for demonstrated failures | 06, 09 |
| 2 | Reviewer brief: check every checklist answer; a false "done" is a blocker | skill: review.md, question-everything §3 | Aims at 28 of 83 late findings | minutes | High for a focused pilot | 06, 07, 01, 09 |
| 3 | Hand-off records the failing run of each regression test without its fix, and actual test counts | skill: test-quality, build-loop §6d, §12 | Puts the A-grade test-validity result into practice | minutes | High for checking test meaning | 01, 06, 09 |
| 4 | SessionStart(compact) hook: restart the tick, inject the REREAD line, load a constraints file kept apart from progress notes | hook (partly built) | 7 of 44 dead chains; 42 of 44 missing re-reads | hours | High for recovery checks | 06, 01, 09 |
| 5 | PreToolUse gates: AskUserQuestion only if your last prompt is under 2 minutes old; Agent blocked at the §9 cap | hook | 8 of 14 hand-labelled corrections, and one 30-minute stall | hours | High for honoring stated preferences | 06, 09 |
| 6 | vigil skill: glob inputs need `pattern`; a `change` watch ends after firing; a full disk breaks vigil | skill: vigil | First watch create failed on this | minutes | Observed this run | §5 |
| 7 | State what the tick is for (turn liveness, the TIMINGS clock) and remove the cache claim for 1-hour sessions | skill: manual-keepalive, build-loop §10 | Corrects a false reason; no saving alone | minutes | B for TTL facts | 06, 09 |
| 8 | On exit 127, suggest `nix shell nixpkgs#<pkg>` | hook | 25 errors, 2.1% | 1 hour | High for demonstrated failures | 06 |
| 9 | Scale manual mutation count to risk; keep revert-the-fix | skill: test-quality §4 | Less cost on small edits; no measured number | minutes | D for any quota | 01, 02 |
| 10 | Replace "No test or review needed" after a type fix with "test boundary conversions and serialization"; narrow mandatory CLAIM/WHY | skill: technical-excellence §2, §5 | None measured | minutes | Low | 02, 09 |
| 11 | Tier-2 reviewer writes a verdict before seeing the ledger | skill: review.md | None measured | minutes | D | 02, 04 |
| 12 | Blameless agent-failure log in `knowledge/`, one entry per class | habit | Feeds test-quality modes | minutes per entry | C | 05 |

### (b) Tooling projects

| # | Action | Target | Expected effect | Cost | Confidence | Sources |
|---|---|---|---|---|---|---|
| 13 | Keepalive pilot: 270 s tick, ~50-minute tick (`sleep 3000`, timeout ≥ 3,300,000 ms) and vigil keepalive, on 1-hour-cache main sessions. Measure delivery, liveness, recovery, cost | habit + tool | Modeled 22.6% gross, or 12.8% at one call per tick | 1–2 days of runs | Moderate for the pilot, low for the number | 06, 09 |
| 14 | Review ledger v2: base SHA, last-reviewed SHA, class, accepted/rejected/disputed/stale outcome, owner minutes; fed into each review and compaction hand-off. **BL** | tool: review-ledger | Makes yield measurable; 7 recurring Codex classes, 1 traced reversal | 1–2 days | High for measurement | 07, 04, 09 |
| 15 | Equal-cost comparison on a fixed task set: one review vs full loop, short workflow vs full package, 3 repeats per task, pinned models | habit + tool | This is the measurement the rest depends on | days | High for running it, low for predicting the winner | 01, 02, 04, 09 |
| 16 | Diff-core prerequisite: restore the void drafts and compare them with 03 and 04 | diff-core | Avoids designing against an obsolete interface | hours once void is up | High | 03, 04, 09 |
| 17 | Evidence contracts and bundle CLI: snapshot, entity, fact, evidence, claim, finding, with partial/stale/refused states (03's moldable-view spec). **BL** | diff-core | Shared input for every layer below | 1–2 weeks | Moderate for two fixtures | 03, 04 |
| 18 | Two hand-reviewed fixtures (a TS error-contract change, a Rust error conversion), then ~30 labelled changes and 12 seeded tasks | diff-core eval | Defines success before any UI | days | Moderate | 03, 04 |
| 19 | Story layer: ordered chapters, intent with provenance, a hunk-coverage list so nothing goes untold, tested with misleading explanations. **BL** | diff-core | Order effect B (330,343 PRs); explanation risk A (74%/49%) | weeks | Low to moderate | 04 |
| 20 | Visualizer: table renderer first, TS error/service and Rust crate/error views, then architecture and flow deltas. **BL** | diff-core | Comprehension took ~58% of developer time pre-agents (B); no view effect measured | weeks | Low for a platform | 03, 04 |
| 21 | Architecture questions (depth, information hiding, coupling, contracts), each tied to a concrete future change. **BL** | diff-core | None measured | weeks | Low | 04, 05 |
| 22 | Council layer: one primary review, escalate for persistence, trust boundaries, migrations, concurrency; compare with equal-cost single-model repeats; audit suppressed findings. **BL** | diff-core | None measured | weeks | Low for the council | 04 |
| 23 | Child hand-off index (paths, versions, checks done, decisions), then fresh-brief vs resume comparison. **BL** | tool | Modeled 6.4%; 4,229 shared child reads | days | Moderate | 06, 07, 09 |
| 24 | Versioned read: hash, range, changes since the last read, spill file over budget. **BL** | tool | Codex: 27.6% of text bytes in repeat reads; Claude: 1.3% of cost | days | Moderate to test, low for 8 KiB | 06, 07, 09 |
| 25 | Compact at ~300 k tokens on one workstream | habit: uw-agent | Modeled ≤10.1%; post-compaction reading ran 1.6× | 1-week trial | Unproven benefit | 06, 09 |
| 26 | Property tests plus independent fixtures for tea, vigil and apk-builder parsers and state transitions. **BL** | tool code | Examples plus properties caught 13 of 16 bugs against 11 | days | A, narrow sample | 01 |
| 27 | Holdout acceptance fixture and preserve/change labels for the next parser, migration or consumed output (apk-builder JSON, CLI formats, flake outputs) | skill + habit | None measured | hours per task | Moderate | 01, 02, 05, 09 |
| 28 | Residual-cli consumes the bundle CLI; scope after the drafts are back | residual | Unknown; 1 local Codex session | unknown | Unverified | 03, 04, 07 |
| 29 | Later experiments: periodic mutation tool on one stable module, a warnings/complexity limit that only tightens, Verus on one small Rust module | tool | He et al. saw ~30% more warnings and ~41% more complexity, estimator-sensitive | a day each | Low to D | 01, 05, 09 |

### (c) Habits and study

| # | Action | Target | Expected effect | Cost | Confidence | Sources |
|---|---|---|---|---|---|---|
| 30 | Ask for a walkthrough of unfamiliar, consequential changes | habit | Guards against the 50% vs 67% learning gap | 20–30 min each | External support only | 01, 02, 09 |
| 31 | For the next ten substantial tasks, log owner minutes, elapsed time, accepted defects per tier, reverts | habit | Baseline for #15 | minutes per task | High for measurement | 02 |
| 32 | Weekly mock interview with a human | habit | Observation halved scores for 48 students; practice effect is vendor data | 1 h/week | External only, D for dose | 08, 09 |
| 33 | Three one-page case studies, each with a "what went wrong" line and an AI-use paragraph | habit | Verifiable specifics survive AI polish | 1 day each | D | 08 |
| 34 | Three messages a week to people you have worked with; ask the edge and fauxx maintainers first (~400 of ~1,800 edge commits are yours) | habit | Weak ties A/B; referrals B, one firm | 1 h/week | External only | 08 |
| 35 | Brag document from git history; agents critique, you write | habit | AI help raised story similarity by 10.7% of the human-only range in one condition | 2 hours, then biweekly | A, short fiction | 08 |
| 36 | Classic reading, first four items: Parnas twice, Ousterhout, Naur | study | Path totals 40–45 hours; these carry most of it | ~8 hours | C/D | 05 |

## 5. Field notes from this run

These are observations from the research session itself, not from the
section files.

- The vigil CLI test this session: the watch woke early on real file events
  twice, 179 s and 59 s into a 270 s tick, where a manual sleep tick would
  have waited the full interval.
- A `change` watch ends after firing and must be re-created each time.
- The vigil SKILL.md omits that glob inputs need a `pattern` field; the
  first create failed on it.
- vigil fails hard with "No space left on device" when the disk is full.
- The vigil MCP server was not connected to that Claude Code session, so it
  was used through the CLI.
- The nixed root disk hit 100% during the run, with 24 GB in
  `edge.worktrees`.
- qex is referenced by the updated build-loop but was not installed on nixed
  during the run. Checked while writing this index: system generation 16,
  activated 2026-11-10 17:42 -0700, puts qex 0.33.0 on PATH, and the root
  disk stood at 88% with 20 GB free.
- 06 attributes ~25% of Claude spend (24.9%) to turns started by 270 s
  keepalive ticks, while main sessions run on the 1-hour cache. This bears
  directly on manual keepalive versus vigil. vigil wakes on the event instead
  of the next tick, which improves latency. Its keepalive still returns after
  at most 270 s when nothing happens, so on an idle wait it costs about one
  call per 270 s. That resembles 06's one-call-per-tick variant, modeled at
  12.8%, more than its 50-minute variant at 22.6%. This comparison is my
  inference and needs pilot #13.

## 6. Open decisions for you

1. **What must the tick do?** If it only keeps the cache warm, a ~50-minute
   tick fits 1-hour main sessions. If T3 needs a turn event every few minutes,
   or you use ticks as the TIMINGS clock, keep a short tick and cut its cost
   another way. Pilot #13 needs your answer on which of these matter.
2. **Manual tick or vigil as the default wait?** vigil gives early wakes and
   a written fire rule; it needs the MCP server connected and disk space.
3. **Which diff-core layer first?** I recommend contracts plus two fixtures
   (#17, #18) before the story layer. You may know from the void drafts that
   the story layer already exists.
4. **Scores: gate or summary?** Keeping 8/10 and 9/10 as gates is a choice
   with no evidence on either side.
5. **Mutation tooling.** Adopt cargo-mutants or Stryker on a schedule, or keep
   manual risk-scaled mutations only?
6. **Holdout tests.** For which projects are you willing to write acceptance
   tests the implementer never sees?
7. **Fresh child or resume.** Will you accept a bounded comparison run that
   may cost more in its first week?
8. **Compaction threshold.** Try ~300 k tokens on one workstream, given the
   rule-loss cost in finding 4?
9. **Career time budget.** 08's plan assumes 6–8 hours a week for 12 weeks.
   Is that the number, and does the weekly human mock interview fit it?

## 7. How to read the rest

| File | What it answers | Words |
|---|---|---|
| [BRIEF.md](BRIEF.md) | Writing rules and grades used throughout | 374 |
| [01-research-literature.md](01-research-literature.md) | What controlled studies say about tests, review, multi-agent setups, context and productivity | 4,455 |
| [02-practitioners.md](02-practitioners.md) | What Theo, Lauren Tan, Willison, Karpathy and others do, and how build-loop compares | 4,496 |
| [03-moldable-development.md](03-moldable-development.md) | What moldable development offers, plus a language-agnostic view spec with TS and Rust examples | 5,668 |
| [04-code-review-and-diff-core.md](04-code-review-and-diff-core.md) | What review products and studies show, and a four-layer diff-core rewrite | 4,435 |
| [05-classic-engineering.md](05-classic-engineering.md) | Which classic books and laws hold up, what agents change, and a reading path | 8,311 |
| [06-usage-claude.md](06-usage-claude.md) | Where Claude tokens and errors go on nixed | 4,342 |
| [07-usage-codex.md](07-usage-codex.md) | Where Codex context, waits and failures go on nixed | 2,904 |
| [08-career-communication.md](08-career-communication.md) | Workplace communication and the 2026 job search, with a 12-week plan | 5,744 |
| [09-cross-check.md](09-cross-check.md) | Corrections, contradictions, schema mismatches and triangulated confidence | 5,060 |
| [22-agent-cadence.md](22-agent-cadence.md) | Whether one model's output changes how another writes, and a way to measure it here | 496 |
| [23-legible-cores.md](23-legible-cores.md) | The core-edge-chaos ethos against the bitter lesson and harness-deletion writers, and tool state as HTML | 840 |

**For tooling work:** 09's triangulation table, then 06 sections 1 and 5,
07's candidate actions, 01's "Where your setup differs", 04's recommended
rewrite, then 03's spec. Read 02's practice matrix when editing build-loop.

**For professional growth:** 08's "Where you likely are" and its 12-week
plan, then 05's reading path starting with the first four items, then 02 for
how practitioners you follow actually work. Keep 09's corrections to 08 in
view: the interview and mock-practice evidence is weaker than 08's first
draft suggested.
