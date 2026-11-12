# Top findings

- **B:** Review presentation affects attention. A 2026 study of 330,343 pull requests associates later file positions with more subsequent bug fixes. This supports testing logical ordering, but does not prove a particular ordering prevents bugs. [Rahman et al., 2026-09-18](https://arxiv.org/abs/2609.22610)
- **C for capability, D for effectiveness:** Story-based review already has commercial precedents. Graphite launched Code Tours; CodeRabbit documents coherent change layers and dependency navigation. Your opportunity needs to extend beyond generated summaries. [Graphite, 2026-04-01](https://graphite.com/blog/code-tours); [CodeRabbit, undated, accessed 2026-11-10](https://docs.coderabbit.ai/change-stack)
- **A, vendor benchmark:** Greptile's widely quoted 82% catch rate measures 50 historical bugs and excludes false positives from scoring. It cannot establish low noise. [Greptile, measured 2025-07](https://www.greptile.com/benchmarks)
- **B:** In a feedback-bearing CodeRabbit cohort, 36.4% of 31,073 review/feedback pairs were accepted and 56.3% rejected. Rejection includes incorrectness, redundancy, scope, and intent mismatch. [Lin et al., 2026-07-23](https://arxiv.org/abs/2607.03316v2)
- **C for workflow, D for benefit:** Theo Browne's council is three independent provider delegates, scored reviews, synthesis, and repeated review after fixes. Its published skill supplies no measured defect or cost advantage. [Browne, undated, accessed 2026-11-10](https://raw.githubusercontent.com/t3dotgg/tstack/main/skills/council/SKILL.md)
- **A:** Better AI suggestions can still worsen review. Meta's safety trial initially increased reviewer time by over 5%; showing patches only to authors removed the regression. [Maddila et al., 2025-07-17](https://arxiv.org/abs/2507.13499)
- **A:** A story can increase confidence without improving judgment. In an experiment with 86 programmers, poor explanations impaired assessment while increasing confidence. [Kaufman et al., 2026-07-09](https://arxiv.org/abs/2607.08885)
- **D, proposed direction:** Build diff-core around revision-pinned change stories, inspectable evidence, architecture deltas, and a bounded review ledger. Current project compatibility remains **[unverified]** because both local repositories contain zero files and the newest drafts are on offline void.

## Scope and evidence

Researched on 2026-11-10. Grades follow [BRIEF.md, inspected 2026-11-10](BRIEF.md): A is a controlled study or benchmark with published method and data; B is substantial observational evidence with a stated sample; C is a concrete practitioner report or reproducible demonstration; D is opinion or an untested proposal. A vendor-run benchmark can qualify as A for its method while retaining selection bias and commercial conflicts. A capability demonstration does not establish productivity gains.

I inspected `/home/mini/Documents/repos/diff-core`, including `residual/research`, `docs`, and `eval`, and `/home/mini/Documents/repos/residual-cli`, including `research` and `docs`. Both contain directory skeletons but zero files, including their `.git` trees. Git reports that neither is a repository. No README, design, evaluation corpus, or implementation could be read. This is a stronger local limitation than merely missing the latest rewrite. The [brief](BRIEF.md) also identifies offline void as the location of newer drafts and transcripts. I cannot say which recommendations already exist there.

Available context consists of your requested direction, the [local skill collection](../../../scout-modules/agent-integration/skills/), and the developing [moldable-development companion](03-moldable-development.md), all inspected on 2026-11-10. The recommendations below specify proposed contracts, not changes to verified existing interfaces.

### Keep the denominators separate

Precision is the proportion of reported findings that are valid. Recall is the proportion of known issues found. A false-positive rate divides false alarms by genuinely clean cases; it is not automatically one minus precision. Acceptance and resolution measure developer behavior. A valid finding can be declined, while an accepted suggestion can be unnecessary or wrong. Silence can mean clean code, a miss, a skipped run, or missing context.

For your evaluation, record all of these separately. Also measure time spent checking findings and answering comprehension questions. A tool that posts fewer comments may preserve precision by missing more bugs. A tool that gets more suggestions applied may be generating attractive maintenance work. These are proposed measurement rules, not claims of an established universal metric.

## What the products demonstrate

### Graphite, stacking, Diamond, and Graphite Agent

Stacked pull requests express a feature as dependent, individually reviewable changes. Graphite combines that workflow with review, rebasing, and a stack-aware merge queue. Diamond launched on 2025-03-17; the launch page later recorded its incorporation into Graphite Agent on 2025-10-08. **C for documented workflow.** [Graphite, 2025-03-17, updated 2025-10-08](https://graphite.com/blog/series-b-diamond-launch)

Its 2024 report analyzes over five million PRs from more than 35,000 engineers. Reviewed PRs of at most 50 changed lines had a median publish-to-merge time of about 100 minutes; those over 50 had a median of 19 hours. **B.** [unverified in this cross-review: the primary PDF exceeds the web tool's size limit, so the exact latency medians and cohort filters remain provisional.] The methodology selects merged PRs and active contributors from synced organizations. Complexity, urgency, team process, and selection affect this association. It supplies no randomized estimate of stacking's benefit and no universal 50-line quality threshold. [Graphite, 2024-07-17](https://static.graphite.dev/Graphite_State_of_code_review_2024.pdf)

An Anthropic customer case reports 96% positive feedback, 67% implementation of suggestions, and feedback latency falling from an hour to 90 seconds. It mentions a 500-PR evaluation but supplies insufficient denominators for independently reproducing these production rates. **C for the numerical report.** Its Claude 3.5 Sonnet context is historical, not a current-model comparison. [Anthropic, undated, accessed 2026-11-10](https://claude.com/customers/graphite)

Code Tours now combines PR descriptions, conversations, stack context, and code into a guided narrative beside the diff. The launch promises visual artifacts and test validation as subsequent work; that announcement alone does not establish their delivery or comprehension benefit. **C for demonstrated presentation, D for benefit.** [Graphite, 2026-04-01](https://graphite.com/blog/code-tours)

### CodeRabbit

CodeRabbit documents PR summaries, walkthroughs, inline review, and generated interaction diagrams. Change Stack groups contracts, implementation, and tests into coherent layers with explicit dependencies and source ranges. Layers can span directories, and grouping may change on later review runs. These are close precedents for your desired story and visualizer layers. **C for documented mechanisms.** [Walkthroughs](https://docs.coderabbit.ai/pr-reviews/walkthroughs), [Change Stack](https://docs.coderabbit.ai/change-stack), both undated, accessed 2026-11-10.

The strongest independent reception evidence inspected here is the 2026 study of 31,073 review/feedback pairs from 10,191 PRs across 239 repositories. It reports 36.4% accepted, 7.3% discussed, and 56.3% rejected. **B.** These are feedback-bearing pairs, not a random audit of every comment. Intent mismatch and out-of-scope advice matter alongside technical errors. [Lin et al., 2026-07-23](https://arxiv.org/abs/2607.03316v2)

CodeRabbit's own 470-PR authorship study reports 10.83 issues per AI-coauthored PR versus 6.45 for its human group. **B, vendor observation.** Authorship is inferred and findings use its taxonomy. This measures differences in a sample of changes, not CodeRabbit's review precision or causal harm from AI. [CodeRabbit, 2025-12-17](https://www.coderabbit.ai/blog/state-of-ai-vs-human-code-generation-report)

### Greptile

Greptile reviews with repository context and publishes inspectable benchmark PRs. Its July 2025 test reconstructs 50 historical bugs across five repositories. Default hosted configurations score Greptile 82%, Bugbot 58%, Copilot 54%, CodeRabbit 44%, and Graphite 6%. A catch requires a line comment identifying faulty code and impact. **A, vendor-run benchmark.** False positives and unrelated comments do not affect that catch score; very large and single-file changes were excluded. This is useful evidence of historical detection differences, with no basis for ranking present-day precision. [Greptile, measured 2025-07](https://www.greptile.com/benchmarks)

Greptile's v3 announcement describes moving from a linear review pipeline to an agent that investigates context and can pursue findings. **C for architecture and examples.** Treat announced percentage improvements as internal comparisons until tested on your corpus. [Greptile, 2025-11-26](https://www.greptile.com/blog/greptile-v3-agentic-code-review)

### Cursor Bugbot

Bugbot investigates logic, security, and performance problems and supports repository rules. Cursor reports 40 experiments increasing resolution from 52% to over 70%, while findings per run increased from 0.4 to 0.7. **C**, because the January report does not expose a full trial dataset. [Cursor, 2026-01-15](https://prod.cursor.com/blog/building-bugbot)

An April comparison reports 78.13% resolution for Bugbot across 50,310 public PRs. An LLM judge checks whether comments were addressed by merge. **B, vendor telemetry**, not independently labeled correctness. Cursor subsequently reports that higher effort finds 35% more bugs at an unchanged 80% resolution rate, without a published sample. **C.** The transferable practice is measuring findings together with outcomes and tuning effort. [Cursor, 2026-04-08](https://prod.cursor.com/blog/bugbot-learning); [Cursor, 2026-05-11](https://prod.cursor.com/blog/may-2026-bugbot-changes)

### GitHub Copilot code review

GitHub describes an agentic reviewer that retrieves context, remembers repository information, clusters repeated problems, and offers batch fixes. By March 2026 it reports 60 million reviews, actionable feedback in 71% of reviews, and about 5.1 comments per review. **B for usage scale; C for effectiveness figures**, whose adjudication and cohort details are insufficiently exposed. The figures are not comment precision. GitHub also reports an 8.1% increase in positive feedback from its agentic architecture. That is an internal comparison, not evidence that 8.1% more defects were prevented. [GitHub, 2026-03-05](https://github.blog/ai-and-ml/github-copilot/60-million-copilot-code-reviews-and-counting/)

### Qodo

Qodo 2.0 uses specialized review agents and organizational context, including rules and prior decisions. **C for documented capability.** Its February launch reports 56.7% recall and 60.1% F1, the harmonic mean of precision and recall, in its recall-oriented configuration. [Qodo, 2026-02-04](https://www.qodo.ai/blog/introducing-qodo-2-0-agentic-code-review/)

The accompanying benchmark injects 580 issues into 100 genuine merged PRs and publishes reviews. **A, vendor-run benchmark.** It improves on single-bug evaluation by counting noise and multiple issues, but injected bugs and best-practice violations have a different distribution from naturally occurring regressions. Judge criteria and issue categories affect rankings. Use it as a test-design precedent; reproduce both functional and architecture categories locally before importing its leaderboard. [Qodo methodology, 2026-02-04](https://www.qodo.ai/blog/how-we-built-a-real-world-benchmark-for-ai-code-review/)

### Ellipsis and Sourcery

Ellipsis currently presents managed cloud agents with configurable prompts, environments, models, permissions, logs, and spending caps; review can run on each push. **C for documented capability.** I found no inspectable vendor precision, recall, or acceptance series in the primary material examined. Present-day review effectiveness is **[unverified]**. Its useful precedent is an explicit execution and budget contract. [Ellipsis, undated, accessed 2026-11-10](https://www.ellipsis.dev/)

Sourcery documents a summary, a file-by-file reviewer's guide, inline suggestions, and security/status handling. Re-review checks existing findings and new security results while preserving much of the initial explanation. **C.** No general accuracy series was verified in those docs. A practitioner comparison of eight tools on one PR reported one useful catch and one false alarm for Ellipsis, and one useful catch, two weak flags, and one false alarm for Sourcery. **C**, a tiny demonstration with no useful population-level precision estimate. Running tools on the same PR also created interaction effects. [Sourcery docs, undated, accessed 2026-11-10](https://docs.sourcery.ai/reviews/anatomy-of-a-review/); [Jones, 2025-05-10, subsequently updated](https://blog.bluedot.org/p/best-ai-code-review-tools-2025)

### Anthropic review and security review

Claude Code's hosted Code Review dispatches agents to investigate, verify, deduplicate, and rank findings. The March launch reports substantive comments on 54% of Anthropic PRs versus 16% previously, and fewer than 1% of findings marked incorrect. **C**, since sample sizes and response coverage are absent. Unmarked findings cannot establish 99% precision. March's average latency was about 20 minutes; October's general-availability announcement reports 6 to 10 minutes and repository effort levels. [Anthropic, 2026-03-09](https://claude.com/resources/articles/code-review); [Anthropic, 2026-10-15](https://claude.com/resources/articles/code-review-is-now-generally-available)

The separate `/security-review` command and GitHub Action target vulnerability classes and allow filtering. **C for capability; catch and false-positive rates unverified in this documentation.** Keep threat-model relevance and exploit preconditions in your finding contract. [Anthropic security-review documentation, undated, accessed 2026-11-10](https://support.anthropic.com/en/articles/11932705-automated-security-reviews-in-claude-code/)

## What Theo's council actually is

Browne's skill requests three read-only delegates from three providers at high effort, each giving a ten-point score. The orchestrator synthesizes findings and disagreements, fixes accepted issues, and repeats until satisfaction while limiting scope. **C for the reproducible procedure.** [Council skill, undated, accessed 2026-11-10](https://raw.githubusercontent.com/t3dotgg/tstack/main/skills/council/SKILL.md)

The procedure requires neither formal debate nor majority voting. It publishes no catch, noise, or cost comparison. Its advantage over equal-cost single-provider repeats remains **D/[unverified]**. Treat ten-point scores as subjective assessments.

For diff-core, compare one reviewer, repeated independent runs of that reviewer, and a mixed-provider panel at equal spending. Measure unique validated findings added by each member. Preserve disagreement: a rare correct finding may have only one supporter.

## Google and Meta: lessons beyond generating comments

Google's Critique study combines nine million reviewed changes, 12 interviews, and a 44-person survey. **B for telemetry.** It describes a mature lightweight review system whose purposes include maintainability and knowledge sharing. It predates today's agents and does not evaluate AI review. [Sadowski et al., 2018](https://research.google/pubs/modern-code-review-a-case-study-at-google/)

Google's AutoCommenter learns best-practice violations for C++, Java, Python, and Go, with findings tied to guideline URLs. It estimates about 40% comment resolution using 6,000 snapshot pairs and a manual check of 40 candidate resolutions. Only about 10% of review comments received explicit feedback. Suppression improved positive acceptance among feedback-bearing comments to over 80%. **B for deployment observations**, with limited manual validation. These older models are not current frontier agents. The useful result is the distinction between guideline grounding, user reaction, and actual code change. [Vijayvergiya et al., 2024-07-15](https://homes.cs.washington.edu/~rjust/publ/code_review_automation_aiware_2024.pdf)

Google also generates edits that resolve human review comments. Its 2024 paper reports that authors address 7.5% of all comments through ML suggestions. **C for that production rate**, since the abstract gives no observation count. Its earlier engineering account reports a discoverability change increasing suggestion previews from about 20% to 40%. These measure assistance uptake, not reviewer bug detection. [Frömmgen et al., 2024](https://research.google/pubs/resolving-code-review-comments-with-machine-learning/); [Google, 2023-05-23](https://research.google/blog/resolving-code-review-comments-with-ml/)

Meta separates waiting for reviewers from time actively inspecting code. Its 2022 account targets the slowest quarter of waiting times and keeps active viewing time as a guard against rubber stamps. Nudgebot reduced average waiting time by 7% and diffs waiting over three days by 12%. **C for the numerical engineering report**, which does not state experiment n. [Meta, 2022-11-16](https://engineering.fb.com/2022/11/16/culture/meta-code-review-time-improving/)

Related randomized reviewer-recommendation experiments cover 82,000 diffs, 28,000 authors, and 12,500 authors. Explicitly assigning a recommended individual reduced latency; workload balancing had mixed results. **A.** Review speed depends on ownership and routing as well as comprehension. [Rigby et al., revised 2025-05-05](https://arxiv.org/abs/2312.17169v2)

Meta documents reviewing and submitting stacks through Phabricator. Sapling's ReviewStack supplies an explicit stack-aware interface. **C for capability**, with no isolated causal stacking speedup established by those descriptions. [Meta, 2023-06-27](https://engineering.fb.com/2023/06/27/developer-tools/meta-developer-tools-open-source/); [Sapling, undated, accessed 2026-11-10](https://sapling-scm.com/docs/introduction/getting-started/)

MetaMateCR's 2025 work supplies a stronger warning. A 64,000-pair comment/patch benchmark yielded 68% exact-match patches, but the initial randomized deployment increased reviewer time by over 5%. Showing patches only to authors removed that regression; production actionable-to-applied rate reached 19.7%. **A for benchmark and trial.** Its task is fixing human comments, not discovering defects, and its GPT-4o baseline is historical. [Maddila et al., 2025-07-17](https://arxiv.org/abs/2507.13499)

A newer Meta study follows over 10,000 developers and 400,000 diffs with character-level AI provenance. AI-containing diffs have shorter review time and lower incident rates in naive comparisons, but AI appears in less central contexts, confounding both associations. **B.** This cautions against reading the CodeRabbit authorship comparison, or a favorable AI adoption report, as a universal causal result. Stratify your evaluations by change purpose, dependency centrality, size, and reviewer familiarity. [Mockus et al., 2026-10-05](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ESEM.2026.93)

Meta's Glean provides an architectural precedent: machine-readable diff sketches record added classes, removed methods, new calls, and other semantic changes, supporting navigation and analysis. **C for implementation.** Build trustworthy change facts before asking models to explain their significance. [Meta, 2024-12-19](https://engineering.fb.com/2024/12/19/developer-tools/glean-open-source-code-indexing/)

## Comprehension, tours, untangling, and trust

The foundational Microsoft change-understanding study surveys 180 engineers and identifies completeness, consistency, and risk to other components as difficult information needs. It also motivates decomposition by development purpose. **B.** Its enduring contribution is a question set for evaluation; it predates current models. [Tao et al., 2012-11](https://people.csail.mit.edu/hunkim/papers/tao-fse2012.pdf)

The 2025 comprehension study observes ten experienced reviewers performing 25 real reviews. Reviewers build context, inspect code, test, discuss, and opportunistically revise their mental model. **C under the brief's size-sensitive rubric**, a small qualitative study with shared materials. It supports multiple exploration routes, not a compulsory linear narrative. [Gonçalves et al., 2025-03-27](https://arxiv.org/abs/2503.21455)

File ordering has broader observational support. IntelliJ research finds more comments on earlier files. A 2026 survey of 1,355 developers reports only 10.2% prefer alphabetical order and 66% request customizable or dependency-aware ordering. **B.** A separate analysis covers 330,343 multi-file PRs and 756,814 file instances. Later positions correlate modestly with subsequent bug-fixing changes; comments are an attention proxy, not a complete account of inspection. Neither establishes that generated ordering causally improves correctness. [Bagirov et al., 2023-06-12](https://arxiv.org/abs/2306.06956); [Rahman et al., 2026-05-22](https://arxiv.org/abs/2609.04207); [Rahman et al., 2026-09-18](https://arxiv.org/abs/2609.22610)

Untangling means separating changes by purpose. EpiceaUntangler records fine-grained editing information and evaluates grouping against developer-labeled tasks. **A for its published benchmark**, with only two developers contributing the four-month labeled dataset. [Dias et al., 2015-02-24](https://arxiv.org/abs/1502.06757)

A controlled decomposition experiment with 28 participants found fewer wrongly reported issues and more improvement suggestions, but no statistically significant net review-time difference. **A**, with limited sample and tasks. Splitting changes also imposes navigation overhead. Offer logical grouping inside one review before assuming every chapter needs a separate PR. [di Biase et al., 2019-05-13](https://pmc.ncbi.nlm.nih.gov/articles/PMC7924728/)

CodeTour demonstrates replayable, ordered explanations attached to files and lines. Hannah Potter's Change Tours project proposes interleaving explanations and conceptually grouped changes. **C for the working CodeTour mechanism; D for the research proposal's benefits.** Neither inspected page establishes a controlled productivity gain. [CodeTour, undated, accessed 2026-11-10](https://marketplace.visualstudio.com/items?itemName=vsls-contrib.codetour); [Potter, undated, accessed 2026-11-10](https://hannahpotter.github.io/projects/change_tours.html)

Intent needs independent evidence. In the 86-programmer assertion experiment, participants assessed correct assertions with 74% accuracy and incorrect ones with 49%. Natural-language explanations offered no overall benefit; poor explanations increased confidence while hurting assessment. **A.** This is a constrained assertion task, not proof that all narrative review fails. It makes explanation fidelity a necessary test target. [Kaufman et al., 2026-07-09](https://arxiv.org/abs/2607.08885)

Prompt framing also affects automated review. A study revised in October tests six models and attacks review pipelines through biased metadata. **A for controlled experiments**, with model- and attack-specific outcomes. Treat an author's statement that a change is safe as an assertion to check. Preserve desired behavior without feeding the council an authoritative conclusion that implementation is correct. [Alexopoulos et al., 2026-10-27](https://arxiv.org/html/2603.18740v5)

## Recommended rewrite

The following design is **D, a testable proposal** informed by the evidence above. Its central object should be a versioned change explanation backed by inspectable facts. Each layer consumes the same snapshot and evidence references.

### A. Story layer

Represent a change as a short explanation of the user-visible problem, expected behavior, implementation decisions, and remaining uncertainty. Then offer ordered chapters. Each chapter names its purpose, dependencies, affected entities, behavioral examples, and exact source anchors. Preserve author-stated intent separately from model-inferred intent. Where they conflict, show the conflict. If intent is absent, say so.

For a queue rewrite, a useful order could be the request contract, lifecycle transitions, persistence/recovery, worker integration, and observable results. Tests should appear beside the claims they support. Let a reviewer switch to alphabetical, dependency, risk, or author-defined ordering. Keep an explicit list of ungrouped changes, ignored files, and unsupported artifacts so the story cannot quietly omit inconvenient work.

Group mechanical renames and generated changes, but make them expandable. Permit one file to participate in several chapters. Keep chapter identity stable across revisions when its purpose survives, and flag changed evidence as stale. Reading a chapter should record only that it was inspected; approval must be a separate decision.

Make intent extraction inspectable. Save which issue text, design decision, commit message, test, or author annotation supports each intent claim. A model's retrospective explanation must never overwrite an original decision. Ask reviewers whether the implementation matches the desired behavior, and whether that desired behavior still makes sense.

### B. Visualizer layer

Start with four views, selected by the question they answer:

| View | Human question | Evidence required |
|---|---|---|
| Architecture delta | Which responsibilities and boundaries moved? | Before/after modules, public contracts, dependency edges, source anchors |
| Dependency and flow delta | Which callers, services, stores, or error paths are newly connected? | Typed relation facts; static versus observed edges distinguished |
| Behavior comparison | What happens to the same scenario before and after? | Inputs, environment, outputs, events, failures, and revision pins |
| Claim and test map | Which promised behaviors have evidence, and which remain uncertain? | Claim IDs, test assertions, results, fixtures, mutation observations |

Render the changed neighborhood first. Expand unchanged context when asked. An added dependency edge must identify the extractor and its limits. Dynamic dispatch, runtime configuration, reflection, and unavailable services should produce visible uncertainty. A syntactic reference is not an observed call. A before/after screenshot demonstrates appearance under one scenario, not correctness of every behavior.

The companion [03-moldable-development.md, inspected 2026-11-10](03-moldable-development.md) proposes contextual view discovery and inspectable examples. Give each view a predicate over entity type and available capabilities, an evidence query, and a renderer. The agent receives the same structured answer as the human view. A queue transition can activate a lifecycle view; a schema change can activate migration examples. Avoid making every plugin parse Git or invent entity identity again.

Proposed shared records are `ChangeSnapshot`, `EntityRef`, `RelationDelta`, `StoryChapter`, `Claim`, `Evidence`, and `Finding`. Evidence stores source revision, producer/version, inputs, content digest, and completeness. It may reference a durable artifact or an expiring live inspection handle. This matches the companion's snapshot/live distinction without assuming its final implementation choices.

### C. Architecture-quality layer

Translate your architectural preferences into focused questions backed by deltas:

- Module depth: did a public interface gain concepts, parameters, or call-order requirements? Show what callers must now know and what complexity moved behind the boundary.
- Information hiding: did callers begin depending on storage layout, internal state, transport details, or sequencing? Identify the newly exposed decision and a concrete caller.
- Coupling: show added dependency cycles, reverse dependencies, fan-in/fan-out changes, cross-layer access, and shared mutable ownership. Explain the affected change scenario.
- Contracts: compare errors, invariants, units, exhaustiveness, persistence, and paired reader/writer assumptions. Link each concern to an actual claim or boundary.
- Test claims: distinguish an assertion from execution evidence, and execution evidence from an independent oracle. Show which behavior fails when the relevant fix is removed.

Use deterministic extractors for computable facts and model judgment for meaning. Do not turn interface/body line ratios or raw dependency counts into a universal architecture score. More coupling can be justified by a useful integration; a short wrapper can enforce an important policy. Every architecture concern should explain a future change that becomes harder, or an invariant that becomes vulnerable.

Begin with one language or domain that your restored projects actually need. Add Rust symbol relations or TypeScript call/contract information only after inspecting the available implementation. Architecture adapters should also admit Nix configuration, schemas, workflows, and documentation. This keeps the human question broader than changed source lines.

### D. Council and review layer

Run cheap structural checks first. Give independent reviewers a pinned snapshot, neutral statement of desired behavior, threat model, known constraints, and evidence access. Keep author explanations labeled by provenance. Reviewers return candidate claims with trigger, consequence, source anchors, evidence, uncertainty, and a suggested verification step.

Adjudication should search for counterevidence and execute a focused check when possible. Cluster by violated invariant and root cause, preserving all affected instances. Treat votes as supporting observations. One member's reproducible counterexample outweighs three unsupported approvals. Store verified, rejected, disputed, deferred, stale, and not-investigated outcomes explicitly.

Publish a small priority queue rather than every candidate. Keep architecture questions visible without mislabeling them as proven bugs. Route low-confidence candidates to an expandable investigation list. Do not silently erase them, because the filter itself can miss real findings. Record why each candidate was suppressed and audit samples of suppression.

Use one primary review by default, then escalate for uncertain findings or changes involving persistence, trust boundaries, migrations, or concurrency. Test a three-provider council against cheaper alternatives. Stop after a declared round or spending cap; unresolved disagreement becomes a human decision. A timeout or budget limit must never become approval.

## Where your setup differs

The local procedures below are **C for their inspectable workflow, D for effectiveness that has not been measured here**.

Your [build-loop skill and review reference, inspected 2026-11-10](../../../scout-modules/agent-integration/skills/build-loop/references/review.md) already define stable finding IDs, scored bars, incremental review, scope control, a ledger, and capped rounds. They use sequential tiers and an explicit stopping policy. Browne's council uses three providers in parallel and satisfaction-based repetition. Keep your bounded ledger while testing whether provider diversity earns its cost. Neither procedure currently supplies controlled evidence of its local benefit.

Your [question-everything skill, inspected 2026-11-10](../../../scout-modules/agent-integration/skills/question-everything/SKILL.md) moves clarification, lifecycle analysis, reuse, and spec review before implementation. That gives the story layer a source of original intent. Import those decisions with provenance instead of reconstructing all rationale from the final diff.

Your [technical-excellence skill, inspected 2026-11-10](../../../scout-modules/agent-integration/skills/technical-excellence/SKILL.md) explicitly asks for deep modules, information hiding, rich interfaces, claims, types, and threat models. These are richer criteria than a generic bug-comment list. Preserve them as inspectable questions and evidence links; their presence in a skill does not validate automatic scoring.

Your [test-quality skill, inspected 2026-11-10](../../../scout-modules/agent-integration/skills/test-quality/SKILL.md) emphasizes independent oracles, mutation checks, and tests that state why they exist. Use those distinctions in the claim map. A green test badge alone hides whether a test proves the story's claim.

Your [bot-triage reference, inspected 2026-11-10](../../../scout-modules/agent-integration/skills/build-loop/references/bots.md) separates bugs, edges, taste, wrong findings, and pre-existing issues. Reuse that outcome vocabulary and preserve reasons. **C as a concrete local procedure; D for unmeasured effectiveness.** Your reports can then measure disagreement and attention cost without equating every declined suggestion with a false positive.

## Candidate actions

Ranked by expected value relative to cost:

1. **Restore project context before choosing implementation boundaries.** High value, low cost once void is reachable. Compare its actual story, residual, adapter, and evaluation work against this report to avoid rebuilding existing pieces.
2. **Specify the snapshot, claim, evidence, and finding contracts.** High value, moderate cost. They let stories, custom views, and reviewers share provenance and stale-state handling.
3. **Build a local evaluation set before a broad UI.** High value, moderate cost. Start with about 30 representative changes, including clean changes, real regressions, architecture tradeoffs, and missing context; label independently.
4. **Prototype ordered chapters and one behavior comparison.** High value, moderate cost. Compare ordinary diffs against stories and stories plus evidence using counterbalanced comprehension tasks, defect detection, confidence, and active time.
5. **Add a verified-finding ledger and suppression audit.** High value, moderate cost. Measure valid findings per reviewer minute, severity-weighted recall, rejection reasons, and novel defects from an extra reviewer.
6. **Add architecture delta views, then evaluate the council.** Potentially high value, higher cost. Require architecture concerns to identify concrete consequences; compare mixed models with equal-cost single-model repeats.

Suggested success criteria are accurate answers about purpose, boundaries, and behavior without increased missed-defect rates or checking time. Report uncertainty and reviewer familiarity. Include deliberately misleading explanations to test resistance to confident stories. These are proposed experiments, **grade D**, until you run them.

## Sources

All web sources were accessed on 2026-11-10. Dates in the body are publication, revision, or measurement dates as specified. Undated documentation has an access date rather than an invented publication date. No outreach was performed.

- Product and benchmark sources: [Graphite report, 2024-07-17](https://static.graphite.dev/Graphite_State_of_code_review_2024.pdf), [Diamond launch, 2025-03-17](https://graphite.com/blog/series-b-diamond-launch), [Code Tours, 2026-04-01](https://graphite.com/blog/code-tours), [Graphite customer case, undated](https://claude.com/customers/graphite), [Greptile benchmark, 2025-07 measurements](https://www.greptile.com/benchmarks), [Greptile v3, 2025-11-26](https://www.greptile.com/blog/greptile-v3-agentic-code-review).
- Current presentation contracts: [CodeRabbit Change Stack](https://docs.coderabbit.ai/change-stack), [walkthroughs](https://docs.coderabbit.ai/pr-reviews/walkthroughs), [Sourcery review anatomy](https://docs.sourcery.ai/reviews/anatomy-of-a-review/), [Ellipsis](https://www.ellipsis.dev/), all undated.
- Production reports: [Cursor experiments, 2026-01-15](https://prod.cursor.com/blog/building-bugbot), [Cursor telemetry, 2026-04-08](https://prod.cursor.com/blog/bugbot-learning), [Cursor effort, 2026-05-11](https://prod.cursor.com/blog/may-2026-bugbot-changes), [GitHub, 2026-03-05](https://github.blog/ai-and-ml/github-copilot/60-million-copilot-code-reviews-and-counting/), [Qodo methodology, 2026-02-04](https://www.qodo.ai/blog/how-we-built-a-real-world-benchmark-for-ai-code-review/), [Anthropic launch, 2026-03-09](https://claude.com/resources/articles/code-review), [general availability, 2026-10-15](https://claude.com/resources/articles/code-review-is-now-generally-available).
- Review and trust studies: [Google Critique, 2018](https://research.google/pubs/modern-code-review-a-case-study-at-google/), [AutoCommenter, 2024-07-15](https://homes.cs.washington.edu/~rjust/publ/code_review_automation_aiware_2024.pdf), [MetaMateCR, 2025-07-17](https://arxiv.org/abs/2507.13499), [CodeRabbit reception, 2026-07-23](https://arxiv.org/abs/2607.03316v2), [assertion judgment, 2026-07-09](https://arxiv.org/abs/2607.08885), [bias injection, 2026-10-27](https://arxiv.org/html/2603.18740v5).
- Comprehension foundations: [review strategies, 2025-03-27](https://arxiv.org/abs/2503.21455), [file ordering, 2023-06-12](https://arxiv.org/abs/2306.06956), [ordering survey, 2026-05-22](https://arxiv.org/abs/2609.04207), [ordering outcomes, 2026-09-18](https://arxiv.org/abs/2609.22610), [fine-grained untangling, 2015-02-24](https://arxiv.org/abs/1502.06757), [decomposition experiment, 2019-05-13](https://pmc.ncbi.nlm.nih.gov/articles/PMC7924728/), [CodeTour, undated](https://marketplace.visualstudio.com/items?itemName=vsls-contrib.codetour).
