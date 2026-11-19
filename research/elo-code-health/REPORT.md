# Historical code health experiment results

## Top findings

- [C] Edge is the best primary subject among the inspected local histories: 637 mainline integrations, 216 fix-title source-touch integrations, and 384 current eligible source files.
- [C] The preregistered Elo aggregation did not outperform recent change frequency on the two held-out windows in any of the four subjects. This rejects using this variant as the default historical hotspot ranking.
- [C] Edge's Elo ranking captured 35.2% of eligible future fix-related file touches at an approximately 20% file budget; recent change frequency captured 56.0% and historical fix count 53.0%.
- [C] The strongest current change pair is derivation engine/database, with 21 cochanges. Patch inspection shows both mixed sweeps and a concrete shared retention invariant. Counts alone cannot justify a boundary change.
- [C] Label quality and limited independent holdouts restrict every predictive claim. These are observed fix-commit involvement proxies, not confirmed defects, calibrated risks, or evidence of successful architectural repair.

## Project selection

Use Edge for primary longitudinal evaluation. Use Analytics for algorithmic scenarios and Qex for lifecycle/transaction scenarios. Diff-core is a useful portability and confounding check; its history contains many evaluation-only commits and an old source-directory rename. Residual and Paneweft are integration targets, with only six and one fix-title source integrations respectively in the selected histories. That is insufficient for this ranking study.

All refs are cached local refs, pinned in `inventory.json`. The Edge checkout itself was on an older feature branch, so the analysis reads `upstream/main` objects without checking it out. Qex intentionally uses the owner working branch. Edge's pinned head carries a 2026-11-17 date, later than the protocol's UTC date; ordering uses the first-parent chain and makes no wall-clock as-of claim. Commit windows have unequal elapsed durations. No network fetch, source checkout, build, paid model call, or remote write was performed.

## Held-out comparison

Each model chooses ceil(20% of eligible source files), with fractional allocation for tied scores. Percentages below pool the final two chronological windows by fix-related file touches. A file touched in two fix commits contributes twice. The denominators exclude new files that did not exist at the prediction revision; cold-start exclusions were Edge 8, Analytics 0, Qex 1, Diff-core 20. The source filter includes inline Rust test code when it shares a production file, and can include fixture-like source files outside explicitly excluded directories.

| Project | Elo | Historical fix count | Recent change frequency | Random expectation | Eligible fix touches |
|---|---:|---:|---:|---:|---:|
| edge | 35.2% | 53.0% | 56.0% | 20.3% | 267 |
| openstrap-analytics | 25.5% | 29.5% | 28.4% | 21.1% | 47 |
| qex | 11.9% | 41.1% | 42.4% | 21.0% | 59 |
| diff-core | 33.3% | 33.8% | 47.5% | 20.6% | 75 |

Equal file count does not imply equal review effort. Large files and routine version stamps can make both activity and defect-count baselines look useful. Neither has been validated for actual inspection time saved. `windows.csv` contains all windows, precision, unique-file recall, positive counts, and cold-start counts; `summary.json` contains all model/label aggregates. Display rounded values are not additional precision.

## Elo definition and sensitivity

After the initial results, the owner questioned K's assumptions. An independent subagent audit found substantial block-size weighting: a file participates in n−1 updates in an n-file block. At Edge's 80% boundary, the largest block contains 251 files and supplies 31,375 of 93,374 comparisons, or 33.6%. These are dependent transformations of the same observations. Match count is update exposure, not realized net influence. The initial K=16/32/64 sweep does not isolate this confound. See `WEIGHTING-PROTOCOL.md` and `WEIGHTING-RESULTS.md` for the separate exploratory diagnostic. The original protocol and result files remain unchanged.

This is one specific exploratory Elo construction. In each 25-commit training block, files compete according to their Laplace-smoothed fix/touch rates. Higher observed rate wins. K=32 is fixed; ratings start at 1500. Ratings measure relative involvement under noisy labels. There is no executable challenge difficulty or demonstrated correctness outcome in these matches.

On Edge, K=16 and K=64 capture 37.1% and 36.0%; five shuffled within-block match orders capture 35.2–35.6%. These do not reach the change-frequency baseline. Analytics is less stable: the seeded orders capture 29.8–34.0% versus 25.5% for canonical order. Its permuted-training-label control captures 31.9%, above canonical Elo. A single control is diagnostic and supplies no p-value.

Strict title labels produce Elo recalls of 36.3% for Edge, 17.0% for Analytics, 6.8% for Qex, and 11.3% for Diff-core. The labels alter training histories even when the holdout positive events happen to coincide. Constant-rating controls match the random budget expectation in every window. One Diff-core development window has a single positive touch and two have none; those missing recalls remain null.

The rate-based construction can favor sparsely touched files because smoothing adds a prior rate of one half. It also answers a rate question while the primary metric rewards event volume. This is a reason to distrust this construction's fit to the task, not evidence that every possible Elo model fails. No hyperparameter was selected from the holdout, and no improved variant was fitted after these results.

## Architectural investigation

The last 200 source-touch integrations in Edge contain 12 changes touching more than 20 source files; these are excluded from pair analysis. The remaining 188 produce these candidate relations:

| Pair | Cochanges | Interpretation |
|---|---:|---|
| Derivation engine / database | 21 | Shared retained-data decisions, but inspected mixed sweeps also inflate the count |
| Database / app state | 16 | Storage and orchestration boundary; needs invariant-level inspection |
| Derivation engine / read repository | 15 | Derived output and serving contracts; direct import exists |
| App state / background sync | 9 | Foreground/headless coordination; 9 of 10 background-sync touches also change app state |

`architecture.json` provides support, directional conditional frequencies, example commit SHAs and direct-import checks. The import scan resolves literal Dart relative imports and imports for the declared package at the pinned current revision; it does not prove reachability or absence of indirect dependencies. Current imports never enter the historical ranking evaluation. Conditioning pair membership on files surviving to the current tree introduces survivorship bias into this descriptive scan.

Inspecting the first three examples for the highest-support pair found one concrete retention coupling and two mixed sweeps. See `label-audit.md`. The useful next question is whether retained-window completeness can have one decision interface used by every derive entry path, with atomic pruning metadata, while preserving all existing outcomes. This might reduce duplicated decisions; it might also add an unnecessary abstraction. A behavioral comparison must decide.

## Residual and Paneweft

`evidence.json` separates observations from hypotheses and keeps exact revisions. `residual-draft.json` records one proposed retention stressor, outcomes, component candidates, and held-out cases. It is an analysis interchange file, not a Residual CLI import format. No established force or coupling matrix has been modified.

`paneweft.bundle.json` uses Paneweft's existing list view format to show current activity with parsed provenance and a partial-completeness warning. It deliberately labels activity rather than quality. The real CLI validated the bundle, stored it, and read back all 20 rows in an isolated runtime with the declared production dependencies. An independent JSON Schema validator also accepted it. The session has no registered Edge root, so Paneweft correctly reports freshness as unverified. The pinned historical tree is explicit; the live checkout is different. Results and the session path are recorded in `integration-checks.json`. No viewer server was started.

## Schedule status and follow-up

E0–E5 completed for this bounded observational pass, including the real Paneweft CLI round trip and inline comparison. The proposed behavioral retention comparison and prospective review study have not run. No unattended calendar task or weekly collector was installed. The HTML screenshot preflight was unavailable because this host lacks the browser libraries; the inline HTML renderer accepted and displayed the artifact, and no host browser setup was changed.

The next experiment should be a within-repository behavioral comparison on Edge's retention boundary. Hold correctness outcomes fixed. Compare the current decision paths against one candidate interface, then vary a retention requirement and measure edits and regressions. Only after that experiment should ratings be attached to actual stressor outcomes. A four-week prospective check starts when a collector is installed, not at this report's timestamp.

## Reproduce

From the mstack root, run the following through the local queue:

```sh
qex submit --wait --cpu 1 --mem 128MB -- python3 -m unittest discover -s research/elo-code-health -p 'test_*.py'
qex submit --wait --cpu 1 --mem 384MB -- python3 research/elo-code-health/replay.py --revisions research/elo-code-health/inventory.json
qex submit --wait --cpu 1 --mem 128MB -- python3 research/elo-code-health/check_mutations.py
qex submit --wait --cpu 1 --mem 128MB -- python3 research/elo-code-health/summarize.py
qex submit --wait --cpu 1 --mem 320MB -- python3 research/elo-code-health/check_integration.py
```

With `--revisions`, the script uses the recorded SHAs; without it, it resolves available refs anew. `run.json` binds the protocol and replay script hashes. Nine focused tests cover selection arithmetic, cold starts, missing positives, Elo direction, future exclusion, filtering and a real temporary Git merge. Three deliberate defects must fail those tests: future leakage, reversed rating update, and selecting all tied files. No product test suite was run.

## Where your setup differs

`technical-excellence` asks for explicit invariants and `test-quality` asks for assertions that catch actual defects. The evaluator applies those checks, but the product labels still lack independent adjudication. Paneweft already accepts evidence provenance and completeness, which makes it suitable for showing this distinction. Residual already has outcomes and component relations, so the next step can use checkable stressors rather than inventing a repository-wide quality number.

## Candidate actions

1. Use recent change frequency plus visible fix evidence for the initial investigation queue. It beat this Elo variant on every subject's holdout and is cheaper to explain.
2. Run the retention behavioral comparison on Edge before building automatic rerouting. It has one inspected shared invariant and concrete held-out failure cases.
3. Adjudicate labels and measure inspection time before claiming defect-detection improvement. The current proxy cannot support that claim.
4. Revisit Elo or an ability/difficulty model only with repeated executable stressor outcomes. It would then have a defensible match definition.

## Sources

Local evidence is reproducible from the pinned revisions in `inventory.json`, the saved first-parent histories, the patch audit, and the frozen `PROTOCOL.md`. External background and dated source links are listed in that protocol. Grades C here indicate this bounded, reproducible local experiment; none of the results establish general software-quality effects.
