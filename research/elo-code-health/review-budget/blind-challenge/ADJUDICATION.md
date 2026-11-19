# Historical challenge result

## Top findings

- [C, focused challenge] The fresh reviewer assigned the buggy historical version identified the predeclared cancellation family before receiving the parent's follow-up.
- [C, focused challenge] The reviewer assigned the fixed version reported no established material finding after checking the identity and cancellation-response guards.
- [C, evidence] The existing independent three-case replay and inspected adjacent fix support the historical family. No new current-product defect was established.
- [C, protocol deviation] A parent follow-up shared a hypothesis across arms. Post-follow-up observations cannot be treated as independent detections.
- [D, inference] This demonstrates an evidence-collection workflow, not reviewer accuracy, a rating gain, or the appropriate number of rounds.

## Assignment and scope

Neutral arm A contained fixed revision `d89c0e7b750786a84ef8bf9a468967707333a9eb`; B contained buggy revision `3fa003c852bef303ffe48c788093c2659d677870`. `assignment.json` preserves the deterministic assignment and every archived production-file hash. Tests and Git/review history were excluded. Both fresh contexts used the same inherited Codex configuration and received the same contract and output constraints, with only input/output paths changed. No Claude model or repository program ran.

Input restriction was by instruction, not filesystem isolation. Source comments can themselves reveal the presence of defensive fixes. These limits prevent a claim of strong experimental blinding.

The challenge specifically directed attention to collection lifecycle and cancellation. It was not an unprompted general review, a representative defect sample, or a trial of live build-loop rounds.

## Observations and adjudication

| Arm | Final report | Parent classification |
| --- | --- | --- |
| A, fixed | No material finding established; late-marker race withdrawn; export-finalization availability left uncertain | No supported finding in the predeclared family. This is not a clean-code label. |
| B, buggy | Stale export observation can finalize a live run; completed-export cancellation leaves run submission enabled | Supported historical family, counted once. Existing replay covers the stage-identity and cancel-before-finish mechanisms. |

B's initial message already described the completed-export cancellation path and stale-stage observation before the parent follow-up. Its final P1/P2 details correspond to the pinned test groups `[T5] a finish belongs to the qex job of the stage on disk` and `[T6] a cancel is recorded before a stopped export is decided`. The same three selected test-file bytes fail before the adjacent fix and pass after it, as recorded in `../REPRODUCTION.md`. The reports themselves were static analyses, not additional test executions.

A initially considered a cancellation marker written after the last check. The reviewer withdrew a claim of violated accepted cancellation because the marker alone is not a successful API response: the cancellation loop follows the changed queue-job ID and can return cancelled, too-late or indeterminate. This distinction is useful evidence about adjudication, not an extra defect discovery. Both reports leave cancellation availability during a live export-finalization lease as a contract question where the inspected interface is insufficient. That question was not promoted to a new bug.

## Dialogue and deviation

Both reviewers received an identical parent challenge after their initial messages:

> Please pin the externally observable cancellation acceptance point. Writing intent alone may not imply the API promised cancellation; distinguish an allowed cancel-too-late/indeterminate outcome from a violated contract. Check whether existing lease/state or late-cancellation branches close each proposed interleaving, and withdraw candidates they do. For any stale-stage stop, verify whether Qex job identity is checked before current-stage state is interpreted. Preserve exact source reasoning and evidence limits; no runtime execution.

The final stale-stage sentence was informed by B's newly raised hypothesis. Sending it to both arms breached the protocol's separation of newly discovered hypotheses. The initial messages still establish what each reviewer considered beforehand, but later findings cannot supply independent overlap or sensitivity observations. No capture–recapture estimate, Elo update, false-positive rate or accuracy percentage is calculated from this exercise.

The parent initially challenged whether a cancellation request marker alone constituted acceptance. Both reviewers correctly distinguished request recording from the returned result. The final records preserve provisional concerns, withdrawn claims, final reports, test-supported family identity and contract uncertainty separately. A scoring pipeline that counts every provisional concern as a defect would get this exercise wrong.

## Where your setup differs

`build-loop` deliberately uses substantive exchanges and prior-finding context to improve a review. Those exchanges can correlate findings across otherwise fresh reviewers. `test-quality` supplies the independent behavioral evidence for the historical family. A future rating or overlap study must log shared hypotheses and keep private detections separate before discussion.

## Candidate actions

1. Record an initial private finding set before orchestrator feedback if measuring reviewer overlap.
2. Preserve provisional, withdrawn, accepted and independently supported findings as separate events.
3. Keep this one-family challenge out of optional-review model training and performance claims.

## Sources

`PROTOCOL.md`, `assignment.json`, `replies/A.md`, `replies/B.md`, session-order progress messages and the exact parent follow-up above; `../cancellation-reproduction.json` and pinned historical source/tests. All work occurred 2026-11-17. No current-source change, live review gate or upstream action occurred.
