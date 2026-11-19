# Additional review budget experiment

## Top findings

- [D, hypothesis] Earlier review outcomes and the shape of subsequent fixes may help identify changes that benefit from another review round.
- [C, inventory] Local records include structured rounds and prose replies, with missing finding sets and incomplete dispositions. Missing observations remain unknown.
- [C, audit] Some later findings concern regressions introduced by previous fixes. Remaining defects and fix-induced defects require separate labels.
- [D, decision] This pilot may recommend additional review or abstain. It cannot lower existing mandatory reviews, relax score bars, approve a change, or override phase caps.
- [D, acceptance] A better fit to existing weak labels is exploratory. Deployment requires independent change-level evaluation and a complete evidence record.

## Time and spend

Owner authorization: work up to two hours starting 2026-11-17 07:06:26 UTC, hard deadline 09:06:26 UTC. Codex models only; no Claude calls. No paid model APIs, product builds, upstream writes, or changes to live skills during this research pass. Small analyses use the local qex queue. Stop new substantial launches by 09:01 UTC. If no meaningful improvement is established, stop at the deadline and go cold.

## Decision and baseline

The desired decision is whether an additional review is worth its cost after the currently required review path. The existing build-loop schedule is the policy baseline: passing tier-1 rounds 1–2 still requires fresh tier 2; passing Fable round 3+ ends without tier 2; pilots require their Fable pass and owner approval. The current cap remains binding. A cap hit requires escalation or a pivot, never automatic extra rounds.

The historical prediction task is narrower: predict whether the next **observed** round identifies a new material finding. This can evaluate a ranking or probability model, but cannot establish the benefit of a review that was never performed. It cannot equate stopping on a first approval with the current baseline. Historical records that predate the current schedule are not automatically policy-comparable.

## Evidence contract

Each observation names one change group, source hash, reviewed revision when available, round/tier/approach/reviewer and coverage status. The discovery round of a finding must be explicit. Invalidated, wrong-snapshot and duplicated reports are excluded or flagged, never accumulated as extra discoveries. Distinct finding IDs across replies are not proof of distinct defects.

Keep separate labels:

1. **Reported material finding**: a newly recorded blocker/should in a coverage-known round. This is a reviewer assertion.
2. **Accepted material finding**: reported material plus an explicit fixed/resolved disposition and nonempty fix/evidence reference. This is an accepted-finding proxy, not independent proof of a product defect.
3. **Independently supported material defect**: audit links a concrete incorrect behavior and a reproduction/test/patch that supports it. Count only inspected cases; do not extrapolate the audit sample.
4. **Fix-induced defect**: evidence explicitly links a later defect to a prior review fix. Unknown origin stays unknown.

An empty finding object, missing later reply, unperformed round, unresolved CHANGES verdict, or unverified parsing must not become a negative label. APPROVE is a separate outcome and does not prove absence of defects. Final ledger dispositions may label outcomes, but must not be used as pre-decision predictors for earlier rounds.

## Features and models

Only information available before the target round may enter a prediction. Round number, prior reported counts, prior material severity, prior score/verdict, reviewer/tier information known at assignment, and explicit changes since last review are candidates. Final checks, final status, eventual round count, later finding classes and future reviewer text are prohibited inputs. Group identity may partition validation but cannot act as a predictive lookup.

First compare constant prevalence, round-position prevalence, prior-round material-yield rules, and a small smoothed probability model. Elo variants must use one outcome per genuine observed round/change, not synthetic all-pairs comparisons. A fixed benchmark can turn Elo into an online binary forecast; label it that way. K families may include fixed, evidence-count-decaying and confidence-adjusted updates, with uncertainty based on independent changes rather than number of derived comparisons. No arbitrary reviewer-confidence multiplier counts as calibrated evidence.

Before fitting, freeze a small finite parameter grid. Keep model complexity proportional to independent groups. Use leave-one-change-group-out validation for descriptive predictions, with any parameter selection nested inside training groups. Also examine leave-one-project-out portability where adequate. Do not split rows from one change across training and evaluation. Chronological forward validation is preferred when authentic timestamps establish ordering; filename order and file mtime cannot invent chronology.

## Evaluation and meaningful improvement

Report independent groups, labeled transitions, positive/negative counts, exclusions and coverage. For probability forecasts, use Brier loss and calibration against simple training-only prevalence. For review allocation, compare recall of accepted material findings at matched numbers of additional review assignments, retaining unknown outcomes. Prefer missing fewer consequential findings over saving a round, consistent with the owner's stated preference. An always-add-review baseline has perfect recall on observed positives and maximum review cost; report that trade-off rather than claiming to beat it at the same cost.

A candidate is meaningfully better only if it improves the strongest eligible simple baseline by at least 10% relative Brier loss **and** does not increase consequential misses at the predeclared review allocation. Require at least ten independent evaluable change groups and both outcome classes for a predictive claim. Report change-group bootstrap uncertainty or exact group-level paired comparisons; a non-positive lower bound on improvement means the result remains exploratory. With fewer groups or incomplete labels, produce an abstaining advisory and prospective data collection contract, not a learned stopping policy.

The same observations cannot serve both parameter discovery and independent confirmation. Existing hotspot windows and the previous weighting diagnostic are exploratory background only. Report every predeclared model, including failures. Do not continue parameter search until a favorable result appears.

## Integration constraints

A review-budget advisory may emit `additional-review-recommended`, `insufficient-evidence`, `required-review-still-pending`, or `cap-reached-escalate`, with reasons, uncertainty, evidence and suggested review focus. It never emits approval, early stop, lower bars, or increased caps. Any proposed extra review must name which current mandatory gate has already completed. Unknown evidence favors additional inspection within the owner's allowance, while remaining explicitly unknown.

Keep observed data, probabilistic estimates and policy defaults separate in output. Residual may supply component/force/outcome evidence and Paneweft can display the evidence; neither converts a weak label into a confirmed defect. Do not modify the live build-loop or architecture automatically in this pass.

## Where your setup differs

The `build-loop` skill already has reviewer diversity, mandatory fresh review, score bars, a pivot path and round caps. The experiment seeks useful information within those constraints. `test-quality` requires an independent failure mechanism; accepted reviewer findings alone are weaker evidence. `technical-excellence` requires unknowns and refusals to be explicit in the interface.

## Candidate actions

1. Validate the evidence corpus and label coverage before model fitting.
2. Compare conservative simple rules before spending time on K refinement.
3. Inspect fix-induced regressions as a separate mechanism for recommending another pass.
4. Keep any successful retrospective model in shadow mode until fresh outcomes are recorded.

## Sources

The owner's messages, 2026-11-17; local `build-loop/SKILL.md`, `references/review-v2.md`, `references/bars.md`; structured ledgers and independent patch/reply audits recorded under `corpus/` and `EVIDENCE-AUDIT.md`. External primary sources are collected separately in `METHODS.md` with publication dates and applicability limits.
