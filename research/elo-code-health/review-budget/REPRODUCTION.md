# Independent replay of a review-fix regression

## Top findings

- [C] Three selected cancellation regression tests fail against Paneweft revision `3fa003c` and pass against `d89c0e7b750786a84ef8bf9a468967707333a9eb`.
- [C] Both runs use identical test-file bytes and pinned production source trees. Failures are behavioral assertions, not missing dependencies or test collection failures.
- [C] The earlier revision implements export-first staging introduced to address the preceding review. The later review identified cancellation interactions in that new staging path.
- [C] This is one causal example with several scenarios, not three independent examples and not an estimate of the best number of rounds.
- [D] A substantial lifecycle fix is a defensible candidate trigger for another independent review, but its general predictive value still needs evaluation.

## What ran

The experiment ran only the three `[T5]` and `[T6]` cases in `src/v1/jobs.test.ts`, using the exact file from the fixed revision against both source revisions. The production `createJobService`, cancellation API, filesystem state and leases ran. Qex and Cargo peers were the repository's test fakes. The viewer global setup was omitted because these service tests do not use the viewer; SDK import aliases and test timeouts were retained. Seventy-four unrelated cases were not selected in either run.

| Source | Selected tests passing | Selected tests failing |
|---|---:|---:|
| Before, `3fa003c` | 0 | 3 |
| After, `d89c0e7` | 3 | 0 |

Before the fix, an interleaved cancellation returns `cancel-too-late` while the run succeeds; a cancellation written during export finishing still permits a successful run; and cancellation after export completion returns `indeterminate` with a submitted next stage. All three violate the tested cancellation outcomes. The fixed service returns cancellation and prevents the inappropriate run progression in those cases.

The runtime and source trees were temporary and removed after execution. Neither Paneweft's checkout nor its dependencies were modified. The qex job used about 407 MB maximum resident memory and 13.1 CPU seconds, completing in 15 seconds. Exact revisions, dependency lock, test hash, assertions and reports are saved in `cancellation-reproduction.json`.

## Interpretation

The [independent audit](EVIDENCE-AUDIT.md) links the export-first change to the preceding review's T4 discovery, then the new cancellation interaction to the next review's T5. This replay strengthens the behavior claim beyond trusting a historical report. It does not establish that the newly introduced issue existed in the original architecture, that another reviewer would always catch it, or that adding review beyond the current mandatory schedule is generally beneficial.

The result supports tracking the revision that fixes a finding and treating material changes to state ownership, cancellation or execution stages as new review exposure. It does not support replacing evidence with a higher Elo score.

## Where your setup differs

`test-quality` asks whether the assertion rejects the plausible broken implementation. The same cases were executed against that implementation and its fix. The remaining fake-runner boundary is explicit, so this is not a real Qex interoperability result.

## Candidate actions

1. Capture fix revisions and state-machine changes in each review decision record.
2. Test the fix-shape hypothesis separately from the historical K forecasts.
3. Keep mandatory review gates and caps authoritative while collecting optional-review evidence.

## Sources

- Local Paneweft source revisions above, replayed 2026-11-17.
- `reproduce_cancellation.py` and `cancellation-reproduction.json` in this directory.
- `paneweft.research/v1/fix-t2-r1-report.md`, T4; `fix-t5-report.md`, T5/T6, as cited in `EVIDENCE-AUDIT.md`.
