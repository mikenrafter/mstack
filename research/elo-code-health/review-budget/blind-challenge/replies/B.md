# Historical source review B

Two material findings in the supplied historical snapshot. These are source-derived interleavings, not claims about the current product.

## 1. P1: A delayed export observation can finalize the live run

Location: `src/v1/jobs.ts:628-634`, `finish`, reached through `cancel` at lines 895-900 and `finishWithin` at lines 673-679.

Triggering interleaving:

1. An export-first collection has completed export queue job E, with E still recorded in `state.json`.
2. Caller A invokes `cancel`. It reads E's identity and starts `qex.status(E)` outside the lifecycle lease.
3. Before that response is consumed, caller B invokes `status`. B acquires the lease, finishes E, writes the run decision, and submits run queue job R through `afterFinish` and `advanceOwned`. R remains queued or running when B releases the lease.
4. A receives E's completed response and enters the terminal-queue-job branch at line 897. `finishWithin` acquires the lease and passes E to `finish`.
5. `finish` reads the current state for R, chooses its run stage at line 630, and writes E into `observedStop` at line 634. It never compares E's identity with the persisted R identity. It invokes `finalizeRun` against R's staging directory with E's exit status and logs.

The lease serializes execution but does not make A's earlier queue observation belong to the current stage. The identity check at line 711 applies to `advanceOwned`'s optional observation; `finishWithin` bypasses it.

Violated contract: only the current stage's terminal queue record can authorize finalizing that stage and the collection. R can still execute while its collection becomes permanently terminal. With an empty run staging directory, `reconcile` synthesizes missing invocations and an `incomplete` collection at `src/v1/adapters.ts:286-299,347`; `finish` maps this to terminal `failed` at line 657. `finalizeRun` also persists `finalized.json` and attempts import. Later status calls return the terminal state at line 705 without collecting R's actual results. Subsequent cancel calls return `already-terminal` at line 887 while R can remain live.

Evidence limits: this requires concurrent callers and a delayed status response or scheduling delay before lease acquisition. It does not require a crash or a contradictory queue state. No runtime reproduction was performed. The premature terminal transition follows even if import fails, because the failure handler also produces terminal `failed`. This finding does not claim the API first returned a successful cancellation.

## 2. P2: Cancelling after export completion leaves the unstarted run eligible to launch

Location: `src/v1/jobs.ts:897-900`, `cancel`; related rejection at line 888 and transition in `finishExport` at lines 599-617.

Triggering sequence with no concurrency required:

1. An export-first collection's export E has completed successfully, but no status call has finished it. The example run has never been submitted.
2. `cancel` observes E as terminal at line 897 and calls `finishWithin` before writing `cancel.json`. The cancellation marker is only written in the other branch at line 902.
3. `finish` therefore sees no cancellation request at line 623. It calls `finishExport`, which resolves the examples and changes the collection to `submitted`, `stage: run`, `qexId: null` at line 616.
4. `cancel` returns `indeterminate` at line 899 because this state is not terminal. A later status call or repeated collect advances the collection and submits the example run.

There is a related rejection during asynchronous export finalization. Once `finish` has written `importing`, `cancel` returns `cancel-too-late` at line 888 whenever the lease is live, including when `stageOf` is still export and `finishExport` has not decided or submitted the example run. Export finalization can await staging reads, catalogue validation, fingerprinting, and durable writes before that transition.

Violated contract: completion or finalization of the export stage does not complete the collection. A request to stop a collection whose example run has not begun should be able to prevent that run from being submitted. These paths apply terminal-stage handling to the collection and leave its next stage enabled.

Evidence limits: the completed-export path returns `indeterminate`, and the importing-export path returns `cancel-too-late`. Neither is evidence that a returned `outcome: cancelled` was later violated. This finding concerns cancellation availability and continued advancement before the example run starts; if the intended API explicitly permits rejecting cancellation throughout export finalization, the importing-export portion would instead be a contract question. The sequential completed-export path remains observable as described.

## Scope and uncertainty

Inspected `src/v1/jobs.ts` throughout, with focused helper reads in `src/v1/qex.ts`, `src/core/write-lock.ts`, `src/v1/durable.ts`, the reconciliation function in `src/v1/adapters.ts`, and the validation/import entry path in `src/v1/import.ts`. No tests, repository history, sibling snapshots, review artifacts, scripts, builds, network requests, or runtime execution were used. I did not establish an interleaving where the API returns `outcome: cancelled` and subsequently launches the example run. Other service behavior was not comprehensively reviewed.
