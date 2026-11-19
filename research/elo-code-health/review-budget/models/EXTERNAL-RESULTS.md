# External reported-finding replication

2026-11-17. No meaningful improvement was demonstrated on the separately selected Edge prose-review chains.

The frozen pool contains five chains and 23 rounds. Excluding five first rounds and four unknown labels leaves 14 later review opportunities: 13 reported material findings and one explicit negative. All 14 opportunities lack previous numeric scores, so the frozen missing-score indicator is active. These are reported findings, not independently confirmed defects or accepted-finding outcomes.

Parameters were selected from the structured training snapshot before opening external data. The locked settings are logistic penalty 10 and Elo K=8 with group-count decay. The model receives no updates from external outcomes.

| Model | Brier loss | Expected positive misses at 80% review budget |
| --- | ---: | ---: |
| Training prevalence | 0.090614 | 2.600 |
| Prior verdict and round bucket | 0.095681 | 2.800 |
| Regularized logistic | 0.086796 | 2.800 |
| Anchored Elo, three-order average | 0.090876 | 2.800 |
| Elo order 17 | 0.090187 | 2.800 |
| Elo order 41 | 0.090884 | 2.800 |
| Elo order 97 | 0.091564 | 2.800 |

The logistic model improves Brier loss by about 4.2% relative to training prevalence. Its paired change-bootstrap interval for absolute Brier improvement is [-0.000840, 0.005680], which includes zero, and it misses more positives at the matched budget. The primary Elo forecast is slightly worse than prevalence. The seed sensitivities cannot be selected after seeing the external outcomes.

Always reviewing all 14 opportunities captures all 13 observed positives. Every 80% policy uses 11.2 expected reviews. Fractions describe randomized selection within tied scores, not literal fractional review runs. This pool's single negative gives little information about distinguishing changes that need further review. Five chains do not satisfy the ten-independent-group requirement, and common project code further limits independence.

The external procedure avoids the varying-prior artifact of pooling leave-one-change-out predictions. Training is fixed for every external opportunity. Cohort selection and source assembly were separate from structured model fitting, but outcomes remain historical reviewer assertions selected by the original review process. The experiment does not measure optional reviews at valid build-loop stopping boundaries, review-induced regressions, or architectural quality.

Structured training SHA256: `470561bf8f3bb036bc76fa872ed01371323207dd9457f4e7f65df4d4ef7ed38c`.

External corpus SHA256: `9436791a0d035bd1013c52aac0463f5d9009521c38ad06bacacd50c19ec6907b`.

Exact predictions, locked settings, intervals against each simple baseline, and exclusions are in `external-results.json`. No live review policy changed.
