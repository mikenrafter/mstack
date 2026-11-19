---
name: test-quality
description: >-
  Use when writing tests, reviewing a test diff, fixing a red test, auditing a
  suite, or when a subagent in the build-loop red phase hands back tests.
---

# Test quality

A green run says nothing about whether a test can fail. For every test you
write or review, answer one question: **if the bug came back, would this go
red?** If you can't name the bug it catches, it's hollow.

| Skill | Load it when |
|---|---|
| `technical-excellence` | The test proves an interface, invariant or CLAIM, or a type could make the test unnecessary. Source of the CLAIM convention and mated-part (parity) rule. |
| `build-loop` | You are in a red/green run or a review round. Its red gate uses this skill; review findings about tests are judged with it. |

## 1. Every test says why

The reason a test exists is hard to recall later. Annotate each test with a
short WHY: the bug, rule, incident or claim it guards.

```
// why: a partial chunk must never be ACKed (invariant 3.1; regression of the
//      2026-09 early-ack bug). Fails if commit moves after ack.
// proves: CLAIM(ack-order)
```

- A test proving a CLAIM (see `technical-excellence`) names its id, so the
  claim's grep finds its proof.
- No why, no keep: a test whose purpose nobody can state is a deletion
  candidate.
- Expected values show their derivation (spec section, capture, arithmetic).

## 2. Placement

Co-locate tests with the code they test, unless the repo's convention says
otherwise (when in Rome). A test beside its module shows what the abstraction
is, travels with it, and is deleted with it. Cross-cutting and end-to-end
suites live apart, and say so in their why.

## 3. Techniques worth using

### Monoids and accumulators
If a type combines (`combine`, identity element), property-test the laws:

| Law | Property |
|---|---|
| Identity | `combine(x, empty) == x == combine(empty, x)` |
| Associativity | `combine(combine(a,b),c) == combine(a,combine(b,c))` |
| Commutativity | `combine(a,b) == combine(b,a)` (only if claimed) |
| Split-merge | for any split of the input, `combine(fold(left), fold(right)) == fold(whole)` (single pass equals chunked/parallel/incremental) |

Generate inputs randomly with a fixed seed; shrink failures.

### State machines
Model-based property tests: a small pure model of the intended states and
transitions; generate random command sequences; apply to model and real
system; assert observable state agrees after every step, and that illegal
transitions are refused. Include crash/rollback and retry commands.

### Conditional and leads-to properties
A property shaped *when X, then Y* passes for free when X never happens; so
does *when X, eventually Y*. Give each one a witness:
- a test that drives the system into X through the production entry point,
  with shipped defaults, and asserts it got there;
- for generated runs, a check that the generator reaches X: Hypothesis
  `find(strategy, reaches_x)`, QuickCheck `cover` with `checkCoverage`, or a
  counter asserted above zero (proptest has no built-in).
For *eventually*, end each generated trace with a bounded drain (tick or run
until idle) before checking. The `# catches:` mutation breaks Y; if the
property stays green, suspect X before the assertion. (Hillel Wayne,
2026-02-11; research/20.)

### Oracles
Expected values come from something independent of the code under test:
- a slow, obviously-correct reference implementation;
- a hand-computed fixture (arithmetic in a comment);
- a real capture or spec table, decoded field by field.
Beware a shared oracle: incremental-vs-forced parity can pass while both
paths inherit the same regression. Keep an independently derived fixture next
to the parity test.

### Goldens
High quality means: reviewed by a person, minimal (smallest input that shows
the behavior), deterministic (zone, clock, seed, locale pinned), explained
(why: what it pins, version or pin it was generated at). Regeneration is a
deliberate, flagged act, never silent. A golden nobody inspected is mode 12.
Retain exact comparison for a fixed version; do not hide change behind a
blanket tolerance.

### Parity tests for mated interfaces
Writer/reader, encoder/decoder, client/server: test both against literal
bytes or messages from the spec or a real capture, field by field, not just
against each other. Round-trip tests are a supplement, never the proof.
Dedupe parity corpora and report the real unique count.

## 4. Mutation checks

**Cheap manual mutations (do these every time).** Pick 3-5 spots in the code
under test, mutate one at a time, run the focused tests:

| Mutation | If still green |
|---|---|
| Flip a condition (`<` to `<=`, `&&` to `\|\|`, negate) | Boundary or branch untested |
| Delete a line or a call | That line is unproven; or the test is at the wrong layer |
| Change a constant (offset, threshold, default) | Value not asserted exactly |
| Swap two arguments or an ordering | Order not pinned |

Use the result to decide: more tests needed, or tests that prove nothing
(remove them). Revert every mutation; never commit one.

**`# catches:` and post-green spot mutations (build-loop red/green).** Each
red test carries a `# catches: <a plausible wrong implementation this fails>`
line. If you cannot name one, the test is likely a tautology; rewrite or drop
it. After green, the orchestrator applies 2-3 of those named wrong
implementations and checks the matching tests go red. A green implementer that
edits a red test says so in its report; the edit becomes a review finding.

**Mutation tool, periodically.** If the stack has one (for example Stryker,
mutmut, cargo-mutants, PIT), run it every so often on a stable module.
Surviving mutants show gaps. Tests that kill no unique mutant and duplicate
another test's kills are candidates to prune, which keeps the standard suite
small and fast.

## 5. Hunt tautology explicitly

Before approving any test, ask of each assertion: *can this expression be
false given any implementation?* Tautology signs: value compared to itself;
mock returns what it was told; expected computed by the function under test;
a literal's length asserted on the literal; a test of a pasted copy; a
mirrored formula. Mode 1 and 5 below, with fixes. For tautology, the
tool is the "revert the fix" mutation.

For an implication, also ask: *can the premise be true?* For a property of a
predicate, ask whether it restates the predicate's definition (`P ⇒ P ∨ Q`);
if so, assert the rule the predicate protects on the system's state instead.

## 6. The mutation check that catches most failure modes

Mentally (or actually) mutate the code under test and see if the test fails:

1. Revert the fix the test claims to pin. Still green? The test is wrong.
2. Delete the call site the test claims to cover (not the helper: the place
   production calls it). Still green? Wrong layer.
3. Empty the list, set or config the test iterates over. Still green? Vacuous.
4. Run it under `TZ=UTC` and under a DST zone. Different result, or a skip?
   Host-dependent.
5. Remove the fixture file. Skip with no CI failure? It never runs in CI.
6. Make X unreachable (delete the transition into it, set the limit to 0,
   empty the trigger set). The *when X* properties stay green, as expected;
   the witness must go red. Nothing red? The suite cannot tell a system that
   handles X from one that never reaches it.

Before calling a suite done, do 1 for at least the tests whose names claim a
bug.

## 7. Classic modes

| # | Mode | Looks like | Fix |
|---|---|---|---|
| 1 | Tautology | Value compared to itself; mock returns what it was told; expected computed by the function under test; `hasLength(12)` on a 12-item literal; `isNotNull` on a tear-off | Expected value from the spec or a hand calculation |
| 2 | Over-mocking | The engine/unit under test is stubbed; only fakes run | Mock the clock, network, platform. Never the unit |
| 3 | Asserts current behavior | Magic numbers with no derivation (`9.03`, `closeTo(50, 8)`); comment-free goldens | Show the arithmetic in a comment, or cite the spec/capture the value came from |
| 4 | Happy path only | No empty, null, zero, negative, NaN, boundary, duplicate, truncated, error, or thin-input case | List the edge cases before writing the first test |
| 5 | Mirrored implementation | Test re-implements the formula, or tests a pasted copy of a private helper | Hand-computed constants; test the real symbol |
| 6 | Coverage theater | Code runs, nothing meaningful is asserted; benchmark tests with no `expect` | Every test asserts a concrete value |
| 7 | Existence only | `isNotNull`, `isNotEmpty`, `returnsNormally`, `greaterThan(0)`, `isA<T>()`, `verify(called)` where the exact value is known | Assert the value. If the seeded row count is 3, assert 3 |
| 8 | Weakened during a fix | Exact value became a range; case deleted; `skip:` added; tolerance widened | Treat any loosened test in a fix diff as a red flag. Change the code, not the test. `git log -p` the test file |
| 9 | Volume over quality | Dozens of near-identical cases; parity corpora where the same records repeat (978 unique of 2,934) | Fewer, distinct cases; dedupe corpora and report the real count |
| 10 | Confidently wrong | Expected value contradicts the spec, docs, or the test's own earlier assertion | Flag uncertain inputs instead of guessing |
| 11 | Unreadable failure | `expect(cond, isTrue)` with no `reason:`; byte lists without hex | Match on the value, or add `reason:` naming expected vs actual |
| 12 | Blind golden | Snapshot regenerated by an env var; nobody inspected it | Golden only reviewed output; note who checked it and against what |

## 8. Modes the classic list misses

These came up across three repos, often in tests that looked careful.

**Host-timezone dependence.** DST and local-vs-UTC tests that only bite when
the machine's zone differs from UTC, or that `markTestSkipped` unless
`TZ == America/Denver`. CI runners are UTC, so the check is vacuous there.
Calls that default to the host zone (no offset argument) also flip results
by zone. Fix: pin the zone inside the test, or pass the offset explicitly.
Never derive the expected value with the same `toLocal()` the code uses.
Run CI as a matrix: UTC plus one DST zone.

**Silently skipped fixtures.** The test skips when a data file is absent,
and that file is gitignored or lives outside the repo. CI never runs it, yet
it's often the only end-to-end or real-capture test. Fix: commit a small
fixture, or make the skip loud in CI (fail when `CI` is set). Same for sibling
checkouts: a guard that skips unless `../analytics` exists, when the real
directory is `../openstrap-analytics`, has never run anywhere. Golden groups
that skip because the golden directory is absent are the same mode.

**Source-grep guards.** "Ordering is untouched" checks that two identifiers
appear in a file; "prune order" checks `indexOf` positions; a "no 86400 s"
guard covers 22 hand-listed files and misses `86_400`. These pass if a comment
contains the string, if the code is reordered in a way the regex can't see,
or if the bug lands in an unlisted file. Fix: drive the behavior (seed a
partial day, prune, assert rows survive). Keep grep guards only as a backstop,
cover the whole tree, and include a positive control proving the pattern
matches something. A whole-tree scan for a new caller or forbidden dependency
is the legitimate kind (an audit of 88 guard files kept 18 of this type,
converted 48 to behavior tests, and removed 22).

**Pins dead code or the wrong layer.** The test exercises a pure helper, but
production reads the value through a different path. Real examples: a
readiness-flash test pinning a getter with zero callers; a freeze test that
covers the pure function but not where the screen reads or the engine writes;
a race test that never imports the service and tests `List.remove`; an "edge
half" test that only calls the sibling library; "the stager only runs inside
`Isolate.run`" checked by two strings anywhere in the file (output parity is
not execution placement). Fix: test through the seam the user hits, or add a
test that the production path calls the helper.

**Shared-table round trip.** The test builds a frame at offset 13 and the
parser reads offset 13 from the same constant. A wrong offset passes. Fix:
literal bytes from a real capture or the spec, decoded field by field. When a
real capture exists, assert every field you can hand-decode, not just the
version byte or the first 4 of 8 token bytes.

**Capability tested once, wired N times.** The new decoder is tested
directly, but two other entry points still call the old one. Fix: count the
entry points and test each, or add a guard that they all route through one.

**Iterating over the current set.** `for (op in dangerousCmds) expect(...)`
stays green when the set is emptied or an item is dropped. Fix: pin the
required members by name, then loop.

**Conditional assertions.** `if (row != null) expect(...)` passes with nothing
checked. Fix: assert the precondition first.

**Assertions on absence with no positive control.** "Nothing was written"
checked via `total_changes` or a log line, without proving the probe moves on
a real write. A no-bounce check that matches log wording passes if the log is
reworded. Fix: show the probe detects the positive case in the same test.

**Test-only configuration.** The test runs with thresholds (300/200/200) that
differ from shipped defaults (200/150/750). Fix: test the shipped defaults,
plus overrides as separate cases.

**Change-detector literals.** `expect(kAlgoVersion, 104)` or a literal SHA.
It fails on every bump and catches nothing. Fix: assert the property you care
about (the pinned commit contains the cited change).

**Real time.** `DateTime.now()`, real `Future.delayed` sleeps, and "nothing
yet" checked after 300 ms. Flaky near midnight and on slow runners; a real
one-minute wait inside a correctness test costs a minute on every run. Fix:
`fakeAsync` with `withClock`, or inject the clock.

**Tolerance that spans the plausible universe.** VO2max accepted in 30-70
when the hand value is 49.14; RMSSD up to 500 ms; one-sided bounds with no
upper limit; `closeTo(50, 8)` where the formula gives exactly 50 at z=0, so
weights and signs go untested. Fix: tolerance sized to numeric error, not to
"looks reasonable."

**Vacuous antecedent.** A property checks *when X, then Y*
(`if state == RETRY: assert ...`, `prop_assume!(x)`, a filtered strategy) and
X never occurs: the generator never makes the triggering input, the test
builds the object with non-shipped settings, or a refactor removed the only
path into X. It stays green with Y broken. Hillel Wayne's example: "a worker
in Retry eventually leaves Retry" holds for any worker that never retries.
Detect: break Y; still green means X never fired. Fix: a witness that
reaches X through production with shipped defaults, plus a generator check
(§3).

## 9. Domain checks worth adding wherever they apply

- **Absent input.** Missing or thin input returns null, absent, or "—", never
  a default or a value derived from another metric.
- **Idempotence.** Run the computation three times with slightly more data;
  the persisted value stays stable. Append a duplicate day; the baseline
  doesn't move.
- **Failure paths.** Every flag set on the happy path is cleared on error,
  timeout, and give-up.
- **Durability ordering.** Commit before acknowledge, tested by driving the
  real engine and observing the order, including a rollback case.
- **Ambient state.** Globals that change output are re-armed inside isolate
  closures, and a test shows output changes when they're set.

## 10. Grounding from suite audits

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

## 11. When writing tests (especially as a subagent)

- Write expectations from the spec before reading the implementation's
  output. Show the arithmetic.
- State each test's why and CLAIM id (section 1).
- List inputs you're unsure about instead of inventing expected values.
- Confirm each new test fails against the broken code (red first).
- Never loosen an existing assertion to make a fix pass. If it must change,
  say why in the commit message.

## 12. When reviewing

Read assertions before the green checkmark. For each test, name the bug it
catches and run the mutation check above. Report hollow tests with the
assertion quoted, the mode, and a concrete fix.
