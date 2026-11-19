# Real-corpus collector smoke results

Collected 2026-11-17 08:21:50–08:21:51 UTC under [the frozen protocol](PROTOCOL.md). This is integration coverage on historical ledger/object snapshots, not predictive or optional-review policy validation.

All 21 frozen ledger hashes matched. All 21 repositories and latest current-phase reviewed commits resolved; every full commit matched the established snapshot map. There were no missing revisions or pre-capture refusals. Collector, manifest, groups, snapshot map and protocol hashes stayed unchanged. Exact commands, stream hashes, return codes, UTC times and elapsed durations are in [records.jsonl](records.jsonl); aggregate provenance is in [summary.json](summary.json).

The CLI completed a supported capture for 3/21 ledgers (14.3%). The other 18/21 have no declared schema version and returned exit 2 with `unsupported-ledger-schema`; their JSON explicitly retained insufficient evidence. They were not migrated or treated as clean reviews. Of the three supported schema-2 inputs, w46 lacked a supplied trigger, w47 had exhausted its declared channel cap, and w49 required a mandatory review. None produced an additional-review recommendation.

| Group | Schema | Exit | Canonical step | Collector status |
|---|---:|---:|---|---|
| edge.research/guides/pr1 | absent | 2 | unknown | insufficient-evidence |
| edge.research/sol/db-split | absent | 2 | unknown | insufficient-evidence |
| edge.research/sol/graphs/graphs | absent | 2 | unknown | insufficient-evidence |
| fauxx.research/appkind-review | absent | 2 | unknown | insufficient-evidence |
| fauxx.research/fauxx-implementation | absent | 2 | unknown | insufficient-evidence |
| fauxx.research/location-review | absent | 2 | unknown | insufficient-evidence |
| fauxx.research/optout-review | absent | 2 | unknown | insufficient-evidence |
| fauxx.research/phases-review | absent | 2 | unknown | insufficient-evidence |
| fauxx.research/seeding-review | absent | 2 | unknown | insufficient-evidence |
| paneweft.research/review | absent | 2 | unknown | insufficient-evidence |
| paneweft.research/v1/review | absent | 2 | unknown | insufficient-evidence |
| phoe-nix.research/vigil-auto-interval | absent | 2 | unknown | insufficient-evidence |
| phoe-nix.research/vigil-disk-full | absent | 2 | unknown | insufficient-evidence |
| phoe-nix.research/w46-vigil | 2 | 0 | STOP-AGREED | insufficient-evidence |
| phoe-nix.research/w47-router | 2 | 0 | STOP-AGREED | cap-reached-escalate |
| phoe-nix.research/w49 | 2 | 0 | ROUND | required-review-still-pending |
| polara-port.research/build-loop/clouds | absent | 2 | unknown | insufficient-evidence |
| polara-port.research/build-loop/l48 | absent | 2 | unknown | insufficient-evidence |
| polara-port.research/build-loop/modes/credits | absent | 2 | unknown | insufficient-evidence |
| polara-port.research/build-loop/modes/modes | absent | 2 | unknown | insufficient-evidence |
| residual-cli.research/reviewer-notes | absent | 2 | unknown | insufficient-evidence |

For every one of the 21 CLI JSON outputs, `execution_allowed` was false and `outcome` remained `unobserved`. Unsupported schema, absence of a trigger, and missing outcomes did not become negative defect labels. All captures used an explicit named Git object and no supplied fact; none executed reviewers, builds, repository scripts, model calls or outcome recording. The canonical ledger policy itself ran against a temporary copy as designed.

The predefined w49 seam passed: the collector returned `ROUND: tier 2 round 1 (full diff, fresh Fable); reviewer: fable`, with `required-review-still-pending`. An independent invocation of the installed canonical policy on a byte-identical temporary ledger copy produced exactly the same stdout; [verification metadata](w49-canonical.json) records the hashes and return code. This is evidence that mandatory review was preserved, not authorization to launch Fable or any Claude model.

No observed canonical STOP-AGREED status is an authentic earlier optional-review boundary: these are final saved ledgers inspected now. Supplied histories are assertions rather than independent proof of review execution. Working-tree contents remain outside coverage. All 21 records are explicitly excluded from optional-review training eligibility. The smoke supports conservative handling of these inputs; it does not measure residual defects, extra-round benefit, or live-build readiness. Legacy schema coverage would require a separate authorized adapter design and validation.
