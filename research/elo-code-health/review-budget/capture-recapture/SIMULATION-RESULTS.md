# Capture–recapture assumption stress test

[C, synthetic diagnostic, 2026-11-17] A simple overlap estimate can be close on average under its assumptions and severely misleading when reviewers share hard-to-detect defects. This establishes a failure mechanism, not its frequency in real code review.

The frozen design ran 120,000 trials: six regimes, two initial populations (40 and 100 defects), 10,000 trials per combination. Seed 20261117 and per-stream hashes are retained in [raw results](simulation-results.json). The estimate of unseen defects is `(nA-overlap)*(nB-overlap)/(overlap+1)`.

For the initial population of 100:

| Regime | Mean actual unseen | Mean estimated unseen |
| --- | ---: | ---: |
| independent | 25.04 | 24.99 |
| unequal-abilities | 18.71 | 18.63 |
| shared-difficulty | 40.97 | 1.96 |
| common-blind-spot | 51.99 | 1.99 |
| dependent-reports | 43.71 | 0.90 |
| changed-snapshot | 30.00 | 1489.82 |

Different reviewer abilities alone do not break the homogeneous-defect model. Shared difficulty does: both reviewers repeatedly find easy defects and miss the same hard ones. Correlated reports make overlap still less informative. The changed-snapshot case deliberately removes detected defects and introduces ten new ones; it is ineligible for the closed-population estimator, and the large estimate illustrates misuse rather than estimator performance under valid conditions.

Even favorable mean behavior is not casewise assurance. At population 40 in the independent regime, mean actual unseen is 9.96 and mean estimated unseen 10.02, but 17.33% of trials estimate less than half the actual remainder. Neither a small estimate nor a zero estimate licenses stopping.

Four focused tests cover hand arithmetic, empty/identical captures, deterministic streams and changed-population accounting; three deliberate mutations are caught. The [protocol](SIMULATION-PROTOCOL.md) fixes assumptions and applicability. No parameters were selected from these outcomes. No empirical reviewer sensitivity, code-quality improvement or optimal round count is established.
