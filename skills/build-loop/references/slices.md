# build-loop reference: sliced red/green (structural round onward)

Policy since 2026-11-27 (owner). The design record, with the owner's decisions as they were made, is
`mstack.research/test-quality-core/slices/spec-draft.md`. Read this file before cutting slices for a
structural, hardening or release round, and paste the slice rules into the red and green briefs.

## Until the tooling ships

Three tools this process names are not built yet. Use these equivalents and say so in the slice log:

| Named here | Until it ships |
|---|---|
| `tq slice check N` | Red runs, in a scratch copy at its commit: `tq lint --since <slice base>` (no gating rows), the slice's tests (each fails on an assertion), and a check that every test has `catches:` naming a mutant id (and `reaches:` where it states *when X, then Y*). Once green lands: `tq catches` with each mutant as a `[patch: …]` fault patch, so every named mutant is killed by its test. |
| vigil `log:` item kind | Marker files beside the slice log (`NN.green-done`, `NN.gate-ok`), held with `vigil hold --for file:<marker>`. Never orchestrator mode for red or green. |
| `tq mutants check` (inline `tq-mutant` blocks) | Write each pinned mutant as a fault patch named in the test's `catches:` comment; keep the inline block as documentation. |
| `tq revert-check` | By hand, in a scratch worktree only (`git worktree add --detach`): apply the mutant or revert, run the test (red), restore, run it (green). Never `stash`, `reset`, `checkout` or `clean` in the live tree. |

## Why

Big red rounds write the whole spec as tests before any code exists. The weak tests surface
late, far from the reasoning that produced them, and the retro sees only the end state. Dan
Luu's runs point the same way: agents asked for TDD or mutation testing mostly did ordinary
testing under that name. So the parts agents skip are made into checks a program runs, and
the agents argue over small slices while the code is fresh.

## When it applies (owner, 2026-11-27)

Only the structural round and later stages (hardening, releases). Pilots and other early,
malleable work keep the batch flow: one red run, then one green run. Their tests are expected to
be thrown away with the design, so the rigor isn't worth its cost there.
tq still runs in every red gate, pilots included (`tq lint --since`, `tq log`). Only the
slice-by-slice argument is saved for the stages where it matters.

## Roles

| Role | Default | Does |
|---|---|---|
| Orchestrator | Opus | Holds project direction. Interjects about five minutes into each slice, settles disputes, keeps the journey |
| Red | Sonnet, one session kept for the whole feature | Writes each slice's tests and pinned mutants, runs the slice gate itself, reads each finished green slice, does the white-box pass |
| Green | Sol | Implements one slice at a time; reads the slice log; may add notes to it |

This fits the current cap: red is the one working Claude agent, and Sol does not count.

## The slice loop

A slice is 2 to 4 tests, plus the pinned mutants they must kill (below), for one small piece of
behaviour.

1. Red writes slice 1 and runs `tq slice check 1` (below). Once it passes, green starts slice 1.
2. While green works on slice N, red writes slice N+1.
3. **Red is never more than one slice ahead.** When red finishes N+1 before green finishes N,
   it waits on its own vigil hook: `vigil hold --for log:<slice log>?event=green-done&slice=N` (marker file `NN.green-done` until the `log:` kind ships), then
   `keepalive`, never in orchestrator mode. When the event lands, red wakes up, reads green's
   slice N and only then writes N+2. That keeps the built system in mind when it writes tests
   that must make sense in the full system. (owner, 2026-11-27)
4. About five minutes into each slice, the orchestrator reads the log and red's tests and
   pushes on one or two points: direction, a weak input, a missing case. It does not referee
   anything the gate already settled.
5. Some tests in most slices will not survive. Each drop goes in the log with its reason.

**Each agent holds itself.** The three agents can have different prompt-cache lifetimes. A
Claude subagent's cache and a Sol session's cache expire on their own clocks, and the
orchestrator's clock is a third. So every agent that waits keeps its own vigil hold, and vigil
paces each keepalive to that agent's cache lifetime. Ending the turn and having the
orchestrator resume it would let red's cache go cold and reread the system from scratch, and it
would make the orchestrator a relay. Green does the same while it waits on slice N+1's
`NN.gate-ok`. The orchestrator's own hold covers all three, so a stalled agent raises
`item overdue`.

vigil already does most of this: keepalive reads the cache lifetime it observes in the
session's Claude transcript (5m or 1h), and uses 270 s for Codex when it can't observe one. Still
to check in the trial: that a subagent's keepalive finds the subagent's own transcript, not the
orchestrator's.

## The slice gate (red runs it; a program decides)

`tq slice check N` passes when:
- `tq lint --since <slice base>` shows no gating rows on the slice's tests;
- every new test fails on an assertion, never on an import, compile or collection error. The
  check runs in a scratch copy at red's commit, not in green's live tree;
- each test has `# catches:` naming a pinned mutant id and `# reaches:` where it states
  *when X, then Y*;
- every pinned mutant in the slice is killed by the test that names it. This is checked once
  green's code lands, because a mutant needs code to mutate.

Red sees the gate output directly. The orchestrator steps in only on a failure red cannot
settle, or for the five-minute check.

## The slice log, and vigil hooks

One append-only log per slice, `slices/<feature>/NN.jsonl`, with these events:
`proposed`, `gate`, `argument`, `dropped`, `green-note`, `slice-done`, `white-box`, `mutant`.
A readable `NN.md` is generated from it.

- Green reads the log when it picks up a slice and adds `green-note` events. That gives it the
  debate without stopping it and without making it hold every message in context.
- **vigil hooks (owner, 2026-11-27).** Each agent holds on the log events it waits for, through a
  dedicated vigil `log:` item kind: red on `green-done`, green on `gate-ok`, and the
  orchestrator on `dropped`, `argument` and gate failures. No marker file per event. Until
  `log:` ships, marker files stand in.
- The logs are the retro's raw data: which reasoning keeps producing tests that get dropped,
  which slices argued longest, and which mutants survived.

## Pinned mutants

Each test names the wrong implementation it catches, as a mutant with an id that a program
can apply. Then mutation testing is a check tq runs, not something we ask an agent to do.

There are two formats. A project picks one (see "Choosing a variant" below).

**Variant A: sidecar.** The swap lives in a side file, and the source carries a one-line
marker.

```python
def window(items, n):
    # tq-mutant: M-012 (window end is inclusive)
    return items[:n]
```

`.tq/mutants/M-012.json`:

```json
{"id": "M-012", "file": "src/window.py", "anchor": "return items[:n]",
 "swap": "return items[:n - 1]", "assumes": "A-07",
 "flip": "boundary", "killed_by": ["tests/test_window.py::test_last_item_kept"]}
```

The anchor is the original text, not a line number, so the mutant survives edits that move
code.

**Variant B: inline (owner, 2026-11-27).** The swap sits as a comment block right above the
lines it replaces. There's no sidecar and no anchor to match. A reader, a reviewer and the
agent editing that code all see the assumption and its wrong version in the same place.

```python
def window(items, n):
    # tq-mutant M-012 boundary assumes=A-07 killed-by=test_last_item_kept
    # | return items[:n - 1]
    return items[:n]
```

```rust
// tq-mutant M-031 drop-effect assumes=A-02 killed-by=store::tests::flush_writes_once
// | // self.flush()?;
self.flush()?;
```

- The header line gives the id, the flip type, the assumption and the killing tests.
- Each `| ` line is one line of the swap. By default the swap replaces the same number of code
  lines right below the block. `replaces=N` overrides that count.
- tq applies the swap in a scratch copy only, keeping the indentation of the lines it replaces.

What tq checks for this variant:
- The block is still followed by code, and the swap still parses once applied.
- When a later commit edits the lines below a block but not the block, `tq mutants check`
  flags the mutant as `stale` for review, because the swap may no longer be the wrong version
  of the new code. This catches the main drift risk of inline comments.

**Choosing a variant.** Both use the same ids, fields and outcomes, and tq reads both. A
project picks one in `.tq/config` (`mutants = inline | sidecar`). The default is inline, since
colocation helps every reader. Sidecar is for projects that won't carry the comments.

**Which flips.** Each mutant challenges one assumption. The guideline set, in order of how
often it found real bugs in the corpus rounds:

| Flip | Example |
|---|---|
| boundary | `<` ↔ `<=`, `n` ↔ `n-1`, inclusive ↔ exclusive end |
| skip the branch | drop an early return, a guard or an error path |
| constant result | return the empty value, the default or the input unchanged |
| drop an effect | skip a write, a lock, an invalidation or a notify |
| order | reverse an iteration, swap two arguments, reorder two state steps |
| wrong fallback | take the fallback on success, or never take it |
| swallow | catch and continue where the code must fail |

A random mutant does not count. Each one names its assumption (`assumes:`), and each assumption
gets at least one mutant.

**What tq checks** (`tq mutants check`), each mutant in its own scratch copy:

| Outcome | Means | Action |
|---|---|---|
| killed by its named test | the test holds | none |
| survived | the test is weak, or the assumption was false | red fixes the test, or the assumption ledger records that the assumption did not hold |
| anchor missing | the code was restructured | retire the mutant; the journey says why |
| no longer expressible (e.g. a type now rules the bug out) | the structure guarantees it | the test may be redundant; the journey records the guarantee the structure now gives, so later agents know why the architecture moved |

The assumption ids are shared with the assumption ledger and with the queued
assumption-masked differential experiment (`test-audit-2026-11-26/experiments-queued.md` #2):
build variants with one assumption withheld, then check whether the pinned mutants and the
variants' disagreements point at the same places.

## White-box pass and the revert check

When green is mostly done, red reads the whole implementation, adjusts tests at the real edges
and adds mutants for parts that are not obviously correct. For each adjusted test,
`tq revert-check TEST --mutant ID|--revert COMMIT` must show it red with the code broken and
green with the code back.

**Data safety 10.** The script never touches the live tree:
- it copies the tree into a scratch worktree (`git worktree add --detach` under the scratch
  directory) and works only there;
- no `stash`, `reset`, `checkout` or `clean` in the live tree;
- before and after, it records `git status --porcelain` and a hash of every tracked and
  untracked file in the live tree, and fails loudly if they differ;
- it removes the scratch worktree in a `finally`, and on failure keeps it and prints the path;
- it writes a `kill` event to the test ledger for every result.

## Batch variant (pilots, and low budget)

Pilots always use it. Structural work falls back to it when budgets are low (build-loop B5):
the legacy batch flow, which is one red run for the
whole scope and one green run. Then the white-box follow-up, with pinned mutants and
`tq revert-check` on the tests it touches.

## Ledger additions

`slice` (feature, number, tests proposed and kept, drops and their reasons, argument count,
wall time), `mutant` (id, assumption, flip, outcome), plus the existing `born`, `died`, `kill` and
`cost` events. The questions this adds: are slice tests kept more often than batch tests? Do
pinned mutants find more escapes than white-box tests? What does a slice cost against a batch?

## Cost

Unmeasured. Record tokens per slice through agentpace on every sliced round, and compare it with
the batch flow of earlier rounds.

## Decided (owner, 2026-11-27)

1. **Pinned-mutant format:** inline is the default, with sidecar as the opt-out (variant B above).
2. **Orchestrator interjection:** every slice in an area whose concern bar is 9 (review ledger
   bars). Below 9, only when the gate fails.
3. **Slice size:** the orchestrator proposes a slice plan for each feature from the bars, the
   budget and the urgency, read from vigil advisories and agentpace ETAs. A slice covers at
   least two methods and at most one module. It is never one method, and never more than a
   module.
4. **Log events:** a dedicated vigil hook, not marker files. vigil gets a `log:` item kind
   (`log:<file>?event=green-done&slice=3`) that fires when a matching JSONL line is appended. Red,
   green and the orchestrator each hold on the events they wait for. Marker files are only the
   fallback until that ships.
5. **Review-fix slices (owner, 2026-11-27):** a fix slice takes a soft maximum of three review
   findings. It's soft because one fix sometimes closes several findings. Those count as one,
   and the slice log names every finding the fix closes.

## Open questions

- Is one `| ` prefix fine for inline swaps in both Python and Rust?
- The vigil `log:` item is new vigil work (the vigil repo, Rust). It needs its own spec and red
  tests before the slice trial.
