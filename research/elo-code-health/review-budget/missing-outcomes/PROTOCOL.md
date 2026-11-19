# Missing-outcome sensitivity

Frozen 2026-11-17 before calculating the bounds. This is an exploratory sensitivity analysis after the structured results were examined. It changes no model, grid, target or policy.

Among the 54 observed later rounds, 39 have known accepted-finding proxy labels and 15 are unknown. Preserve all unknowns. Use the already frozen K8/decay Elo and training-only prevalence forecasts, holding each target change entirely out of training. Known-label predictions must agree with preserved outer predictions. For unknown rows, fit only the known outcomes from other groups and produce forecasts without filling an outcome. Hyperparameters do not change.

Calculate sharp best/worst differences in Brier loss over all binary completions of the 15 unknown outcomes, conditional on these fixed forecasts. For each unknown row, separately compute the contribution with outcome 0 and outcome 1. Summing each row's minimum/maximum gives the exact extremes because the difference is additive. Independently verify by enumerating all 32,768 completions. Also bound `0.9 * baseline loss - Elo loss`, the frozen 10% relative improvement condition. A bound is not a confidence interval.

Report simple prevalence bounds for structured and external observed later rounds. Unknown outcomes remain null in saved prediction records. These bounds cannot recover unperformed reviews, correct accepted-finding labels, establish independent groups, or estimate optional-review benefit. They condition on fixed forecasts and do not refit models for each hypothetical completion. Do not select a favorable completion or use the bounds to launch another tuning search.
