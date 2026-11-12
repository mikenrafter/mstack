---
name: question-everything
description: >-
  Interrogate a feature before any implementation code exists, so defects are
  caught cheaply in the spec and red tests instead of in review rounds. Covers
  the designer interview (high-fidelity detail, push back), the questions to
  ask the user and yourself (which checklists apply, what is reusable, what
  recurs), turning recurring findings into project checklists early, and a
  bounded cross-model spec review (spec + red tests, up to two rounds) before
  green. Use at the start of any feature, before writing a spec, before the
  green phase, and whenever review findings start to repeat. Companions:
  build-loop (the workflow), technical-excellence, test-quality.
---

# question-everything

A defect costs least in a sentence of the spec, more in a red test, and most
in reviewed code. Spend questions early.

| Skill | Load it when |
|---|---|
| `build-loop` | The feature is multi-phase; this skill is its pre-green gate (build-loop §4a). |
| `technical-excellence` | Shaping interfaces, invariants and types while you question the spec. |
| `test-quality` | Judging whether the red tests prove the spec. |

## 1. Interview the designer

The user is the designer. Get high-fidelity detail before anyone writes code.
Push back: an answer that leaves a state, edge or failure undefined is not an
answer yet.

Ask, with a proposed default for each, so the user can answer in a word:
1. **States.** Every state the thing can be in, including empty, unknown,
   partial, stale, refused, failed. What does the user see in each?
2. **Edges.** Time (midnight, time zones, DST, nights that cross dates),
   units, limits, duplicates, retries, concurrency, offline, first run,
   upgrade from old data.
3. **Lifecycle of data.** Created, edited, deleted, exported, restored,
   merged, migrated: what happens to this feature's data on each path?
4. **Precedence.** When two sources disagree (user edit vs derived value,
   local vs backup, old vs new), which wins, and is that visible?
5. **Safety.** What must never happen (e.g. "never tell a wearer to skip a
   prescribed drug")? Write it as an invariant the types or tests enforce.
6. **Look.** Layout constraints the user cares about (stable row height,
   locked visuals). Get a mockup or golden description.
7. **Checklists.** "Which checklists should this run through?" Offer the
   project's existing ones as defaults (see §3).
8. **Reuse.** "What here could be reused elsewhere, or should reuse
   something that exists?" Offer your own candidates first.

If the user is away, take the safe default, log it, and raise it later
(build-loop §1a). Never block.

## 2. Ask yourself the same questions

Before writing the spec, answer §1 yourself from the code:
- grep for existing seams that already solve part of it (a reconcile helper,
  a write seam, a scheduler, an id generator), and require their use;
- list every path the data travels (§1.3) and name the code for each;
- list the invariants and how each is enforced (type > test > review);
- list what is unknown, and how unknown stays unknown (never a silent zero).

## 3. Turn recurrence into checklists, early

Watch review findings across features. When the same family shows up twice
(e.g. "new table missing from export/restore", "delta arithmetic drifts from
the canonical total"), stop and write or extend a project checklist. Do not
wait for a fifth round. Keep checklists in the project (not in a generic
skill), each item citing the findings that taught it. Every later spec that
touches that area pastes the checklist, and the implementer answers each line
("done: <test>" or "n/a: <reason>").

Also ask at each feature start: "Which recurring families could this
feature hit?" and pre-empt them in the spec.

## 4. Cross-model spec review (before green)

After the red phase commits and before any green code:
1. Send the reviewer (e.g. Sol) the spec, the red tests, the applicable
   checklists, and the designer's answers. Ask for: gaps (states, edges,
   lifecycle paths, precedence), contradictions, tests that would pass
   without the feature, missing invariants, and simpler designs or reuse.
2. Fix the spec and red tests. Re-run the red gate.
3. At most two spec rounds. Anything still open after round two becomes an
   explicit decision (default + log + raise), not a third round.
4. Then implement, and run the normal code review loop (build-loop §6).

The spec review is cheap: no code to read, so it should take one run.
Findings here save whole code-review rounds later.

## 5. Signs you skipped this

- review rounds keep finding new cases of the same family;
- fixes introduce ids, flags or columns the spec never mentioned;
- the implementer picks between designs mid-green ("I chose X over Y");
- defaults are discovered in reports instead of decided in the spec.

When you see these, pause the loop and come back here.
