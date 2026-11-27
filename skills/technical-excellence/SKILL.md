---
name: technical-excellence
description: >-
  Use when designing an abstraction, writing or reviewing code or comments,
  naming things, or judging a review finding.
---

# technical-excellence

Standards for what the code says and how it is shaped.

| Skill | Load it when |
|---|---|
| `test-quality` | Writing or reviewing the tests that prove an interface, claim or invariant here. |
| `build-loop` | The work is multi-phase, or a cross-model review will judge it. Its review step uses sections 6 and 7 below. |

First rule: **when in Rome.** Follow the repo's conventions (AGENTS.md,
existing style, lexicon) before anything below. Apply this skill where the repo
is silent.

## 1. Rich interfaces

An interface is more than signatures. Each abstraction documents:

| Part | Says |
|---|---|
| Error detail | What can fail, and how it is reported (type, code, null, exception). Callers must be able to handle each case without reading the body. |
| Reason | Why it exists. What breaks or duplicates if it is removed. |
| Invariants | What is always true before, during and after calls. |
| Mating parts | If it has a second or third counterpart (writer/reader, encoder/decoder, client/server), name them. |

**Agent-facing tools refuse with the next step.** When a tool an agent calls
says no, the message names the call to make first ("remove the subclasses
first", "pass --confirm 50b2f3d3"), and its errors carry values the agent can
pass straight back in. A destructive action goes through a preview or an undo.
vigil and `review-ledger` already work this way; new tools follow them
(practice-watch 2026-11-27, gt4llm).

**Mated parts need parity tests** proving both sides agree: round trip, plus
independent fixtures (see `test-quality`, parity and oracles). A pair that is
only tested against each other's constants proves nothing.

## 2. Claims are cited

Module-level comments and comments above code blocks contain verifiable
claims ("this is O(n)", "the device sends big-endian", "idempotent",
"commit happens before ACK"). Every such claim is anchored and sourced.

Convention (adapt the comment syntax to the language):

```
// CLAIM(ack-order): the commit completes before the ACK is sent [spec §4.2; ack_order_test]
...
// ↳ CLAIM(ack-order)
ack(token);
```

- The comment states a **verifiable** claim and its **source or proof** in
  brackets: a spec section, capture file, proof sketch, or test name.
- The code the claim governs carries `↳ CLAIM(<id>)`.
- A maintainer changing that code greps the id, finds the claim and its
  proof, and re-checks it.
- Tests that prove the claim name the id in their why (`test-quality`).
- Ids are short, unique, stable. Unprovable "claims" are opinions: label them
  as such or delete them. A comment with no source is a rumor.

Comments that are not claims or interface contracts are smells
(`comment-audit`). Never write a note from your session into a comment
("added for ticket 4", "now uses X", "as requested"); that belongs in the
commit message. A comment that excuses a workaround in our own code marks
code to reshape, not explain. A decision's why that spans modules goes in an
ADR, and the site carries `ADR-NNNN`.

## 3. Deep modules

Prefer a simple interface over a substantial implementation. Few entry
points, few parameters, no leaked internals. Smells: shallow wrappers that
forward one call; interfaces as long as the body; callers that must know
call order. Hide the complexity; do not spread it across callers.

## 4. Lexicon and naming

Keep a project lexicon (a glossary doc: term, meaning, where it lives). Name
code in correspondence with it. Add a term to the glossary when you coin one;
do not use two words for one concept. Where the project uses residual, its
lexicon is the source; how terms are tested and which near-synonyms to avoid
belong to the lexicon, not here (`question-everything` §1a).

Outside any convention:

- Clear names, **no abbreviations**.
- 1-2 primary words, plus optional small words (determiners, prepositions):
  `rowsToPrune`, `nightOfRecord`.
- Be deliberate about grammar:
  - functions and methods: verbs (`parseFrame`); predicates read as
    questions (`isFinalized`, `hasPendingWrite`);
  - values and types: nouns (`dayLabel`, `HistoryToken`);
  - qualifiers: adjectives (`pendingRows`);
  - tense shows state: `committedRows` (done), `rowsToCommit` (not yet).
- Name by how the value is used, not its type. Avoid vague names such as
  `value`, `data`, `result`, `tmp`. A function that sums two numbers returns
  `sum`; a truly generic result is `returnValue`.

## 5. Type-level safety first

Algorithmic and algebraic design shrinks runtime checks, tests and review.
Reach for these before adding a check:

| Tool | Effect |
|---|---|
| Make invalid states unrepresentable (sum types, non-empty lists, state enums carrying only valid fields) | The bug cannot compile. No test or review needed. |
| Newtypes / branded types (`LocalDayLabel` vs `UtcTimestamp`, `Milliseconds` vs `Seconds`) | Mixed-up units and ids fail to compile. |
| Exhaustive matching, no default branch | Adding a case forces every consumer to be updated. |
| Monoids (identity, associative combine) for accumulators | Split-merge equals single pass; parallelism and incrementality are safe. Prove laws with property tests (`test-quality`). |
| Parse, don't validate: convert raw input to a checked type once, at the boundary | Inner code never re-checks. |
| Smart constructors, private fields | Invariants hold by construction. |

If a runtime check or a test exists only to catch an invalid state a type
could forbid, change the type.

## 6. Security stance review

Security judgments are made against a **threat model**, never by reflex.

1. Use the project's existing framework (a residual-risk framework, AGENTS.md
   invariants, an existing model).
2. If none exists, write a short `THREAT_MODEL.md`: assets, actors, trust
   boundaries, in scope, out of scope. Leave it UNCOMMITTED unless the user
   says otherwise.
3. Question the stance itself: which assets matter most, who can reach which
   boundary, what is knowingly accepted. Record accepted risks with a reason.
4. For each security-relevant change or review comment, decide: real exposure
   under the model, hardening nicety, or out of scope. State which and why.
5. Where a project limits reviewers to correctness findings, honor that for
   what you ask of them, but still assess security yourself.

## 7. Judging review findings

A finding is not a nit because it is small. Check it against: the claim it
contradicts (section 2), the invariant it breaks (section 1), the type that
could prevent it (section 5), and the threat model (section 6). Then apply
the smallest fix, with a test that fails without it (`test-quality`).
