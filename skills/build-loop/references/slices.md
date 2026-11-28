# build-loop reference: sliced red/green (structural round onward)

Policy since 2026-11-27 (owner). The design record, with the owner's decisions as they were made, is
`mstack.research/test-quality-core/slices/spec-draft.md`. Read this file before cutting slices for a
structural, hardening or release round, and paste the slice rules into the red and green briefs.

## Tools

| Tool | Does |
|---|---|
| `tq slice check N` | Red: in a scratch copy, `tq lint --since <base>` has no gating rows, each test fails on an assertion, and its notes are well formed. After green: every named mutant is killed, with one non-trivial flip per slice. Logs `gate` / `gate-ok`. |
| `tq mutants check` | Replays inline `tq-mutant` blocks or sidecar pins against clean and mutated trees; classifies each `trivial` / `non-trivial`. |
| `tq revert-check` | Applies a pin or revert in a detached scratch worktree, runs the restored test there, and compares the live tree before and after. Never `stash`, `reset`, `checkout` or `clean` in the live tree. |
| vigil `log:` item | `vigil hold add <hold> --for 'log:<slice log>?event=gate-ok' --label <slice>` ends when the gate passes. Never orchestrator mode for red or green. |

## When it applies (owner, 2026-11-27)

The structural round and later (hardening, releases). Pilots and other malleable work keep the batch
flow; their tests are thrown away with the design. tq still runs in every red gate, pilots included.

## Roles

| Role | Default | Does |
|---|---|---|
| Orchestrator | Opus | Holds project direction. Interjects about five minutes into each slice, settles disputes, keeps the journey |
| Red | Sol by default, Sonnet now and then (B1); one thread kept for the whole feature | Writes each slice's tests and pinned mutants, runs the slice gate itself, reads each finished green slice, does the white-box pass |
| Green | The other model | Implements one slice at a time; reads the slice log; may add notes to it |

This fits the current cap: whichever side Sonnet holds is the one working Claude agent, and Sol
does not count.

## The slice loop

A slice is 2 to 4 tests, plus the pinned mutants they must kill (below), for one small piece of
behaviour.

1. Red writes slice 1 and runs `tq slice check 1` (below). Once it passes, green starts slice 1.
2. While green works on slice N, red writes slice N+1.
3. **Red is never more than one slice ahead** (owner, 2026-11-27). Done with N+1 before green
   finishes N, red waits on its own hold (`vigil hold --for log:<slice log>?event=green-done&slice=N`;
   marker file `NN.green-done` until the `log:` kind ships), never in orchestrator mode, then
   reads green's slice N before writing N+2, so its tests fit the built system.
4. About five minutes into each slice, the orchestrator reads the log and red's tests and
   pushes on one or two points: direction, a weak input, a missing case. It does not referee
   anything the gate already settled.
5. Each dropped test goes in the log with its reason.

**Each agent holds itself.** Their prompt caches expire at different times, so each waiting agent keeps
its own vigil hold instead of ending its turn. The orchestrator's hold covers all three, so a stalled
agent raises `item overdue`.

## Why can't this run in parallel? (owner, 2026-11-27)

Ask it at every cut. If the answer is budget, live with the slower serial path. If it is the code (two
slices edit the same file), split the module first or resolve the merge afterwards, whichever is faster.

## The slice gate (red runs it; a program decides)

`tq slice check N` passes when:
- `tq lint --since <slice base>` shows no gating rows on the slice's tests;
- every new test fails on an assertion, never on an import, compile or collection error. The
  check runs in a scratch copy at red's commit, not in green's live tree;
- each test has `# catches:` naming a pinned mutant id, and a *when X, then Y* test has a
  `# reaches:` note in one of the two forms in `phases.md` §4 (another test's name, or the
  condition and effect in your own words);
- every pinned mutant in the slice is killed by the test that names it. This is checked once
  green's code lands, because a mutant needs code to mutate.

Red sees the gate output directly. The orchestrator steps in only on a failure red cannot
settle, or for the five-minute check.

Read [holdouts.md](holdouts.md) before the red and green briefs.

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

Two formats: inline (default, below) and a sidecar file (`.tq/mutants/M-012.json`, opt-out).

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

tq applies a swap only in a scratch copy, and flags a mutant `stale` when a later commit edits the lines
below a block but not the block.

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

Mutant ids point at the assumption ledger (`assumes=A-nn`).

## White-box pass and the revert check

When green is mostly done, red reads the whole implementation, adjusts tests at the real edges
and adds mutants for parts that are not obviously correct. For each adjusted test,
`tq revert-check TEST --mutant ID|--revert COMMIT` must show it red with the code broken and
green with the code back.

**Data safety 10.** It works only in a scratch worktree (`git worktree add --detach`), never runs
`stash`, `reset`, `checkout` or `clean` in the live tree, checks the live tree's status and file hashes are
unchanged before and after, and writes a `kill` event to the test ledger per result.

## Batch variant (pilots, and low budget)

Pilots always use the batch flow (`phases.md` §4–§5). Structural work falls back to it on a low budget
(B5), followed by the white-box pass with pinned mutants on the tests it touches.

## Decisions (owner, 2026-11-27)

- Pinned mutants are inline by default; sidecar is the opt-out.
- The orchestrator interjects on every slice in an area whose concern bar is 9; below 9, only when the
  gate fails.
- The orchestrator proposes the slice plan from the bars, the budget and the urgency (vigil advisories,
  agentpace ETAs). A slice covers at least two methods and at most one module.
- Log events use a vigil `log:` item kind once it ships; marker files until then.
- A review-fix slice takes a soft maximum of three findings; one fix that closes several counts as one,
  and the log names every finding it closes.

Open questions (inline-swap prefix, the vigil `log:` spec) live in the design record.
