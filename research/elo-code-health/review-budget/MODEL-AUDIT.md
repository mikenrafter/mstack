# Forecast model audit

The logistic baseline has a numerical optimizer defect that must be corrected before interpreting comparisons. Its strongest regularization setting diverges on a simple balanced fixture, while all 11 supplied tests pass. Group splitting, literal Boolean label handling, shared test coverage, Elo evidence counts, and fractional allocation follow the stated design on inspection.

This audit inspected `models/forecast.py`, `models/test_forecast.py`, `models/PROTOCOL.md`, and the parent `PROTOCOL.md` on 2026-11-17. It did not read external-corpus labels or model performance artifacts. Tests and a synthetic numerical probe ran through qex with one CPU and a 128 MB claim. No author files were changed.

Reviewed source SHA256: `forecast.py` = `19ede0626eb80932224b9fcb6093b2ed0179ab402a8677fcf5deb5e603aa3141`; `test_forecast.py` = `9d537bec6980fd46fd29dac18dc98461a893329e9f25fa57c04f73ffc4199086`; model protocol = `2a1ece3b44c346403112c899bc85b1ab6b0908017ac58d7bcc51afc7aed69447`. These identify the pre-correction implementation. During the audit, the extractor agent sent an unsolicited summary of external negative-label cases. Those files and model results were not opened, and the requested external label check was declined.

## Required fix

**R1, correctness, `models/forecast.py:134-145`.** The logistic penalty grid includes 10, but every gradient step has size 0.5. For a nonintercept coefficient, the penalty alone contributes a recurrence factor of `1 - 0.5 * 10 = -4`. A nonzero score/outcome covariance starts a rapidly growing alternating sequence. The bounded likelihood gradient cannot stabilize it. The routine therefore fails its declared task of minimizing penalized Bernoulli loss.

`audit_probe.py` uses eight balanced synthetic changes, all at ordinal 2 and prior verdict CHANGES. Even-numbered changes have prior score 0 and outcome false; odd-numbered changes have score 10 and outcome true. It traces the actual function's final coefficients without altering them. The lambda-10 fit produces maximum absolute coefficient `3.643300471237133e239`, an overflowing penalized objective, and predictions `[1.0, 9.85967654375977e-305]` against outcomes `[0, 1]`. Brier loss is 1.0. An intercept-only solution has objective `log(2) = 0.6931471805599453`, so the failed objective is worse than an immediately available valid solution.

An isolated temporary copy using step size `0.5 / (1 + penalty)` produces predictions `[0.48780723676820537, 0.5121927632317946]` and Brier `0.23795590024343197`. Lambda 0.1 and 1 produce the same forecasts as the original to displayed precision. The temporary comparison is diagnostic, not a selected research model.

Use a mathematically bounded step, with the bounded feature norm accounted for, and add a regression that checks the penalized objective is finite and improves over the intercept-only solution for every frozen penalty. Avoid pinning arbitrary exact coefficients. Correct the frozen optimizer description explicitly and quarantine prior result files as invalid optimizer runs. Keep the model/penalty grid fixed. This is an implementation correction, not permission to search for a favorable result.

The parent independently identified the same candidate and challenged the audit to demonstrate nonzero covariance and objective failure. The synthetic probe answers both. Qex job `7fb535c4-6ed1-4ee5-b1ec-9539a8f45527` completed successfully using 22.2 MB and 0.1 CPU seconds. `python -m unittest test_forecast -v`, qex job `11e6299b-86bf-416d-996e-68cc90a823e9`, passed all 11 existing tests. Their current coverage does not exercise logistic optimization.

## Verified boundaries

| Boundary | Source | Assessment |
| --- | --- | --- |
| Unknown labels | `forecast.py:59-78` | `type(outcome) is bool` excludes nulls and numeric zero/one. Ordinal validation excludes Boolean ordinals and first rounds. Duplicate eligible group/ordinal identities fail. Existing tests exercise the null/count boundary. |
| Predictor boundary | `forecast.py:38-56` | Only previous score/verdict and ordinal enter the feature vector. Final dispositions and current outcomes do not enter it. The existing mutation test changes future fields and checks the literal expected vector. Authentic availability of upstream `features_before_round` remains an extractor responsibility. |
| Outer group exclusion | `forecast.py:106-112, 231-245` | All rows of a held change are removed before fitting and before parameter choice. Project holdout also removes all rows of its held project. The group-fold unit test checks a multi-round change. |
| Nested selection | `forecast.py:177-189, 234-235` | Inner folds receive only outer training rows. Each configuration's score uses all inner-held rows; one-class folds return the training prior instead of disappearing. Selection minimizes row-average Brier as declared. Inspection found no outer-test label input to parameter choice. There is no integration regression for this nesting boundary yet. |
| Common model coverage | `forecast.py:236-260` | Every model predicts the same outer test rows. All one-class or empty training folds return one prior value per test row with fallback metadata. No model-specific test-row omission was found. |
| Elo evidence count | `forecast.py:153-166` | Every genuine training round updates its bucket once. Decay counts complete preceding groups; bucket shrinkage counts a set of distinct changes. A long change can still move the rating repeatedly, as the protocol explicitly states. The evidence count is not the number of round rows. |
| Bootstrap sampling unit | `forecast.py:212-225` | Complete groups are sampled with replacement; all their rows are retained, including repeats of a sampled group. The aggregate is row weighted as declared. A long change therefore contributes more loss within each sample, and change-average Brier is reported separately. |
| Allocation ties | `forecast.py:192-209` | A tie crossing the 80% budget receives equal fractional review probability. The existing independent arithmetic test checks a partial tie, a fully tied pool, and zero budget. This is expected capture, not a claim about an integer deployment schedule. |
| Baseline identity | `forecast.py:261-275` | The best simple baseline is selected descriptively from outer Brier scores and named in output. All candidates use its predictions for paired comparisons. Always-continue and random-80% allocation are also returned. No undisclosed baseline switch was found. |

## Interpretation limits

`paired_interval` resamples already fitted out-of-fold predictions. It estimates conditional variation across observed change groups. It does not refit parameter selection or reselect the strongest baseline inside bootstrap samples, and overlapping training folds are not independent experiments. The protocol acknowledges selection uncertainty; the interval should retain that descriptive interpretation. A positive lower endpoint alone cannot establish independent confirmation.

The three seed-specific Elo diagnostics use the configuration chosen for the averaged three-seed model in each outer fold. This supports order sensitivity under a shared configuration. It should not be described as separately tuning each seed's best model. The frozen wording "same nested parameter selection" is compatible with the implementation but could be read either way.

`main` records corpus and protocol hashes at lines 303-304 but currently does not record the executable's hash. The required optimizer correction changes the model implementation while retaining the same corpus. Save the old source hash alongside quarantined artifacts and include the new source hash with corrected artifacts so the result is reproducible.

This inspection found one required implementation correction. It does not certify the labels as independent defects, establish temporal forecasting, or validate the optimal number of architectural reviews. Those are separate evidence and prospective-evaluation questions.
