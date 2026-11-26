# test-quality reference: lessons from suite audits

Read when auditing a suite or prioritising test work.

## Grounding from suite audits

Two audits of a large suite (about 14,000 test blocks across three repos)
produced these lessons; use them to prioritize.

| Lesson | What to do |
|---|---|
| Many tests never ran: TZ-gated, fixture-gated, sibling-checkout-gated skips | Fix execution first (TZ matrix, committed fixtures, fail-on-skip under `CI`) before writing new tests. |
| Invariant gaps sat next to thousands of passing tests (ACK ordering, prune safety, RAM-only streams, dangerous-opcode lists) | Map each written invariant to a behavioral test that drives the real engine; grep-guards do not count. |
| Source-grep guards: 88 audited, about a fifth worth keeping | Keep whole-tree dependency/caller bans with a positive control; convert ordering/token greps to behavior; delete comment-proximity checks. |
| Shared-oracle limit: incremental-vs-forced parity passes when both inherit a regression | Keep an independent versioned fixture beside parity tests; store the generating algorithm version/pin with each golden. |
| Characterization suites overlap controller tests, but not fully | Trim case by case; do not delete wholesale. Check what the higher layer still uniquely covers (real claims, persistence, races). |
| Real waits dominated cost (a 60 s breathing session, fixed 5 s reply windows) | Inject clocks and parameterize windows; keep timing out of correctness tests. |
| Vacuous tolerances and `greaterThan(0)` everywhere | Sweep mechanically after reworks, not before, to avoid collisions. |
| A test endorsed behavior a written invariant forbids | When a test and an invariant conflict, stop and ask the owner. Do not "fix" either silently. |
| Golden baseline failed after an algorithm version bump; nothing recorded which version made it | Diff old vs new at field level; rebaseline only if all changes are the intended ones; store version and pin beside the golden. |


## The 2026-11-26 audit (about 20 repos, through Dan Luu's agentic-testing lens)

Source: `mstack.research/test-audit-2026-11-26/SUMMARY.md`. Large, careful suites still missed the same few
places; check these first:

| Gap | Seen in |
|---|---|
| Concurrency tested one process at a time: deleting the lock left all 17 queue tests green | workq, agentpace share, job-seeking `flock` |
| The last fallible step never fails in the test (spy always succeeds) | edge workout cancel, usagewindow delivery, qex host measurement |
| Inputs that cannot tell right from wrong: equal delays, empty HKDF `info`, disjoint move/split, canonical-only columns, one-row restore, windows shorter than one window | edge, adb-bridge, diff-core, residual-cli, polara-port |
| Self-round-trip or shared table where literal bytes were needed | openstrap-protocol CRC/COBS, adb-bridge crypto, polara scene table |
| Token greps standing in for behaviour | nix-scout activation |
| Absence asserted with no positive control (`called` recorded, never asserted empty) | phoe-nix obsidian-mcp (a live bypass) |

Fix history is a useful prior, not a sufficient one: the queue lock had no fix commits. Ownership crossing a
module or process boundary was the stronger risk signal.
