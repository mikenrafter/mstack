# Research direction: views that teach (2026-11-11)

Status: proposed direction from the owner, written up for paneweft v1 and later. Builds on
[03](03-moldable-development.md) (moldable development), [04](04-code-review-and-diff-core.md)
(explanation fidelity), [05](05-classic-engineering.md) (Naur, Parnas), [11](11-moldable-components.md)
and [12](12-paneweft-v1-in-code-views.md) (in-code views).

## Goal

Faster, deeper understanding of a codebase through tools instrumented inside it, so they last,
stay correct as the code changes, and compose. Two threads serve that goal: a benchmark that
measures whether a view actually teaches, and tooling that records the thinking behind the code,
dead ends included.

## 1. The teaching benchmark

The question: does a view make another agent understand the code, and how well compared with
reading the code itself?

### Protocol

1. **Teacher.** An agent with full repository access crafts one or more views (or a notebook)
   explaining a chosen topic: "how ContainMarks opens a bookmark in a container", "where a vigil
   keepalive result can be lost".
2. **Question author, blind to the views.** A separate agent writes the questions from the code
   alone, with an answer key that cites code lines. Keeping it separate stops the teacher from
   writing questions its own view happens to answer.
3. **Student.** A fresh agent with no file or tool access receives only the view material. It must
   handle visual material well: Opus or Sol.
4. **Examiner.** The parent agent asks the questions, one at a time, and records each answer with
   the student's stated confidence.
5. **Grader.** A third agent scores the answers against the key. Use a different model family from
   the teacher where possible, so neither side grades its own family.

### Question kinds

Each topic gets a mix, tagged by kind, so results show *what* a view teaches:

- recall: what does X store, which permission does Y need;
- trace: what happens, in order, when Z;
- locate: which file or function decides W;
- causal: why does the code do V;
- counterfactual: what breaks if U changes;
- boundary: what does this view *not* tell you (tests whether the student knows the gaps);
- why-not: why was the obvious alternative not used (tests section 2 below).

Some questions are answerable from the code but deliberately outside the view's scope. A good
view makes its gaps visible; the student should say "the view does not cover this" rather than
guess.

### Conditions (same topic, same questions, same token budget)

| Condition | Student receives |
|---|---|
| A. Nothing | only the topic sentence (measures prior knowledge) |
| B. Code | the relevant source excerpts, budget-matched |
| C. Prose | a teacher-written explanation, budget-matched |
| D. View, text form | paneweft's bounded text answers |
| E. View, rendered | screenshots of the rendered views |
| F. View, both | screenshots plus text form |
| G. Misleading view | a view with one planted error (see below) |
| H. View + trail | condition F plus the decision trail (section 2) |

Use the owner's private repositories, which no model has trained on, so condition A stays near
zero.

### Measures

- accuracy per question kind;
- calibration: confidence against correctness. Section 04's 86-programmer study found poor
  explanations *raised* confidence while lowering accuracy, so a view that makes students
  confidently wrong is a failure even when average accuracy rises;
- detection rate of the planted error in condition G (does the student catch a view that
  contradicts itself or its cited evidence?);
- cost: tokens and wall time for the teacher to produce the views, and for the student to answer;
- durability: re-run the same questions after later commits. In-code views (v1) should keep
  scores up; agent-collected JSON views should decay, and stale-view detection should flag them.

### What it tells us

- which components teach which question kinds (graph for trace, data shape for recall, and so on);
- whether rendered views beat text form for capable visual models;
- whether views beat raw code at equal budget (if not, the view is decoration);
- whether in-code views stay accurate longer than collected ones;
- a regression suite for paneweft itself: a fixed set of topics and questions run on every
  release.

### Risks

- Teacher and grader from one family can share blind spots; rotate roles across Claude and Codex.
- Students may guess well from names alone; condition A controls for that.
- Budget matching is approximate across modalities; record actual tokens, not just limits.

## 2. Showing the thinking, dead ends included

Moldable development needs humility. Code that hides its false starts teaches readers less than
code that shows them: the reader re-walks the dead end, or never learns why the obvious approach
fails. Naur's point (section 05) is that the theory behind a program lives in people; written
reasons and preserved alternatives are the best available way to pass part of it on.

What the tooling should support:

- **A decision trail component.** Ordered entries linked to code entities: the question, options
  tried, what happened, the evidence, and the decision. Abandoned options stay visible with their
  reason ("superseded", "failed", "too costly").
- **Dead ends as examples.** A rejected approach can keep a runnable example that shows why it
  failed, so the reason stays checkable rather than anecdotal.
- **Capture from the work itself.** Agents already produce this material: build-loop's step-backs,
  declined review findings with reasons, spec amendments, rejected designs. Example from this
  week: paneweft's lock went through three rounds of a userspace recovery protocol before a
  step-back replaced it with kernel `flock`. That trail ("why not a userspace lock?") is exactly
  what a future reader needs and today it lives only in a review ledger. The tool should make it
  cheap to promote such a ledger into a trail linked to `write-lock.ts`.
- **Questions in the benchmark.** The why-not questions above measure whether the trail teaches.

## 3. Where it lives: first-class and sidecar

Two placements, both needed:

- **First-class.** In-code views, examples and trails in the repository, maintained with the code
  (paneweft v1 SDKs). Best durability; requires the team to accept the tooling.
- **Sidecar.** For repositories the owner does not control, or where adding tooling is unwelcome
  (for example upstream contributions, see build-loop §2a reviewer analysis): views, trails and
  example adapters live beside the repo, not in it. Prior art: residual stores its metadata on a
  git sidecar branch (`src/storage/git_sidecar.rs`), and the owner already keeps `<repo>.research/`
  directories next to each checkout. Options to evaluate: a sidecar branch (`refs/paneweft/*`), the
  sibling research directory, or a separate repository, each pinned to the commit it describes,
  with stale detection when that commit moves.

The same views should work in both placements; only where they are stored and how they attach to
code differs.

## Purpose stressor: insight, not decoration (owner, 2026-11-11)

Views exist to produce insight. Edtech platforms, the math-video community's tooling (likely Manim),
plotting practice (matplotlib, Vega-Lite, Grammar of Graphics), visualization research and GT's own
dogfood views show how pictures earn understanding. PLAN W22 turns them into guidelines (question kind →
view kind); the benchmark (section 1) is how a view proves it meets them. Raise this as a stated
purpose when paneweft's residual walk is formalized.

Insight and maintainability are one coin: a view should also add structural safety, making tests,
invariants and their coverage visible so a wrong change looks wrong. Angles (PLAN W22a): System 1 /
System 2 views (fast recognition vs deliberate checking), coarse-to-fine errors as compilers and LSPs
present them, and formal correctness made visible and operable, possibly as an agent-built GUI.

## Next steps

1. Fold section 1's protocol into paneweft v1's spec as a benchmark harness (a small runner that
   assigns roles, manages the student's no-file-access context, and records scores).
2. Add the decision-trail component to the v1 component list, with ledger import.
3. Run a pilot on two topics (ContainMarks and vigil) under conditions A, B, D, E and F before
   building the rest.
4. Decide the default sidecar placement after the pilot.
