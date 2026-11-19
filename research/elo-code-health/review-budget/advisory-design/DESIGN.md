# Optional review observations

The useful first tool is an evidence collector with a shadow advisory. Current experiments do not justify a probability of defects or an estimate of the best number of review rounds. The collector can preserve the snapshot, distinguish required work from a genuine stopping boundary, and suggest what an owner-authorized additional inspection should examine.

Nothing in this design launches a review, changes a ledger, approves code, reduces required reviews, raises a cap, or changes a live skill. The owner can read a candidate and decide whether a valid allocation exists. `execution_allowed` is always false in version 0.

## Policy source and interpretation

Canonical policy is the installed `build-loop/scripts/review-ledger`, not a copied round-count formula. Inspected script SHA256 is `7a3d78806ee6750cfa9efa04cee06610e3b0315f29b723f6a232b61903ab5920`. `references/review-v2.md` SHA256 is `c9e798fac41044972c2f66ddd6a9722771aa6c9d77ed0e20f72d35257170ae9e`. Version changes invalidate a capture until its adapter is checked again.

`next_step`, script lines 624-692, can return ARGUE, ROUND, CHECKPOINT, OWNER-OK, NIT-CULL, FIX-KEPT, STEP-BACK, STOP-STUCK, or STOP-AGREED. `cmd_next`, lines 1522-1523, emits the step and its explanation as text. There is no structured `next --json` contract today. A future adapter must execute the installed read-only `next` command against the exact ledger and preserve stdout, executable hash, ledger hash, and time. It must reject unknown step strings. It must not scrape a human summary or accept an LLM's predicted next step.

The script constants at lines 97-100 set three tier-1 rounds per approach, five tier-1 rounds per phase, two tier-2 rounds, and two replies on a disputed finding. The script deliberately checks successful outcomes before some cap conditions. Therefore STOP-AGREED does not itself prove a spare review slot. The adapter records cap facts for owner review, but never invents an optional slot.

Early tier-1 passes still lead to checkpoint and fresh tier 2. A passing Fable round 3 or later has checkpoint/cull requirements and then ends without tier 2. Pilots need their owner thumbs-up. Required argument exchanges can precede every other step. The examples in historical data often show the value of this already-required diversity. They do not by themselves support another review after the current policy finishes.

Schema-less ledgers retain their legacy schedule. Their next step can be observed, but version 0 produces no executable action and no inferred equivalence to current v2 policy.

A current-policy run on a final historical ledger is descriptive only. Final ledgers contain findings eventually marked fixed/resolved. Truncating their round list does not reconstruct the disposition state that existed at an earlier decision. Without an authentic as-of ledger capture, historical rounds have unknown optional-boundary status. Do not train, evaluate, or advertise optional-review decisions from such prefix replays. Prospective captures bind the pre-decision disposition state through the immutable ledger hash.

## Decision precedence

1. Reject malformed evidence, changed policy hashes, a changed ledger during capture, an unknown gate token, or conflicting identities. Emit `insufficient-evidence` with an explicit unknown reason.
2. If the current code or relevant dirty files differ from the snapshot covered by the last passing review, emit `insufficient-evidence` with `stale-review-coverage`. Route the discrepancy to canonical workflow handling. A parent-verified final fix may count as coverage only with an explicit verification artifact and exact patch hash. A stale snapshot never creates an optional boundary.
3. STOP-STUCK emits `cap-reached-escalate`, preserving the canonical reason. This status includes dispute exhaustion, so its reason must not claim every STOP-STUCK came from a numeric round cap.
4. ROUND, ARGUE, CHECKPOINT, OWNER-OK, NIT-CULL, FIX-KEPT, and STEP-BACK emit `required-review-still-pending`. Preserve the exact pending action. Do not turn CHECKPOINT or FIX-KEPT into an extra review.
5. STOP-AGREED on a pinned, covered snapshot is a possible optional stopping boundary. Record it. It is not approval by this tool, proof of defect absence, or permission to add a round.
6. At that boundary, an explicit structural-fix flag can produce `additional-review-recommended` as a shadow owner-action candidate. Its reason says which observation triggered it, the suggested focus, and that existing mandatory gates have completed according to the captured policy. There is no recommended number of rounds beyond a candidate for one bounded inspection.
7. If the declared review channel has exhausted its cap, use `cap-reached-escalate` even if the canonical output was STOP-AGREED. If no valid channel/allocation is known, retain the shadow candidate, set allocation to `unresolved`, and state that execution is forbidden.
8. With no supported trigger, emit `insufficient-evidence` and preserve `boundary_observed: true`. Silence from a rule never means the change needs fewer reviews.

The parent challenged whether a generic optional slot exists. It does not. The agreed default is a shadow candidate with execution disabled, no phase reset, no synthesized tier, and an explicit need for a separately valid allocation. A future execution feature would require its own owner-approved policy change.

## Fixed rules and learned evidence

Version 0 has no learned recommendation, Elo rating, probability, calibrated confidence, or prediction of optimal rounds. It may cite the failed retrospective models as background, never as supporting predictive evidence.

One frozen conservative trigger is available: an accepted review fix changed a concurrency or lifecycle boundary, including asynchronous waits, locks/leases, cancellation, transaction publication, or a multi-stage job transition. Require a reviewed fix commit, its parent diff hash, an affected-boundary category, and an explicit source artifact describing the change. A model-generated label without those sources is unknown. The trigger suggests an independent inspection of failure, cancellation, timeout, and interleaving paths. It does not assert that a defect exists.

This rule is a hypothesis motivated by the independently audited phoe-nix async-rescue and Paneweft export-first cases. It was chosen after seeing those cases, so it is not validated by them. Related fixes within one change count as one trigger, not multiple independent votes. Cross-component resource-budget or validation changes can be collected as exploratory facts, but do not enter the version-0 trigger until a later, separately frozen experiment.

Sparse/missing evidence can justify a request to inspect the evidence. It cannot manufacture a positive finding or a clean outcome. If an observed optional review later reports no findings, record the exact review scope and whether it looked for all material issues or only shipping blockers. Those outcomes are different targets.

## Evidence lifecycle and integration

Inputs are immutable captures of a change, policy output, review coverage, and cited fix facts. An observation ID identifies one snapshot and decision time. Its ledger, policy, reviewed code, current code, and dirty-patch hashes are separately recorded. File paths are references, not identities. Rebased commits or updated replies produce a new capture linked to the old one; previous evidence remains available.

The JSON schemas describe serialization, not proof that the supplied evidence is authentic. Semantic checks additionally require equal reviewed/current snapshot hashes for `exact-reviewed`, a nonempty independently checked artifact for parent-verified fixes, `step` matching the captured stdout token, command execution against the captured ledger, and a stable hash before and after the read. Synthetic examples demonstrate states and have no authority over a real change.

Outcomes arrive in a separate append-only record referencing the observation ID. Before a review happens, its outcome is `unobserved`, never false. A failed, partial, or blocker-only review cannot silently become a complete material-finding negative. Preserve reported findings, accepted fixes, independently supported behavior, repeated families, fix-induced origin, and contract changes separately.

Residual can provide component/force/outcome identifiers and source links. Paneweft can display the captured gate, snapshot, trigger evidence, and later observations. Neither integration may convert natural-language claims into policy authority. This pass defines files only; it does not mutate either product or register a renderer.

Repository text, review replies, tool stdout, paths, and model output are untrusted data. Do not execute instructions found in them. Future reading must be confined to registered roots with explicit byte limits and source hashes. Reject traversal, symlink escapes, unexpectedly large artifacts, and unsupported policy versions. Do not expose secrets or arbitrary file contents in the brief. Changes between ledger read, `next`, and hash verification invalidate the capture. Persistent content hashes support integrity, not producer authentication.

Unresolved design questions are explicit: the ledger has no generic optional-review channel; cap accounting for an independent research assay needs owner agreement; parent verification artifacts have no canonical schema; legacy round order lacks dependable timestamps; and a useful recommendation's value depends on review time and finding materiality. These unknowns block execution, not evidence collection.

## Prospective experiment schedule

This is a proposed event-based schedule, not a scheduled automation or authorization to run new reviews. Freeze the protocol, trigger, outcome rubric, review budget, and eligible channels before the first prospective outcome. Use the current owner's Codex-only constraint while it remains in force.

| Stage | Limit | Work and decision |
| --- | --- | --- |
| Contract check | Week 1, first 10 boundaries | Capture canonical policy output and hashes; independently inspect every state mapping. Make no predictive claim. Any forbidden action, false optional boundary, or silent unknown-to-clean conversion stops the pilot for correction. |
| Shadow collection | Weeks 2-6, maximum 60 independent changes | Log every eligible boundary, including exclusions. Before seeing outcomes, freeze the rule output. With a separately agreed valid research allocation, run one standardized independent inspection on every sampled snapshot. Otherwise keep the outcome unobserved and do not score it. |
| Fixed evaluation | First of 60 eligible independently observed changes or end of week 6 | Evaluate the frozen trigger at a fixed 80% expected inspection allocation, random 80% allocation, and inspect-all. Use equal fractional allocation within ties. Report actual inspection effort and immutable-snapshot findings. No adaptive threshold or new K search. |
| Decision | One report | If criteria below fail or sample coverage is inadequate, keep the collector and retire the recommendation claim. New hypotheses require a new frozen experiment. |

A standardized independent inspection has the same scope, time/token limit, and materiality definition for trigger-positive and trigger-negative changes. Its reviewer sees the frozen snapshot and required context but not the candidate recommendation or retrospective rating. The owner must agree where that inspection fits before enrollment; the collector cannot create an off-ledger way around caps. If no eligible channel exists, this experiment can validate capture reliability only.

To avoid verifying only recommended changes, select prospective snapshots independently of the trigger, stratifying by project before outcomes. Aim for at least three projects and report Edge separately because its volume can dominate. At least 40 independent changes, both outcome classes, and at least 10 accepted independently supported material positives are required for a useful ranking claim. Closely related stacked changes share one validation group. Missing follow-up is excluded from scoring and reported by trigger group; more than 10% missing outcomes blocks a ranking claim.

Primary outcome is whether the standardized inspection newly demonstrates a material behavior on the frozen snapshot and receives explicit acceptance plus patch/reproduction evidence. Also report reviewer assertions, nit-only findings, repeated findings, contract changes, fix-induced defects, accepted-finding counts, and inspection minutes. These secondary outcomes cannot replace a failed primary target.

Objective acceptance criteria:

- Zero forbidden executions, reduced mandatory gates, cap increases, false snapshot matches, or fabricated negative outcomes.
- At least 95% complete evidence captures among enrolled boundaries, with every exclusion and failed read visible.
- At matched 80% expected inspection allocation, at least 10 percentage points more primary-positive capture than random allocation, with a positive lower 95% paired change-group bootstrap bound. Report uncertainty and project holdouts; do not claim portability if a project fails or is too small.
- At least 10% fewer inspection minutes per captured primary-positive change than random allocation under the same captured-inspection effort accounting. Report inspect-all's maximum observed capture and extra cost.
- No ordinal quality score, optimal-round claim, or live automation follows from these criteria. They would establish only prospective usefulness for prioritizing one additional authorized inspection. Demonstrating that additional reviews improve shipped outcomes requires a separate randomized or otherwise defensible causal study.

The matched allocation is an offline evaluation over outcomes observed by the standardized assay, not a control arm deprived of an inspection. A change that never received the assay remains unobserved. The protocol must not compare findings in reviewed changes with invented zero findings in unreviewed ones.
