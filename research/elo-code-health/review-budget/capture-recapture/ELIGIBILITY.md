# Existing reviews do not support capture-recapture estimation

None of the inspected records establishes two independent reviews of the same defect population on an unchanged code snapshot, with complete comparable detection sets. One same-snapshot pair remains unknown because its original prompts and full replies were not found in the inspected source family. No estimator was fitted.

This audit covers all 75 structured rounds and all 23 external paired rounds already selected for the review-budget experiment. Every recorded SHA resolves to a full Git commit. Grouping by project and resolved commit, rather than abbreviated SHA text, produces five repeated-snapshot clusters containing 11 rounds and seven candidate review pairs. The other 87 rounds have no second matching project/commit in this pool. There are 92 distinct project/commit combinations overall.

The three within-change unchanged transitions in `snapshot-features.jsonl` are Edge guides rounds 2/3, Fauxx seeding rounds 3/4, and phoe-nix W46 rounds 2/3. Two additional external clusters share snapshots across different scoped changes. W46 and W47 also share one repository commit while reviewing different paths.

## Eligibility rule

A usable existing pair would need all of the following, supported by saved artifacts:

- The same resolved commit and the same reviewed path/base/contract scope, before fixes between the two inspections.
- Separate reviewer contexts that had not seen the other inspection's findings, fixes, score, or suggested focus. A different model name or a "fresh" label alone does not establish this.
- Complete per-review detection sets under the same materiality definition, including repeated detections. "New findings only" output cannot supply the overlap count.
- A defensible mapping of two reports' manifestations to the same underlying defect, preserving uncertain matches. Shared finding IDs after ledger exposure are not independent rediscoveries.
- No substitution of fix verification, a changed-code re-review, or a fix report for a new inspection.

These are operational inclusion criteria for this experiment. They do not prove all statistical assumptions of a future estimator. Fresh LLM contexts may still have correlated failure modes; changing models does not establish statistical independence.

## Candidate pairs

Paths in this table are relative to `/home/mini/Documents/repos/`. Round references are to the existing corpus, not inferred from file names. Full snapshot identities and source hashes are preserved in `eligibility.json`.

| Candidate | Snapshot | Judgment | Evidence |
| --- | --- | --- | --- |
| Edge guides PR1, tier-1 round 2 Sol versus tier-2 round 3 Opus | `9ec5bd6d7c05b869d8acc1d0e067e3df92e6009f` | Ineligible. Changed review scope and shared prior findings; detection overlap suppressed. | `edge.research/guides/pr1-brief-r2.txt:5-7` restricts round 2 to fixes since `1ec82e44`, while `pr1-brief-t2.txt:5` asks for the full diff since `69341a6e`. Both include S1/S2. Tier 2 explicitly says "Do not re-raise ledger items" at line 18. The ledger confirms the common target SHA. |
| Fauxx seeding, tier-1 round 3 Sol versus tier-2 round 4 Opus | `1ff4822f8a558a58e7e8a124ea33663c9656d97c` | Unknown, not eligible for fitting. Same snapshot and differing reviewer aliases are recorded, but independence, equal scope, complete detection sets, and overlap are unproven. | `fauxx.research/seeding-review.ledger.json` records both rounds and assigns new S8-S15 to round 4. `seeding-handoff.md:26` calls tier 2 fresh Opus, but the handoff is a summary rather than the original complete prompt/reply. No seeding prompt/reply artifacts were found in the bounded inspected family. The absence of newly assigned round-3 findings is not an observed empty independent capture. |
| phoe-nix W46, tier-1 round 2 Opus versus tier-2 round 3 Opus | `018c71c1e05fda35315222e14148f7227d4702b5` | Ineligible. Different review scope, shared ledger, and explicit repeat suppression. | `phoe-nix.research/w46-vigil.brief2.txt:13-15` reviews only changes since `6ecd7fc9`, whereas `w46-vigil.brief-t2.txt:13` reviews the full diff since `58d0844f~1`. The tier-2 brief includes S1-S4 and instructs the reviewer not to re-raise ledger items. `w46-vigil.reply2.txt` verifies earlier fixes; this is not an independent full-population capture. |
| phoe-nix W46 round 2 versus W47 round 4 | Same `018c71c1…` | Ineligible. Different path and contract populations. | W46 briefs restrict to `scout-modules/vigil`, base `58d0844f~1`. `phoe-nix.research/w47-router.brief-t2b.txt:7,14-16` concerns the build-loop router and transcript checker, restricting the diff since `49cbb769` to `scout-modules/agent-integration/skills/build-loop`. Its ledger and open findings are included. |
| phoe-nix W46 round 3 versus W47 round 4 | Same `018c71c1…` | Ineligible for the same scope mismatch, regardless of differing Opus/Fable aliases. | The same saved briefs establish disjoint principal paths and different bases/intents. A shared merge commit does not make the reviewed defect population identical. |
| External Edge T1-T2 round 4 versus T3 round 3 | `aeb1e36974c7d35ad4023095b7e327a8d7e7ca97` | Ineligible. Explicitly different populations and sequential, fix-aware contexts. Reviewer identity is also unstated in the extracted rows. | `edge.research/wake-pr/review-t12-r4.md` names earlier verdict/findings, fix reports, T1-T2 scope, and T3 as out of scope. `review-t3-r3.md` names earlier T3 findings and fixes and explicitly excludes T1-T2 unless they break T3. Both ask for closure of known IDs and new regressions. |
| External Edge T1-T2 round 5 versus T3 round 4 | `0ae8fdc9b34eb3c274953dddb8cca94d7044992c` | Ineligible. Different populations, prior findings/fixes supplied, and budget-sensitive output thresholds. | `edge.research/wake-pr/review-t12-r5.md` is the final budgeted T1-T2 pass and excludes T3. `review-t3-r4.md` is the T3 detection/experiment pass with detailed earlier findings and merged fixes. Both narrow the final decision toward shipping blockers. Neither is a blind full-population capture. |

Result across the seven candidate pairs: zero eligible, six ineligible, one unknown. Unknown is excluded, not treated as independent. The 87 unmatched rounds cannot be paired with a changed-SHA successor to increase sample size.

## Why the current finding tables cannot supply overlap

The structured corpus preserves discovery IDs and eventual dispositions. It was built to distinguish newly reported findings from repeated unresolved ones. That purpose differs from capture-recapture's need for every independently detected defect in each inspection. A reviewer instructed not to repeat an existing ID may notice that same issue and omit it; an omitted repeat would appear as zero overlap if the table were used blindly.

Fix-induced defects are a second problem. When a correction changes asynchronous waits, cancellation, or validation behavior, the next review observes a changed population. Equal defect-class names across changed versions cannot make those captures comparable. The previously audited phoe-nix and Paneweft fixes illustrate this, but neither supplies an eligible unchanged, blind pair.

The records also lack reliable review timestamps and complete context provenance. Exact Git identity verifies code objects, not the absence of untracked changes in a historical review environment or the actual context seen by a reviewer. A prompt that names a detached SHA is stronger scope evidence than a mutable checkout path, but it still does not authenticate an independent session.

## What could make the approach testable

Existing owned projects can supply frozen snapshots for a future experiment. Edge's volume is useful for sampling; it does not repair missing historical independence. Select a bounded change and freeze the full commit, base, relevant contract, path scope, materiality definition, and allowed evidence. Obtain a valid owner-authorized review allocation without changing existing caps or floors.

Run at least two separate contexts against exactly that snapshot and scope before sharing any findings or applying fixes. Give each reviewer the same code/context package, with no previous ledger findings, prior score, fix hints, or other reviewer's report. Preserve full reports even when they contain no detections. Keep the ordinary policy workflow and its existing findings separate from this blind research assay.

After both reports are locked, adjudicate defects and match manifestations while preserving uncertain matches, false positives, contract changes, and evidence strength. Only then assess whether enough overlap and capture variation exist to fit an estimator and examine dependence. Different reviewers or random seeds are design choices to test; they are not evidence of independence by themselves. More than two captures may help assess dependence, but no budget or new review run is authorized by this feasibility audit.

This would estimate residual defects for a defined snapshot under stated assumptions. It would still need separate evidence to choose an optimal number of build-loop review rounds or claim that an architectural change improved shipped outcomes.

## Audit provenance

Inputs were `corpus/rounds.jsonl` SHA256 `470561bf8f3bb036bc76fa872ed01371323207dd9457f4e7f65df4d4ef7ed38c`, `external-corpus/rounds.jsonl` SHA256 `9436791a0d035bd1013c52aac0463f5d9009521c38ad06bacacd50c19ec6907b`, and `snapshot-features.jsonl` SHA256 `d8ac9bee540c25e43ef38d75302a3ed8d47df4d1a1baa67320ebd62d84db55da`. Structured full SHAs came from already observed snapshot features. External SHAs were resolved using read-only Git with replacement objects disabled. Only repeated-snapshot candidate artifacts were read in detail. No findings were relabeled, no estimator was fitted, and no subject repository or review record was changed.
