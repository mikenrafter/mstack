# Fix-shape forecast diagnostic

Frozen 2026-11-17 before examining feature/outcome correlations. This is one post-hoc, explicitly exploratory diagnostic motivated by independently inspected review-induced defects. The earlier structured outcomes have already been examined. No external confirmation, new Elo model, adaptive threshold search, or live policy change is authorized.

## Inputs and joins

Use the preserved structured-training.jsonl accepted-finding target, ordinal > 1, literal Boolean labels only. Join snapshot-features.jsonl by group_id and ordinal. Require exact matching project, round, and source path/hash. An observed snapshot's full target/base SHA must match the recorded target/previous SHA prefixes. Refuse a mismatched or duplicate key rather than silently joining a different revision. Missing snapshots remain unknown with explicit indicators; they do not exclude observations. Record both input hashes and a preserved feature snapshot.

## Frozen features

Append these five values and five corresponding missing flags to the existing lag score/verdict/ordinal features:

- Source churn: min(log1p(source_changed_lines)/log1p(10000), 1).
- Source file span: min(log1p(source_files)/log1p(100), 1).
- Test share: test_changed_lines/(source_changed_lines+test_changed_lines+1), capped at 1.
- Stateful-path presence: 1 when state_path_files > 0, otherwise 0.
- Same reviewed snapshot: a literal Boolean feature.

Negative, nonfinite, Boolean, absent, or unobserved numeric inputs are missing. Missing values use zero plus a missing flag; observed zero uses zero and a clear flag. The test share is missing if either required count is unknown. Path names are coarse hints and do not establish an architectural or concurrency defect. All transforms are fixed, bounded, and training-independent.

## Models and validation

Compare training-only Beta(1,1) pooled prevalence, fixed lag bucket, corrected lag-score logistic, and augmented logistic. Both logistic models select lambda from [0.1,1,10] using nested complete-change holdout on training rows only. Keep the corrected global Lipschitz gradient step and 400 iterations. No grid changes. Every model evaluates the same opportunities. One-class training returns the same training prior with explicit fallback status; no folds disappear.

Primary descriptive evaluation is outer leave-one-change-group-out. Also report leave-one-project-out sensitivity. Report Brier loss, change-average loss, and paired baseline-minus-augmented Brier intervals using 5,000 resamples of complete change groups and, separately, projects; seed20261117. Six project clusters give weak uncertainty estimates. Group identities do not establish independent changes, and no result constitutes independent confirmation.

Allocation is a within-held-out-change diagnostic at an 80% budget per change, using equal fractional probability at cutoff ties. Report pooled, lag bucket, lag-score logistic, augmented logistic, source-churn-only, and stateful-first-then-source-churn ranks. The two fixed ranks have no fitted thresholds or calibration claims. A missing rank is tied below known values, and a separate coverage count is reported. Compare equal expected review budgets; always-continue uses all opportunities. Do not treat pooled cross-fold global ranks as deployment performance.

State whether the augmented model improves Brier loss by at least 10% against the strongest simple descriptive baseline, whether paired group/project intervals exclude zero, and whether within-change allocation has more expected positive misses. Even if those checks pass, the outcome is post-hoc and independent change sampling remains unestablished. A negative result ends this diagnostic without further model or threshold searches.
