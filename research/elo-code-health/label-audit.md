# Patch audit of commit-title labels

## Top findings

- [C] Twelve deterministic positive-title candidates were inspected, three per prediction subject. The sample uses the 25%, 50%, and 75% positions in first-parent positive-title history. It is a small diagnostic sample, not a precision estimate.
- [C] Two sampled Diff-core candidates change evaluation metadata only and produce zero eligible source touches. The source filter prevents these from becoming positive file events, but they still occupy commit-based time windows.
- [C] Analytics' consolidated audit mixes corrections, formatting, and helper changes across 42 eligible source files. Treating every touched file as defective overstates the evidence.
- [C] Targeted inspection found plausible corrective changes with negative title labels in Edge, Analytics, and Diff-core. The labels miss real behavior changes.
- [D] Independently adjudicated defects and actual inspection time are necessary before claiming defect-detection value.

## Inspected positive candidates

| Project | Revision | Patch interpretation |
|---|---|---|
| Edge | `eab24735aae8a47adda4d37a5e1c5f81443b6736` | Readiness display and pipeline saturation changes, plus tests. Corrective intent is evident; the patch is not a reproduced production incident in this experiment. |
| Edge | `3b791cc2ef7a8841847c9dbfc8a4b93a5840922e` | Replaces an infinite upper zone bound before downstream rounding. Concrete crash mechanism and added regression assertions. |
| Edge | `1eca7a8ba6dfe839f716e36776a789ddb8f44e33` | History-drain ownership, cancellation and retry changes across foreground/background paths. Corrective lifecycle work involving several components. |
| Analytics | `168d97677570cbb97a2d1504d80df7029476f327` | Replaces whole-night references with local estimates in cardio staging; adds a captured-night fixture. Corrective algorithm change. |
| Analytics | `1fa8144a5e3b728ce91eeed6ecbc15d482933b44` | Mixed audit: title/body describes corrections, while inspected hunks also include formatting and helper replacements. Attribution of defects to every touched file is unjustified. |
| Analytics | `3a524e176b46bae0d53cd393c5f9f49e2ce62d2e` | Separates unobserved intervals from wake and changes gap handling. Concrete abstention/representation correction. |
| Qex | `c6d71c263aecca91feceeea59d74ff17e35dc7af` | Writes retry state after deciding whether another attempt will run, preventing a transient terminal record. Concrete lifecycle correction. |
| Qex | `c0f245a9e73fed83a27c5dbce2e97604b1be6c9e` | Protects records needed by unfinished work and revises selection/reporting behavior. Corrective change mixed with interface work. |
| Qex | `995186cd5eea55c8005fca70d58b3c9998ee8b0f` | Adds nonblocking open and a bounded read to peer records. Concrete blocking and resource-bound mechanisms. |
| Diff-core | `75eee76119a0b1fcc41af4947436bff89eea2e75` | Adjusts four golden-evaluation TOML files. No eligible source file event. |
| Diff-core | `9ee2dd6108c6e66d2c8b52e4db0b2054c8329f57` | Appends one experiment-log entry. No eligible source file event. |
| Diff-core | `254ec5a90812d09e36d9452b7b44e0f9b6c11780` | Release combines a helper extraction, UI removal, tests and stated clipboard correction. Weak localization label. |

## Targeted negative-label checks

These were selected by words such as `keep`, `guard` and `honor`, after the first metrics were available. They are evidence of a limitation, not a revised evaluation set. The frozen labels and reported holdouts remain unchanged.

- Edge `79abcbc350751dc57ded244c47b7cfdc9314d05e`, "Sleep coach: keep target bedtime/wake on the user's local clock after a zone change." The commit body explicitly describes an incorrect target after a flight and several fixes; the subject has no positive keyword.
- Analytics `3a7ca34d30233ff11e6c2877083f319a907ccb31`, "autoDetectWorkouts: keep a mid-session rest inside one workout." The body describes a real session split and the patch changes gap bridging. This could be adjudicated as a defect fix or a behavior extension; the title rule cannot resolve it.
- Diff-core `d556539e8038a49ed7fbf8bb260728c358b63d54`, "repo eval: honor deleted-file golden expectations." The patch adds deletion handling to the evaluator without a positive title keyword. It changes the measurement tool rather than a deployed application defect.

## Architectural pair audit

The first three retained examples for Edge's highest-support pair, derivation engine and database, illustrate a major confound:

- `b369f1022ff4d1fb304953cd73fa1cb30fefe814` combines readiness notification changes in the engine with private-session filtering in the database. Sharing one integration commit does not establish one architectural cause.
- `c11f5cbac942969a410764e86d1a13bdd39a8651` links retention pruning, a monotonic prune cursor, and refusal to rederive a truncated night. This is a concrete shared invariant across the pair.
- `8246fefdc33d623b4a70246d81afb2a0ff13b3b5` combines cross-day rollup behavior with salvage-table changes. Again, a mixed sweep inflates apparent coupling.

The retention example is the strongest candidate for a subsequent boundary experiment. Counts alone would not have selected its invariant.

## Where your setup differs

`test-quality` requires an independent reason for each assertion. Applying that discipline here exposes the distance between "a fix commit touched this file" and "a test independently demonstrated a defect in this file."

## Candidate actions

1. Adjudicate a larger source-level sample with a frozen rubric before extending the predictor.
2. Separate mixed integration commits into independently supported changes before interpreting coupling as architecture.
3. Replay a retention/pruning scenario across both implementations before proposing a boundary move.

## Sources

Local Git patches at the full revisions above, read 2026-11-16 UTC. Reproduce with `git -C <repository> diff <revision>^ <revision> -- <source-path>`. No subject tests or historical application versions were executed.
