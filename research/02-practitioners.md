## Top findings

- **C/D:** Executable feedback is the broadest agreement: give agents tests, a running application, traces, or measurable acceptance criteria. Agreement supports trying this; it does not establish the best review ritual. [Cherny and team, 2026-10-15][claude-review]; [Tan, 2026-08-12][lauren-talk].
- **A:** More instructions do not reliably improve results. A September revision of the AGENTS.md benchmark found higher costs without significant overall success gains. Keep your incident-specific knowledge; evaluate the growing workflow package. [Gloaguen et al., 2026-09-29][agents-study].
- **D:** Theo's council uses three providers and continues until satisfaction. Your `build-loop` adds sequential tiers, bounded rounds, evidence-backed disagreement, and a review ledger. Neither exact recipe has controlled validation. [Theo, undated, inspected 2026-11-10][council].
- **C/D:** “Lauren from Cursor” almost certainly means Lauren Tan, whose workshop and public pstack establish the connection. The useful practices are verification maps, skill evaluations, structural constraints, and deliberate parallelism. [2026-08-12][lauren-talk]; [pstack, 2026-11-10 snapshot][pstack].
- **C/D:** Your `test-quality` is unusually explicit about false confidence: independent fixtures, mutations, skipped tests, and production wiring. Keep this substance. The fixed number of manual mutations needs local cost/benefit evidence. [Local skills, inspected 2026-11-10][local].
- **A/C:** There is evidence for measurable autonomous optimization, but little for scaling agent count by itself. Cursor's 235-kernel benchmark demonstrates an effective complete system; it does not isolate the contribution of multiple agents. [2026-04-14][kernels].
- **A:** Preserve your own understanding. A randomized study of 52 developers found quiz scores of 50% with AI versus 67% without; it studied learning a new library, not experienced agentic maintenance. Add selective walkthroughs to your workflow. [2026-01-29][learning].

## Scope and evidence

Research date: 2026-11-10. I read `AGENTS.md`, all 18 `SKILL.md` files under `scout-modules/agent-integration/skills/`, and the build-loop review reference. Those files describe your intended practice; they do not establish what every session actually does. Your void host is offline, so its transcripts and the newest diff-core/residual-cli work are unavailable. Claims about missing practices mean “missing from the inspected skills,” not “you never do this.” [Local snapshot, 2026-11-10][local]; [research brief][brief].

Grades follow the brief: A is a controlled study or benchmark with published method and data; B is large-scale observational evidence with sample size stated; C is a concrete practitioner report or reproducible demonstration; D is opinion or anecdote. A grade applies to the narrow result measured. A benchmark can earn A while the author's explanation of why it worked remains D. These sources do not constitute an independent consensus poll. Several practitioners sell agent products, and many repeat one another's techniques.

### What the data can establish

METR's randomized study assigned 246 tasks among 16 experienced maintainers. AI access increased completion time by 19%. It used early-2025 tools, primarily Cursor with Claude 3.5/3.7 Sonnet, which are obsolete relative to the models in your skills. This is **A** evidence against trusting perceived speed, not evidence that November 2026 agents slow you down. [2025-07-10][metr-2025].

METR's follow-up covered 57 developers, 143 repositories, and over 800 tasks. Recruitment, task selection, and overlapping agent work undermined interpretation. Estimates for returning and new participants suggested faster work, but both confidence intervals included no effect. Grade **A for the published randomized design; inconclusive for current productivity magnitude**, because the authors explicitly call the estimate unreliable. [2026-02-24][metr-2026].

Anthropic surveyed 132 engineers/researchers and conducted 53 interviews. Respondents reported a 50% productivity improvement and delegated tasks they could verify. This is **B observational evidence of reported practice**, with company selection and self-report biases. It cannot attribute gains to one workflow. The data were collected in August 2025 on Sonnet 4/Opus 4. [2025-12-02][anthropic-work].

## Practitioners and disagreements

### Theo Browne, t3.gg / Ping.gg

The primary evidence is tstack. `council` requests independent, read-only reviews from three providers at high effort, collects scores and disagreements, and repeats after accepted fixes until everyone is satisfied. It also tells the parent to resist scope growth. This is **D for effectiveness**, although the instructions are reproducible. [Undated, inspected 2026-11-10][council].

`sol-loop` is more restrained: three rounds by default, later reviews restricted to changes/open findings, a ledger, explicit rejection of weak findings, and extensions for sensitive work. `full-send` authorizes a complete PR lifecycle when invoked; `full-stop` retains a manual merge. Your workflow resembles this bounded loop more than the council. [Undated, inspected 2026-11-10][sol-loop]; [tstack README, same snapshot][tstack].

The 2026-11-03 video *Agents Sucked At UI (Until Today)* reportedly extends council scoring to screenshots and competitor comparisons. **[unverified]** Exact claims of roughly 18 hours, 30-plus rounds, and tool-description savings could not be checked against a primary transcript; the video page exposed no transcript. Treat these as leads, not measured support. The skill itself verifies the council method. Your capped review differs materially from this reported extended UI search. [Primary video][theo-video]; [dated secondary digest, 2026-11-03][theo-digest].

### Lauren Tan and pstack

Identification is high confidence: Maven names Lauren Tan as Cursor technical staff, and pstack's author identifies as poteto and describes work at Cursor. No second comparably supported “Lauren from Cursor” candidate emerged. The user’s intended clip remains unconfirmed. I do not infer a current employer from repost captions. [2026-08-12 workshop][lauren-talk]; [undated pstack, inspected 2026-11-10][pstack].

The workshop advocates reusable verification skills and feature maps, evaluating skills, and establishing trust before parallelizing. Grade **C for the demonstrated workflow; D for general superiority**. Its public chapter list does not substantiate viral PR-volume claims. Pstack adds domain modeling, competing prototypes, reproduced bugs, live UI/CLI checks, and a decision trail. Your setup shares the engineering discipline but lacks a general verification-map workflow. [2026-08-12][lauren-talk]; [poteto-mode, 2026-11-10 snapshot][poteto].

A real disagreement concerns comments. Comment Sicko preserves public API contracts, external constraints, legal headers, and certain tooling exceptions, while targeting narration and explanations of avoidable internal complexity. Your universal CLAIM markers and test WHY annotations retain more prose. Both positions are **D** prescriptions; neither source measures maintenance outcomes. [2026-11-10 snapshot][comments].

### Cursor's engineering team

Cursor's practical guidance recommends planning, focused rules, tests-first commits, and visual feedback. **D** guidance overlaps strongly with your red gate. [2026-01-09][cursor-practice].

Jediah Katz reports dynamically loading tools/context and keeping long outputs and history in files. An internal A/B test reduced total tokens by 46.9% on runs using MCP tools. Grade **C**, because the post omits sample size and sufficient experimental detail for A/B classification here. This supports the direction of `tea` and selective references, not that exact saving on your setup. [2026-01-06][dynamic].

Wilson Lin's long-running-agent experiments found flat coordination unreliable and introduced planners, workers, and periodic fresh starts. Grade **C**: concrete projects and failure descriptions, no controlled comparison. April's CUDA benchmark earns **A for benchmark results**: 235 problems, published solutions, 1.38× geometric-mean speedup against single-agent-optimized PyTorch baselines, with 149 problems improved. Language and implementation strategy also changed, so this does not isolate agent-count effects. Your small concurrency cap suits a different resource envelope. [2026-01-14][scaling]; [2026-04-14][kernels].

### Simon Willison

Willison recommends observed red/green test-driven development, running existing tests first, agent-driven manual testing, and explanations that help the owner understand generated code. His walkthrough example executes commands to quote real source into a reviewable document. Grade **C** for this reproducible demonstration, **D** for the unmeasured TDD recommendation. Your test rules are more detailed; your skills give less attention to teaching you after implementation. Unlike Yegge's willingness to leave code unread, Willison explicitly develops ways to recover understanding. [TDD, 2026-02-23][simon-tdd]; [walkthrough, undated 2026 chapter, inspected 2026-11-10][walkthrough].

### Andrej Karpathy

The clearest inspectable practice is `autoresearch`: freeze the evaluator, restrict changes to the training file, establish a baseline, run five-minute experiments, record outcomes, and keep improvements. Grade **C** for a reproducible system, not A evidence that indefinite loops improve general software engineering. The instructions explicitly keep evaluation code outside the editable scope. This is stronger separation than having an implementer inspect all acceptance tests. [Undated repository, inspected 2026-11-10][autoresearch].

Karpathy's January post recommends success criteria, tests-first work, a simple reference algorithm before optimization, and active inspection for wrong assumptions and excess abstraction. It cautions against swarm hype. Grade **D** advice; the reported shift from 20% to 80% agent coding is **C self-reported usage**, not measured productivity. February's post becomes more optimistic about managing parallel agents, while retaining oversight and verifiable task boundaries. This change matters when comparing claims made a month apart. Both primary post texts were retrieved through a text mirror because X blocked direct access. [2026-01-26][karpathy-post], [mirror][karpathy-mirror]; [2026-02-25][karpathy-feb], [mirror][karpathy-feb-mirror].

### Boris Cherny and the Claude Code team

Cherny's verification-first advice is confirmed in the team's engineering account: give the agent runnable checks and have a fresh-context subagent review the diff. The article attributes a “two to three times” quality estimate to Cherny; grade **D**, since no measurement procedure accompanies that estimate. [2026-10-15][claude-review].

The team reports merged PRs more than doubling from June to September while the proportion reverted fell over 40%. Grade **C**, not B under this brief: denominators are absent. The process combines automated review, CI, security checks, targeted human attention, and rollback. It supports measuring total human effort and downstream failures. It does not demonstrate your specific Opus/Sonnet/Sol allocation or universal second review tier. [2026-10-15][claude-review].

Current documentation distinguishes probabilistic instructions from enforced hooks, permissions, and checks. It recommends brief project instructions and skills for procedures. **D** guidance supports moving non-negotiable rules out of prose. Its current defaults also caution against preserving elaborate prompting after models absorb the behavior. [Undated living documentation, inspected 2026-11-10][claude-practice].

### Geoffrey Huntley

Ralph repeatedly starts a coding loop from written specifications and a durable plan, normally choosing one task per iteration. Huntley stresses tuning the environment after observed failures and conserving primary context. The article favors a single main loop while also using subordinate agents for context-heavy work, so “Ralph means no subagents” would misrepresent it. Grade **C** for the public construction/demo; **D** for broad outsourcing and eventual-success claims. Your practice adds explicit phase verification and bounded review rather than relying on persistence alone. [2025-07-14, living post inspected 2026-11-10][ralph].

### Steve Yegge

Gas Town advocates persistent task state, specialized worker roles, and orchestration of 20–30 agents. Yegge reports 75,000 lines and 2,000 commits in 17 days, while openly describing duplicated fixes, lost work, high cost, and unread implementation. Grade **C for reported production volume; D for net productivity or reliability**. Your controlled single-writer approach rejects that loss tolerance. Lines and commits do not show that accepting lost work is economical for diff-core or Nix deployment. [2026-01-01][gastown].

### Mitchell Hashimoto

Hashimoto learned agents by reproducing personal manual commits without showing the solution, then delegated bounded “slam dunks,” used end-of-day research, and encoded failures in instructions or tools. He deliberately worked on other manual tasks and controlled notifications. Grade **C** for a repeatable learning exercise; **D** for unmeasured efficiency. Your incident-derived checklists match this closely. His measured adoption sequence also challenges treating constant agent activity or elaborate orchestration as a goal independent of useful output. [2026-02-05][mitchell].

### Armin Ronacher

Ronacher advocates fast, debuggable command-line tools, minimal tool output, and ordinary scripts before adding protocol machinery. The June recommendation favored Sonnet and simple Go workflows; those model preferences are dated. Grade **C** for the linked working demonstration, **D** for broad language/model rankings. [2025-06-12][armin].

July's account describes unsuccessful slash commands, hooks, and shared-write delegation. Ronacher evaluates automation by repeating a task three times and checking whether the result is acceptable. **C** for that concrete evaluation procedure; no published comparative results. This directly challenges workflow growth without evaluation, while supporting your `tea`, small concurrency limits, and scripts. Later model improvements could change which restrictions remain useful. [2025-07-30][armin-fail].

### Kent Beck

Beck's *Genie Wants to Leap* describes agents hitting refactoring complexity cliffs and recommends old/new implementations coexisting while each transition remains testable. Grade **D**, a practitioner case without comparative data. This supports your phase gates and independent parity checks. It also conflicts with a blanket demand to delete compatibility states immediately. For diff-core's rewrite, judge temporary duplication by the migration it enables. The accessible source was Beck's own summary; the full newsletter was unavailable. [2025-05-12][beck].

### Harper Reed

Reed's workflow separates idea honing, specification, a small-step prompt plan, and execution with a durable checklist. It includes both TDD and non-TDD planning prompts; representing Reed as universally tests-first would be wrong. The reported planning overhead is about 15 minutes. Grade **C** for concrete prompts and timing, **D** for overall productivity. Your `question-everything` is more explicit about data lifecycle and invariants, and less dependent on an available owner answering one question at a time. This February workflow used now-old o1/o3/R1 and Claude-era tooling. [2025-02-16][harper].

### Dex Horthy

Horthy recommends research, plan, implement, with reviewed intermediate documents and deliberate compaction. Subagents collect information without filling the parent's context. A BAML case reports draft work on two features in about seven hours against maintainers' estimates of several days each. Grade **C**; estimated counterfactual effort and draft PRs do not prove equal production outcomes. Treat the suggested 40–60% context utilization as a workload-specific heuristic. [2025-08-29][dex].

The 12-factor guide emphasizes owning prompts, context, control flow, resumable state, and focused agents. Grade **D** design guidance. Your phase pointers and `uw-agent` align; your requirement to reread workflow files after compaction is more prescriptive. Horthy concentrates human review at research and planning, whereas your workflow adds extensive code-review gates. [2025 guide, living repository inspected 2026-11-10][factors].

### Peter Steinberger

Steinberger favors conversational planning, CLI-first verification, direct iteration, and selective escalation to a stronger model through Oracle. December's account reports a five-hour VibeTunnel conversion and work across three to eight projects. Grade **C**, with linked artifacts but no controlled productivity comparison. He questions elaborate orchestration and rarely reads all generated code. His solo, direct-to-main workflow differs from your commit gates and isolated parallel writers. His report explicitly warns that the approach does not transfer unchanged to larger teams. [2025-12-28][peter].

### swyx / Latent Space, and additional practitioners

Swyx's April discussion treats skills as useful packaging, emphasizes evaluation and observability, and describes an exploratory period where testing capability can justify high token spend. Grade **D**, an informed thesis without a measured workflow comparison. Separate this from guests' claims. Ryan Lopopolo's interview reports a million-line, agent-written product and sub-minute feedback goals; grade **C**, not evidence that swyx personally validated a universal zero-human-review process. [2026-04-23][swyx]; [Lopopolo interview, 2026-04-07][latent-harness].

Jesse Vincent's Superpowers provides a close comparison: fresh implementers with distilled briefs, per-task reviews, durable ledgers, and final review. Its TDD skill mandates observed failures and small cycles. Grade **C for inspectable procedure, D for superiority**. Justin McCarthy's StrongDM account instead pursues unattended generation evaluated through end-to-end holdout scenarios. Grade **C for its concrete system report, D for the general “no human code review” rule**. These approaches disagree about process while sharing verification as the prerequisite. [Undated Superpowers, inspected 2026-11-10][superpowers]; [2026-02-06][strongdm]; [undated principles, same inspection date][holdout].

### The disagreements that affect your choices

There is no single agent-count consensus. Huntley's July 2025 main loop, Yegge's January 2026 orchestration, and Karpathy's changing January/February advice offer different operating points. Their reported outcomes do not control for task difficulty or cost. [2025-07-14][ralph]; [2026-01-01][gastown]; [2026-02-25][karpathy-feb].

Planning also differs. Reed writes a detailed initial plan; Steinberger expects product requirements to evolve through use. Beck preserves testable intermediate versions during migration; pstack favors removing legacy APIs once callers migrate. These can coexist when you distinguish a stable acceptance contract from exploratory product design. That distinction is an inference, not a measured result. [2025-02-16][harper]; [2025-12-28][peter]; [2025-05-12][beck]; [poteto-mode, 2026-11-10 snapshot][poteto].

## Where your setup differs

All local comparisons below refer to the [18-skill snapshot inspected 2026-11-10][local]. Verdicts are recommendations, not measured facts about your outcomes.

### Keep the verification discipline; add a check of the workflow itself

Your `test-quality` identifies failures that a green check cannot expose: shared-oracle mistakes, unexecuted fixtures, vacuous conditions, and tests of helpers that production never calls. Its reported audits of roughly 14,000 test blocks are **C self-reports with unverified underlying records** here. That is useful local motivation, especially for protocol and persistence work. Preserve independent fixtures, real call-path checks, and targeted mutations. Adjust “3–5 mutations every time” to risk and affected behavior; none of the reviewed evidence establishes that universal count.

Your missing feedback loop is evaluation of these skills. `build-loop` records findings and scores but does not compare its outcomes with a cheaper workflow. Tan explicitly teaches skill evaluations, and Ronacher repeats tasks before trusting automation. Their procedures provide **C** support for trying local evaluations. The **A** AGENTS.md study, 138 CTXbench tasks plus 300 SWE-bench Lite tasks, found no significant overall accuracy benefit and higher costs on older Sonnet-4.5/GPT-5.2-era systems. It tested repository context files, not your skills or Nix safety rules. Keep nonstandard operational knowledge; compare a short workflow against the full package on representative tasks. [2026-08-12][lauren-talk]; [2025-07-30][armin-fail]; [2026-09-29][agents-study].

### Keep bounded independent review; adjust the score gate

Your three-round fix cap, final fresh reviewer, stable finding IDs, and evidence-backed rejections are sensible controls on review churn. Theo's `sol-loop` shares many of them; council's satisfaction loop is less bounded. All are **D for comparative effectiveness**. No inspected study establishes an 8/10 default, 9/10 sensitive-work bar, or fixed model-family pairing. Keep scores as summaries and require reproducible failures, affected callers, or explicit invariant violations for blocking decisions. [2026-11-10 source snapshots][sol-loop]; [council][council].

There is a subtler weakness: the build-loop final reviewer receives the earlier score and ledger. Fresh conversation context does not make the judgment blind. An adjustment worth testing is an initial verdict before revealing prior scores, then reconciliation against the ledger. This is a proposed experiment, **D**, not a demonstrated improvement. Reserve the expensive second tier for changes where it finds distinct, consequential defects. Rotate model assignments through actual task results instead of treating the current Opus/Sonnet/Sol split as an established optimum.

### Adjust all-red batching and exhaustive interviews

`rg-implement` and `build-loop` write tests for the entire scope before implementation; `question-everything` seeks detailed states, lifecycle paths, precedence, and reuse. Reed supports explicit planning, while Beck and Superpowers favor small verifiable transitions. No direct comparison proves which granularity wins. **C/D** evidence favors keeping whole-scope acceptance examples for stable contracts while allowing phase-local red tests as interfaces emerge. That reduces the risk of precommitting a rewrite to speculative APIs. [2025-02-16][harper]; [2025-05-12][beck]; [2026-11-10 snapshot][superpowers-tdd].

Keep the interview for product decisions. Use short executable probes for factual uncertainties such as performance or parser behavior. Your safe-default log lets work continue when you are away, but should preserve the difference between a reversible implementation choice and a choice that changes intended semantics. Tan's prototype-before-preference-question rule is a useful **D** alternative. [2026-11-10 snapshot][poteto].

### Keep low concurrency; add risk-based exceptions

Your one-working-agent default, isolated parallel worktrees, and `low-ram-hosts` limits are defensible for your machines. Yegge's throughput counts and Cursor's large experiments do not establish a benefit on an approximately 8GB host. Keep the cap for writers and heavy tests. Permit bounded read-only exploration or independent remote tasks when useful and authorized. Measure completion time, memory pressure, and integration effort before increasing concurrency. **C/D**, with an **A benchmark that does not establish transfer**. [2026-01-01][gastown]; [2026-04-14][kernels].

### Keep typed contracts; narrow mandatory prose

`technical-excellence` favors invalid states excluded by types, explicit errors, and deep modules. Tan's domain-modeling rules strongly overlap. Your stable CLAIM IDs and mandatory test WHY comments are stricter than the surveyed alternatives. Keep them for protocol facts, durability ordering, external constraints, and surprising fixtures. Drop mechanical annotations that repeat an expressive test name or an enforced type. Comment Sicko is too aggressive as a universal replacement; your universal annotation rule is also unmeasured. **D on both sides.** [2026-11-10 snapshots][poteto]; [comments][comments].

Also adjust “No test or review needed” after a type-level fix. The type declaration may encode the wrong domain, and boundary conversion, serialization, or unchecked escapes still require verification. This is a logical limitation of the rule, not a claim that runtime checks should replace your type-first design.

### Add real-artifact verification, holdouts, and owner comprehension

Your Nix procedures require actual affected-output evaluation and builds, which already exceeds generic test advice. The general skills lack an equivalent project-specific feature map for T3 Code, diff-core, or residual-cli. Add a short repeatable CLI/UI workflow with captured output, failure-path checks, and the exact artifact version exercised. Tan and Willison supply **C** demonstrations of this direction. [2026-08-12][lauren-talk]; [2026 walkthrough snapshot][walkthrough].

Your independent fixtures already resist shared mistakes, but there is no general holdout acceptance mechanism outside the implementer's editable tests. Use it selectively for parsers, migrations, and races. Karpathy and StrongDM provide **C/D** support, not proof that every task needs hidden tests. [2026-11-10 snapshots][autoresearch]; [holdout][holdout].

Add an owner walkthrough for unfamiliar or consequential changes. The 52-developer learning experiment is **A** evidence of a risk from delegating unfamiliar work, while its explanation-seeking subgroups are observational and small. It supports a learning safeguard, not a claim that walkthroughs eliminate skill loss. [2026-01-29][learning].

### Keep observability; test keepalive assumptions and enforce true boundaries

`tea`, `vigil`, `uw-agent`, early reports, and `manual-keepalive` address recoverability and long jobs. Cursor's file-backed context supports this direction, **C**. Keep the tools and streamed build logs. **[unverified]** The claim that periodic sleep/echo events preserve useful provider prompt caching needs measurements of cache hits, billed input, and session recovery on the actual harness. Keep ticks only where they solve an observed transport problem; replace the ritual when native task notifications suffice. [2026-01-06][dynamic].

Your `no-unsolicited-upstream`, lock-update approval, and untrusted-upload instructions preserve meaningful owner boundaries. Keep them. Add enforceable permission controls where available; prose cannot guarantee compliance. Current Claude documentation explicitly makes this distinction, **D design guidance**. `plain-writing` and `unslop` need no heavy engineering loop, but their expanding stylistic bans should remain preferences that yield to a document's actual needs. [Documentation snapshot, 2026-11-10][claude-practice].

The narrower operational skills already fit the tool-first approach: `github-stars` reads a known local snapshot, `tailcook` treats uploads as untrusted, and `iterating-with-nix`, `nix-test-rebuild-override`, and `scout-module-locks` define concrete producer/consumer and deployment steps. Keep these task-specific procedures. Their value depends on your environment and failure history; a generic council or factory workflow supplies no contrary evidence. This is **D for measured benefit**, with explicit operational mechanisms you can exercise. [Local snapshot, 2026-11-10][local].

### Practice matrix

Dates and source links refer to the practitioner sections above. Grades describe evidence for the practice, not its popularity.

| Practice | Who advocates | Evidence grade | Your skill doing it, or none | Verdict |
|---|---|---|---|---|
| Executable acceptance feedback | Cherny, Tan, Willison, Hashimoto | C/D; B reported adoption | `build-loop`, Nix skills | Keep; add project feature maps |
| Observed red before green | Willison, Cursor, Vincent | C/D | `rg-implement`, `test-quality` | Keep; allow smaller cycles |
| All tests before any implementation | Your workflow; partial Cursor overlap | D for exact batching | `rg-implement`, `build-loop` | Adjust for evolving interfaces |
| Independent fixtures and mutations | Your audit rules; related evaluator separation in Karpathy | C local report, D fixed quota | `test-quality` | Keep substance; adjust quota |
| Three-provider council | Theo | D | `build-loop` uses two families/two tiers | Keep bounded alternative; evaluate |
| Numeric approval threshold | Theo; your variant | D | `build-loop` | Advisory score; evidence gates |
| Skill/workflow evaluation | Tan, Ronacher | C; A context-file caution | none general | Add small task set |
| Focused context and durable state | Horthy, Huntley, Katz, Vincent | C/D | `uw-agent`, `tea`, phase pointers | Keep; load references selectively |
| High-concurrency workers | Yegge, Cursor | C; A narrow kernel benchmark | capped in `build-loop` | Keep resource-aware cap |
| Type-first domain design | Tan | D | `technical-excellence` | Keep; test boundaries |
| Sparse explanatory comments | Tan | D | stricter CLAIM/WHY prose | Adjust annotation scope |
| Tests withheld from implementer | Karpathy, StrongDM | C/D | none general | Add for high-risk contracts |
| Owner learning/walkthroughs | Willison, Hashimoto | C; A learning-risk study | none explicit | Add selectively |
| Enforced external-action limits | Claude Code docs | D | approval skills mainly prose | Keep policy; enforce where possible |
| Periodic cache-preserving tick | Your setup | D; cache effect unverified | `manual-keepalive` | Measure; remove redundant ticks |
| Production rollback and incident feedback | Claude Code team | C | partial Nix deployment practice | Add explicit outcome tracking |

## Candidate actions

1. **High value / low cost:** Record human minutes, elapsed time, accepted defects by review tier, and rework/reverts for the next ten substantial tasks. This gives your review process an outcome measure beyond scores.
2. **High value / low cost:** Create one project-local verification map for the active diff-core or residual-cli checkout when void returns. It connects feature claims to commands and real artifacts.
3. **High value / medium cost:** Compare the full build-loop with a short plan/test/fresh-review workflow on a small fixed task set, with repeated runs and versioned models. Keep the gates that improve outcomes per unit cost.
4. **High value / low cost:** Make scores advisory, narrow mandatory CLAIM/WHY annotations, and permit phase-local red tests. These changes preserve evidence while reducing process overhead.
5. **Medium value / low cost:** Request a walkthrough on unfamiliar changes and add an independently maintained acceptance fixture for the next consequential parser or migration task.
6. **Medium value / low cost:** Measure whether keepalive ticks change cache use or recovery before retaining them as a general rule. Prefer event-driven continuation when the harness provides it.

## Sources

Publication dates appear in the text. “Snapshot” means undated living material inspected on 2026-11-10, not a claimed publication date. Primary pages were read unless an access limitation is stated. No private transcripts, complete workshop recording, or Theo video transcript was available. Local audit counts and unavailable video-transcript claims remain explicitly unverified. Karpathy post texts were recovered through FxTwitter, with original and mirror links supplied.

- Local authority: [brief][brief], [all 18 skill files][local], and [review-loop reference][local-review], 2026-11-10 snapshot.
- Theo: [tstack][tstack], [council][council], [sol-loop][sol-loop], snapshots; [video][theo-video] and [secondary digest][theo-digest], 2026-11-03.
- Tan: [Maven workshop][lauren-talk], 2026-08-12; [pstack][pstack], [poteto-mode][poteto], [Comment Sicko][comments], snapshots.
- Cursor: [practical guidance][cursor-practice], 2026-01-09; [dynamic context][dynamic], 2026-01-06; [scaling agents][scaling], 2026-01-14; [CUDA benchmark][kernels], 2026-04-14.
- Willison: [red/green TDD][simon-tdd], 2026-02-23; [linear walkthrough][walkthrough], 2026 living chapter.
- Karpathy: [autoresearch instructions][autoresearch], snapshot; [January post][karpathy-post], 2026-01-26; [February post][karpathy-feb], 2026-02-25. Both post texts retrieved through linked mirrors after X access failed.
- Anthropic: [workplace study][anthropic-work], 2025-12-02; [learning experiment][learning], 2026-01-29; [Claude Code review][claude-review], 2026-10-15; [current guidance][claude-practice], snapshot.
- [Huntley][ralph], 2025-07-14; [Yegge][gastown], 2026-01-01; [Hashimoto][mitchell], 2026-02-05.
- Ronacher: [recommendations][armin], 2025-06-12; [failed approaches][armin-fail], 2025-07-30.
- [Beck's own summary][beck], 2025-05-12; [Reed][harper], 2025-02-16, retrieved directly after web-tool failures.
- Horthy: [context engineering][dex], 2025-08-29; [12-factor agents][factors], 2025-origin living repository.
- [Steinberger][peter], 2025-12-28; [swyx discussion][swyx], 2026-04-23; [Lopopolo interview][latent-harness], 2026-04-07.
- [Vincent workflow][superpowers] and [TDD][superpowers-tdd], snapshots; [McCarthy][strongdm], 2026-02-06; [holdout principles][holdout], snapshot.
- METR: [randomized trial][metr-2025], 2025-07-10; [follow-up][metr-2026], 2026-02-24. [AGENTS.md benchmark v3][agents-study], 2026-09-29.

[brief]: ./BRIEF.md
[local]: ../../../scout-modules/agent-integration/skills/
[local-review]: ../../../scout-modules/agent-integration/skills/build-loop/references/review.md
[tstack]: https://github.com/t3dotgg/tstack
[council]: https://github.com/t3dotgg/tstack/blob/main/skills/council/SKILL.md
[sol-loop]: https://github.com/t3dotgg/tstack/blob/main/skills/sol-loop/SKILL.md
[theo-video]: https://www.youtube.com/watch?v=xq0eB8vxeqk
[theo-digest]: https://www.alcreon.com/podcast-digest/agents-sucked-at-ui-until-today
[lauren-talk]: https://maven.com/p/e23d9c/how-cursor-turned-ai-agents-into-better-engineers
[pstack]: https://github.com/cursor/plugins/tree/main/pstack
[poteto]: https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/SKILL.md
[comments]: https://github.com/cursor/plugins/blob/main/pstack/agents/comment-sicko.md
[cursor-practice]: https://cursor.com/blog/agent-best-practices
[dynamic]: https://cursor.com/blog/dynamic-context-discovery
[scaling]: https://cursor.com/blog/scaling-agents
[kernels]: https://cursor.com/blog/multi-agent-kernels
[simon-tdd]: https://simonwillison.net/guides/agentic-engineering-patterns/red-green-tdd/
[walkthrough]: https://simonwillison.net/guides/agentic-engineering-patterns/linear-walkthroughs/
[autoresearch]: https://github.com/karpathy/autoresearch/blob/master/program.md
[karpathy-post]: https://x.com/karpathy/status/2015883857489522876
[karpathy-mirror]: https://api.fxtwitter.com/status/2015883857489522876
[karpathy-feb]: https://x.com/karpathy/status/2026731645169185220
[karpathy-feb-mirror]: https://api.fxtwitter.com/status/2026731645169185220
[claude-review]: https://claude.dev/blog/solving-code-review-at-anthropic/
[claude-practice]: https://code.claude.com/docs/en/best-practices
[anthropic-work]: https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic
[learning]: https://www.anthropic.com/research/AI-assistance-coding-skills
[ralph]: https://ghuntley.com/ralph/
[gastown]: https://yegge.ai/essays/welcome-to-gas-town/
[mitchell]: https://mitchellh.com/writing/my-ai-adoption-journey
[armin]: https://lucumr.pocoo.org/2025/6/12/agentic-coding/
[armin-fail]: https://lucumr.pocoo.org/2025/7/30/things-that-didnt-work/
[beck]: https://kentbeck.com/summaries/genie-wants-to-leap/
[harper]: https://harper.blog/2025/02/16/my-llm-codegen-workflow-atm/
[dex]: https://www.humanlayer.dev/blog/advanced-context-engineering
[factors]: https://github.com/humanlayer/12-factor-agents
[peter]: https://steipete.me/posts/2025/shipping-at-inference-speed
[swyx]: https://latent.space/p/unsupervised-learning-2026/
[latent-harness]: https://latent.space/p/harness-eng/
[superpowers]: https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/SKILL.md
[superpowers-tdd]: https://github.com/obra/superpowers/blob/main/skills/test-driven-development/SKILL.md
[strongdm]: https://factory.strongdm.ai/
[holdout]: https://factory.strongdm.ai/principles
[metr-2025]: https://arxiv.org/abs/2507.09089
[metr-2026]: https://metr.org/blog/2026-02-24-uplift-update/
[agents-study]: https://arxiv.org/html/2602.11988v3
