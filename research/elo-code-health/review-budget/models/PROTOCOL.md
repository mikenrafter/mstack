# Frozen forecast experiment

Frozen 2026-11-17 before fitting. Parent protocol controls evidence and deployment claims.

## Rows and target

Read ordinal > 1 rows with a literal Boolean `documented_accepted_consequential_discovery`. Null is excluded; integer counts are not labels. Reported discovery is a separate, explicitly selected sensitivity target and never substitutes automatically. Record input SHA256. The unit is an actual observed round. All rows from a `group_id` remain together; project is a validation partition only. No group or project lookup feature.

Read predictors only from `features_before_round`, plus ordinal known at assignment. The frozen feature vector contains an intercept, previous score centered at 5 and divided by 5, missing-score flag, previous verdict APPROVE/CHANGES/unknown one-hot, and ordinal 2/3/4plus one-hot. Unknown means any unrecognized or missing verdict. Scores outside [0,10] are missing. Group IDs order training deterministically but never imply chronology.

## Models

- `pooled`: training-row prevalence with Beta(1,1) smoothing, mu=(successes+1)/(rows+2).
- `lag_bucket`: bucket by prior verdict and ordinal stratum; p=(bucket successes+4mu)/(bucket rows+4). Shrinkage mass4 is fixed.
- `logistic`: intercept starts at logit(mu); all other coefficients0. Minimize mean Bernoulli log loss plus lambda/2 times the sum of squared NONINTERCEPT coefficients using400 full-batch gradient steps of size1/L, where L=0.25*max(training feature squared norm)+lambda. Lambda grid[0.1,1,10]. Predictions clipped only for numerical safety. Missing classes return training-only mu with `insufficient-training-classes` rather than dropping evaluation rows. The original unstable step0.5 is invalidated in OPTIMIZER-AMENDMENT.md; no other model choice changed.
- `anchored_elo`: online binary risk forecast, not zero-sum player Elo. Fixed benchmark B=1500, scale400. Every verdict/ordinal bucket starts R=B+400log10(mu/(1-mu)). A row's outcome y updates its bucket exactly once: R <- R+K*(y - 1/(1+10^((B-R)/400))). No invented opponents. At inference shrink p=(n*q+4mu)/(n+4), where q is the bucket's final Elo probability and n is the number of DISTINCT training changes observed in that bucket. Cold buckets return mu. Distinct-group n prevents repeated rounds from creating independent-evidence shrinkage.

Elo grid K0=[8,16,32,64], schedule=[fixed,decay]. Decay K=K0/(1+g/4), where g counts complete prior independent training groups. K stays fixed across every row of the current group. Training groups are ordered by SHA256(seed + group_id), with seeds[17,41,97]. Rows within a group use ordinal order. The main Elo prediction averages the three seed forecasts. Report each seed separately for order sensitivity, with the same nested parameter selection. Multiple real outcomes in a long change still move its rating; they count only once toward decay and evidence shrinkage. This is a modeling choice, not a claim of independent rounds.

## Validation and abstention

Outer leave-one-change-group-out predicts every eligible labeled row. Parameter selection is inner leave-one-change-group-out on the outer training rows only, minimizing mean row Brier loss. Break ties by the grid order above. Inner one-class training returns mu with abstention metadata. Outer one-class training does the same for EVERY model. No folds disappear. A model using this fallback cannot claim learned discrimination on that fold.

Main comparison uses identical rows for all models. Also run outer leave-one-project-out when at least two projects exist. Report it descriptively, including one-class fallback. No authentic timestamps are currently present; do not claim chronological forecasting.

Report row-average Brier for comparability with a random review opportunity and change-average Brier as a sensitivity to long changes. The paired interval resamples complete groups with replacement5000 times, seed20261117, computing row-weighted baseline-minus-model Brier in each resample. Report percentile95% bounds and raw group count. Selection of the strongest simple baseline uses outer descriptive scores and adds selection uncertainty; it is not independent confirmation.

Allocation budget is80% of evaluated opportunities. Rank descending predicted risk. If a score tie crosses the budget, assign equal fractional review probability to every row in that tie. This produces EXPECTED captured positives/misses, not an integer deployment action. Compare all policies at the same expected review budget. `always_continue` captures every observed positive at100% budget; it has no probability/Brier score.

## Interpretation

A meaningful candidate needs >=10 evaluable independent change groups, both outcome classes, >=10% relative Brier improvement over the strongest simple baseline, no more expected positive misses at the80% budget, and a positive lower paired bootstrap bound. Local data may not establish group independence. All claims remain retrospective accepted-finding proxy claims, with selection and label limitations. No calibrated probability claim and no live process edits. Fewer groups, one class, or missing evidence returns an abstaining research result.
