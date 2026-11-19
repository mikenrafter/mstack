# Reproduction boundaries

All recorded runs are local research from 2026-11-17. Preserve the existing artifacts before rerunning: many scripts write results beside themselves. Use a separate copy of this research directory for fresh results and compare it with the preserved hashes. Do not merge new outcomes into the frozen corpora.

The cheapest integrity check, from the mstack root, is:

```sh
python3 research/elo-code-health/review-budget/verify_artifacts.py
```

This checks 19 byte bindings and integration facts. It does not rerun subjects, authenticate producer claims or validate statistical assumptions. The saved result is `artifact-integrity.json`.

For a bounded local test, run one component from its own directory through the shared queue. For example, from `review-budget/models`:

```sh
qex submit --wait --cpu 1 --mem 256MB -- python3 -m unittest test_forecast.py
```

The test modules are deliberately separate; a single top-level unittest discovery does not recursively cover these non-package research directories.

| Directory under review-budget | Focused tests | Relevant saved result |
| --- | --- | --- |
| `corpus` | `test_extract.py` | `summary.json`, `rounds.jsonl` |
| `external-corpus` | `test_extract.py` | `summary.json`, `rounds.jsonl` |
| `models` | `test_forecast.py` | `accepted-results.json`, `reported-results.json`, `external-results.json` |
| `models/fix-shape` | `test_diagnostic.py` | `results.json` |
| `missing-outcomes` | `test_bounds.py` | `results.json` |
| `identifiability` | `test_demonstration.py` | `results.json` |
| `power` | `test_planning.py` | `results.json` |
| `capture-recapture` | `test_simulate.py`, `test_empirical.py`, `test_coverage.py` | Simulation, 602-pair empirical and exact coverage outputs |
| `advisory-prototype` | `test_collector.py` | `VALIDATION.md`, `mutation-results.json`, `batch-smoke/RESULTS.md` |
| `.` | `test_snapshots.py` | `snapshot-summary.json` |

Each component's mutation script is a separate run. It deliberately substitutes a known-wrong implementation; the expected result is that its focused test rejects that implementation. The corresponding saved mutation JSON identifies what was caught. Historical optimizer outputs marked `invalid-optimizer-v1` remain invalid and must not be substituted for corrected forecasts.

`queue-records.json` preserves the resolved job IDs, working directories, commands, exit codes and measured usage for the 14 available `.qex` pointers. All 14 completed with exit code zero. This is a subset of the work, not an assertion that every experimental command or intermediate version passed. Component reports preserve failure and correction history.

The product-level cancellation replay and Paneweft CLI integration have additional dependencies. `reproduce_cancellation.py` and `evidence-graph/check_cli.py` use immutable Git archives and temporary Node runtimes. They must not be treated as a full subject build, current-checkout assessment or real Qex/Cargo interoperability test. Read `REPRODUCTION.md` and `evidence-graph/README.md` before repeating them. Do not install missing browser libraries merely to recreate a screenshot; the inline views were displayed separately from CLI validation.

The collector intentionally refuses a changed installed policy hash, legacy ledgers, dirty-worktree coverage and unsupported verification forms. A future policy change needs adapter review; replacing its pinned hash just to obtain a passing run would invalidate the capture contract.
