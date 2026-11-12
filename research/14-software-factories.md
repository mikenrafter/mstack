# Software factories, review gates, and workflow benchmarks

Research date and access date: 2026-11-11. Research only. No code, commits, pushes, registrations, or outreach.

## Evidence and limits

- Both videos now have local transcripts from the owner's Readwise Reader, pulled on 2026-11-11. The review video is [How to fix the code review bottleneck][review-transcript]. The benchmark video is [How to make a software factory that's not expensive][bench-transcript]. Both name Warp as author. Their metadata has `Source: null`; the original video links remain below.
- Positions such as "~50% through" locate passages by transcript text length. They are approximate, not playback timestamps. Auto-captions join words and may misstate names. The screen diagrams and numerical plots were not independently inspected.
- "Verified" means the cited source says this. Vendor performance numbers remain vendor reports. "Inference" identifies my interpretation or proposed transfer. Model names below follow the captions, not an independent check of model availability. Living sources without a confirmed publication date are marked undated.

## 1. State machine

### The video's flow and gates

The presenter calls the factory a state machine described to an agent through configured stages. The agent decides when to transition, including when triage is complete. This is agent-directed routing within a declared workflow. The table reconstructs the spoken flow; its labels are not a transcription of the on-screen configuration. [Review transcript, ~25% and ~51% through][review-transcript].

| State or decision | Runner | Transition and gate | Transcript evidence |
|---|---|---|---|
| New task / intake | Foreman receives the request and coordinates work. | Enter the relevant stages; an existing PR comment can re-enter at implementation. | [Review, ~25% to ~27% and ~56% through][review-transcript] |
| Triage | Builder in the shown configuration. | Investigate, then let the agent decide whether to hand off. | [Review, ~51% and ~56% through][review-transcript] |
| Spec, when needed | Builder drafts; human approves. | Larger workflows get numbered testable behaviors, edge cases, and a testing strategy. Human review precedes implementation. A bug fix may skip this. | [Review, ~54% to ~56% through][review-transcript] |
| Implement and verify | Builder implements. The implementation agent owns app testing in their setup. | Run the app, exercise the relevant flow, and retain screenshots or recordings for the human. | [Review, ~29% to ~35%, ~41% to ~48%, and ~56% through][review-transcript] |
| Review needed? | Implementing agent uses judgment. | Gate expensive review by PR risk. This also applies after a human requests changes. No numeric trigger is specified. | [Review, ~27% to ~28% through][review-transcript] |
| Internal review and revision | Reviewer in a separate context; implementer fixes findings. | Approved ends review. Needs-changes returns to implementation and another review. Requires-human-input exits early to a PR with the unresolved decision called out. | [Review, ~13% to ~20% through][review-transcript] |
| Risk assessment before PR | Implementation or review agent, placement still experimental. | Assess and mitigate risk before opening; include the resulting report in the PR description. | [Review, ~60% to ~70% through][review-transcript] |
| PR / human handoff | Human reviews evidence, risk, and unresolved decisions. | Human decides whether to merge. Feedback returns to implementation, optional review, then human handoff again. | [Review, ~3% to ~6% and ~25% to ~28% through][review-transcript] |

Stages and workers are separate. The shown configuration has two configured agents and five stages. Triage, spec, and implement bind to the same builder context. The foreman has a separate context so it can answer while work continues. The earlier reviewer is a separately invoked context within the implementation flow. The captions do not enumerate all five configured stage labels. Do not infer five fresh sessions from five stages. [Review transcript, ~56% to ~58% through][review-transcript].

### Review rounds, severity, and visibility

The reviewer returns a structured verdict plus line/block findings, suggestions, and notes. The three outcomes are approved, needs changes, and requires human input. The last gives the reviewer an escape when a product or safety decision exceeds its context. Findings pass internally as JSON and remain in conversation traces. Routine agent-to-agent findings stay off GitHub to reduce noise for humans. [Review transcript, ~14% to ~19% through][review-transcript].

The suggested cap is three to five turns, tuned for cost and latency. Findings have nit, important, or critical severity. Nits may be filtered out before they reach implementation to avoid repeated needless revisions. The speaker recommends a capable reasoning model to reduce over-flagging. He does not specify a critical/important blocking matrix or the exact disposition after the cap. [Review transcript, ~19% to ~22% through][review-transcript].

This is filtering, not a promised "hide until later" queue. No rule says to reveal nits after higher-severity findings pass. Nor does the video require fixing only nits resolved by one central change. Those are W23's additions. All ordinary review chatter is hidden from the PR, but retained in the trace. [Review transcript, ~17% to ~21% through][review-transcript]. [Owner policy][plan].

Warp reports roughly 3x cost for its review-loop experiment, with higher correctness. Later Q&A identifies the tested reviewer as Opus 5.5 with enforced multiple rounds. That comparison does not isolate every choice of model, prompt, or round cap. Risk-based review gating is an experiment to control that cost. The merge-risk report guides mitigation and human attention; the video specifies no risk-score-based automatic merge or mandatory high-risk rejection. [Review transcript, ~27%, ~75% to ~77%, and ~78% to ~80% through][review-transcript].

### Agreement and disagreement with the cited sources

- The lifecycle docs agree on optional planning, human spec approval, revisions, and human merge authority. They add explicit Complete and Cancelled states, which the spoken walkthrough does not detail. Their Building stage opens a PR before Reviewing. The video emphasizes internal review before opening or presenting the PR. [Lifecycle, accessed 2026-11-11][lifecycle]. [Review transcript, ~22% to ~27% and ~54% through][review-transcript].
- The review article agrees with repeated bounded rounds and an experimental gate for expensive review. [Article, 2026-11-05; accessed 2026-11-11][review-blog]. [Review transcript, ~19% to ~28% through][review-transcript].
- The default foreman prompt disagrees on review repetition. It orders one review per work item, one implementer revision for clear findings, and no second review dispatch. It also dispatches review as a separate stage after the implementer reports a PR. The video's builder configuration and internal review loop are a different arrangement. [Default foreman, accessed 2026-11-11][foreman]. [Review transcript, ~13% to ~28% and ~56% to ~58% through][review-transcript].
- The marketing sequence, triage → spec → implement → verify → ship → monitor, describes a broader lifecycle. It should not supply missing labels for the video's five-stage configuration. [Factory page, undated; accessed 2026-11-11][factories]. [Review transcript, ~56% to ~58% through][review-transcript].

Inference: retain the owner's explicit bounded, scored review policy. Treat Warp's video, article, and default prompt as distinct policies. [Local review policy][owner-review].

## 2. Warp offering, deployment, and cost

### Verified facts

The current product is Warp Factories. Oz names remain in worker, CLI, and SDK interfaces. The platform connects repositories, agents, runners, integrations, skills, and measurement through factory definitions. It is still labeled Early Access. [Factories overview, undated; accessed 2026-11-11][overview]. [Self-hosting, undated; accessed 2026-11-11][selfhost].

| Part | Open-source and deployment status | Evidence |
|---|---|---|
| Warp Terminal client and Warp server | The public Warp repository is issues-only. Its README describes client open-sourcing as planned and the server as closed source. No complete open-source factory control plane was identified. | [Warp README, undated; accessed 2026-11-11][warp-readme] |
| `oz-agent-worker` | Source is public under MIT. It connects to Warp and runs assigned tasks using Docker, Kubernetes, Direct, or an external command. | [Worker README, undated; accessed 2026-11-11][worker]. [License, undated; accessed 2026-11-11][worker-license] |
| Common skills | Public MIT instructions, including merge-risk and the spec skills. They can be adapted outside Warp. | [License, undated; accessed 2026-11-11][common-license]. [Spec article, 2026-06-11; accessed 2026-11-11][spec-blog] |
| Factory examples and default prompts | Public MIT examples. These are definitions and prompts, not the hosted service implementation. | [Examples, undated; accessed 2026-11-11][examples]. [License, undated; accessed 2026-11-11][examples-license] |
| Python API SDK | Public Apache-2.0 client library. It calls Warp's REST API. | [SDK, undated; accessed 2026-11-11][sdk]. [License, undated; accessed 2026-11-11][sdk-license] |
| Control plane | Warp hosts orchestration. Self-hosted workers still require outbound access to Warp. This is managed self-hosting, not an offline factory. | [Self-hosting, undated; accessed 2026-11-11][selfhost] |
| Run data | Checkout and execution can stay on customer infrastructure. Transcripts and artifacts use Warp storage by default. Separate bucket configuration can move selected run-data categories. Warp retains control-plane metadata, operational logs, and billing records. | [Self-hosting, undated; accessed 2026-11-11][selfhost] |
| Linux and ARM | Docker workers support `linux/amd64` and `linux/arm64`, with glibc task images. Factory runner definitions accept Linux `aarch64`. Terminal downloads also include Linux ARM64. | [Docker worker, undated; accessed 2026-11-11][docker-worker]. [Definition syntax, undated; accessed 2026-11-11][definition]. [Downloads, undated; accessed 2026-11-11][pricing] |

The public worker references separate `warp-agent`, coding-agent, and computer-use sidecar images. Its MIT license does not establish those images' source availability or license. This research did not verify an open-source license for the first-party Warp agent runtime or Oz CLI. [Worker source, undated; accessed 2026-11-11][worker]. [Worker license, undated; accessed 2026-11-11][worker-license].

The Direct backend runs tasks on the host in per-task workspaces. It shares the host OS and kernel. Docker and Kubernetes provide alternative execution boundaries. [Direct backend, undated; accessed 2026-11-11][direct].

Inference: ARM support is documented, but this research did not install Warp on NixOS/Asahi or test nixed's page size, desktop stack, or worker dependencies. "Linux ARM64 supported" is not a verified nixed deployment result. [Docker worker, undated; accessed 2026-11-11][docker-worker]. [nixed configuration, undated; accessed 2026-11-11][nixed].

### Published factory prices

| Plan | Base price | Usage and relevant limits | Evidence |
|---|---|---|---|
| Pay as you go | $0/month | Usage at 20% above API rates; Warp-hosted definition and runners. | [Pricing, undated; accessed 2026-11-11][pricing] |
| Build | $20/month | Usage at API rates; Claude Code and Codex; GitHub-hosted factory definition. | [Pricing, undated; accessed 2026-11-11][pricing] |
| Business | $50/user/month | Adds governance, custom inference endpoints, and customer API keys. | [Pricing, undated; accessed 2026-11-11][pricing] |
| Enterprise | Custom | Adds self-hosted workers, compute, transcripts, and conversation data. | [Pricing, undated; accessed 2026-11-11][pricing] |

Factory usage is billed separately for inference, compute, and agent usage. The $20 base is not a total monthly factory budget. The separate Terminal plans should not be substituted for factory pricing. [Pricing, undated; accessed 2026-11-11][pricing].

### T3 Code interoperability

- Verified: Factory MCP is a hosted remote server at `https://app.warp.dev/api/v1/mcp/factory`. It supports dispatch, task search, conversation reads, local continuation, and returning work. It has no read-only or per-factory scopes. [Factory MCP, undated; accessed 2026-11-11][factory-mcp].
- Verified: local pickup returns context and suggested worktree commands. Pickup does not lock or pause factory work. The factory cannot see local uncommitted or unpushed changes. Returning work requires a pushed branch or PR reference. [Factory MCP, undated; accessed 2026-11-11][factory-mcp].
- Inference: T3 could remain the owner's local session and worktree controller. A connected coding session could send selected tasks to Warp and retrieve results through MCP. This is an integration path, not a tested native T3 connector. [Factory MCP, undated; accessed 2026-11-11][factory-mcp]. [Local T3 configuration, undated; accessed 2026-11-11][owner-t3].
- Inference: assign one system responsibility for each active branch. Concurrent Warp foreman and T3 work need explicit coordination because factory pickup does not suspend the remote worker. Warp's main added value here would be shared intake, replay/evaluation infrastructure, and managed execution. [Factory MCP, undated; accessed 2026-11-11][factory-mcp]. [Factory overview, undated; accessed 2026-11-11][overview].

### Locally runnable alternatives

These are source and documentation checks. None was installed or benchmarked here. Maturity judgments are inferences from the cited release and implementation evidence.

| Project | License | What can run locally and match the machine | Maturity assessment and evidence |
|---|---|---|---|
| Kilroy | MIT | Go CLI executes Attractor graphs in Git worktrees. Nodes include agents, tools, human gates, branches, retries, and parallel joins. Checkpoints support resume. Uses API or coding CLI backends; CXDB records run history. | Inference: experimental but concrete and runnable. Published v0.1.0. Needs workflow authoring and provider/CXDB setup. [README, undated; accessed 2026-11-11][kilroy]. [License, undated; accessed 2026-11-11][kilroy-license]. [Release, 2026-04-16; accessed 2026-11-11][kilroy-release] |
| Agent Orchestrator, now Orchestrator.inc | Apache-2.0 | Local desktop agent fleet with per-task branches/worktrees. CI failures, review comments, and conflicts return to the responsible worker. Optional reviewer agents precede human review. | Inference: active pre-1.0 alternative with substantial overlap with T3. v0.14.10 is published; Linux desktop is documented. [README, undated; accessed 2026-11-11][ao]. [License, undated; accessed 2026-11-11][ao-license]. [Release, 2026-11-06; accessed 2026-11-11][ao-release] |
| OpenHands Agent Canvas | MIT in the inspected repository | Local stack, Docker, VM, or remote agent backends. Supports OpenHands and third-party coding agents. Schedules and webhooks start automations. Cloud and Enterprise services are optional. | Inference: established project with an evolving Canvas product. Workflows still need explicit spec/review/merge policy. [README, undated; accessed 2026-11-11][openhands]. [License, undated; accessed 2026-11-11][openhands-license]. [Release, 2026-11-11; accessed 2026-11-11][openhands-release] |
| LangGraph | MIT library | Python or JavaScript state graphs, persisted execution, and human interrupts can implement the same gates. Runs standalone; LangSmith services are optional additions. | Inference: mature infrastructure, with more integration work than a ready-made coding factory. The owner must supply coding-agent adapters, worktrees, scoring, and merge policy. [README, undated; accessed 2026-11-11][langgraph]. [License, undated; accessed 2026-11-11][langgraph-license] |

StrongDM's Attractor repository is Apache-2.0 and publishes natural-language specifications for a graph runner, coding-agent loop, and common model client. Its README tells users to have an agent implement it. It is not itself a ready-to-run factory distribution. Kilroy is one concrete implementation. [Attractor README, undated; accessed 2026-11-11][attractor]. [License, undated; accessed 2026-11-11][attractor-license]. [Kilroy, undated; accessed 2026-11-11][kilroy].

Inference: Kilroy offers the clearest explicit pipeline experiment. Agent Orchestrator overlaps most with T3. LangGraph fits only if a durable programmable state machine becomes a demonstrated need. Retaining T3 and borrowing specific gates is the smallest experiment. [Kilroy, undated; accessed 2026-11-11][kilroy]. [Agent Orchestrator, undated; accessed 2026-11-11][ao]. [LangGraph, undated; accessed 2026-11-11][langgraph].

## 3. Merge-risk skill

### Verified scoring

Quoted dimension names and allowed grades are below. The source maps bad/middle/good grades to 3/2/1. [Skill, undated; accessed 2026-11-11][merge].

| Quoted dimension | Grades, worst to best | Weight |
|---|---|---|
| "Alignment" | poor / decent / good | 1 |
| "Impact" | large / medium / small | 2 |
| "Verification" | poor / decent / good | 2 |
| "Rollback cost" | high / medium / low | 1.5 |
| "Error detection" | poor / decent / good; N/A also scores 1 | 1 |

`score = (alignment + 2*impact + 2*verification + 1.5*rollback + detection) / 7.5`. [Skill, undated; accessed 2026-11-11][merge].
Low is `<1.5`; medium is `1.5` to `<2.25`; high is `>=2.25`. The skill hides the number and calculation. It outputs the overall grade, every category verdict, and concise gaps. [Skill, undated; accessed 2026-11-11][merge].

- Alignment requires documented assumptions and drive-by edits. Impact covers blast radius and sensitive paths even in tiny diffs. [Landing page, undated; accessed 2026-11-11][merge-page].
- Verification requires screenshots/recordings for user-experience changes and profiling for meaningful performance effects. Edge cases need tests or documentation. [Skill, undated; accessed 2026-11-11][merge].
- Rollback distinguishes reversible work from destructive or hard-to-reverse decisions. Detection checks monitoring and errors hidden by swallowing or fallback behavior. [Skill, undated; accessed 2026-11-11][merge].
- Splitting: the article recommends removing unaligned work and stacking high-impact changes. The skill itself has no PR-splitting algorithm or threshold-triggered split rule. [Review article, 2026-11-05; accessed 2026-11-11][review-blog]. [Skill, undated; accessed 2026-11-11][merge].

### Inferences

- With rollback=3 and all other grades=1, the formula gives `1.4`, still low. A one-way change does not automatically force high risk. Preserve explicit migration/rollback approval gates separately. [Formula, undated; accessed 2026-11-11][merge].
- A useful local split would isolate unrelated cleanup and separate reversible preparation from a destructive migration. Each piece should carry its own verification and recovery plan. That is my proposed application, not a rule in the skill. [Risk discussion, 2026-11-05; accessed 2026-11-11][review-blog].

## 4. HumanLayer show-me

### Verified workflow and license

The skill explains the current topic visually. It is manually invoked through `/show-me`; its metadata disables model invocation. Matt Pocock's PR skill credits this source to Dex Horthy at HumanLayer. [Show-me, undated; accessed 2026-11-11][show]. [Attribution, undated; accessed 2026-11-11][pocock].

1. Choose the smallest useful representation for the current question. Keep prose brief. [Show-me, undated; accessed 2026-11-11][show].
2. Use pseudocode for logic, a call tree for runtime flow, a component tree for UI structure, or a shallow file tree for responsibility. Use Mermaid for interactions or data flow. [Show-me, undated; accessed 2026-11-11][show].
3. Show changes as a diff when the surrounding shape exists. Show the whole block when it is mostly new, ownership/order needs context, or the user needs a copyable target. [Show-me, undated; accessed 2026-11-11][show].
4. For dense concepts or visual layouts, write one focused HTML artifact. Match the product's styling, use real labels/data, support desktop/mobile, and open it with `open path/to/show-me-{description}.html`. [Show-me, undated; accessed 2026-11-11][show].
5. Put each view next to its short explanation. Include only relevant calls, files, states, and boundaries. It is a choice of representations, not a required sequence of every format. [Show-me, undated; accessed 2026-11-11][show].

HumanLayer's skill repository is MIT. [License, undated; accessed 2026-11-11][human-license].

Inference: this is useful for one-off explanations. Paneweft addresses retained, inspectable views with shared data and provenance. Show-me does not prescribe that persistence or evidence contract. [Show-me, undated; accessed 2026-11-11][show]. [Local Paneweft design, 2026-11-11; accessed 2026-11-11][owner-paneweft].

## 5. Warp's three spec skills

### Verified flow

The article names `/write-product-spec`, `/write-tech-spec`, and `/validate-changes-match-specs`. The flow is product spec → technical spec → implementation → spec comparison → computer-use validation. Markdown specs accompany the implementation PR. The computer-use step is additional to the three named skills. [Article, 2026-06-11; accessed 2026-11-11][spec-blog].

| Skill | Current source workflow | Evidence |
|---|---|---|
| `write-product-spec` | Gather behavior and design context. Write `specs/<id>/PRODUCT.md`. Describe the consumer's experience as numbered invariants. Keep implementation and test planning in TECH.md. Small obvious fixes can skip a spec. | [Product skill, undated; accessed 2026-11-11][product-skill] |
| `write-tech-spec` | Read PRODUCT.md and inspect current code. Write sibling TECH.md with context, proposed changes, and validation mapped to product invariants. Pin important code references. Consider work division when agent tooling is available. | [Technical skill, undated; accessed 2026-11-11][tech-skill] |
| `validate-changes-match-specs` | Discover relevant specs and compare implementation. Report material mismatches with source anchors. Ask whether to resolve individually or collect decisions before batch edits. For each, offer code correction, spec correction, explanation, or acknowledgement. Apply decisions and validate. Offer cloud computer-use validation for product behavior. | [Validation skill, undated; accessed 2026-11-11][validation-skill] |

These skills use the common-skills MIT license. Their current files contain more procedure than the June article, so the article is not a full specification of today's skill behavior. [License, undated; accessed 2026-11-11][common-license]. [Validation skill, undated; accessed 2026-11-11][validation-skill].

Inference: the owner's design interrogation, red tests, and review gates already cover much of this. The useful addition is stable numbered behavior invariants and an explicit code-versus-spec reconciliation step. Do not automatically rewrite an acceptance criterion merely because implementation diverged. [Local build-loop, undated; accessed 2026-11-11][owner-loop]. [Product skill, undated; accessed 2026-11-11][product-skill]. [Validation skill, undated; accessed 2026-11-11][validation-skill].

## 6. Benchmarking and cost

### The video's task selection and replay method

The speaker opens by calling benchmarking the least settled part of factory design. He mixes current recommendations with research notes. His main recommendation is to test the team's own workload. Public benchmarks help shortlist models, but may miss review difficulty, tool-call volume, or specialized work such as API design. Changing team defaults week by week confounds model changes with skills, task mix, and other settings. [Benchmark transcript, ~0% to ~3% and ~22% to ~36% through][bench-transcript].

1. Choose the question first. Test a generalist, hard tasks, a domain such as front-end, or a particular role such as foreman or implementer. Gather past conversations and outputs across the team's work. [Benchmark transcript, ~40% to ~49% through][bench-transcript].
2. Find tasks by hand or ask an agent to search run history. The demonstrated selection skill excludes release management, cherry-picks, and unsuitable one-offs. It ranks candidates by difficulty and area, including back-end, front-end, tooling, and migrations. [Benchmark transcript, ~46% to ~52% through][bench-transcript].
3. Ask for candidate pools, not an agent-picked final ten. The example searched about 2,700 runs. Humans choose representative tasks from easy, medium, and hard pools. The skill was written that morning and remains exploratory. [Benchmark transcript, ~51% to ~57% through][bench-transcript].
4. Record task IDs, prompts, model/harness choices, and judging criteria in versioned benchmark files. Prompts derive from real work but can incorporate context learned during the original conversation. They also instruct the agent to finish without human checkpoints and deliver a reviewable PR artifact. [Benchmark transcript, ~58% to ~66% through][bench-transcript].
5. Replay in a fresh sandbox using the same image and repository access. In the shown foreman test, swap only the foreman's model. Keep the other agents' models constant. The foreman can delegate as usual. Human gates are removed for the benchmark, so this does not reproduce the whole human workflow. [Benchmark transcript, ~60% to ~68% through][bench-transcript].

### Measures and bias controls

An LLM-as-a-judge scores the conversation and resulting artifact against task criteria. Correctness can be binary for a coding task or fractional for a spec. Deterministic tasks can supply checking scripts. Reports show aggregate and per-task results, average cost, and average duration. The speaker recommends a quality-versus-cost plot to identify choices where neither quality nor cost can improve without sacrificing the other. Latency matters too, especially for the foreman a human talks to. [Benchmark transcript, ~43% to ~44% and ~68% to ~83% through][bench-transcript].

The explicit controls are representative real tasks, human curation, common replay environments, a fixed rubric within a comparison, and changing one target agent while holding other agents constant. Some later tests repeat each task/model twice. Public results and earlier local tests narrow the expensive candidate set. These controls reduce confounding and benchmark cost. They do not establish an unbiased estimate by themselves. [Benchmark transcript, ~51% to ~68% and ~79% to ~86% through][bench-transcript].

The video does not describe preregistration, blinded graders, randomized assignment, a separate tuning/holdout split, or confidence intervals. Human curation can favor familiar tasks. Adding hindsight to prompts can change difficulty. A model judge can carry its own preferences. These are methodological limits and proposed checks, not controls claimed by the speaker. [Benchmark transcript, selection/replay ~46% to ~68%, judging ~69% to ~85% through][bench-transcript].

### Spoken costs and results

These are reported examples. Average task cost, total benchmark spend, and production cost per PR have different denominators.

| Example | Spoken result and limit | Transcript evidence |
|---|---|---|
| Early implementation comparison | GPT-5.6 averages $4.74 per task; GLM 5.3 averages $1.59. GPT has higher correctness. GPT takes about 12 minutes and GLM about 17. No exact correctness percentages are spoken here. | [Benchmark, ~74% to ~77% through][bench-transcript] |
| Size of that early sample | The speaker first says ten tasks, then corrects himself to twenty. He describes this early sample as less carefully chosen than the new corpus. | [Benchmark, ~68% to ~69% through][bench-transcript] |
| Triage comparison | Opus has the highest correctness but costs about $8 in the displayed comparison. Grok 4.6 is the cheaper efficient choice he would consider. | [Benchmark, ~80% to ~82% through][bench-transcript] |
| Spec comparison | GLM leads on cost with some quality sacrifice. Sol offers high performance at lower cost. Specs use a fractional rubric. No exact dollar result is spoken. | [Benchmark, ~82% to ~84% through][bench-transcript] |
| Expensive broad model test | The high-reasoning candidate captioned Claude Fable 5 improves correctness by only a few percentage points at higher cost. He would now compare just the incumbent and challenger. No total benchmark bill is spoken. | [Benchmark, ~85% to ~89% through][bench-transcript] |
| Production optimization target | Moving from $30 to $20, then $10, is the goal for finer routing. It is not a reported achieved saving. | [Benchmark, ~95% to ~97% through][bench-transcript] |

The separate published WarpBench case study reports 30 tasks, 3h 46m, and $2,130.57 total spend. It reports production cost per PR falling from about $80 to $30, stable merge rate, and compliance rising from 69% to 87%. Do not attribute these page-only numbers to the spoken comparison or equate its corrected twenty-task sample with this thirty-task suite. [Case study, 2026-09-02; accessed 2026-11-11][warpbench]. [Benchmark transcript, ~68% to ~69% through][bench-transcript].

Current docs count trial and scorer costs, but external inference may be estimated or absent. Benchmark totals do not reconcile invoices. They also document saved run inputs and repetitions. These details supplement the transcript. [Benchmark docs, undated; accessed 2026-11-11][bench-docs].

### The routing tree, recommendations, and open research

Start broad, then make routing more specific as evidence accumulates. The spoken sequence is generalist selection → easy/medium/hard → focus area → role-specific task routing. His concrete illustration is an implementation agent choosing GPT for some back-end tasks and Claude Opus 5 for some front-end tasks. This is an example of a rule to investigate, not a demonstrated universal winner for each domain. [Benchmark transcript, ~53% to ~56% through][bench-transcript].

Earlier examples suggest cheap GLM for research, Claude for readable specs, Sol for general implementation, and Astra for front-end computer use. These are illustrative or provisional choices. The speaker is unsure which review model they currently use. The later review video recommends stronger reasoning for review, so the series does not establish one fixed role-to-model map. [Benchmark transcript, ~12% to ~20% through][bench-transcript]. [Review transcript, ~20% through][review-transcript].

The harness can route among models inside one agent; separate agents for each task type are optional. A specialized agent can also be benchmarked alone, then tested with the foreman to check whether it delegates to that specialist correctly. [Benchmark transcript, ~91% to ~94% and ~97% through][bench-transcript].

The recommendation is to start with a broad, affordable comparison and refine only where useful. The open research is which corpus, rubric, repetitions, model mix, and routing depth produce reliable gains for a particular team. Code quality and efficiency scorers are mentioned as future discussion; the shown reports primarily judge correctness. [Benchmark transcript, ~54% to ~57%, ~84% to ~89%, and ~99% through][bench-transcript].

### Proposed controls for the owner's benchmark

- Freeze a small paired task set. Keep prompts, commits, environments, permissions, and acceptance criteria equal. Charge retries, reviews, graders, and failed runs. This extends the replay method. [Benchmark transcript, ~60% to ~68% through][bench-transcript]. [Cost definitions][bench-docs].
- Preregister measures, hide historical outcomes, blind artifact graders, mix model families, and reserve tasks for validation after tuning. Repeat trials and report uncertainty. These are W28 requirements or proposed extensions, not demonstrated Warp safeguards. [Owner plan, W28][plan].
- Record human review time, rework, incidents, and accepted changes alongside cost. The review article names cost per PR, cycle time, and incident rollbacks. [Review article, 2026-11-05; accessed 2026-11-11][review-blog].
- The page's reported $50 saving implies about 43 subsequent PRs to repay $2,130.57. This calculation assumes stable savings and excludes engineering time. It is not a measured payback result. [Inputs, 2026-09-02; accessed 2026-11-11][warpbench].

## 7. "Arc analyzer"

### The phrase occurs; tool identification remains unresolved

The review transcript contains both "arc analyzers" in an audience question and "arc analyzer" in the presenter's reply, around lines 539 to 548. The presenter says, "I don't know what an arc analyzer is" and expresses interest in learning more. He does not name, demonstrate, or endorse a tool. This corrects the premise that neither transcript contains the phrase. [Review transcript, ~50% to ~51% through][review-transcript].

I checked both full texts, literal arc/ark/analyzer variants, and whitespace-joined variants for split captions. No corresponding tool reference appears in the benchmark transcript. The review occurrence supplies no spelling or identity beyond the auto-captioned phrase. Another video in the series may explain it, but that remains unverified. [Review transcript, ~50% through][review-transcript]. [Benchmark transcript, full text][bench-transcript].

A tool explicitly called Arc Analyzer exists in Michael Rothrock's `mrothroc/claude-code-log-analyzer`. It reads local Claude Code logs and groups prompts into coherent units of work. Semantic segmentation uses Gemini Flash Lite. Agent-session counting is a separate command. [README, undated; accessed 2026-11-11][arc].

Its companion Gate Analyzer discovers review tools, extracts decisions, classifies rejections, and computes overlap between gate types. The repository is MIT. The documented inputs are Claude Code history and session/subagent JSONL files. [README, undated; accessed 2026-11-11][arc]. [License, undated; accessed 2026-11-11][arc-license].

The source describes an older pattern-based analysis and a newer semantic approach that produces different arc counts. Arc counts depend on the segmentation method. They are not objective counts of completed engineering outcomes. [README, undated; accessed 2026-11-11][arc].

**Owner confirmation, 2026-11-11:** the owner confirms `mrothroc/claude-code-log-analyzer`'s Arc Analyzer is the tool meant. Trial queued as PLAN W34.

Neither transcript connects that repository to the audience question; the identification rests on the owner's confirmation. It could also be a caption for another term; there is no basis here to identify it as an architecture analyzer or arc42 tool. [Review transcript, ~50% through][review-transcript]. [Benchmark transcript, full text][bench-transcript]. [Candidate, undated; accessed 2026-11-11][arc].

### Fit, as inference

Use it as an offline process-analysis experiment. Join inferred work arcs to the build-loop's reviewed commits and finding ledger. Compare time, recovery, and repeated findings across review tiers. Claude-only log assumptions need checking before importing T3/Codex sessions. [Analyzer inputs, undated; accessed 2026-11-11][arc]. [Local review ledger, undated; accessed 2026-11-11][owner-review].

Residual can hold the architectural forces and proposed changes prompted by those findings. Paneweft can show trace-backed views of arcs, gate decisions, and repeated findings. Keep model-inferred segmentation separate from observed events. This is a proposed connection, not an existing integration. [Residual, undated; accessed 2026-11-11][owner-residual]. [Paneweft design, 2026-11-11; accessed 2026-11-11][owner-paneweft]. [Analyzer, undated; accessed 2026-11-11][arc].

Inference: repeated gate rejections do not establish redundant reviews. Different gates may inspect different artifacts or catch different defects within one work item. Validate defect identity against the ledger before using overlap to remove a tier. [Analyzer's overlap discussion, undated; accessed 2026-11-11][arc]. [Local finding ledger, undated; accessed 2026-11-11][owner-review].

## 8. Existing coverage and additions

These are comparisons and proposed transfers. The baseline is the owner's stated build-loop, holdout tests, residual, vigil, qex, and T3 delegation. Local source checks confirm the ledger/review procedure and residual/Paneweft roles; they do not measure the stack's effectiveness. [Build-loop, undated; accessed 2026-11-11][owner-loop]. [Review ledger, undated; accessed 2026-11-11][owner-review]. [Residual, undated; accessed 2026-11-11][owner-residual]. [Paneweft design, 2026-11-11; accessed 2026-11-11][owner-paneweft].

| Item | Already covered → genuinely new or still worth testing |
|---|---|
| Factory state machine | T3 delegation and build-loop phase/review gates → durable shared intake, explicit handoff/completion states, and production feedback. [Workflow, undated; accessed 2026-11-11][owner-loop]. [Lifecycle, undated; accessed 2026-11-11][lifecycle] |
| Warp infrastructure | T3 sessions/worktrees; qex resource queue; vigil waits → packaged team integrations, unified run data, and replay benchmarks. These do not replace local scheduling or architecture analysis. [Workflow, undated; accessed 2026-11-11][owner-loop]. [Factory overview, undated; accessed 2026-11-11][overview] |
| Merge-risk | Scored review, scope control, and ledger → a separate weighted view of impact, reversibility, evidence, and detection. This grade measures something different from reviewer confidence. [Local review, undated; accessed 2026-11-11][owner-review]. [Risk skill, undated; accessed 2026-11-11][merge] |
| Show-me | Paneweft's question-focused views → a small representation-selection prompt for immediate explanations and PR summaries. [Paneweft design, 2026-11-11; accessed 2026-11-11][owner-paneweft]. [Show-me, undated; accessed 2026-11-11][show] |
| Spec skills | Design questioning and red/green implementation → numbered behavior invariants, separate PRODUCT/TECH documents, and explicit mismatch decisions. [Workflow, undated; accessed 2026-11-11][owner-loop]. [Spec flow, 2026-06-11; accessed 2026-11-11][spec-blog] |
| Benchmarking | Holdout tests and per-change review evidence → frozen historical task replay, total-cost comparison, and validated task-specific routing. [Workflow, undated; accessed 2026-11-11][owner-loop]. [Benchmarks, undated; accessed 2026-11-11][bench-docs] |
| Arc Analyzer candidate | Finding ledger and authored residual forces → retrospective work segmentation and gate-overlap analysis, subject to manual validation. [Ledger, undated; accessed 2026-11-11][owner-review]. [Analyzer, undated; accessed 2026-11-11][arc] |
| Kilroy | Existing phase orchestration → declared graph transitions, per-node checkpoints, and resume history in CXDB. [Workflow, undated; accessed 2026-11-11][owner-loop]. [Kilroy, undated; accessed 2026-11-11][kilroy] |
| Agent Orchestrator | T3 already runs agent sessions/worktrees → another local controller with automatic CI/review reactions; measure benefit before adopting duplicate orchestration. [Local T3, undated; accessed 2026-11-11][owner-t3]. [Alternative, undated; accessed 2026-11-11][ao] |
| OpenHands Agent Canvas | T3 local sessions and delegation → optional always-on automation/backend management. A migration still needs evidence. [Local T3, undated; accessed 2026-11-11][owner-t3]. [Canvas, undated; accessed 2026-11-11][openhands] |
| LangGraph | Existing procedural gates → persisted executable transitions and interrupts if ad-hoc coordination becomes unreliable. [Workflow, undated; accessed 2026-11-11][owner-loop]. [LangGraph, undated; accessed 2026-11-11][langgraph] |

Inference: first test merge-risk, explicit before/after proof, and one small cost/quality replay suite inside the current stack. The evidence does not justify replacing T3 or treating additional agents as an improvement by themselves. [Risk skill, undated; accessed 2026-11-11][merge]. [Review article, 2026-11-05; accessed 2026-11-11][review-blog]. [Benchmarks, undated; accessed 2026-11-11][bench-docs].

## 9. Owner reactions and PLAN mapping

The reactions come from the owner's PLAN, not from the webinar audience. The mapping below distinguishes the spoken advice from the owner's additions. [PLAN, W23 to W28][plan].

| Topic | Video's framing | PLAN mapping |
|---|---|---|
| Factory state machine | Configure stages, let the agent choose transitions, and bind stages to workers. A stage need not create a fresh context. [Review, ~25%, ~51%, and ~56% to ~58% through][review-transcript] | W24 can place opening and closing checks in explicit states. Recording opening concerns in residual is the owner's extension. |
| Hiding nits | Filter nits before implementation to avoid churn. Keep agent review chatter internal and traceable. No later-release checkpoint is specified. [Review, ~17% to ~21% through][review-transcript] | W23 adds the hidden stash, release after tier 1, and central-change-only criterion. |
| Product and architecture | Warp uses one reviewer. The presenter attributes a product/architecture split to Matt Pocock and suggests benchmarking a second reviewer as an experiment. [Review, ~28% to ~30% through][review-transcript] | W24 goes further with both kinds of review at both ends and a closing check against recorded concerns. |
| Budget decisions | The review loop cost about 3x as much in one experiment, motivating selective review. Benchmark cost also multiplies with tasks, models, and repetitions. [Review, ~27% through][review-transcript]. [Benchmark, ~79% to ~86% through][bench-transcript] | W25's usage-event thresholds and automatic role changes are separate runtime policy. The videos support measuring the tradeoff, not a specific usage trigger. |
| Merge risk and drive-bys | Assess alignment, impact, verification, rollback cost, and error detection before opening, then report them. Call out drive-bys; drop irrelevant ones. A large example reduces risk through more flow/performance evidence and splitting PRs. [Review, ~60% to ~70% and ~78% to ~80% through][review-transcript] | W27 adds the owner's rule to put drive-bys in separate PRs. The video supports scoping and splitting but does not prescribe a stash-to-PR mechanism. |
| Benchmarking cost without bias | Replay team work, curate task pools, isolate the changed agent, and compare correctness/cost/time. Treat fine routing as an experiment. [Benchmark, ~46% to ~89% through][bench-transcript] | W28 adds historical failures and undone decisions, hidden outcomes, preregistration, blind grading, and cross-family trials. |

## Source URLs

Local transcripts were accessed on the research date above; other citations carry source and access dates. Local baseline links name canonical repository locations; baseline files were inspected in the earlier research pass. Paneweft v1's cited research document is a design, not proof that every proposed feature has shipped.

[video-review]: https://www.youtube.com/watch?v=uPCH2axUpbc
[video-bench]: https://www.youtube.com/watch?v=XuvFo0q5TpU
[review-transcript]: data/transcripts/uPCH2axUpbc-code-review-bottleneck.md
[bench-transcript]: data/transcripts/XuvFo0q5TpU-software-factory-not-expensive.md
[plan]: PLAN.md
[review-blog]: https://www.warp.dev/blog/agent-code-review-bottleneck
[factories]: https://www.warp.dev/factories
[overview]: https://docs.warp.dev/factories/
[lifecycle]: https://docs.warp.dev/factories/how-factories-work/
[roles]: https://docs.warp.dev/factories/factory-agents/
[foreman]: https://github.com/warpdotdev/warp-factory-examples/blob/main/examples/00-warp-default-agents/agents/foreman/agent.md
[warp-readme]: https://github.com/warpdotdev/Warp/blob/main/README.md
[worker]: https://github.com/warpdotdev/oz-agent-worker
[worker-license]: https://github.com/warpdotdev/oz-agent-worker/blob/main/LICENSE
[common-license]: https://github.com/warpdotdev/common-skills/blob/main/LICENSE
[examples]: https://github.com/warpdotdev/warp-factory-examples
[examples-license]: https://github.com/warpdotdev/warp-factory-examples/blob/main/LICENSE
[sdk]: https://github.com/warpdotdev/oz-sdk-python
[sdk-license]: https://github.com/warpdotdev/oz-sdk-python/blob/main/LICENSE
[selfhost]: https://docs.warp.dev/factories/self-hosting/
[docker-worker]: https://docs.warp.dev/factories/self-hosting/managed-docker/
[direct]: https://docs.warp.dev/factories/self-hosting/managed-direct/
[definition]: https://docs.warp.dev/factories/factory-as-code/
[pricing]: https://www.warp.dev/pricing
[factory-mcp]: https://docs.warp.dev/factories/factory-mcp/
[kilroy]: https://github.com/danshapiro/kilroy
[kilroy-license]: https://github.com/danshapiro/kilroy/blob/main/LICENSE
[kilroy-release]: https://github.com/danshapiro/kilroy/releases/tag/v0.1.0
[ao]: https://github.com/OrchestratorInc/agent-orchestrator
[ao-license]: https://github.com/OrchestratorInc/agent-orchestrator/blob/main/LICENSE
[ao-release]: https://github.com/OrchestratorInc/agent-orchestrator/releases/tag/v0.14.10
[openhands]: https://github.com/OpenHands/OpenHands
[openhands-license]: https://github.com/OpenHands/OpenHands/blob/main/LICENSE
[openhands-release]: https://github.com/OpenHands/OpenHands/releases/tag/v1.39.0
[langgraph]: https://github.com/langchain-ai/langgraph
[langgraph-license]: https://github.com/langchain-ai/langgraph/blob/main/LICENSE
[attractor]: https://github.com/strongdm/attractor
[attractor-license]: https://github.com/strongdm/attractor/blob/main/LICENSE
[merge-page]: https://www.warp.dev/merge-risk
[merge]: https://github.com/warpdotdev/common-skills/blob/main/.agents/skills/merge-risk/SKILL.md
[show]: https://github.com/humanlayer/skills/blob/main/plugins/show-me/skills/show-me/SKILL.md
[pocock]: https://github.com/mattpocock/skills/blob/main/skills/engineering/pr/SKILL.md
[human-license]: https://github.com/humanlayer/skills/blob/main/LICENSE
[spec-blog]: https://www.warp.dev/blog/three-skills-for-spec-driven-development
[product-skill]: https://github.com/warpdotdev/common-skills/blob/main/.agents/skills/write-product-spec/SKILL.md
[tech-skill]: https://github.com/warpdotdev/common-skills/blob/main/.agents/skills/write-tech-spec/SKILL.md
[validation-skill]: https://github.com/warpdotdev/common-skills/blob/main/.agents/skills/validate-changes-match-specs/SKILL.md
[warpbench]: https://www.warp.dev/factories/benchmarks/warpbench
[bench-docs]: https://docs.warp.dev/factories/benchmarks/
[production]: https://www.warp.dev/blog/build-production-software-factory
[arc]: https://github.com/mrothroc/claude-code-log-analyzer
[arc-license]: https://github.com/mrothroc/claude-code-log-analyzer/blob/main/LICENSE
[owner-loop]: https://github.com/mikenrafter/phoe-nix/blob/main/scout-modules/agent-integration/skills/build-loop/SKILL.md
[owner-review]: https://github.com/mikenrafter/phoe-nix/blob/main/scout-modules/agent-integration/skills/build-loop/references/review.md
[owner-t3]: https://github.com/mikenrafter/phoe-nix/blob/main/scout-modules/t3/flake.nix
[owner-residual]: https://github.com/mikenrafter/residual/blob/main/README.md
[owner-paneweft]: https://github.com/mikenrafter/phoe-nix/blob/main/knowledge/research/agentic-practice-2026-11/12-paneweft-v1-in-code-views.md
[nixed]: https://github.com/mikenrafter/phoe-nix/blob/main/hosts/nixed.nix
