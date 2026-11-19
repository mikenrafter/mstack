# Public human-inspection matrix diagnostic

The fixed Chapman estimate underestimates the remaining study reference faults on average in all eight matrices. Depending on artifact/session, between 51.9% and 100% of pairs estimate less than half the actual remaining reference count. These are descriptive results on historical human requirements inspections, not evidence of improved LLM code review or a safe stopping rule.

All eight frozen matrices and all 602 unordered inspector pairs are retained. No parameters, review thresholds, or group filters were fitted. Pairs share inspectors, documents, and reference faults; 602 is a record count, not 602 independent experiments. No pair confidence intervals or significance claim are reported.

## Source and parsing

The unchanged [UMD PBR laboratory source](https://www.cs.umd.edu/projects/SoftEng/ESEG/manual/pbr_package/docs/total.cc) is read as data only. SHA256 is `696c9397d1213da986db451ab83c369e328e46d6d22afd9091c2ea066faffbcd`. Its declared matrix dimensions, fixed 35-column rows, `ID P` headers, and `ERR+2` computation loops establish two metadata fields followed by the declared reference-fault columns and checked zero padding. Perspective 0 is the usual NASA technique, 1 designer, 2 tester, and 3 user. Perspective 4 occurs in synthetic relabeling code and is not accepted as an observed participant category.

One exact source anomaly was identified before accepting results: `pg_jun` prints 29 header labels but declares 27 reference faults. The parent approved `EMPIRICAL-AMENDMENT.md` before estimator output was accepted. The exception applies only to the pinned source hash and exact stale header; the 27 declared columns are used and all six trailing values must be zero. Other malformed headers, constants, row widths, nonbinary detections, repeated participant IDs, and nonzero padding are refused. The source was never compiled or executed.

These columns describe seeded/reintroduced study reference faults. They do not establish an exhaustive population of every natural defect in the requirements. Inspector IDs are grouped as cohort plus ID across documents, with a cross-cohort identity crosswalk left unknown. This all-pairs diagnostic uses different grouping choices from published capture-recapture inspection analyses, so it is not an exact replication of a Briand experiment or a reading-technique comparison.

| Matrix | Inspectors | Reference faults | Pairs | Zero overlap |
| --- | ---: | ---: | ---: | ---: |
| atm_nov | 12 | 29 | 66 | 8 |
| atm_jun | 14 | 29 | 91 | 7 |
| pg_nov | 12 | 27 | 66 | 2 |
| pg_jun | 14 | 27 | 91 | 3 |
| a_nov | 12 | 18 | 66 | 31 |
| a_jun | 13 | 15 | 78 | 5 |
| b_nov | 12 | 15 | 66 | 46 |
| b_jun | 13 | 15 | 78 | 9 |

## Remaining reference faults

Actual remaining is the declared reference count minus the observed union. Estimated remaining is Chapman estimated total minus that same union. Error is estimate minus actual; a negative mean error indicates underestimation. Counts below are faults, not probabilities.

| Matrix | Actual mean / median | Estimated mean / median | Mean error | RMSE |
| --- | ---: | ---: | ---: | ---: |
| atm_nov | 16.94 / 17.00 | 8.06 / 6.00 | -8.88 | 12.95 |
| atm_jun | 16.58 / 17.00 | 6.65 / 4.67 | -9.94 | 12.93 |
| pg_nov | 17.94 / 18.00 | 5.19 / 3.50 | -12.75 | 14.44 |
| pg_jun | 13.47 / 14.00 | 6.66 / 5.00 | -6.81 | 9.75 |
| a_nov | 13.74 / 14.00 | 2.12 / 2.00 | -11.62 | 12.06 |
| a_jun | 4.23 / 4.00 | 2.65 / 1.69 | -1.59 | 4.73 |
| b_nov | 11.59 / 12.00 | 0.95 / 0.00 | -10.64 | 11.05 |
| b_jun | 4.13 / 3.00 | 1.59 / 0.62 | -2.53 | 4.14 |

The less-than-half denominator includes only pairs with a nonzero actual remainder. A zero estimate with reference faults still unseen is a failure of that estimate, not evidence of clean requirements. Zero-estimate frequency is also reported against every retained pair.

| Matrix | Less than half remaining | Zero estimate while unseen, all pairs | Zero estimate while unseen, nonzero-remainder pairs |
| --- | ---: | ---: | ---: |
| atm_nov | 39/66 (59.1%) | 3/66 (4.5%) | 3/66 (4.5%) |
| atm_jun | 67/91 (73.6%) | 5/91 (5.5%) | 5/91 (5.5%) |
| pg_nov | 52/66 (78.8%) | 3/66 (4.5%) | 3/66 (4.5%) |
| pg_jun | 56/91 (61.5%) | 4/91 (4.4%) | 4/91 (4.4%) |
| a_nov | 66/66 (100.0%) | 16/66 (24.2%) | 16/66 (24.2%) |
| a_jun | 40/77 (51.9%) | 20/78 (25.6%) | 20/77 (26.0%) |
| b_nov | 64/66 (97.0%) | 39/66 (59.1%) | 39/66 (59.1%) |
| b_jun | 57/78 (73.1%) | 34/78 (43.6%) | 34/78 (43.6%) |

## Total-population relative error

This separate target uses `(estimated total - declared reference count) / declared reference count`. It can look milder than relative error in the remaining faults because its denominator is larger. It must not be substituted for remaining-fault error.

| Matrix | Mean relative error | Median relative error | Relative RMSE |
| --- | ---: | ---: | ---: |
| atm_nov | -30.6% | -41.4% | 44.6% |
| atm_jun | -34.3% | -38.4% | 44.6% |
| pg_nov | -47.2% | -51.9% | 53.5% |
| pg_jun | -25.2% | -26.7% | 36.1% |
| a_nov | -64.6% | -66.7% | 67.0% |
| a_jun | -10.6% | -13.3% | 31.6% |
| b_nov | -70.9% | -73.3% | 73.7% |
| b_jun | -16.9% | -13.3% | 27.6% |

## Independent checks and limits

The parent recorded `MANUAL-ORACLE.md` before receiving parser counts. For `atm_nov` participants 1 and 2, the parser independently matches detection counts 9 and 7, overlap 3, union 13, declared reference count 29, actual remaining 16, estimated total 19, and estimated remaining 6. Remaining error is -10 faults, or -62.5%; total relative error is about -34.5%. This arithmetic check is one original source pair, not a representative sample or code-defect ground truth.

Six focused tests pass, including literal independent arrays, separate total/remaining arithmetic, zero-overlap and subset captures, malformed metadata/header/constant/width/padding cases, the pinned source exception, and the original-pair oracle. Qex test job `a4055c22-2df6-4300-ac44-144c82987ebc` used 22.7 MB and 0.1 CPU seconds. Three isolated mutations were caught by assertions: replacing declared reference count with observed union, ignoring nonzero padding, and confusing estimated total with remaining. Mutation job `5adaf105-4271-47aa-99ad-3b708c6252ea` used 23.2 MB and 0.2 CPU seconds.

The parser exports `normalized-matrices.json`, every pair in `empirical-pairs.jsonl`, and exact summaries/protocol hashes in `empirical-results.json`. Reproduce them with `python empirical.py`; the Python parser never invokes the C++ program.

Common detectability differences, shared blind spots, reviewer dependence, and the finite selected inspector pool can all matter here; this diagnostic does not identify which mechanism caused a given error. It supports treating residual-defect estimates as assumption-sensitive diagnostics and collecting independent frozen-snapshot detections. It provides no calibrated code-quality score, longitudinal architectural rating, causal review benefit, or optimal review-round recommendation.
