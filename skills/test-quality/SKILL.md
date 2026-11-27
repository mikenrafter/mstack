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

Agents test under the streetlight by default: many tests where code was
already likely correct, few where it is hard, and inputs that cannot tell a
right implementation from a wrong one. This skill does three jobs. It steers
away from those defaults (the tester brief), it caps how many tests a change
launches with, and it holds the reference detail for when you need it.

| Skill | Load it when |
|---|---|
| `technical-excellence` | The test proves an interface, invariant or CLAIM, or a type could make the test unnecessary. Source of the CLAIM convention and mated-part (parity) rule. |
| `build-loop` | You are in a red/green run or a review round. Its red gate uses this skill; review findings about tests are judged with it. |

| Reference | Read it |
|---|---|
| `references/tester-brief.md` | **Always**, before writing or reviewing a test. Paste it verbatim into every brief for an agent that writes or reviews tests. |
| `references/mutation.md` | Before the red gate, for post-green spot mutations, and in any test review. |
| `references/techniques.md` | When a test uses a technique: algebraic laws, state machines, conditional properties, oracles, goldens, parity, domain checks. |
| `references/shapes.md` | When choosing what kind of test to write: 13 valuable shapes, what each catches, and a table from the risk in the code to the shape. |
| `references/modes.md` | When reviewing or auditing tests: failure modes 1–14 and the ones the classic list misses. Cite mode numbers in findings. |
| `references/audits.md` | When auditing a suite or deciding where test work goes first. |

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

## 3. Launch budget (owner, 2026-11-26)

You never know the problem space well enough before the code exists. Red
first can reduce that gap but not close it. So launch with few tests, aimed
well, and add tests where the code shows they're needed.

- Rank the risk areas first (tester brief, set 2). Most tests go to the top
  areas, one or two to each of the rest.
- A build-loop red run launches with at most about 12 tests per pilot scope.
  Each one past that, or past the share for its area, states why in its WHY
  line. The orchestrator may raise the ceiling for a structural round; say so
  in the brief.
- No-panic tests and source greps don't count toward the budget. They also
  never stand in for a risk-area test.
- Table-driven cases count as one test when they share one oracle and one
  fault.

## 4. Writing tests (especially as a subagent)

- Write expectations from the spec before reading the implementation's
  output. Show the arithmetic.
- Pick inputs on which the plausible wrong versions disagree (tester brief,
  set 3). Name the wrong version in `# catches:`.
- State each test's why and CLAIM id (section 1).
- List inputs you're unsure about instead of inventing expected values.
- Confirm each new test fails against the broken code (red first).
- Never loosen an existing assertion to make a fix pass. If it must change,
  say why in the commit message.

**After green: the white-box pass.** Red first steers toward black-box tests,
and the hard cases often only show once the code exists. Read the
implementation and list what is not obviously correct: a reversed loop, an
off-by-one window, a lock, a fallback, an `if` that hides a second rule. Add a
test at each, inside the remaining budget, and run the spot mutations
(`mutation.md`).

**For high-risk sections: an independent re-derivation.** A fresh-context
agent works from the spec alone, without the production code or its helpers.
Diff its result against ours. Each disagreement is a test to write or a spec
question to settle. This is for finding unknown bugs, not for checking known
ones.

## 4a. tq in every red gate (owner, 2026-11-27)

`tq` ([testquest](https://github.com/mikenrafter/testquest), installed through phoe-nix) is on
PATH. Use it in every red phase, pilots included:

- `tq lint --since <base>` on the new and changed tests. A gating row blocks the gate.
  A deliberate form gets `# tq: allow RULE REASON` on the flagged line or the line above it
  (for no-assert and guarded-assert, that is the `def`/`fn` line), with a reason the reviewer can
  check. `tq rules` lists the rules and what each one exempts.
- `tq catches` replays each `# catches:` fault in a temporary copy, so the spot mutations are
  run by a program, not described.
- `tq log record --since <base>` after each phase commit, `tq log lint --since <base>` with
  the gate, and `tq log kill` with the replays. They write the test ledger
  (`tq log where` shows where it is; a config file sets it). Phase commits carry a
  `Test-Phase:` trailer (`red`, `green`, `white-box`, `re-derivation`, `hardening`,
  `review-fix`, `bug-fix`).
- `tq log report` shows survival by phase, rule precision and deletion candidates;
  `tq log report --global` does the same across every repository, for retros.

## 5. Reviewing tests

Read the assertions before the green checkmark. For each test, name the bug it
catches and run the mutation check (`mutation.md`). Check the inputs: would the
plausible wrong version pass? Check the budget: are the tests aimed at the
risk map, or under the streetlight? Report each hollow test with the assertion
quoted, the mode number (`modes.md`) and a concrete fix.

A checked proof (Lean, Verus, a property a solver discharges) is a test, and it
can be hollow in the same ways: it proves the wrong statement, its hypotheses
contradict each other, or its guarantee restates a precondition. For a new
proof, name the requested behaviour in the theorem, show one case that meets the
premises, and name one plausible broken implementation the theorem excludes
(owner, 2026-11-27).

Findings outside the change under review go to `<repo>.research/nitpicks.md`
(format: build-loop `references/nitpicks.md`), not into this diff.
