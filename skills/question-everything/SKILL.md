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
| `pr-stacks` | Writing the stack plan at the end of the grill (§6). |

This interview is the **grill**: questions before code, for alignment. It is
not the **teach-back**, the per-PR questions that keep the owner
understanding the code (`pr-stacks` §4).

## 1. Interview the designer

The user is the designer. Get high-fidelity detail before anyone writes code.
Push back: an answer that leaves a state, edge or failure undefined is not an
answer yet.

**Format.** Ask in rounds. Each round asks every question whose
prerequisites are settled, numbered, each with your recommended answer, so
the user can answer in a word. Find facts yourself (grep, read, or a fresh
subagent); never ask the user what the code can tell you. Decisions are the
user's.

**Shorthand: "zoom" and "wide".** When the user answers a question and adds
"zoom" (or "zoom Q3"), that question is the crux. Elaborate on it first:
what rides on it, the options, what the code says, and your own position.
Then ask one question per message on that topic, each building on the last
answer, until the user says "wide". "Wide" returns to numbered rounds over
everything still open, starting with what the zoom uncovered.

**When a round comes back all "yes".** Your defaults on that topic are right.
Move on: look for what has not been explored yet (other states, edges,
lifecycle paths, neighbouring features, the stack plan) and raise the most
important of those. Say what you are moving to. The grill ends only when the
user says so.

Cover, with a proposed default for each:
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

## 1a. Language and decisions

Name things while you grill; the names become the data model.

- **Glossary.** Check every new term against the project lexicon
  (`technical-excellence` §4). Refuse a term that collides with a framework
  word (component, scene, model, service) or an existing entry; qualify it
  instead ("diagram component"). Record words to avoid with each entry.
- **Scenario test every new or contested term.** Write five to seven real
  sentences about the feature using each candidate, in a table, with a
  column for "is this how the owner talks". Pick the name that reads true in
  every sentence. This is the strongest naming check we have; run it
  whenever a lexicon gains a term, not only when names compete.
- **Avoid lists.** Record the confusing near-synonyms for each term in the
  lexicon (residual's lexicon where the project uses residual).
- **ADRs.** Have a strong opinion about when a decision deserves one: it is
  hard to reverse, surprising without context, and the result of a real
  trade-off; all three must hold. When you see one, propose it in the grill
  with the draft's gist (context, options, why this one, what would change
  it) and say why it qualifies. Write it once the user confirms. Every ADR
  must be defensible from its own text. Store it in
  the project's ADR store (residual if the project uses it, else
  `docs/adr/NNNN-slug.md`). Read existing ADRs before proposing to change
  anything they cover.

## 1b. Prototype or mockup

When an answer depends on how something looks or feels, or on behaviour
nobody can predict, stop asking and build. Two or three throwaway variants,
started in the background (Sol or Codex where the Claude agent cap is full,
build-loop §2) while the grill continues. Mockups go to the owner through
`html_preview`. Prototype code lives on `prototype/<topic>`, is never merged,
and is reimplemented under tests. A bad variant teaches as much as a good
one. If the open question is whether the approach works on real cases, that is
a pilot (build-loop `references/scoping.md`), not a prototype.

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
2. Exchange at least one substantive argument with each spec reviewer before
   accepting its review, even an approval. Fable needs at least two. Give the
   reviewer the round priorities and invariants; record the exchange using
   build-loop `references/dialogue.md`. Fix the spec and red tests, then rerun the red gate.
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

## 6. End of the grill

The grill ends when the list of open questions is empty or the user says so.
Before anything else, write down:

1. the intent, in one or two sentences;
2. glossary changes and any ADRs the user approved;
3. the spec, with states, edges, invariants and test seams;
4. the stack plan with door labels (`pr-stacks` §2), one ticket per line.

Every decision must now live in a file. This is the best moment to compact:
nothing important exists only in the conversation. If the session is large,
compact yourself (`uw-agent compact ask <session-id> --reason "grill done;
next: <first ticket>"`) and reread this skill and build-loop after.
