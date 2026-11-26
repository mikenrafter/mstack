# test-quality reference: mutation and tautology checks

Moved verbatim from SKILL.md (2026-11-26 refactor). Read before the red gate, post-green spot mutations, and any review of tests.

## Mutation checks

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

## Hunt tautology explicitly

Before approving any test, ask of each assertion: *can this expression be
false given any implementation?* Tautology signs: value compared to itself;
mock returns what it was told; expected computed by the function under test;
a literal's length asserted on the literal; a test of a pasted copy; a
mirrored formula. Modes 1 and 5 in `modes.md` give fixes. For tautology, the
tool is the "revert the fix" mutation.

For an implication, also ask: *can the premise be true?* For a property of a
predicate, ask whether it restates the predicate's definition (`P ⇒ P ∨ Q`);
if so, assert the rule the predicate protects on the system's state instead.

## The mutation check that catches most failure modes

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

