# What the missing outcomes could change

## Top findings

- [C, exact sensitivity] The 15 unknown accepted-finding labels permit 32,768 binary completions across 54 observed later reviews.
- [C, exact sensitivity] Some completions reverse the very small Elo-versus-prevalence loss difference.
- [C, exact sensitivity] No completion lets the fixed K8/decay forecasts reach the frozen 10% relative Brier improvement target.
- [C, coverage] Accepted-finding prevalence among these selected observed rounds is bounded between 55.6% and 83.3% without assuming missingness is random.
- [D, decision] Better labels remain useful, but completing these labels alone cannot validate this fixed forecast as the desired improvement.

The baseline and Elo forecasts hold each target change out of training. All 39 known-label forecasts match the preserved evaluation. The 15 unknown labels remain null in saved predictions. For sensitivity only, the calculation evaluates every possible binary completion without treating any completion as observed truth.

| Fixed-forecast quantity | Worst completion | Best completion |
| --- | ---: | ---: |
| Baseline Brier minus Elo Brier | -0.000468 | +0.000154 |
| 0.9 × baseline Brier minus Elo Brier | -0.029406 | -0.015962 |

Positive values favor Elo; the second row must be nonnegative to reach the 10% threshold. Its upper bound remains negative. An independent enumeration of all 32,768 completions agrees with the additive extrema to numerical tolerance.

These are exact bounds conditional on fixed forecasts, not confidence intervals and not a refitted-model analysis. A different model trained after observing the missing labels could behave differently; this analysis makes no claim about it. The selected reviews include required rounds. Unperformed reviews and optional stopping decisions are outside the data. Accepted fixes remain a proxy for material defects, and change-group independence remains unestablished.

Three arithmetic and unknown-label tests pass. Three isolated wrong implementations are caught: treating unknowns as negatives, reversing the lower extreme, and ignoring the relative-improvement factor.

## Where your setup differs

Your `test-quality` guidance asks for an independent oracle. The full-completion calculation computes complete squared losses separately from the row-wise bound. Its small hand-computed fixtures also reject the plausible wrong implementations above.

## Candidate actions

1. Keep all missing outcomes visible; they affect descriptive conclusions even though they cannot rescue this fixed forecast's improvement threshold.
2. Collect new evidence at authentic optional boundaries rather than repeatedly tuning this sample.
3. Preserve the failed forecasts as baselines for a separately frozen future experiment.

## Sources

Local `models/structured-training.jsonl`, SHA256 `470561bf8f3bb036bc76fa872ed01371323207dd9457f4e7f65df4d4ef7ed38c`; preserved `models/accepted-results.json`; `PROTOCOL.md`, `bounds.py`, `results.json`, `test_bounds.py`, and `mutation-results.json` here, executed 2026-11-17.
