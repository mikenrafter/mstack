# Methods for recommending additional review

Research date: 2026-11-17. Audience: the owner and experiment implementer.

## Decision and evidence target

Predict the probability that one additional, specified review at an eligible stopping boundary will find a previously unreported material defect, independently confirmed against that boundary's code version. Predicting whether historically observed round N+1 contained an accepted finding is a useful preliminary association. It does not establish that adding round N+1 improves delivered code.

The deployment question is the net effect of extra review and any resulting fixes. Keep these observations separate:

- Newly discovered defects already present at the stopping boundary.
- Previously known defects still open or incorrectly fixed.
- Defects introduced after the boundary by review-driven fixes.
- Duplicate, speculative, stylistic, or out-of-scope findings.
- Review time, fix time, and independently verified outcomes.

A finding accepted by the orchestrator is provisional evidence. A failing reproducer, violated explicit contract, or independent causal assessment is stronger. A merged fix alone is not proof. Later independent inspection or tests should check both claimed fixes and regressions. Architecture findings need a named scenario, affected outcome, and a defensible causal path. Dependency or complexity scores alone cannot establish a defect.

The most useful first output is a recommendation for one next review, its focus, estimated yield, uncertainty, and evidence. An exact total-round recommendation assumes a reliable model of future findings and future fixes. Current data will rarely support that.

## Existing process is the baseline

The baseline must preserve the current [schema-2 build-loop schedule](/home/mini/.agents/skills/build-loop/references/review-v2.md). Passing rounds 1 or 2 still require a fresh tier-2 reviewer. A passing Fable round 3 or later completes the specified closing steps without tier 2. Pilots require Fable at round 2 and owner approval. First approval is therefore an invalid stopping baseline.

Only evaluate an additional-review recommendation after the actual mandatory path would stop. Mandatory unresolved defects remain process obligations. Keep the existing cap of three rounds per approach and five tier-1 rounds per phase. At a cap, recommend an owner decision or a pivot; a score cannot raise the cap. The research output must not modify the skills or silently extend the process.

For retrospective yield prediction, retain mandatory-round observations, but label them as mandatory and report them separately from optional stopping-boundary observations. A predictor trained mostly on rounds that follow rejection will overestimate the yield of review after a valid approval.

## What published evidence supports

Grades describe relevance to this experiment. A means established mathematical result or direct independently evaluated outcome. B means direct empirical evidence with material limits. C means adjacent observational evidence or an unreplicated case study. No located paper establishes a production policy for the owner's build loop.

| Source and date | Grade | Supported claim and limit |
| --- | --- | --- |
| [McIntosh et al., The impact of code review coverage and participation on software quality, MSR 2014](https://rebels.cs.uwaterloo.ca/papers/msr2014_mcintosh.pdf) | C | Qt, VTK, and ITK show an association between review coverage/participation and post-release defects after statistical controls. This supports measuring review exposure. It does not identify the causal benefit of another round or the right stopping rule. |
| [Bacchelli and Bird, Expectations, outcomes, and challenges of modern code review, ICSE 2013](https://www.microsoft.com/en-us/research/publication/expectations-outcomes-and-challenges-of-modern-code-review/) | C | Interviews, observations, surveys, and classified review comments show benefits beyond defects, including knowledge transfer and alternative solutions. Defect counts alone omit some architectural-review value. They remain the clearest first measurable target. |
| [Xiang et al., Cross-model LLM code review, 2026-07-22](https://arxiv.org/html/2607.21656v1) | B, preprint; single-pass, adjacent task | On 116 paired LiveCodeBench tasks, review improved one writer/reviewer combination from 71.6% to 89.7%, while the reverse direction reduced 91.4% to 82.8%. Reviewers emitted final programs without executing tests. This directly demonstrates that review interventions can repair and regress code. It does not generalize to multi-file architectural reviews, and its rewrite affordance differs from a review-only finding workflow. |
| [Zheng et al., MCR-Bench, 2026-08-27](https://arxiv.org/html/2608.27442v1) | B for state tracking; C for allocation policy, preprint | 2,269 multi-round tasks have defect cards and New/Open/Resolved/Reopened states. Candidate extraction uses an LLM, consistency filtering, then manual verification. Only multi-round PRs are included. Later-round detection and state-tracking performance generally degrades. Resolved issues repeatedly flagged and speculative over-review are documented errors. This supports versioned defect identities, not an unconditional benefit from extra rounds. Human checks validate extracted cards; missing defects and discarded uncertain cases remain limits. |
| [Huang et al., Large language models cannot self-correct reasoning yet, ICLR 2024](https://proceedings.iclr.cc/paper_files/paper/2024/file/8b4add8b0aa8749d80a34ca5d941c355-Paper-Conference.pdf) | C for code review | Experiments on intrinsic reasoning correction show that revisions can reduce accuracy and expose problems with oracle stopping and unmatched budgets. This motivates independent verification and equal-budget controls. It is not evidence about the current coding models or repository reviews. |
| [Nalbant, An evaluation of reinspection decision policies for software code inspections, 2005 master's thesis](https://open.metu.edu.tr/handle/11511/14858) | C, simulation | Compares reinspection policies in a Monte Carlo process covering inspection, reinspection, testing, and field use. Useful precedent for cost/quality decisions. Simulator conclusions depend on assumed detection and defect-generation processes and cannot validate a learned policy here. |
| [Pelanek, Applications of the Elo rating system in adaptive educational systems, Computers & Education 2016](https://www.fi.muni.cz/~xpelanek/publications/CAE-elo.pdf) | B for rating construction; C for transfer | A learner answering a question is treated as a match, jointly estimating learner ability and item difficulty. This supplies a closer analogy than ranking files against every other file. A reviewer/challenge interpretation still needs observable success and failure labels. |
| [Glickman, Example of the Glicko-2 system, 2022-03-22](https://www.glicko.net/glicko/glicko2.pdf) and [Herbrich and Graepel, TrueSkill, 2006](https://www.microsoft.com/en-us/research/wp-content/uploads/2006/01/TR-2006-80.pdf) | A for specified models; C for transfer | Glicko-2 maintains rating deviation and volatility and updates simultaneous rating periods. TrueSkill models skill uncertainty explicitly. Both offer alternatives to pretending K is uncertainty. Neither corrects biased labels or dependent observations automatically. |
| [Howard et al., Time-uniform, nonparametric, nonasymptotic confidence sequences, Annals of Statistics 2021](https://arxiv.org/abs/1810.08240) | A for inference under its assumptions | Confidence sequences permit valid repeated looks at accumulating evidence. An ordinary interval inspected repeatedly until success can mislead. A fixed evaluation endpoint is simpler for this pilot. Dependence, selection, and changing target distributions still require explicit treatment. |

## K, noise, and uncertainty

In ordinary Elo, K is the update magnitude, not a random distribution. The expected-result function is logistic. With scale s=400, rating difference d gives p=1/(1+10^(-d/s)); the update is K times the prediction residual. Rescaling ratings, s, and K together leaves equivalent probabilities. Treat K/s as the effective step size.

Separate four choices:

1. Observation noise: whether confirmed outcomes are reliable and how materiality is judged.
2. Update speed: how much a new independent observation changes the estimate, controlled by K.
3. Parameter uncertainty: how little evidence exists, represented by an interval or posterior distribution.
4. Temporal change: whether old observations should weaken as code and models change.

A small K smooths noisy labels but cannot remove systematic bias. A large K adapts rapidly but makes order and clustered observations influential. Do not inflate evidence by constructing all file pairs from one observation. Update once per independently observed change-round, or use a clearly defined cluster weight. Repeated findings on one defect and files touched by one fix are dependent. The effective evidence count is not the number of pairwise updates.

For this dataset, compare a few preregistered K/s values, a decreasing learning rate, and an explicit uncertainty baseline. Select parameters inside the training interval only. Tune no more than the evidence can support. Report sensitivity instead of choosing the best value on the final test interval.

If retaining Elo, a reviewer-versus-challenge experiment is defensible when challenges have known defects and clean controls. A reviewer detects the defect or does not; challenge difficulty and reviewer ability can then be jointly estimated. A no-finding result on ordinary code is not a verified clean outcome. Review yield is also affected by how many defects remain, so skill estimates alone do not determine whether another round is worthwhile.

An online logistic predictor for next-round yield may use Elo-like residual updates, but calling its scalar output a code-quality rating would overstate what it estimates. Its target is conditional review yield under the observed reviewer, brief, and process.

## Baselines and uncertainty-aware decisions

Use these in increasing complexity:

1. Follow the existing schedule. For optional allocation comparisons, also evaluate always add one eligible round at the same total cost.
2. Randomly choose eligible changes for extra review at a fixed budget. This is essential when any selection rule is compared with spending the same review budget indiscriminately.
3. Use the training-set prevalence of confirmed new material findings at equivalent stopping boundaries. A beta-binomial model provides a simple interval under exchangeability, with the prior and sensitivity stated.
4. Rank by changed lines or affected components, then by the previous round's independently validated new material yield. Use only information known at the decision boundary.
5. Fit a regularized logistic model with a small feature set. Add reviewer type, cross-boundary change, and unresolved uncertainty only if reliably recorded.
6. Compare Elo-like online residual updates or an uncertainty-aware rating against the same labels and budget.

Small samples favor simple pooled estimates. Hierarchical component/reviewer models need enough repeated observations to identify separate effects. A census of 21 ledgers and 75 rounds, as reported by the parallel extractor, is not 75 independent experiments and may contain few optional stopping boundaries.

Express the decision as expected avoided defect loss minus review cost, false-positive fix cost, and regression loss. Severity weights and acceptable cost are owner policy choices. Report sensitivity if those costs are unknown.

The owner's preference for extra review can be represented by a low benefit threshold and a conservative uncertainty rule. For example, request one additional review when the upper bound on material yield exceeds that threshold, then reassess within existing caps. That is an exploration policy: a high upper bound does not establish that benefit is likely. Report this distinction in the output. Unknown or unsupported cases can receive one explicitly budgeted evidence-gathering review. They must not generate an endless series of extra rounds.

Do not use an upper uncertainty bound to claim demonstrated improvement. Demonstrated improvement needs a held-out effect estimate and uncertainty that exclude an agreed practically negligible result.

## Independent validation

Freeze the split, labels, features, hyperparameter search, review budget, and success criterion before fitting. Split by complete change or ledger, ordered by time. Keep all rounds and duplicate findings from one change together. Fit normalizers, priors, component statistics, and model choices using earlier training data. Use future held-out changes once. Any subsequent tuning requires new held-out data.

For the retrospective feasibility test, report how many boundaries have a next round, how many lack one, why they continued, and which are mandatory. Evaluate the observed-next-round prediction only on observable cases. Keep its conclusion explicitly conditional on that selection. Do not label the absent next round as zero defects.

For a prospective pilot, all changes complete the existing mandatory path. At an eligible stopping boundary, record features and freeze the code hash. Randomize a bounded extra review among consenting eligible changes, stratified by risk, or add one shadow review to every sampled boundary for a ranking-only study. Shadow review estimates detection yield; it does not estimate the net effect of applying the fixes. Reviewers must not see the score or their allocation rationale. An independent adjudicator sees findings and code without the model recommendation. Adjudicate accepted and rejected findings, plus sampled no-finding cases.

Assess deployment benefit separately. Randomized extra review plus resulting fixes can be evaluated by a common independent final audit and regression tests applied to both groups. Avoid shipping known defects for the experiment; comparisons can occur on frozen branches. The final audit should use equal resources and stay blind to allocation. Track regressions introduced by fixes separately from defects already present at the boundary.

Compare policies at equal review cost. Primary allocation metric: independently confirmed new material defects discovered per extra review unit. Report the number of positive changes captured, misses, false-positive findings, review time, and fix-induced regressions. For probabilities, include Brier score or log loss and calibration. For a small sample, report raw counts and change-level intervals without claiming a stable model ordering.

The useful success criterion is better allocation of marginal review effort than the strongest simple equal-budget baseline, with independently supported findings and no concealed regression cost. Improving an old fix-title hotspot proxy does not meet this criterion.

## Bias checks

- Continuing after a bad review is selective. A high later-round yield may describe difficult changes already chosen for continued review.
- Final disposition can leak future information. Use the state available at the boundary for features; later adjudication belongs only in labels.
- Merged changes overrepresent work that eventually succeeded. Preserve failed, abandoned, and capped loops with their observation limits.
- Reviewer model, focus, scope, and tools vary. Record them; the next review is a specified intervention, not a generic round.
- One discovered defect can lead to several finding IDs, files, commits, or repeated round mentions. Deduplicate by causal defect and version.
- Adjudication on findings alone measures precision but misses defects no reviewer reported. Independently inspect sampled negatives.
- Retrospective architecture claims need revision-specific dependency information. Current dependency structure is unavailable historical evidence.
- Bootstrap or resample whole changes, not findings. With few changes, intervals may remain too wide for a deployment conclusion.

## Experiment order within this research window

1. Audit the ledger census and eligibility. If optional-boundary labels are absent, state the feasibility limit immediately.
2. Run the retrospective observed-next-round task with frozen chronological groups and simple baselines.
3. Compare a bounded Elo K sensitivity experiment only on the same target, split, and cost.
4. Check candidate findings independently on a small, blinded sample, including negatives and suspected fix-induced defects.
5. Decide whether evidence warrants a shadow advisory. If the evidence is too small or no model beats a simple baseline, retain the data protocol and report no demonstrated allocation improvement.

Broad literature searching ended after the primary sources above. The next useful work is adjudication and the frozen experiment, not a larger parameter search.
