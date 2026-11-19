# Optimizer correction

2026-11-17, before any external replication data was opened. The parent and an independent auditor identified that fixed gradient step0.5 is unstable for the predeclared lambda10 candidate. The quadratic penalty alone multiplies a coefficient by -4 each step, so divergent coefficients can corrupt the baseline comparison. This is an implementation defect, not evidence that regularization or logistic forecasting fails.

Preserve the original outputs under `invalid-optimizer-v1`. Do not interpret them. Replace the fixed step with1/L, where L=0.25*max(training feature squared norm)+lambda. Each Bernoulli logistic Hessian is bounded by0.25*x*x-transpose, and the penalty Hessian has spectral norm at mostlambda. The stated L therefore bounds the full objective's gradient Lipschitz constant. The step1/L provides descent for this convex differentiable objective. Keep400iterations, the feature vector, every parameter grid, split, seed, label, and comparison unchanged.

Add a balanced two-row fixture with score and outcome covariance. At lambda10 the sole nonzero coefficient approaches0.04878072; the penalized objective must decrease from the intercept-only log(2), remain finite, and decrease along all iterations. Rerun all nested fits and reselect external settings from structured training only before external evaluation.
