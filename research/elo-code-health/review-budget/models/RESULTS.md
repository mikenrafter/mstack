# Forecast results

2026-11-17. Historical accepted-finding proxies; no live policy changes.

## Accepted material finding proxy

Input SHA256: `470561bf8f3bb036bc76fa872ed01371323207dd9457f4e7f65df4d4ef7ed38c`.

Inventory: {"eligible_rows": 39, "excluded": {"first_or_invalid_ordinal": 21, "unknown_label": 15}, "groups": 16, "label": "documented_accepted_consequential_discovery", "negative_rows": 9, "positive_rows": 30, "projects": 6}.

### group holdout

Strongest simple baseline by descriptive outer Brier is `pooled`.

| Model | Brier | Change-average Brier | Relative improvement vs best simple | Paired group 95% interval, baseline minus model | Expected misses at 80% budget | Fallback rows | Meets numeric gates |
| --- | ---: | ---: | ---: | --- | ---: | ---: | --- |
| anchored_elo | 0.192690 | 0.216258 | -0.2% | [-0.000585, -0.000001] | 7.800 | 0 | False |
| elo_seed_17 | 0.192528 | 0.216227 | -0.1% | [-0.000697, 0.000367] | 7.800 | 0 | False |
| elo_seed_41 | 0.192654 | 0.216249 | -0.1% | [-0.000700, 0.000100] | 7.800 | 0 | False |
| elo_seed_97 | 0.192893 | 0.216302 | -0.3% | [-0.001029, 0.000037] | 7.800 | 0 | False |
| lag_bucket | 0.210224 | 0.241869 | -9.3% | [-0.034778, -0.001851] | 7.800 | 0 | False |
| logistic | 0.193023 | 0.217928 | -0.3% | [-0.006241, 0.004133] | 7.800 | 0 | False |
| pooled | 0.192399 | 0.215930 | 0.0% | [0.000000, 0.000000] | 7.800 | 0 | False |

Always continue: {"captured_positives": 30.0, "expected_reviews": 39.0, "missed_positives": 0.0, "recall": 1.0}.
Random 80% allocation: {"captured_positives": 24.000000000000004, "expected_reviews": 31.200000000000003, "missed_positives": 5.9999999999999964, "recall": 0.8000000000000002}.

### project holdout

Strongest simple baseline by descriptive outer Brier is `pooled`.

| Model | Brier | Change-average Brier | Relative improvement vs best simple | Paired group 95% interval, baseline minus model | Expected misses at 80% budget | Fallback rows | Meets numeric gates |
| --- | ---: | ---: | ---: | --- | ---: | ---: | --- |
| anchored_elo | 0.244871 | 0.275777 | -0.9% | [-0.004838, -0.000172] | 7.800 | 0 | False |
| elo_seed_17 | 0.244347 | 0.275317 | -0.6% | [-0.004381, 0.000389] | 7.800 | 0 | False |
| elo_seed_41 | 0.244914 | 0.275837 | -0.9% | [-0.004902, -0.000193] | 7.800 | 0 | False |
| elo_seed_97 | 0.245357 | 0.276181 | -1.1% | [-0.005178, -0.000740] | 7.800 | 0 | False |
| lag_bucket | 0.253736 | 0.296664 | -4.5% | [-0.030670, 0.005630] | 6.800 | 0 | False |
| logistic | 0.246829 | 0.278545 | -1.7% | [-0.013528, 0.003938] | 7.800 | 0 | False |
| pooled | 0.242770 | 0.272585 | 0.0% | [0.000000, 0.000000] | 7.800 | 0 | False |

Always continue: {"captured_positives": 30.0, "expected_reviews": 39.0, "missed_positives": 0.0, "recall": 1.0}.
Random 80% allocation: {"captured_positives": 24.000000000000004, "expected_reviews": 31.200000000000003, "missed_positives": 5.9999999999999964, "recall": 0.8000000000000002}.

## Reported material finding sensitivity

Input SHA256: `470561bf8f3bb036bc76fa872ed01371323207dd9457f4e7f65df4d4ef7ed38c`.

Inventory: {"eligible_rows": 42, "excluded": {"first_or_invalid_ordinal": 21, "unknown_label": 12}, "groups": 16, "label": "documented_consequential_discovery", "negative_rows": 9, "positive_rows": 33, "projects": 6}.

### group holdout

Strongest simple baseline by descriptive outer Brier is `pooled`.

| Model | Brier | Change-average Brier | Relative improvement vs best simple | Paired group 95% interval, baseline minus model | Expected misses at 80% budget | Fallback rows | Meets numeric gates |
| --- | ---: | ---: | ---: | --- | ---: | ---: | --- |
| anchored_elo | 0.182774 | 0.216993 | -0.2% | [-0.000590, -0.000051] | 8.400 | 0 | False |
| elo_seed_17 | 0.182621 | 0.217024 | -0.1% | [-0.000677, 0.000286] | 8.400 | 0 | False |
| elo_seed_41 | 0.182759 | 0.217015 | -0.2% | [-0.000692, 0.000038] | 8.400 | 0 | False |
| elo_seed_97 | 0.182947 | 0.216945 | -0.3% | [-0.001012, 0.000049] | 8.400 | 0 | False |
| lag_bucket | 0.200457 | 0.240617 | -9.9% | [-0.033804, -0.002978] | 8.400 | 0 | False |
| logistic | 0.182870 | 0.218959 | -0.2% | [-0.005888, 0.004005] | 8.400 | 0 | False |
| pooled | 0.182451 | 0.216694 | 0.0% | [0.000000, 0.000000] | 8.400 | 0 | False |

Always continue: {"captured_positives": 33.0, "expected_reviews": 42.0, "missed_positives": 0.0, "recall": 1.0}.
Random 80% allocation: {"captured_positives": 26.4, "expected_reviews": 33.6, "missed_positives": 6.600000000000001, "recall": 0.7999999999999999}.

### project holdout

Strongest simple baseline by descriptive outer Brier is `pooled`.

| Model | Brier | Change-average Brier | Relative improvement vs best simple | Paired group 95% interval, baseline minus model | Expected misses at 80% budget | Fallback rows | Meets numeric gates |
| --- | ---: | ---: | ---: | --- | ---: | ---: | --- |
| anchored_elo | 0.226548 | 0.270793 | -0.8% | [-0.004177, -0.000348] | 8.400 | 0 | False |
| elo_seed_17 | 0.226033 | 0.270377 | -0.6% | [-0.003755, 0.000208] | 8.400 | 0 | False |
| elo_seed_41 | 0.226616 | 0.270897 | -0.9% | [-0.004282, -0.000380] | 8.400 | 0 | False |
| elo_seed_97 | 0.227001 | 0.271108 | -1.0% | [-0.004533, -0.000827] | 8.400 | 0 | False |
| lag_bucket | 0.236542 | 0.290780 | -5.3% | [-0.029502, 0.003054] | 7.400 | 0 | False |
| logistic | 0.227506 | 0.273226 | -1.3% | [-0.011506, 0.004201] | 8.400 | 0 | False |
| pooled | 0.224658 | 0.267880 | 0.0% | [0.000000, 0.000000] | 8.400 | 0 | False |

Always continue: {"captured_positives": 33.0, "expected_reviews": 42.0, "missed_positives": 0.0, "recall": 1.0}.
Random 80% allocation: {"captured_positives": 26.4, "expected_reviews": 33.6, "missed_positives": 6.600000000000001, "recall": 0.7999999999999999}.

## Frozen K grid sensitivity

| K and schedule | Accepted-proxy Brier |
| --- | ---: |
| K16_decay | 0.192974 |
| K16_fixed | 0.193694 |
| K32_decay | 0.193523 |
| K32_fixed | 0.194968 |
| K64_decay | 0.194552 |
| K64_fixed | 0.197462 |
| K8_decay | 0.192690 |
| K8_fixed | 0.193049 |

Every frozen K/schedule is worse than training-only prevalence on these observed rounds. These are sensitivity diagnostics; no candidate was selected from outer scores.

## Limits and verification

The folds contain selected observed reviews, including mandatory rounds. They do not estimate the causal benefit of adding reviews after the current mandatory path stops. Final acceptance is a weak outcome proxy; no result is an independently established defect reduction.

The first logistic implementation had an unstable fixed step for lambda10. Its outputs are quarantined under invalid-optimizer-v1. The corrected runs use the derived gradient bound in OPTIMIZER-AMENDMENT.md. Thirteen boundary and arithmetic tests pass; five specified incorrect implementations are caught, including the original optimizer defect.

The parameter grid was fixed before fitting. Nested training folds select parameters; all held-out rows remain evaluated, including one-class training fallback. Bootstrap intervals resample complete changes. Group independence and future transfer remain unproven.

The 16 group IDs do not establish 16 independent changes. Some phoe-nix groups share reviewed revisions. Project holdout has only six project clusters. No numerical gate alone establishes meaningful improvement under this unresolved dependence.

Pooling leave-one-group-out forecasts for allocation creates a ranking artifact. Each held-out group receives a different training-prior intercept. Holding out a mostly negative group raises its remaining-training prevalence, which can assign higher risks to that negative group. The cross-fold allocation columns are descriptive and cannot establish deployment allocation performance. Fixed-training external forecasts avoid that particular artifact.

The K distribution interpretation is analytical. A Beta(a,b) posterior for review yield has mean a/(a+b), and its log-odds rating is R=1500+400log10(a/b). A positive outcome changes R by400log10(1+1/a); a negative changes it by-400log10(1+1/b). The equivalent Elo K depends on the outcome as well as evidence strength. A single pre-outcome K generally cannot reproduce both Bayesian updates exactly. The lag-bucket baseline already uses this form of probability shrinkage. This derivation adds no new fitted model or performance claim.
