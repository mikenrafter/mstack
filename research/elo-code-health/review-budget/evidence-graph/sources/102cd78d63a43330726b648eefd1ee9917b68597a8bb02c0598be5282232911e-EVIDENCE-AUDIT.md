# Evidence audit for review-round budgeting

Later reviews in this sample found reproducible defects, including defects introduced by earlier fixes. The records do not establish how many rounds an unreviewed change needs. They also omit enough findings and review attempts that treating empty ledger rounds as clean rounds would produce incorrect training labels.

This audit is for the owner deciding whether a review-budget experiment is useful. It is independent of the rating experiment and changes no project source. Existing reports and Git commits were inspected; their tests were not rerun.

## Sample selected before detailed reading

On 2026-11-17, select the ledger with the greatest recorded round count in each of four projects; break ties by lexicographically sorted full path. Selection used only filenames and round counts, before reading finding bodies. The available counts were Edge 3/2/3, Paneweft 6/7, residual-cli 3, and phoe-nix 1/5/3/4/2.

| Project | Selected source | Recorded rounds |
| --- | --- | ---: |
| Edge | `/home/mini/Documents/repos/edge.research/guides/pr1.ledger.json` | 3 |
| Paneweft | `/home/mini/Documents/repos/paneweft.research/v1/review.ledger.json` | 7 |
| residual-cli | `/home/mini/Documents/repos/residual-cli.research/reviewer-notes.ledger.json` | 3 |
| phoe-nix | `/home/mini/Documents/repos/phoe-nix.research/vigil-disk-full.ledger.json` | 5 |

This selects long review histories deliberately. It cannot estimate the frequency of useful extra reviews in the owner's ordinary changes. Edge's three-round tie selected `guides/pr1` ahead of `sol/graphs`.

## Label rubric

Each finding needs separate judgments:

1. **Discovery:** newly reported behavior, a repeated unresolved claim, an extension of an earlier finding, or unknown. A new ID alone does not establish independence.
2. **Materiality:** a concrete unwanted runtime or policy outcome, a maintenance/design suggestion, or unknown. Severity and `needed` are reviewer judgments, retained separately.
3. **Acceptance and verification:** reviewer assertion only; accepted with a reported fix; or supported by an inspected fix commit and a report describing a failing-before/passing-after regression. The strongest label here still relies on historical test reports, not an independent rerun.
4. **Origin:** apparently present before the previous fix, supported fix-induced regression, newly agreed contract, or unknown. `pre_existing: false` in a ledger does not answer this question; it often means introduced within the whole change.

Related manifestations can both be material while belonging to one defect family. Keep a family identifier and a distinct observed scenario. Record the exact commit and policy stage at the decision point. Final resolution is an outcome, never an input available to the earlier decision.

## Audited cases

Paths in the tables below are relative to `/home/mini/Documents/repos/`. Round numbers refer to the selected ledger, unless explicitly unknown.

| Source, round, finding | Judgment and evidence | Remaining uncertainty |
| --- | --- | --- |
| `edge.research/guides/pr1.ledger.json`, round 1, S1 | Material marker geometry defect. Ledger identifies the `_track` fix and a regression test that fails without it. Round 2 correctly pinned reply confirms resolved. | No independent test rerun. |
| Same ledger, round 3, S3 | Newly recorded step-identity concern, `nit/no`, left open with no fix evidence. Could cause unnecessary reset behavior, but the ledger does not demonstrate the user-visible outcome. | Materiality and acceptance unknown. Do not call it a confirmed defect solely from a new ID. |
| Same ledger, round 3, S8 | Newly recorded whole-tree-per-frame performance concern, `nit/no`, open and without measurement or fix evidence. | Actual cost and a warranted additional review unknown. |
| `paneweft.research/v1/review.ledger.json`, round 2, S23 | Recursive reservation collision is a distinct concrete scenario in the shared capture-budget family. `fix-r2-report.md` names its accepted correction. | Earlier implementation ancestry was not fully traced. |
| Same ledger, round 3, S24 | Ownership validation added around shared content-addressed pages rejects valid shared data. Claim explicitly refers to the new reader and the pre-existing writer. Accepted in `consolidate-report.md`. Strong candidate for fix-induced interaction, rather than independent evidence of an unchanged original defect. | Exact introducing commit not audited. |
| Same ledger, round 4, S27, then round 5, S39 | S27 requires bounded reads; S39 finds the aggregate budget rejects valid individually bounded captures. `fix-na-r2-report.md` reports multiple failing regressions and fix `d37c728`; it explicitly replaces a previous S27 test that asserted the defective aggregate behavior. | This is evidence of a wrong earlier fix/interpretation. It should not count as two independent examples of generic architecture complexity. |
| Same ledger, round 6, T1 in `review-t2-r1.txt` | Newly reported lifecycle failure: invalid view lowering leaves a job stuck importing and uncancellable. `fix-t2-r1-report.md` describes three failing scenarios and fix `49c42d7`. Material and accepted with regression evidence. | Real qex/cargo were not exercised for this round; the report explicitly uses fakes. |
| Same ledger, round 6, T2 in `review-t2-r1.txt` | Concurrent cancel writes stale state outside its lease. Report describes two red tests and fix `e69eeee`. Material, accepted. | Broader interleavings unknown. |
| Same ledger, round 6, T4; round 7, T5 | T4's fresh-repository discovery failure is fixed by export-first staging in `3fa003c`. T5 then finds cancel finishing the run with the stopped export job. `fix-t5-report.md` describes two failing interleavings on `3fa003c`; inspected fix commit `d89c0e7` adds the qex-ID guard, rechecks cancellation, and adds regressions. Material, accepted, and supported fix-induced regression. | This supports reviewing a structural fix. It does not prove a predetermined extra round would have found a defect in the original version. |
| `residual-cli.research/reviewer-notes.ledger.json`, round 2, S15 | HTML-comment text acquires requirement authority. `reviewer-notes/red-report.md`, Review round 2 fixes, gives a failing literal hidden/visible-label scenario. Inspected commit `03581cb` adds comment handling. Material despite `needed: no`. | Classification as a missed original variant versus round-1 interaction needs deeper ancestry. |
| Same ledger, round 2, S17 | Pipe backpressure deadlocks the process under a large check-ignore stderr stream. The report names a 10-second watchdog failure and a positive control; fix `03581cb` is recorded. A `nit` can describe a demonstrated runtime failure. | Later tier-2 T3 removes the entire special-file discovery mechanism. Treating S17's fix as a lasting architecture improvement would be misleading. |
| Same ledger, round 3, T1 in `reviewer-notes.reply-t2.txt` | One stale/invalid item suppresses a distinct valid policy violation by changing the process exit from 1 to 2. Report describes five failing independent scenarios; inspected fix `d570aba` changes completeness handling and adds tests. Material and accepted. | Similar later T9 is an extension of this family, not automatically independent discovery. |
| Same ledger, round 3, T2 in `reviewer-notes.reply-t2.txt` | Mid-line comment openers bypass S15's line-start fix. Same authority-promotion family, a newly tested variant. Report extends the S15 regression and fixes comment scanning in `d570aba`. | This variant may have existed originally; it is not proven introduced by S15's fix. |
| Same history, round unknown, T9-T12 | `reviewer-notes/red-report.md`, Final fixes T9-T12, describes three additional failing regressions and fixes after `d570aba`; inspected Git history contains `6094b7d` with title "final fixes after tier-2 approval". T9 extends T1's completeness issue; T10 addresses a comment-diagnostic regression; T11 corrects duplicate/misleading diagnostics; T12 is explanatory documentation. | No recorded ledger round or matched final reviewer reply. Do not invent round 4 or treat these as four material defects. |
| `phoe-nix.research/vigil-disk-full.ledger.json`, round 2, S4/S5 | Lost sensed answers and stale rescue deadlines. `vigil-disk-full/disk-full-green-report.md`, Review round 2 fixes, explicitly says both were caused by the async rescue introduced for round-1 S3. It records red commits `711bc6a`/`a9a2ab1` and fixes `b28802e`/`d9c13fe`. `b28802e` was inspected. Material, accepted, fix-induced. | No independent runtime rerun. |
| Same ledger, round 4, T1 in `vigil-disk-full.reply-t2.txt` | Persistently full disk makes quiet keepalive calls return immediately, allowing agent-level spin. Report records nine red tests and fix `19b98c3`. Material and accepted. | Explicitly a revised DF1a contract. Earlier tests required immediate return and were changed. This is both a useful design finding and contract evolution, not clean evidence of failure against an unchanged specification. |
| Same ledger, round 5, T10/T11 in `vigil-disk-full.reply-t2b.txt` | T10 points out a misleading deadline-test name; T11 points out latency with unequal watch intervals and an unclosed min/max mutation gap. Both `nit/no`. | T11's behavioral significance deserves inspection, but no fix evidence was audited. Neither is automatically a confirmed new material defect. |

## Record contradictions and missing coverage

The residual ledger ends at S17 in round 2, although its round-3 reply has T1-T8. The phoe-nix disk-full ledger ends at S5 in round 2, although rounds 4 and 5 contain T1-T11. Paneweft's ledger ends at S41 in round 5, although rounds 6 and 7 contain T1-T5. All three have later `CHANGES` verdicts that would be mislabeled as zero findings by a ledger-only counter.

Edge's `pr1-r2.log` contains a 4/10 `CHANGES` response against a different observed checkout state, with S1/S2 still open and S3 a scope mismatch. `pr1-r2b.log` explicitly inspects `9ec5bd6d` and concludes 10/10 `APPROVE`, S1/S2 resolved. The ledger uses the latter. Both logs repeat their final response after token usage. A raw-text collector must identify the reviewed snapshot, superseded attempt, and duplicate final blocks. It cannot count both as independent review outcomes. The reason the first attempt saw a different state was not independently established.

Reports also contain evidence beyond final replies: Paneweft's `fix-t5-report.md` discusses T6/T7 and T8 coverage beyond the saved round-7 reply's T5. These are useful leads, but their review round and original reviewer wording remain unknown. Final dispositions do not reconstruct a complete discovery timeline.

## Implications for the experiment

The observable target should be "a later review found a newly demonstrated material problem," with separate flags for fix-induced regression, repeated family, and contract change. Preserve an unknown outcome when later review is absent or its reply is missing. A review that happened and found nothing needs an intact final reply, pinned snapshot, and an explicit coverage check.

Evaluate at a stated policy boundary. Under the legacy two-tier process, a first tier-2 finding is evidence for the existing fresh review. It does not demonstrate benefit from adding another round beyond that policy. Current build-loop v2 has different scheduling and can skip tier 2 after a passing Fable round; retain the workflow version and decision stage rather than assigning a universal round threshold.

The strongest concrete trigger in this sample is the size and kind of the previous fix: async control flow, leases, cancellation state machines, multi-stage execution, and cross-component validation changes produce new interactions. Any proposed Elo/K feature must beat a simple rule that requests another independent review after such fixes, while leaving required review policy intact.

No causal estimate of the optimal number of rounds is available here. Review continuation depends on earlier findings, code changes, reviewer choice, and policy. The histories demonstrate useful catches and failure modes for the labels; they do not show what would have happened if otherwise comparable changes received a different number of reviews. A prospective shadow recommendation with subsequent independent review is needed to test that question.
