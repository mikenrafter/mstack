# test-quality reference: the tester brief

Paste this file verbatim into every brief for an agent that writes or reviews tests: build-loop red runs,
test fixes, spec-gate and test reviews, suite audits (owner, 2026-11-26). Each set is five steers away
from what agents do by default. The names say whose way of working the set follows; they are not a
role-play.

Why steers and not a tutorial: a model already knows the techniques. Left alone it tests where the light
is: no-panic fuzzing, round trips of trivial properties, inputs that cannot tell a right implementation
from a wrong one, a technique used in name only (Dan Luu, "How well do agents use test/verification
techniques?", 2026). The steers push against those defaults. The references hold the detail.

## Set 1 · Dan Luu: aim at the bugs

1. Before implementing, name the areas likely to hold subtle bugs. For each, state the likely mistakes and
   plausible alternative readings of the spec, then write a check where they give different results.
   Prefer asymmetric and boundary examples, on both sides of each boundary.
2. After implementing, for high-risk areas, re-derive the result independently, without the production
   code in context and without its helpers, and compare. This finds bugs nobody knew to look for; a
   literal oracle for a known case does not replace it.
3. When feasible, use property-based tests or randomized inputs to explore the space. Spend little on
   no-panic or no-crash randomization.
4. When randomizing, aim the inputs at interesting state and code paths, not at the same error path over
   and over. This usually needs structured generators.
5. When unsure about a detail, settle it by independent reasoning (fresh context, no reused helpers), not
   by reading what the code does.

## Set 2 · Lisa Crispin, Janet Gregory: risk first, few tests

1. Map risk before the first test. Use code mechanics (byte layout, ordering, time and zones,
   concurrency, state machines, parsing, boundaries), fix history, and ownership that crosses a module or
   process boundary. History alone misses things: a queue lock with no fix commits had no real test.
2. Launch with few tests. Spend most of the budget on the top risk areas and little elsewhere. Every test
   past the budget says why it is worth its cost (SKILL.md, launch budget).
3. Each risk-focused test records four things: the production entry point, the plausible fault, the input
   that exposes it, and an oracle independent of the code.
4. Test through the seam the user hits, with shipped defaults. A pure helper with zero production
   callers proves nothing about the product.
5. Spend tests on essential complexity, the complexity the problem demands. Flag accidental complexity,
   which comes from our own design, for removal instead of testing around it.

## Set 3 · John Hughes, Hillel Wayne: inputs that discriminate

1. Pick inputs on which the plausible wrong versions disagree. Use distinct values for fields that feed
   separate decisions. Avoid palindromes for order code, identical streams, equal arguments to swappable
   parameters, UTC-only times, one-row deletes and windows shorter than one window.
2. Every *when X, then Y* property gets a witness that X happened, through production, with shipped
   defaults. Generated runs report how often each action fired.
3. When a rule picks a first or best candidate, generate cases where each candidate can win, and assert
   which one won.
4. For concurrency, make the owners really differ (separate processes, workers or sessions). Gate on the
   contended step and assert the final persisted identities.
5. Force one failure at the last fallible step (a refused write, a dropped send). Assert both the stored
   intent and the real effect.

## Set 4 · Gary Bernhardt: guardrails

1. Never mock the unit under test. Mock the clock, the network and the platform. Name the assumption each
   mock adds.
2. Never take an expected value from the code under test or its helpers. A round trip is never the only
   proof: mated parts also meet literal bytes from the spec or a real capture.
3. Never assert an absence without a positive control in the same test, and never guard an assertion
   with an `if`.
4. Never loosen an assertion to make a fix pass. No tolerance wider than the numeric error, and no
   test-only thresholds.
5. No-panic tests and source greps don't count toward the launch budget. Keep a grep only as a
   whole-tree ban with a positive control.

## Text output: goldens, not micro-snapshots

When the code's output is text someone reads (a message, advice, a report, a prompt),
pin the whole of it in one golden, not with several substring checks (techniques.md,
"Goldens", mode 13). Use an invariant when only a property of the text matters. Do not
regenerate an existing golden unless the change the owner asked for moves it; say which
goldens moved and why.

## Before you hand back

Run `tq lint --since <base>` on your tests. Fix every gating row, or mark a deliberate form with
`# tq: allow RULE REASON` and say why in your report. Run `tq catches` and report which named
faults did not turn a test red.
