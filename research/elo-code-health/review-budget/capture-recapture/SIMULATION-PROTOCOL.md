# Capture–recapture stress test

Frozen 2026-11-17 before implementation or simulated results. This tests a simple estimator's assumptions, not empirical code-review performance. No K tuning, model selection, live review or stopping policy is introduced.

Use the Chapman two-list population estimate `(nA+1)*(nB+1)/(overlap+1)-1`. Subtracting the observed union gives estimated unseen defects `(nA-overlap)*(nB-overlap)/(overlap+1)`. Formula and closed-population, capture and reporting assumptions: [recapr's first-party documentation](https://search.r-project.org/CRAN/refmans/recapr/html/NChapman.html), retrieved 2026-11-17, citing Chapman (1951). Software-specific evidence is reviewed separately in `MEMO.md`.

Freeze N=40 and N=100 actual synthetic defects, 10,000 independent trials per scenario and seed 20261117. Six scenarios:

1. Fixed snapshot, homogeneous independent reviewers: each detects each defect with probability 0.5.
2. Fixed snapshot, different reviewer abilities: probabilities 0.25 and 0.75, independent conditional on each defect.
3. Fixed snapshot, shared difficulty: half the defects have detection probability 0.9 for both reviewers, half 0.1; detections independent conditional on defect difficulty.
4. Fixed snapshot, common blind spot: half have detection probability 0.8 for both reviewers, half are undetectable by either.
5. Fixed snapshot, dependent reports: A detects with probability 0.5. For each defect B copies A's detection with probability 0.75, otherwise independently detects with probability 0.5.
6. Changed snapshot: A detects with probability 0.5; its detected defects are removed, exactly 10 new defects are introduced, then B independently detects each remaining defect with probability 0.5. This deliberately violates the closed-population assumption and is ineligible for the estimator.

For fixed snapshots, actual unseen defects are N minus the union. For changed snapshots, actual unseen defects belong to the post-fix population and were missed by B. Report mean true unseen, mean naive estimate, bias, fraction estimating less than half the actual unseen count, zero-estimate-with-unseen frequency, and zero-overlap frequency. A naive zero is never interpreted as a safe stopping decision. Always preserve the explicit assumption violation. Do not compare or choose estimators after seeing results.

Retain scenario parameters, deterministic per-scenario seeds, trial-stream hashes and first-five examples. Verify hand-computed overlap arithmetic, empty/identical capture cases, and changed-population accounting before running. Check a few deliberately wrong implementations. The simulation can illustrate failure mechanisms and guide capture design. It cannot establish reviewer sensitivity, defect prevalence, optimal rounds, or superiority to the failed Elo forecasts on real projects.
