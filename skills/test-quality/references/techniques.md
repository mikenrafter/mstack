# test-quality reference: techniques

Moved verbatim from SKILL.md (2026-11-26 refactor). Read when a test uses one of these techniques.

## Techniques worth using

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
Report each command's firing count. A property "holds" vacuously when the action that would
break it never fired; fail the run when a declared action has zero firings.

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

**Golden, invariant or substring: pick by what the contract is** (owner, 2026-11-27).
- **The whole output is the contract** (text an agent or person reads and follows:
  hook advice, CLI help and messages, a rendered prompt or brief, a report): one golden
  of the complete output, normalised only for what really varies (temp paths, clocks).
  Not a row of substring checks: those are micro-snapshots (mode 13), which pin a few
  fragments and let every other sentence change unreviewed. The iterative red-green
  loop drifts into them, because each fix round adds one more `assertIn` for the
  phrase it just changed.
- **Only a property matters** (every output names a next step, no output exceeds a
  width, every row has an owner): an invariant checked over every output or a
  generated set, not a snapshot.
- **One fact must survive rewording** (the alert names the changed file): a single
  substring check is fine.
- Prefer a golden that covers a larger part of the system (a whole session's output,
  a whole report) over many small ones.

**Who may regenerate a golden.** Regenerating is the owner's call by default: ask, show
the diff, and list each regenerated file and why it changed in the commit message.
The exception is a golden that moves because of a change the owner asked for: when the
owner requests a skill or wording change and the hook's golden changes with it, the
request is the approval. Regenerate, read the diff to confirm it shows that change and
nothing else, and say so in the commit. Any change you did not expect in the diff goes
back to the owner.

### Parity tests for mated interfaces
Writer/reader, encoder/decoder, client/server: test both against literal
bytes or messages from the spec or a real capture, field by field, not just
against each other. Round-trip tests are a supplement, never the proof.
Dedupe parity corpora and report the real unique count.


## Domain checks worth adding wherever they apply

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

