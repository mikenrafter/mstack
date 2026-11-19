# Code health ranking experiment protocol

## Top findings

- [C, design] Edge is the primary subject because the available mainline contains substantially more fix-related history than the smaller integration projects. Exact revisions and counts will be recorded in `inventory.json`.
- [D, hypothesis] Pairwise ratings might improve prioritization of files for investigation. This experiment can reject that hypothesis for its historical proxy; it cannot establish defect detection accuracy.
- [C, method] The observable target is future involvement in commits with fix-related titles. A touched file is not necessarily defective. No fix-related commit is not evidence of correctness.
- [C, method] Predictions use only earlier first-parent commits and files present at the prediction revision. Holdout results must be reported even when unfavorable.
- [D, hypothesis] Repeated changes across directories may identify architectural investigation targets. They do not prove a boundary should move.

## Schedule and stopping rules

Written before running the ranking experiment, 2026-11-16. These are execution stages, not unattended calendar jobs. Run the bounded historical stages now. Behavioral intervention requires a separate executable scenario and remains a follow-up if this pass cannot supply one.

| Stage | Budget | Work and output | Completion condition |
|---|---|---|---|
| E0 | 15 minutes | Inventory Edge, Analytics, Qex, Diff-core, Residual, Paneweft; select and pin revisions | `inventory.json`, source selection and timestamp limitations recorded |
| E1 | 45 minutes | Implement temporal replay and independent correctness fixtures; audit a deterministic sample of label candidates against patches | Passing focused tests; `label-audit.md` identifies label ambiguity |
| E2 | 30 minutes | Replay Edge, Analytics, Qex, Diff-core at five successive boundaries | `results.json` and `windows.csv`, including failures and sparse windows |
| E3 | 20 minutes | Change Elo update constant, comparison order, fix-label definition; run no-signal controls | Sensitivity and controls recorded; no settings selected from holdout |
| E4 | 30 minutes | Find recurring cross-directory change pairs; check current Edge relative imports; inspect candidate boundaries | Evidence-linked investigation candidates, no automatic code changes |
| E5 | 20 minutes | Export an evidence bundle for Residual/Paneweft integration and show results | Versioned JSON with observed/inferred separation, HTML chart, report |
| Follow-up | 1 working day | Choose one boundary, define executable stressor outcomes, compare existing and candidate implementations on shared and held-out scenarios | Measured behavioral evidence before promoting any architecture change |
| Prospective check | 4 weeks after installing a collector | Freeze weekly predictions and independently adjudicate subsequently confirmed defects | Compare captured defects at equal review time; retire ratings if they do not help |

Budgets are upper bounds, not promises of statistical power. No builds, model API calls, source modifications in subject repositories, remote fetches, PRs, or automatic architectural changes in E0–E5.

## Fixed evaluation design

- Pin available local refs, preferring `upstream/main` for Edge, Analytics and Diff-core. Qex uses its owner working branch, explicitly recorded. Residual and Paneweft are inventory/integration subjects only. No claim that cached refs equal the latest remote state.
- Replay commits in first-parent topological order, including merge diffs against the first parent, once per mainline integration. Commit timestamps are descriptive only. Source files come from the prediction tree, excluding tests and generated files. Renames are treated as deletion/addition and reported as a limitation.
- Use the first 50% of commits as initial history. Predict the next 10% at each of 50%, 60%, 70%, 80%, and 90%. The last two windows are held out. Do not tune settings after viewing these results.
- Primary label: title contains `fix`, `fixes`, `fixed`, `bug`, `regression`, `race`, `deadlock`, or `crash` as a word. Strict sensitivity: conventional `fix:` / `fix(scope):` or merge title containing `/fix/`. Titles and branches are noisy weak labels, not verified bug reports.
- Primary metric: proportion of future fix-related source-file touches captured by selecting 20% of eligible source files. Each file contributes once per future fix commit. Also report unique affected-file recall, precision, sample size and cold-start touches outside the eligible set. Equal files is a budget proxy; it is not equal review time.
- Resolve score ties by fractional selection of the tied group. Report a random-selection expectation under the same budget. This avoids favorable filename ordering.
- Baselines: all-history fix count; last-100-commit fix count; last-100-commit touch count; Laplace-smoothed all-history fix/touch rate.
- Elo experiment: in non-overlapping 25-commit training blocks, compare files touched in that block by their smoothed block fix/touch rate. Higher rate wins, equal rates draw. Initialize risk ratings at 1500; higher means greater observed fix involvement. Update both contestants with standard Elo, K=32. Only files observed in that block play. This is an aggregation of weak labels, not a direct measure of latent quality.
- Sensitivities: K=16 and K=64; five seeded within-block match permutations; strict labels. Primary settings remain unchanged.
- Controls: constant ratings must equal random expectation; seeded permutation of training fix labels with fixed future labels tests whether apparent benefit persists without chronological training signal. A single control is diagnostic, not a significance test.
- Report per-window and pooled metrics. Windows within a repository are dependent, and two holdout windows cannot support strong significance claims. Do not equate proxy predictive success with causal repair benefit.

## Architectural evidence and integration

Use the last 200 source-touch commits for recurring file pairs, excluding commits touching more than 20 source files. Require at least three cochanges. Record support, conditional cochange probabilities, directories, example commits and resolvable direct imports. Cross-directory changes are candidates for investigation, not established defects or fusion/fission recommendations. Current imports must never enter historical predictions.

Each export carries project/revision, evidence kind, provenance commits, uncertainty/limitations, and a suggested question. Residual force mappings require inspected outcomes; cochange alone cannot create a validated stressor or alter its binary matrix. Paneweft should display the evidence and provenance, without presenting a rating as a calibrated defect probability.

## Where your setup differs

The `test-quality` skill asks whether a test detects a plausible wrong implementation. The experiment needs the same discipline for its evaluator: manually computed budget examples and future-leakage fixtures precede real runs. The `technical-excellence` skill favors explicit invariants, so the evidence export distinguishes observations from hypotheses and keeps subject repositories read-only. These checks measure analysis correctness, not product correctness.

## Candidate actions

1. Run the historical comparison before building a rating service. Cost is small and an unfavorable result prevents unnecessary infrastructure.
2. Audit weak labels before interpreting predictive metrics. Misclassified maintenance commits can dominate the apparent signal.
3. Prepare one behavioral boundary experiment only after inspecting its evidence. Favor a concrete failure outcome over a broad quality score.

## Sources

- Chen et al., 2025, [CodeRankEval](https://jcst.ict.ac.cn/cn/article/cstr/32374.14.s11390-025-5514-9). A, published benchmark; code-solution ranking, not longitudinal repository health.
- 2021, [Weighted software metrics aggregation and its application to defect prediction](https://link.springer.com/article/10.1007/s10664-021-09984-2). A, published ranking evaluation; motivates baselines and effort-aware evaluation.
- Xiao et al., 2016, [Identifying and Quantifying Architectural Debt](https://www.cs.drexel.edu/~yc349/papers/2016/icse2016-ArchDebt.pdf). B, seven-project observational evaluation; motivates historical coupling analysis, not causal rerouting.
- Zheng et al., 2026-02-05, [When Elo Lies](https://arxiv.org/abs/2602.05891). A, controlled preprint evaluation in competitive programming; motivates sensitivity checks. Transfer to this application is a hypothesis.
