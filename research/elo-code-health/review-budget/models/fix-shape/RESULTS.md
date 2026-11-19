# Fix-shape diagnostic results

2026-11-17. Adding the frozen revision-shape features did not improve the forecast. This ends the diagnostic without another feature or threshold search.

This is a post-hoc exploratory analysis of the already examined structured corpus. No external chain outcomes enter fitting or evaluation. The accepted-finding target remains an acceptance proxy, not independently verified defects.

Inventory: {"excluded": {"first_or_invalid_ordinal": 21, "unknown_label": 15}, "feature_missing_rows": 0, "groups": 16, "negatives": 9, "positives": 30, "projects": 6, "rows": 39}.

All 39 labeled later rounds have observed pinned snapshot comparisons. The join verifies source identity, project, round, and recorded revision prefixes. Missing snapshots would use explicit missing flags; none were needed here.

## group holdout

| Model | Brier loss | Change-average Brier | One-class fallback rows |
| --- | ---: | ---: | ---: |
| augmented_logistic | 0.201659 | 0.225307 | 0 |
| lag_bucket | 0.210224 | 0.241869 | 0 |
| lag_logistic | 0.193023 | 0.217928 | 0 |
| pooled | 0.192399 | 0.215930 | 0 |

The strongest simple descriptive baseline is pooled. Relative Brier improvement is -4.8%; a negative value means worse loss.

Paired baseline-minus-augmented Brier interval: change-group resampling [-0.019993, -0.000119], project resampling [-0.023784, 0.000579]. These use 16 group IDs and six project clusters; independence is unestablished.

### Within-change allocation

| Forecast or fixed rank | Expected reviews | Expected captured positives | Expected missed positives |
| --- | ---: | ---: | ---: |
| always_continue | 39.000 | 30.000 | 0.000 |
| augmented_logistic | 31.200 | 23.000 | 7.000 |
| lag_bucket | 31.200 | 23.000 | 7.000 |
| lag_logistic | 31.200 | 23.000 | 7.000 |
| pooled | 31.200 | 24.000 | 6.000 |
| random80 | 31.200 | 24.000 | 6.000 |
| source_churn_only | 31.200 | 23.300 | 6.700 |
| stateful_then_churn | 31.200 | 23.300 | 6.700 |

## project holdout

| Model | Brier loss | Change-average Brier | One-class fallback rows |
| --- | ---: | ---: | ---: |
| augmented_logistic | 0.258386 | 0.291361 | 0 |
| lag_bucket | 0.253736 | 0.296664 | 0 |
| lag_logistic | 0.246829 | 0.278545 | 0 |
| pooled | 0.242770 | 0.272585 | 0 |

The strongest simple descriptive baseline is pooled. Relative Brier improvement is -6.4%; a negative value means worse loss.

Paired baseline-minus-augmented Brier interval: change-group resampling [-0.027217, -0.005789], project resampling [-0.029510, 0.004085]. These use 16 group IDs and six project clusters; independence is unestablished.

### Within-change allocation

| Forecast or fixed rank | Expected reviews | Expected captured positives | Expected missed positives |
| --- | ---: | ---: | ---: |
| always_continue | 39.000 | 30.000 | 0.000 |
| augmented_logistic | 31.200 | 23.000 | 7.000 |
| lag_bucket | 31.200 | 24.800 | 5.200 |
| lag_logistic | 31.200 | 23.000 | 7.000 |
| pooled | 31.200 | 24.000 | 6.000 |
| random80 | 31.200 | 24.000 | 6.000 |
| source_churn_only | 31.200 | 23.300 | 6.700 |
| stateful_then_churn | 31.200 | 23.300 | 6.700 |

## Interpretation

No frozen augmented forecast meets the 10% improvement threshold. The within-change allocations are descriptive. Every change receives an 80% expected budget, with uniform random selection at tied scores. They do not determine which changes deserve an additional review. Always continuing uses every observed opportunity.

The fixed ranks use source churn and stateful path names without fitted thresholds. A stateful path name is a scope hint. It does not prove a defect, dangerous architecture, or that a review fix caused an observed defect. Source churn can also describe legitimate complexity or review effort already selected for difficult changes.

The model adds five bounded revision features and five missing flags to the lag-score features. Both logistic models use the original regularization grid with nested training-only parameter selection and the corrected bounded gradient step. All observations share the same label coverage. No discarded fold or new outcome-derived feature improves the reported numbers.

Seven feature-boundary tests pass. Three deliberate mutations are caught: erasing unknown indicators, removing the source cap, and ignoring snapshot identity fields. The logarithm fixture uses an independent 40-digit Decimal oracle. Fixed 400-step optimization is the specified approximation, not a convergence guarantee.

The data do not establish independent change sampling. Project-cluster intervals are a sensitivity check with only six clusters. Historical observed reviews include mandatory reviews and selected difficult changes. This experiment does not identify causal benefit at a valid optional stopping boundary. No live policy or review cap changed.

Input hashes: `{"protocol": "f7ca2b69fcb4730670af4690122db7996fe53fc632552aafff7ac1d63d3b963b", "snapshot": "d8ac9bee540c25e43ef38d75302a3ed8d47df4d1a1baa67320ebd62d84db55da", "training": "470561bf8f3bb036bc76fa872ed01371323207dd9457f4e7f65df4d4ef7ed38c"}`.
