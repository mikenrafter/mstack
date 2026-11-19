# Elo and additional code review research

Start with the [review-budget report](review-budget/REPORT.md) and [completed experiments and proposed schedule](review-budget/SCHEDULE.md). The bounded research window is 2026-11-17 07:06:26–09:06:26 UTC. All model work uses Codex.

The tested Elo updates do not improve accepted-finding forecasts over a simple prevalence baseline. No calibrated count of extra rounds, code-quality rating or automated architectural rerouting is justified. The useful implementation is an object-snapshot evidence collector, plus a concrete longitudinal finding/fix/regression graph.

| Need | Artifact |
| --- | --- |
| Main result and limits | [Review-budget report](review-budget/REPORT.md) |
| K, uncertainty and identification | [Methods memo](review-budget/uncertainty/MEMO.md) |
| Forecasts and frozen K grid | [Results](review-budget/models/RESULTS.md) |
| Build-loop evidence capture | [Collector usage](review-budget/advisory-prototype/README.md) |
| Paneweft and Residual evidence | [Historical case graph](review-budget/evidence-graph/README.md) |
| Published residual-defect methods | [Capture–recapture literature](review-budget/capture-recapture/MEMO.md) |
| Public inspection-data coverage | [Coverage diagnostic](review-budget/capture-recapture/COVERAGE-RESULTS.md) |
| Architectural hotspots and rerouting | [Research and bounded comparison design](review-budget/ARCHITECTURE.md) |
| Next proposed experiment | [Consolidated schedule](review-budget/SCHEDULE.md) |

The earlier [file-hotspot report](REPORT.md) and [pair-weighting diagnostic](WEIGHTING-RESULTS.md) are preserved as separate exploratory stages. Their source-activity outcomes differ from the later optional-review question. Neither is a current production defect detector.

Research artifacts remain local. Subject repositories and live review policy were not changed. The collector never executes reviews or grants approval. Future prospective work is proposed only; nothing was scheduled.
