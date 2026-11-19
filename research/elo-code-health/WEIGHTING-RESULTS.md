# Elo block weighting results

Normalizing each file's block update raises Edge's captured future fix-touch share from 35.2% to 38.2%. Recent change frequency captures 56.0%. This diagnostic uses already-inspected windows, so it supplies no fresh validation or basis for choosing a deployment setting.

All arms use K=32, a logistic scale of 400, broad title labels and 25-commit blocks. Sequential ratings are reused from the original experiment. Simultaneous sum computes all pair updates from block-start ratings. Simultaneous average divides that summed update by the file's n-1 opponents. Formula and evaluation limits are in `WEIGHTING-PROTOCOL.md`.

The table pools the original final two windows by eligible future fix touches. Those windows are reused evaluation data in this diagnostic. Fractional counts arise from score ties at the selection boundary.

| Project | Sequential | Simultaneous sum | Simultaneous average | Recent change frequency | Historical fix count | Random expectation |
|---|---:|---:|---:|---:|---:|---:|
| Edge | 35.2% | 32.6% | 38.2% | 56.0% | 53.0% | 20.3% |
| Analytics | 25.5% | 35.5% | 24.5% | 28.4% | 29.5% | 21.1% |
| Qex | 11.9% | 13.6% | 22.0% | 42.4% | 41.1% | 21.0% |
| Diff-core | 33.3% | 30.3% | 33.0% | 47.5% | 33.8% | 20.6% |

Edge captures exactly 94/267 touches sequentially, 87/267 with simultaneous sum, and 102/267 with simultaneous average. Its recent change baseline captures 149.5897435897436/267 and historical fix count captures 141.58823529411765/267. The random expectation is 54.06826956826957/267.

| Edge window | Eligible touches | Sequential captured | Simultaneous sum captured | Simultaneous average captured |
|---|---:|---:|---:|---:|
| 80–90% | 229 | 87 | 72 | 86 |
| 90–100% | 38 | 7 | 15 | 16 |

The average arm's pooled improvement comes from the final small window. It captures one fewer touch in the preceding window. The summed arm beats recent change frequency on Analytics, but this finding follows inspection of the original results and cannot count as an independent success. No arm consistently wins across projects.

## What the weighting changes

Edge's 80% training prefix contains 21 blocks and 93,374 generated comparisons; its 90% prefix contains 23 blocks and 105,202 comparisons. The block at zero-based indices 250–274 touches 251 files and generates 31,375 comparisons, or 33.6% and 29.8% of those totals. Each participant has 250 comparison exposures there, versus 21 in a 22-file block. These counts describe update exposure; sequential cancellation and later updates mean they are not exact fractions of final influence.

The average arm bounds a file's absolute block change by K. This also slows learning substantially relative to applying K to every pair. The comparison therefore does not identify normalization independently from effective learning speed. Further K sweeps would be exploratory until a new evaluation period is frozen.

Simultaneous sum allows very large block steps. Edge ratings at the 80% boundary range from -3871.32 to 7972.11, compared with 1424.77 to 1570.79 for the average arm. The stable logistic avoids exponential overflow, but does not resolve overshooting from large summed updates. These magnitudes are arbitrary risk-rating units.

Every pair in a block still derives from the same fix/touch observations. Averaging does not create independent evidence or calibrate ratings as defect probabilities. Shared commit labels, rate-versus-volume mismatch and uncertain defect labels remain. This diagnostic qualifies the failure of the original construction without establishing a validated replacement.

## Verification and reproduction

Six focused tests pass. They cover hand-calculated two-file and three-file updates, frozen block expectations, conservation, inactive files, order invariance, empty/singleton blocks, extreme logistic gaps, actual runner arithmetic and future exclusion. Three in-memory mutations are detected: reversing outcomes, removing normalization and dropping the opposing update. No original analysis files are modified by the mutation checks.

```sh
qex submit --wait --cpu 1 --mem 256MB -- python3 -m unittest discover -s research/elo-code-health -p 'test_weighting.py'
qex submit --wait --cpu 1 --mem 256MB -- python3 research/elo-code-health/weighting.py
qex submit --wait --cpu 1 --mem 256MB -- python3 research/elo-code-health/check_weighting_mutations.py
```

`weighting-results.json` contains every window, per-block comparison counts, per-file exposures, rating ranges and input/code hashes. `weighting-mutations.json` records mutation outcomes. `weighting-run.json` records artifact hashes and queue job IDs. Subject repositories are read only during these runs. The next evaluation should freeze settings before new independently adjudicated outcomes arrive and measure actual inspection effort.
