# 05 — Classic software and engineering literature: what holds up, what does not, and what agents change

Research date: 2026-11-10. Scope: older software-engineering books and papers,
plus the "is software engineering really engineering" question, graded against
empirical evidence and read through the lens of agent-assisted work.

Limits of this file:

- I read two of your skills in full (`technical-excellence`, `test-quality`).
  I did not read `build-loop`, `question-everything`, `rg-implement`, or the
  Aegis config, so comparisons to those are marked as such.
- The void host is offline. Its transcripts and the newest diff-core and
  residual work are missing, so I could not check how any of this plays out in
  your actual agent runs.
- The initial pass could not open several primary pages. Cross-review on
  2026-11-10 checked the O'Reilly, METR and Goedecke pages directly and
  replaced the affected search-summary claims below.
- Every statement about what agents change is my inference. Almost none of it
  has been tested in a controlled study. The grades say so.

## Top findings

1. **The "late defects cost 10–100x more" curve behind much of Code Complete's
   case for upfront work is weaker than its fame.** Boehm and Papaccio (1988)
   reported up to 50–200x for requirements defects; a 2017 analysis of 171
   projects (2006–2014) did not find a consistent delayed-issue effect.
   Treat it as context-dependent. Grade **B** against, **C** for. Sources 1–3.
2. **Conway's law has the best empirical support of any "law" in this list.**
   Matched-pair comparisons found loosely coupled organizations produced
   products up to six times more modular, and organizational metrics predicted
   Windows Vista failure-proneness better than code metrics. Grade **B**.
   Sources 8, 9.
3. **Deep modules (Ousterhout) are a design heuristic with no direct empirical
   test, but the adjacent evidence points the same way.** Code-quality metrics
   that reward low coupling and small complexity predict defects and cycle
   time (n = 39 codebases, 30,737 files; vendor-affiliated). Grade **D** for
   the claim itself, **B** for the neighboring evidence. Sources 4, 5.
4. **The Ousterhout–Martin debate ended with more agreement than the book
   covers suggest, and it produced one useful measurement.** Splitting a prime
   generator into tiny methods caused a 3–4x slowdown until it was restructured.
   Both agree over-decomposition is real; they disagree on comments and where
   to err. Grade **C** (a reproducible demo on one example). Source 6.
5. **Naur's "theory building" has no empirical agent-era test, and its
   implication is sharp: delegating code requires maintaining your own understanding,
   with documents and executable checks supporting reconstruction.** Grade **D**. The 2025–26
   commentary is blogs. Sources 14, 15.
6. **Brooks's law is a poor rule even for humans, and a poor fit for agents,
   with task-dependent coordination and communication costs.** Sequential tasks degraded under every multi-agent
   variant in the original 180-configuration study; independent parallel agents
   amplified errors 17.2x. Grade **A/B** for the multi-agent result (benchmark
   with published method, though on general tasks, not only coding).
   Sources 10, 22, 23, 24.
7. **TDD's quality benefit is small and inconsistent in controlled studies.**
   Meta-analyses and a family of 12 experiments found weak or task-dependent
   effects. Its value with agents is a different claim (an executable
   specification the agent cannot talk its way past), supported only by
   practitioner reports. Grade **A** for "small effect for humans", **D** for
   "superpower with agents". Sources 11, 12, 30.
8. **Agents raise the speed of writing code and the risk of unmanaged
   complexity.** A difference-in-differences study of Cursor adoption found a
   velocity gain that faded after about two months, with persistent rises in
   static-analysis warnings (about 30%) and code complexity (about 41%).
   DORA 2025 (nearly 5,000 respondents) associates AI use with higher
   throughput and higher instability. Grade **B**, correlational. Sources 18, 19.
9. **The strongest transfer from civil and mechanical engineering is the
   failure-analysis habit, not specs or licensure.** Licensure failed in
   practice (the NCEES software PE exam drew 81 candidates in six years and
   was discontinued); Petroski-style post-mortems and Leveson's Therac-25
   analysis transfer directly. Grade **C**. Sources 25, 26, 27.
10. **The old literature's biggest unaddressed gap for your setup is Hyrum's
    law plus Feathers: agents change observable behavior that nobody wrote
    down.** Your skills pin claims and invariants but say nothing about
    characterization tests for existing behavior. Grade **C**. Sources 16, 28.

## 1. Code Complete (McConnell, 1993; 2nd ed. 2004)

**Claims.** Managing complexity is the main technical imperative; construction
is a design activity; defects found late cost much more than defects found
early; code reviews and inspections find most defects cheaply; individual
variation between programmers is large.

**Evidence.**

- *Late defects cost more.* The most-cited figure is Boehm and Papaccio
  (1988), requirements defects reaching the field costing 50–200x. McConnell
  himself softened this to a 10–100x rule of thumb in a 2001 IEEE Software
  column ([source 1](https://stevemcconnell.com/articles/upstream-decisions-downstream-costs/)).
  Menzies, Nichols, Shull and Layman analyzed 171 projects (2006–2014) and did
  not find the effect: issues fixed later did not consistently take
  substantially more effort ([source 2](https://arxiv.org/abs/1609.04886),
  published in *Empirical Software Engineering*, 2017). They also note that
  effort and cost are not interchangeable. Boehm and Basili's January 2001
  [primary article](https://www.cs.cmu.edu/afs/cs/academic/class/17654-f01/www/refs/BB.pdf)
  explicitly gives about 5:1 for small non-critical systems. This remains a
  context-specific historical report. Grade: **C** for the original claim, **B** against it.
- *Inspections.* I did not verify the inspection-yield numbers in this pass.
  [unverified]

**Applies to software?** Partly. The finding that matters is the dependence on
context. Where deployment is expensive or irreversible (firmware, medical
devices, a published API with many consumers, see Hyrum's law below), late
discovery costs more. For a web service you redeploy ten times a day, it may
not. Most of your work (NixOS config, Rust scout modules, a code review tool)
sits closer to the cheap-to-redeploy end, except where the output is consumed
by other tools.

**With agents.** The relevant cost is no longer "developer-hours to fix". It is
review load plus the chance a defect is accepted. An agent can regenerate
code in minutes, so rework is cheaper, and a wrong requirement discovered late
costs less than it did. The opposite pressure is that a defect an agent
generated and a human skimmed is cheap to introduce and expensive to find
(see section 8). Net: the curve flattens for code, stays steep for
specification errors and for data or API contracts. This is **D** (inference).

**Keep from Code Complete:** the complexity framing (it is the root of
Ousterhout and of your deep-modules rule); treat the defect-cost multiplier
as a prior, not a law; treat construction-practice chapters as a checklist
rather than evidence.

## 2. A Philosophy of Software Design (Ousterhout, 2018; 2nd ed. 2021)

**Claims.** Complexity is the enemy and shows up as change amplification,
cognitive load, and unknown unknowns. Prefer deep modules (simple interface,
substantial functionality), information hiding, general-purpose interfaces,
pulling complexity downward, and defining errors out of existence. Work
strategically, not tactically (invest roughly 10–20% extra in design as you
go). Comments describe what the code cannot say, and are written before or
with the code.

**Evidence.** I found no controlled study of "deep modules" as a treatment.
The author's own page describes the second edition as adding two chapters and a
comparison with Clean Code ([source 7](https://web.stanford.edu/~ouster/cgi-bin/book.php)).
Adjacent evidence exists:

- Code Health (a vendor metric that penalizes complexity, low cohesion and
  similar properties) predicted defects and time-in-development across 39
  proprietary codebases and 30,737 files: low-health code had about 15x more
  defects, and tasks in the worst code took 124% longer
  ([source 4](https://arxiv.org/abs/2203.04374), Tornhill and Borg, 2022). The
  authors work for the vendor and the metric is proprietary. Grade **B**,
  with that caveat.
- MacCormack et al. found modularity, measured as the potential for a change
  in one component to propagate, differs by up to a factor of six between
  matched product pairs ([source 8](https://dash.harvard.edu/handle/1/34403525)).
- The Microsoft Windows refactoring study found modules that were refactored
  with a central effort showed reduced inter-module dependencies and
  post-release defects ([source 13](https://www.microsoft.com/en-us/research/?p=163533),
  Kim, Zimmermann, Nagappan, FSE 2012). Grade **B**. The 2014 journal version
  adds that preferentially refactored modules also grew more.
- Method length: a 2022 mining study of about 785,000 Java methods in 49
  projects found maintenance effort correlates with method length, and
  earlier work (Nagappan et al., not retrieved) correlates length with
  post-release defects ([source 17](https://www.cs.ubc.ca/~rtholmes/papers/msr_2022_chowdhury.pdf)).
  Length alone is a weak predictor, and this does not test "tiny methods are
  better". Grade **B**, weak.

So the pro-modularity direction is supported at **B**. The specific shape
Ousterhout recommends (depth, the ratio of interface to implementation) is
**D**.

### The Ousterhout vs Martin debate

The two held discussions between September 2024 and February 2025 and
published them ([source 6](https://github.com/johnousterhout/aposd-vs-clean-code)).
What the record shows:

| Topic | Ousterhout | Martin | Resolution |
|---|---|---|---|
| Method length | Clean Code's advice "is so extreme that it encourages programmers to create teeny-tiny methods" | "if I must err, I'd rather err on the side of decomposition" | Both agree the Clean Code prime-generator breakdown is poor. Neither moved on where to err. |
| Comments | Missing comments cost far more than wrong ones; comments carry what code cannot | Comments are "a necessary evil"; "I don't trust comments to be maintained" | Both accept comments for public APIs. Real disagreement remains. |
| The prime generator | Rewrote as one commented method, same length | Agreed it was "a considerable improvement" over the book version | Martin's own further split caused a 3–4x slowdown that Ousterhout measured; Martin then restructured into one loop and reported 440 ms vs 561 ms for a million primes |
| TDD | Writes code in larger units, then unit tests | Red-green-refactor, three laws | Ousterhout agreed to correct his book's description of TDD. Both value unit tests. |

I could only read the first ~100,000 of ~125,000 characters, so the
design-up-front discussion is not covered here.

**What this tells you.** The disagreement is mostly about where each author
puts the failure risk. Martin fears long functions you cannot read; Ousterhout
fears many small functions you must read together. Both are right in
different regimes. The prime example is the useful part: a refactoring that
looked clean changed algorithmic cost, and only a measurement caught it.
That is an argument for tests and benchmarks around refactors, not for either
style.

**Where each wins.** My read, grade **D**: Ousterhout on comments and
interfaces, since an interface comment is the part of the theory that survives
(see Naur). Martin on small, well-named units in code you will change often
and test directly. Ousterhout's own advice against over-splitting is supported
by the dependency-and-entanglement argument and nothing stronger.

**With agents.** Two effects that I think favor depth, both inference (**D**):

1. *Context compression.* A deep module's interface is a few lines an agent
   can load instead of the implementation. An agent reading 30 shallow
   wrappers spends its context on forwarding calls. The same reasoning
   explains why CodeScene reports that code with high Code Health is better
   for AI refactoring: in Borg et al. (January 2026), LLM refactorings on 5,000
   competitive-programming Python files were more often correct and beneficial
   for higher-health code ([source 5](https://arxiv.org/abs/2601.02200)). That
   is vendor-affiliated, uses competitive-programming files (not production
   code), and measured refactoring only. Grade **B/C**.
2. *Comments as the persistent record.* An agent starts every session without
   the author's theory. Interface comments and short module-level "why"
   comments are the cheapest transfer channel. This supports Ousterhout over
   Martin's "comments are failures", with the proviso that comments rot and
   agents will happily write stale ones. Your CLAIM convention, which ties a
   comment to a source and a test, answers Martin's maintenance objection
   directly.

A counter-point: the September 2026 revision of the ETH Zurich AGENTS.md study
(138 CTXbench tasks plus SWE-bench Lite) found average resolution changes of
−0.5 and −2 percentage points with generated guidance, neither statistically
significant, while cost rose 20% and 23% in the two settings. Directory
overviews did not improve file discovery
([primary paper, 2026-09-29](https://arxiv.org/html/2602.11988v3)). Python only. This warns
against assuming more descriptive text always helps agents. It does not test
interface comments.

## 3. Brooks: The Mythical Man-Month (1975, 20th anniversary ed. 1995) and No Silver Bullet (1986)

### Brooks's law

**Claim.** Adding people to a late software project makes it later.

**Evidence.** Mixed, and the claim is narrower than its reputation. A QSM
database analysis found staffing up a late project mostly showed in cost and
quality (more defects), not in a notably longer schedule
([source 10](https://qsm.com/blog/2009/empirical-examination-brooks-law)).
Capiluppi and Adams found it holds among core developers of large free
software projects (same search result). McConnell ("Brooks' Law Repealed",
1999) argued the schedule-compression limit runs roughly the other way
(summarized by Meyer). Meyer (2019) calls Brooks's law valid only as a
description of bad management and proposes the "shortest possible schedule"
result (a firm limit of about 25% compression) as its empirical replacement
([source 22](https://bertrandmeyer.com/2019/11/01/theorem-software-engineering/)).
Grade **C**, contested.

**Applies?** As a literal law, weakly. As a statement that onboarding and
communication cost grow with team size, yes. Nagappan, Murphy and Basili's
Windows Vista study (ICSE 2008) found organizational-complexity metrics were
better predictors of failure-prone binaries than churn, complexity or
coverage ([source 9](https://www.microsoft.com/en-us/research/?p=153188)).
A 2013 replication at function level found weaker predictive power. Grade
**B**.

**With agents, fan-out.** The cost in multi-agent systems is not
communication overhead among people. It is conflicting implicit decisions made
in parallel, with no shared theory. Evidence:

- Google's "Towards a Science of Scaling Agent Systems" (arXiv December 2025;
  180 configurations): independent parallel agents amplified errors up to
  17.2x versus 4.4x with a central orchestrator; multi-agent setups degraded
  performance on sequential tasks (reported up to 70% on one planning
  benchmark) and helped parallelizable ones (up to +81% on a finance task);
  gains shrank once the single-agent baseline passed about 45%
  ([source 23](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/)).
  The 39–70% range is present in the [original primary paper](https://arxiv.org/html/2512.08296v1).
  Its April 2026 revision expands to 260 configurations and six benchmarks,
  retaining task-dependent effects of +80.8% to −70.0%
  ([revised paper](https://arxiv.org/abs/2512.08296v3)). Grade **A**
  for controlled benchmarks, not coding-specific or a universal 45% threshold.
- Cemri et al. (NeurIPS 2025, arXiv March 2025) analyzed seven multi-agent
  frameworks over 200+ tasks with six annotators (Cohen's kappa 0.88) and
  found 14 failure modes in three groups: specification and system design,
  inter-agent misalignment, and task verification
  ([source 24](https://arxiv.org/abs/2503.13657v3)). The cited revision reports
  1,600+ annotated traces, with taxonomy development on 150 traces. Grade **B**
  for observational failure analysis, not a controlled intervention.
- Cognition (June 2025, reaffirmed April 2026) argues agents that write in
  parallel make conflicting implicit decisions and should share full context
  ([source 25a](https://cognition.ai/blog/dont-build-multi-agents), [source
  25b](https://cognition.com/blog/multi-agents-working)). Anthropic's research
  system counters with a 90.2% gain over single-agent on an internal research
  eval, at about 15x the tokens of a chat, and says tasks needing shared
  context or many dependencies fit poorly
  ([source 26](https://www.anthropic.com/engineering/multi-agent-research-system)).
  Grade **C** each.

My operating heuristic is to isolate parallel writers and verify parallel
readers' findings. Readers can also propagate errors; these studies do not
establish that read-only fan-out is harmless. This fits your single-implementer
setup in build-loop and the 1x main queue (per AGENTS.md); I did not read
those skills to confirm how fan-out is bounded.

### Conceptual integrity and the surgical team

Brooks argued that a system's most important property is conceptual integrity,
reached by few minds designing. This is Naur's idea from the other side: a
single coherent theory. It is the part of MMM that holds best and the part
agents make most relevant, since an agent supplies exactly the "many hands,
no single mind" failure unless one human or one session holds the design.
Grade **D** for the claim as stated, **B** for its organizational form via
Conway.

### No Silver Bullet

**Claim.** No single development will deliver an order-of-magnitude gain
within a decade, because the hard part is essential complexity (the
conceptual construct), not accidental complexity (tooling).

**Evidence.** Mostly argument. After 40 years, the high-level-language,
OO, and tooling gains do not supply a clean common productivity measure here;
the claim that each fell short of tenfold remains [unverified]. Agent-era commentary applies the same split: coding agents attack
accidental complexity well, leave essential complexity, and add new accidental
complexity (defensive boilerplate), with struggles in codebases over a million
lines ([source 20a](https://www.oreilly.com/radar/the-mythical-agent-month/),
Wes McKinney, O'Reilly Radar, 2026-03-23, checked directly in cross-review). Grade **D**, but the He et
al. finding (complexity up about 41% after adoption) is a **B** data point in
the same direction.

**With agents.** Brooks may be half wrong in a new way. If specification is the
essential work, and writing code is now cheap, the bottleneck moves to
specification, review and verification. That is Kleppmann's point too
(section 6).

## 4. Parnas: information hiding and rational design

### Information hiding (1972)

**Claim.** Decompose systems by hiding design decisions likely to change, not
by flowchart steps. Hide the decision, expose a stable interface.

**Evidence.** Indirect. Brooks reversed his own criticism of information
hiding in a later edition, conceding Parnas was right, per McConnell's
column ([source 3](https://stevemcconnell.com/wp-content/uploads/2017/08/MIAInformationHiding.pdf)).
McConnell also reports Boehm (1987) found it eliminated rework, particularly
during evolution (a practitioner-level report; I could not verify the data).
Navy A-7 project work applied it (SCR). Modularity-measurement studies
(MacCormack; Baldwin and Clark's design structure matrix work, not searched)
support the structure but do not isolate the principle. Grade **C**.

**Applies?** Yes. It underlies Ousterhout's depth, Meyer's contracts and
Hyrum's law (what you fail to hide gets depended on).

**With agents.** Strengthened. An agent that knows only an interface cannot
couple to internals. Languages with private visibility, Rust crates with
narrow `pub` surfaces, and Nix module options are mechanical enforcement of
information hiding. A hidden decision is also one the agent need not read.
This is the best-supported agent-era claim in the file because it needs no
new theory: smaller context, fewer cross-file dependencies (**D**, inference).

### "A Rational Design Process: How and Why to Fake It" (Parnas and Clements, 1986)

**Claim.** Real design is never rational: requirements change, you learn by
doing, you backtrack. But you should produce the documents a rational process
would have produced, as if you followed it, because they help reviewers and
maintainers
([source 31](https://bibbase.org/network/publication/parnas-clements-arationaldesignprocesshowandwhytofakeit-1986)).

**Evidence.** Argument. No study. Grade **D**.

**Applies?** Yes, and it is the paper most directly relevant to agent runs.
Agents do not follow a rational process either, but they can produce the
reference documents cheaply after the fact.

**With agents.** Strongly relevant. The cost that kept humans from "faking it"
was the effort of writing and keeping documents current. Agents lower that
cost. This supports your CLAIM convention and spec-first loop
(`technical-excellence` section 2, `question-everything`). The risk: faked
documents derived from the code by an agent are not independent evidence, the
same shared-oracle problem `test-quality` names for parity tests. A document
generated from the code proves the code matches itself.

## 5. Naur and Reeves: where the knowledge lives

### Naur, "Programming as Theory Building" (1985)

**Claim.** A program is a theory held by the people who built it. The code is
a partial record. Theory means (in Ryle's sense) knowing why the program is as
it is and how to answer questions about it and extend it. A program "dies"
when the team holding its theory dissolves; modifications made without the
theory cause decay
([source 14](https://neonvagabond.xyz/mirrors/naur1985programming.html)
mirror; summaries via [source 15](https://ratfactor.com/papers/naur1)).

**Evidence.** An essay. No test. Grade **D**. It fits observed facts (knowledge
loss on turnover, long onboarding) and the Lehman and Brooks literature, but
that fit is not a test.

**Where does the theory live when an agent writes the code?** Three
candidate answers, none tested:

1. *In the human who supervises.* Only if they review closely enough to
   rebuild the theory. Review that skims transfers none. Beck draws the same
   line: in "augmented coding" the engineer stays responsible for complexity,
   tests and coverage; in vibe coding they watch behavior only
   ([source 12](https://newsletter.kentbeck.com/p/augmented-coding-beyond-the-vibes)).
2. *In the agent's context.* This theory dies at session end. Goedecke's
   essay argues agents rebuild their understanding from scratch each time
   ([source 14b](https://www.seangoedecke.com/programming-with-ai-agents-as-theory-building),
   2026-04-03; checked directly in cross-review). Cekrem calls agent-generated code
   "nobody's theory".
3. *Supported by written artifacts.* Interface comments, claims, tests, lexicon,
   and decision records help a maintainer reconstruct understanding. Naur's
   theory is knowledge held by people; documents cannot fully contain it.
   A test with a stated WHY and CLAIM id preserves a checkable behavioral claim.

My inference (**D**): durable artifacts and continuing human understanding
complement each other. Their quality depends on checking reasons against
requirements and behavior. Naur's essay predicts the failure: modification without theory
produces decay. The He et al. result (complexity and warnings up, velocity
gains transient) is consistent with that prediction but does not test it.

One more reading: the theory is also in the tooling that rejects wrong
changes. Types, property tests and invariants are theory made executable. That
is Meyer and Dijkstra's territory (next section).

### Reeves, "What Is Software Design?" (C++ Journal, Fall 1992)

**Claim.** The source code is the design. Compiling and linking are the
construction phase, which is cheap. Auxiliary documentation still matters
([source 32](https://www.developerdotstar.com/mag/articles/reeves_design.html)).

**Evidence.** Argument. Grade **D**.

**Applies?** Yes. It is the core of the "software is not like bridges"
argument: design is the expensive part and manufacture is nearly free.

**With agents.** It sharpens. If an agent compiles a design in minutes, the
cost lies in design, review and verification. Reeves predicts that
engineering rigor should concentrate there. His view also supports
treating tests and types as part of the design, not afterthoughts. A caution:
if source is the design and an agent produces it, then design decisions are
being made implicitly by whoever prompts, which is Cognition's
"actions carry implicit decisions" point.

## 6. Correctness: Dijkstra, Hoare, Meyer

### Dijkstra

**Claim.** Testing shows the presence of bugs, not their absence; the way to
gain real confidence is to prove correctness, ideally building proof and
program together ("The Humble Programmer", 1972, CACM 15(10); the
short form is from his 1970 notes)
([source 29](https://en.wikiquote.org/wiki/Edsger_W._Dijkstra)).

**Evidence.** The logical claim is true and not contested: testing a
non-trivial input space is not exhaustive. The prescription (proofs for
ordinary software) did not become mainstream for cost reasons. Wayne notes
testing can prove correctness for finite input sets
([source 29b](https://buttondown.com/hillelwayne/archive/testing-can-show-the-presence-of-bugs-but-not-the)).
I did not research the empirical track record of formally verified systems.
The logical claim is deductive, outside the empirical A–D rubric. Grade
**D** for the prescription as a general practice.

**With agents.** The economics of the prescription change. Kleppmann
(December 8, 2025) predicts AI will make formal verification mainstream,
because proof generation gets cheaper, proof checkers are not fooled by
plausible-sounding LLM errors, and the limiting factor becomes writing correct
specifications and culture change
([source 33](https://martin.kleppmann.com/2025/12/08/ai-formal-verification.html)).
The September 2025 [vericoding benchmark](https://arxiv.org/abs/2509.22908)
does exist and evaluates formal specifications in Dafny, Verus/Rust, and Lean.
It does not establish general repository-scale adoption. Kleppmann's forecast
is a prediction, grade **D**. The mismatch risk is the same as for tests: a
wrong specification gets faithfully verified. Your `test-quality` mutation
checks are the cheap version of the same instinct: show the test can fail.

### Hoare

Hoare's 2009 QCon talk called the null reference his "billion-dollar
mistake", introduced in 1965 (ALGOL W) because it was easy to implement, and
named non-null reference types, checkable at compile time, as the solution he
rejected
([source 34](https://www.infoq.com/presentations/Null-References-The-Billion-Dollar-Mistake-Tony-Hoare/)).
The dollar figure was loose rhetoric. The design lesson, make invalid states
unrepresentable, is what your `technical-excellence` section 5 encodes.
Grade **C** (consistent with many bug reports, no clean measurement). For
agents it is among the best returns available: a type that forbids a state
removes a class of review comments and agent mistakes at zero ongoing cost.

### Meyer, design by contract

**Claim.** Preconditions, postconditions and class invariants are a
specification inside the code that make responsibility explicit.

**Evidence.** Estler, Furia, Nordio, Piccioni and Meyer (FM 2014) analyzed 21
projects in Eiffel, C# and Java (JML) with over 260 million lines across 7,700
revisions. Over a third of routines and classes carried contracts in most
projects, and the share was stable over time
([source 35](https://arxiv.org/abs/1211.4775v6)). That shows adoption among
adopters, not benefit. AdaCore's critique notes many sample projects were
written by formal-spec supporters
([source 35b](https://blog.adacore.com/studies-of-contracts-in-practice)).
Grade **C** for "contracts are maintainable in practice", **D** for "they
reduce defects".

**With agents.** Contracts are a good fit: a precondition is a checkable
statement of what the agent may assume, and an assertion fires at the point of
violation. They address the same problem as your "rich interfaces" and CLAIM
rules (`technical-excellence` sections 1–2), in executable form.

## 7. The "laws": Lehman, Conway, Hyrum, Gall

| Law | Claim | Evidence | Grade | Agent-era note |
|---|---|---|---|---|
| Lehman (1970s onward) | Systems in use must keep changing; complexity rises unless work is done to reduce it; growth rate self-regulates | Neamtiu et al. tested all eight laws on nine open-source projects (2013): only continuing change and continuing growth held for all; the other six depended on how they were measured ([source 36](https://www.cs.kent.edu/~jmaletic/cs63902/Papers/jsme11neamtiu.pdf)). Godfrey and Tu found Linux still growing. | **B** (two laws), **C/D** (rest) | Agents may break "self-regulation" (growth limited by team capacity). He et al. suggest complexity rising faster, but with transient velocity ([source 18](https://arxiv.org/abs/2511.04427)). |
| Conway (1968) | System structure mirrors the communication structure of the organization | MacCormack, Rusnak and Baldwin (Research Policy 2012): in every matched pair, the loosely coupled organization's product was more modular, by up to 6x ([source 8](https://dash.harvard.edu/handle/1/34403525)). Nagappan et al. 2008 on Vista (source 9). A 2016 Colfer and Baldwin review lists exceptions (not read). | **B** | The "organization" becomes the agent topology and the context boundaries. An agent per module tends to produce a module per agent. Use that deliberately: cut task boundaries where you want module boundaries (inference, **D**). |
| Hyrum (Wright) | With enough users, every observable behavior of your system will be depended on by somebody, whatever the contract says | Google experience, from *Software Engineering at Google*; Wright's own write-up ([source 16](https://www.gwern.net/docs/www/www.hyrumslaw.com/80a99df5dd87f0da9cb8ceb14399cc94504468b5.html)). No formal study. Examples: changed ordering, error wording, timing, log text. | **C** | An agent making a "safe" refactor changes observable behavior nobody pinned. Mainly a danger in code with consumers: your CLIs, the apk-builder JSON contract, flake outputs. |
| Gall (1975) | A complex system that works evolved from a simple one that worked | Anecdote; commentators note it is more observation than law ([source 37](https://en.wikipedia.org/wiki/Systemantics)). Gall did not call it a law. | **D** | Supports small increments. Agents can generate large complex designs in one shot, which is exactly the case Gall predicts fails. A reason to cap the size of agent tasks. |

**Which to act on.** Conway and Hyrum are the useful ones, in that order.
Lehman's two surviving laws are weaker than their fame and mostly describe
open-source growth. Gall is a heuristic for task sizing.

## 8. Beck, Fowler, Feathers

### Beck: XP, TDD, Tidy First

**Claims.** Write the test first; make small steps; refactor under green;
separate structural changes from behavioral ones (*Tidy First?*, 2023, a
short book on small tidyings before feature changes); keep options open.

**Evidence on TDD.** A [meta-analysis of 27 studies](https://doi.org/10.1109/TSE.2012.28)
(Rafique and Mišić, online 2012-05-08, journal 2013) found a small positive
quality effect and little or no productivity effect overall. Industrial
subgroups had larger quality gains and productivity losses than academic
ones. A
family of 12 experiments (Santos, Vegas, Dieste, Fucci and others) found
novices got slightly higher quality from iterative test-last than from TDD and
that the task largely determines quality. Fucci, Turhan and Oivo's enhanced
replication found no support for quality or productivity gains
([family of 12 experiments](https://arxiv.org/abs/2011.11942),
[replication study](https://link.springer.com/article/10.1007/s11219-020-09512-3),
[source 11b](https://arxiv.org/pdf/2004.05335)). Grade **A**: small and
inconsistent effects for humans in the settings studied.

**Evidence on Tidy First / separating structure from behavior.** None found
beyond practitioner use. Kim et al. support the value of refactoring
(source 13) but not the commit-separation rule. Grade **D**.

**With agents.** Beck reports TDD as a "superpower" with agents because
agents introduce regressions, and he stopped an agent disabling or deleting
tests to force green (Pragmatic Engineer interview, 2025, via secondary
sources: [source 12b](https://exadel.com/news/test-driven-development-ai-coding),
[source 12c](https://signals.aktagon.com/articles/2025/09/augmented-coding-beyond-the-vibes/)).
His B+ tree project used a prompt requiring red-green-refactor and separating
structural from behavioral changes (source 12). Grade **C/D**: one
practitioner, no numbers. Why it plausibly works: a test is an executable
specification written before the implementation, and an agent cannot argue
with a failing test. The human-study evidence (small effect) concerns a
different mechanism, where the programmer's own thinking is the benefit.
Your `test-quality` section 7 mode 8 ("weakened during a fix") is the
failure Beck describes. The separation rule helps review: a structural-only
diff can be checked with unchanged tests plus focused behavior and performance
checks. Existing tests alone cannot establish preservation.

### Fowler: Refactoring

**Claim.** Small behavior-preserving transformations, guarded by tests,
improve design and make change cheaper.

**Evidence.** The Microsoft field study (source 13, **B**): refactored Windows
modules showed fewer inter-module dependencies and fewer post-release defects;
developers also perceived substantial cost and risk; "refactoring" in practice
included non-behavior-preserving changes. I found no direct test of Fowler's
smell catalog. Grade **B/C**.

**With agents.** Agents are good at mechanical refactoring, and the
behavior-preserving definition gives a clean acceptance test. The risk is the
Ousterhout-Martin prime example: behavior preserved, performance not.

### Feathers: Working Effectively with Legacy Code (2004)

**Claim.** Legacy code is code without tests. To change safely you need tests;
to add tests you often must change code first. Break dependencies at seams
(places behavior can change without editing there) and pin existing behavior
with characterization tests that record what the code does, not what it should
([source 28](https://www.web-developpeur.com/en/library/working-effectively-legacy-code/)).

**Evidence.** Practitioner. No controlled study. Practitioner posts apply it
to agents (an agent that refactors first and tests second writes assertions
matching its own refactored output). I found no study of whether it improves
agent outcomes. Grade **C/D**.

**With agents.** This is the most under-used classic for your setup. Agents
treat everything unprotected as free to change. A characterization test is
the Hyrum's-law guard.

## 9. DORA / Accelerate as empirical counterpoint

**Claim.** Four delivery metrics (deployment frequency, lead time for changes,
change failure rate, time to restore) distinguish high performers, and a set
of technical and cultural capabilities (trunk-based development, continuous
integration, small batches, loosely coupled architecture, and others) predict
them (Forsgren, Humble, Kim, *Accelerate*, 2018).

**Evidence.** Survey-based, correlational. The 2025 report drew on nearly
5,000 respondents (survey run June 13–July 21, 2025) and 100+ hours of
qualitative data ([source 19](https://blog.google/technology/developers/dora-report-2025/)).
I could not verify the *Accelerate* sample size (n = 23,000 is commonly quoted)
or its methods from search results. Derek Jones criticizes the analysis
description as "rather sketchy" and says he has not seen the data or survey
questions ([source 38](https://blogs.accu.org/category/dora/)). Practitioners
warn against using the metrics as goals. Grade **B** (large-n, self-reported,
correlational).

**What it adds against the old literature.** It is a counterweight to
armchair design principles: most of its capabilities are about feedback speed
and batch size, not code shape. It says nothing about deep modules.

**DORA 2025 and agents.** AI adoption is associated with higher throughput
(reversing 2024's finding) and still higher instability. The report frames
AI as an amplifier of existing organizational strengths and weaknesses, with
a seven-capability model; I could not confirm the official list
([source 19b](https://services.google.com/fh/files/misc/2025_state_of_ai_assisted_software_development.pdf)).
Commentary attributes the instability to delivery pipelines not keeping pace
with code generation (blogs, vendor commentary; association not
causation). METR's randomized trial of experienced open-source developers
(2025) found 19% slower with AI tools while developers believed they were
faster; the February 2026 follow-up estimated about 4% less task time for newly
recruited developers (CI roughly −15% to +9%), and METR says selection
effects mean the true speedup is probably positive and the estimate a poor
proxy ([primary update, 2026-02-24](https://metr.org/blog/2026-02-24-uplift-update/)).
The interval includes no effect. Both studies used earlier tools. Grade
**A** for randomized design; current effect magnitude remains uncertain.

## 10. Is software engineering really engineering?

Shaw (IEEE Software, 1990) framed engineering as a progression from craft
through commercial practice to professional engineering with science feeding
practice, and judged software not yet there
([source 40](https://www.sei.cmu.edu/library/prospects-for-an-engineering-discipline-of-software/)).
What transfers and what does not:

| Practice in civil / mechanical engineering | Transfers to software? | Why | With agents |
|---|---|---|---|
| **Specifications and tolerances** | Partly | Physical parts vary continuously, and a part 0.1% off usually works. Software behavior is discontinuous: one wrong bit can change everything. So tolerances map to types, contracts and invariants, which are exact, not to ranges. | Agents make exact specifications more valuable: they are the only thing that constrains a fast writer. |
| **Safety factors** | Partly | No physics gives you a margin to over-build. The software analogue is redundancy: timeouts, limits, hardware interlocks, fail-safe defaults. Therac-25 dropped hardware interlocks that earlier models had and relied on software; software interlocks failed through a race condition. Leveson and Turner conclude that focusing on individual bugs is not the way to make a safe system; safety must be assured at the system level despite software errors ([source 27](https://www.se.rit.edu/~swen-342/resources/Leveson,%20Turner%20-%20An%20Investigation%20of%20the%20Therac-25%20Accidents%20-%20IEEE%20Computer%20v26n7%20-%201993-07.pdf)). | Do not let an agent remove a defense-in-depth layer because the code "already handles it". |
| **Standards and codes** | Yes, narrowly | Industry standards exist (safety-critical domains). For general software the equivalents are style guides, linters, CI gates and your lexicon. | Machine-enforced standards are cheap for agents to satisfy and make review smaller. Rules stated only in prose are routinely skipped. |
| **Licensure** | No, so far | NCEES discontinued the PE Software Engineering exam after April 2019 because of low participation: 81 candidates had requested seats since 2013 (Florida board report), the FE prerequisite shut out many software engineers, and boards were not regulating the profession ([source 41](https://ncees.org/ncees-discontinuing-pe-software-engineering-exam/), [source 41b](https://fbpe.org/ncees-ending-software-engineering-discipline-exam/)). Licensure presupposes a regulated duty of care and a stable body of knowledge. | Nobody is licensed to supervise an agent either. Accountability falls on the person who merges. |
| **Post-mortems and failure analysis** | Yes, strongly | Petroski's thesis: progress comes from designing to anticipated limits and learning from what fails; success breeds overconfidence ([source 42](https://www.technologyreview.com/1997/08/01/237228/the-engineers-multifaceted-world/amp/), 1997 review; Groce's review argues failure is more central to software than to other disciplines ([source 42b](https://www.cefns.nau.edu/~adg326/passages/PetroskiReview.pdf)). He also warns that computer-aided design can feed overconfidence. Grade **C**. | Agent failures are a new failure corpus. A blameless write-up of each class of agent failure (test weakening, scope creep, silent behavior change) is worth the minutes it costs. Your `test-quality` audits already do this for tests. |
| **Physics and continuity** | No | Bridges obey known laws, so analysis predicts behavior before building. Software has no governing equations. Verification is by proof, test and review. | Without physics, the agent's output cannot be trusted by extrapolation from past success. |
| **Expensive fabrication forces upfront analysis** | Inverted | Building a bridge twice is impossible, so design review is cheap relative to build. Software build cost is near zero (Reeves), so trying is cheaper than analyzing. | Agents push this further: generation is now cheaper than reading. The scarce resources are specification, review attention, and the maintainers' theory. |
| **Malleability** | Double-edged | Software can be changed after release. But Hyrum's law and Lehman's continuing-change law mean every change meets dependents, and users hold your system to its observable behavior, not its spec. | Cheap change is the reason the cost of rework flattens (section 1), but only up to the point where consumers exist. |

**Summary.** The disciplines transfer where they are about learning from
failure, redundancy, and accountability. They fail where they depend on
physics, continuity, or expensive manufacture. The last of these is the one
agents move most. In civil engineering the gate is the cost of building; in
agent-assisted software the cost of building is near zero, so the gate has to
be something else you build on purpose: tests, types, review, and a
documented theory.

## 11. Synthesis: classic idea to agent-era status

| Idea | Human-era evidence | Agent-era status (inference unless cited) |
|---|---|---|
| Managing complexity (McConnell, Ousterhout) | B (indirect) | **Stronger.** Complexity measurably rises with agent use (He et al.). Agents have no felt cost of complexity. |
| Deep modules | D (B adjacent) | **Stronger.** Interface-sized context beats implementation-sized context. |
| Information hiding | C | **Stronger.** Mechanical enforcement is cheap and an agent cannot misuse what it cannot see. |
| Interface comments | D | **Stronger,** with the CLAIM convention as the freshness guard. |
| Defect-cost curve | C vs B | **Weaker** for code, intact for specs and contracts. |
| Brooks's law | C | **Replaced** by "parallel writers conflict"; evidence from Google and Cognition. |
| Conceptual integrity | D | **Stronger.** Agents are many hands. |
| Naur's theory | D | **Supported** by written artifacts and checks; continuing human understanding still matters. |
| No Silver Bullet | D | **Plausible,** but the essential work moves to specification and verification. |
| TDD | A (small effect) | **Different mechanism, plausibly stronger** (D/C evidence). |
| Refactoring | B | **Stronger enabler,** needs behavior pinning. |
| Feathers / characterization | C/D | **Stronger,** and under-used. |
| Dijkstra on proof | Deductive claim, outside empirical grades | **Economics shifting;** unproven at scale. |
| Hoare / types | C | **Stronger,** best return per unit effort. |
| Contracts | C | **Stronger,** executable theory. |
| Conway | B | **Applies to context boundaries** as well as teams. |
| Hyrum | C | **Stronger.** Agents are fast and indifferent to unwritten dependents. |
| Gall | D | **Supports** small agent increments. |
| Lehman | B (two laws) | **Unclear,** faster growth possible. |
| DORA | B | **The counterweight:** speed without feedback gains instability. |
| Licensure | None | **Not coming back;** failure analysis is what to import. |

## Where your setup differs

I compared against `technical-excellence` and `test-quality` only. For
`build-loop`, `question-everything`, `rg-implement` and Aegis, I have only
what their descriptions say.

**Where you already match the literature, sometimes better than popular
practice:**

- `technical-excellence` section 3 (deep modules, shallow wrappers as smells)
  is Ousterhout directly. Section 1 (error detail, reason, invariants, mating
  parts) is Parnas, Meyer and Hyrum in one table. Section 5 (invalid states
  unrepresentable, parse don't validate) is Hoare's repair. Section 2 (CLAIM
  ids tied to sources and tests) goes past anything in the classic texts and
  answers Martin's objection that comments rot.
- `test-quality` section 6 and mutation checks implement Dijkstra's point
  that a passing test only shows absence of known bugs. The WHY rule keeps
  Naur's theory in the tests. Mode 8 ("weakened during a fix") is the failure
  Beck describes with agents.
- The single-implementer shape of build-loop (Opus orchestrates, Sonnet
  implements) and the 1x main queue (AGENTS.md) are on the safe side of the
  Google, Cemri and Cognition findings. I did not read the skills to see how
  parallel work is bounded.

**Gaps:**

1. *No explicit characterization-test step.* `test-quality` already has
   reviewed goldens, independent fixtures and parity checks that can pin
   existing behavior. The narrower gap is deciding, before a change, which
   legacy outputs to preserve and which to change (Feathers, Hyrum). The apk-builder JSON interface, flake outputs and CLI
   formats are the consumers most at risk.
2. *No rule separating structural from behavioral changes* (Beck, Fowler).
3. *No explicit theory-transfer artifact.* The CLAIM convention captures
   facts and proofs. Naur's theory also includes why alternatives were
   rejected. Nothing I read requires recording rejected options.
4. *No complexity ratchet.* He et al. found complexity and warnings rise
   persistently after agent adoption. Neither skill sets a metric to hold.
5. *No failure corpus.* Petroski and Leveson both build on cataloged failures.
   `test-quality` section 10 records audit lessons but not a running log of
   agent failures.
6. *Deep-modules rule has no stated counter-risk.* The Ousterhout–Martin
   exchange shows a refactor that preserved behavior and cost 3–4x speed.
7. *Naming rule.* `technical-excellence` section 4 (no abbreviations, 1–2
   primary words) leans toward Martin's names-instead-of-comments position,
   while section 2 leans toward Ousterhout's comments. Not a conflict, but
   worth knowing that you hold both sides of the debate.

## Candidate actions

Ranked by expected value over cost.

1. **Add a characterization-test step to build-loop for changes to existing
   behavior.** Before an agent edits code with consumers, write tests that
   pin selected current outputs and label intended changes separately
   (Feathers, Hyrum). Reuse reviewed goldens. This is a risk-based proposal,
   D; no measured local benefit or universal agent default is established.
2. **Add a "structural vs behavioral" commit rule for agent tasks.** A
   structural-only commit must leave the existing tests unchanged and green.
   Rationale: separation can simplify review, but unchanged green tests do not
   prove behavior preservation. Beck's practice has **D/C** evidence; cost is unmeasured.
3. **Add a short "theory" file per major module** (one page: what it is for,
   what was rejected and why, what to never do) written by the human or
   reviewed by them, updated at the end of each build-loop run. Rationale:
   Naur's argument motivates preserving reasons alongside continuing human
   understanding. Reuse existing decision records before adding a new file. Evidence **D**, so run it on diff-core for a month and
   see whether it changes review quality.
4. **Set a complexity and warning ratchet per repo** (clippy or lint count,
   a cyclomatic-complexity ceiling) that agent PRs must not raise. Rationale:
   the He et al. observations (**B**) motivate monitoring. The revised paper
   reports estimator-sensitive magnitudes. A ceiling's effect and setup cost
   remain unmeasured; permit justified exceptions.
5. **Keep fan-out to read-only or disjoint-write work and say so in
   build-loop.** Rationale: Google, Cemri, Cognition agree (**A/B**); check
   what the skill already says before editing.
6. **Start a blameless agent-failure log in `knowledge/`.** One entry per
   failure class: what happened, which invariant or test should have caught
   it, what was added. Rationale: Petroski and Leveson (**C**); cheap and it
   feeds `test-quality` modes.
7. **Add a performance caveat to the deep-modules rule:** a refactor in a hot
   path needs a benchmark before and after. Rationale: the prime-generator
   regression (**C**).
8. **Try Verus on one small Rust module, or model its algorithm in Dafny.**
   A tea cache index is one candidate. Dafny does not directly verify the
   existing Rust implementation. Treat this as a bounded experiment. Rationale: Kleppmann's prediction is
   testable on your code in a weekend; expect specification-writing to be the
   cost. Evidence **D**.
9. **Do not adopt:** the defect-cost multiplier as a reason for heavy upfront
   specification of cheap-to-redeploy code; Brooks's law as a staffing rule
   for agents; Lehman's laws as design guidance; licensure.

## Reading path

Ordered for someone improving as a professional engineer, shortest payoff
first. Publisher and author references below were checked on 2026-11-10.
Time estimates are planning judgments, not measured reading times.

1. **Parnas, "On the Criteria To Be Used in Decomposing Systems into
   Modules" (1972).** About 8 pages, 30 minutes. The origin of information
   hiding. Read the KWIC comparison.
2. **Parnas and Clements, "A Rational Design Process: How and Why to Fake
   It" (1986).** About 7 pages, 30 minutes. Read for the list of documents.
3. **Ousterhout, *A Philosophy of Software Design*, 2nd ed.** About 190
   pages, 5–6 hours. Chapters on complexity (1–2), strategic vs tactical (3),
   deep modules (4), information hiding (5), general-purpose design (6),
   comments (12–13 and 15; chapter 14 covers names), and the added
   Clean Code comparison subsections, not a separate new chapter. The
   [author's second-edition note](https://web.stanford.edu/~ouster/cgi-bin/book.php)
   confirms the subsections; the numbered mapping still needs the reader's
   second-edition contents page [unverified against a primary full TOC]. Then read the
   Ousterhout–Martin transcript (source 6) for 90 minutes, focusing on the
   prime generator and comments sections.
4. **Naur, "Programming as Theory Building" (1985).** About 12 pages, 45
   minutes. Read it twice: once now, once after step 9.
5. **Reeves, "Code as Design: Three Essays".** About 1 hour. Then ask what
   changes when compile is free and generation is free.
6. **Brooks, *The Mythical Man-Month* (anniversary ed.).** Chapters 2
   (Mythical Man-Month), 3 (Surgical Team), 4 (Aristocracy, Democracy,
   and System Design, covering conceptual integrity), 11
   (Plan to Throw One Away), 16 (No Silver Bullet), 17 (Refired). About 3
   hours. [Publisher contents](https://www.informit.com/store/mythical-man-month-essays-on-software-engineering-anniversary-9780321770561)
   confirm these pointers. Read Meyer's rebuttal (source 22) after, 30 minutes.
7. **McConnell, *Code Complete* 2nd ed.** Chapter 5 (Design in
   Construction), 6 (Working Classes), 7 (High-Quality Routines), 24
   (Refactoring), 34 (Themes in Software Craftsmanship). About 4 hours. Read
   Menzies et al. (source 2) alongside chapter 3's cost-of-defects material,
   40 minutes. [Contents](https://www.oreilly.com/library/view/code-complete-2nd/0735619670/toc.html).
8. **Feathers, *Working Effectively with Legacy Code*.** Part I (chapters
   1–5) and chapter 13 on characterization tests. About 3 hours.
   [Publisher contents](https://www.informit.com/store/working-effectively-with-legacy-code-9780131177055).
9. **Beck, *Tidy First?*, and Fowler, *Refactoring* 2nd ed.** Tidy First is
   about 100 pages, 2 hours. In Refactoring, read chapter 1 and
   chapter 3, Bad Smells in Code, 2–3 hours.
   [Second-edition contents](https://www.oreilly.com/library/view/refactoring-improving-the/9780134757681/). Then read Beck's "Augmented Coding: Beyond the
   Vibes" (source 12), 20 minutes.
10. **Leveson and Turner, "An Investigation of the Therac-25 Accidents"
    (1993).** About 25 pages, 1.5 hours. Pair with Petroski, *To Engineer Is
    Human*, 4–5 hours, and Groce's review (source 42b) as a software lens.
11. **Hyrum's law page and Titus Winters et al., *Software Engineering at
    Google*,** chapter 21, [Dependency Management](https://abseil.io/resources/swe-book/html/ch21.html),
    and chapter 22, [Large-Scale Changes](https://abseil.io/resources/swe-book/html/ch22.html).
    There is no chapter titled API Change. 2 hours.
12. **Forsgren, Humble, Kim, *Accelerate*,** Part One, What We Found, chapters 1–11, 3
    hours. [Publisher contents](https://www.oreilly.com/library/view/accelerate/9781457191435/). Then the DORA 2025 AI report executive summary (source 19b), 1
    hour. Read Derek Jones' critique (source 38), 20 minutes, for balance.
13. **Agent-era papers, in this order:** the AGENTS.md study (source 21),
    Google's scaling-agents paper (source 23), the He et al. Cursor study
    (source 18), Cemri et al. (source 24), Kleppmann's post (source 33).
    About 4 hours total.
14. **Dijkstra, "The Humble Programmer" (1972).** About 15 pages, 1 hour.
    Read last, so you meet it knowing which of its claims survived.

Total: about 40–45 hours. The first four items, about 8 hours, carry most of
the value for how you work with agents.

## Sources

Dates are publication dates where I could determine them. "Secondary" means I
saw a summary, not the original.

1. [McConnell, "Upstream Decisions, Downstream Costs"](https://stevemcconnell.com/articles/upstream-decisions-downstream-costs/) — McConnell, IEEE Software column, 2001 (secondary summary of Boehm and Papaccio 1988).
2. [Menzies, Nichols, Shull, Layman, "Are Delayed Issues Harder to Resolve?"](https://arxiv.org/abs/1609.04886) — arXiv 2016, *Empirical Software Engineering* 22(4), 2017; 171 projects, 2006–2014.
3. [McConnell, "Missing in Action: Information Hiding"](https://stevemcconnell.com/wp-content/uploads/2017/08/MIAInformationHiding.pdf) — IEEE Software, 1996 (reports Brooks reversal and Boehm 1987 claim; secondary).
4. [Tornhill and Borg, "Code Red"](https://arxiv.org/abs/2203.04374) — TechDebt 2022; 39 codebases, 30,737 files; vendor-affiliated authors.
5. [Borg, Hagatulah, Tornhill, Söderberg, "Code for Machines, Not Just Humans"](https://arxiv.org/abs/2601.02200) — arXiv January 5, 2026, ACM FORGE 2026; vendor-affiliated.
6. [Ousterhout and Martin, "aposd-vs-clean-code"](https://github.com/johnousterhout/aposd-vs-clean-code) — discussions September 2024–February 2025 (read ~80%).
7. [Ousterhout, book page](https://web.stanford.edu/~ouster/cgi-bin/book.php) — 2nd ed. July 2021.
8. [MacCormack, Rusnak, Baldwin, "Exploring the Duality"](https://dash.harvard.edu/handle/1/34403525) — Research Policy 41(8), 2012.
9. [Nagappan, Murphy, Basili, "The Influence of Organizational Structure on Software Quality"](https://www.microsoft.com/en-us/research/?p=153188) — ICSE 2008 (abstract and secondary).
10. [QSM, "Empirical Examination of Brooks' Law"](https://qsm.com/blog/2009/empirical-examination-brooks-law) — 2009 (vendor blog).
11. [Santos et al., family of 12 experiments on TDD](https://arxiv.org/abs/2011.11942) — arXiv November 2020; separate [replication study](https://link.springer.com/article/10.1007/s11219-020-09512-3), also [arXiv 2004.05335](https://arxiv.org/pdf/2004.05335) (11b).
12. [Beck, "Augmented Coding: Beyond the Vibes"](https://newsletter.kentbeck.com/p/augmented-coding-beyond-the-vibes) — 2025. 12b: [Exadel](https://exadel.com/news/test-driven-development-ai-coding), 12c: [aktagon](https://signals.aktagon.com/articles/2025/09/augmented-coding-beyond-the-vibes/) (secondary).
13. [Kim, Zimmermann, Nagappan, field study of refactoring at Microsoft](https://www.microsoft.com/en-us/research/?p=163533) — FSE 2012; TSE 40(7), 2014; survey of 1,290 engineers.
14. [Naur, "Programming as Theory Building"](https://neonvagabond.xyz/mirrors/naur1985programming.html) — 1985 (mirror). 14b: [Goedecke](https://www.seangoedecke.com/programming-with-ai-agents-as-theory-building) (2026-04-03 blog; primary page checked in cross-review).
15. [Ratfactor, paper notes on Naur](https://ratfactor.com/papers/naur1) — secondary.
16. [Hyrum's Law](https://www.gwern.net/docs/www/www.hyrumslaw.com/80a99df5dd87f0da9cb8ceb14399cc94504468b5.html) — archive of hyrumslaw.com; wording from secondary summaries of *Software Engineering at Google* (2020).
17. [Chowdhury et al., method length and change/bug-proneness](https://www.cs.ubc.ca/~rtholmes/papers/msr_2022_chowdhury.pdf) — MSR 2022, ~785K Java methods, 49 projects.
18. [He et al., "Speed at the Cost of Quality?"](https://arxiv.org/html/2511.04427v1) — 2025-11-06. The 30%/41% figures use one estimator; [v3](https://arxiv.org/html/2511.04427v3), 2026, discusses differing estimates.
19. [Google, "How are developers using AI? Inside our 2025 DORA report"](https://blog.google/technology/developers/dora-report-2025/) — 2025. 19b: [DORA report PDF](https://services.google.com/fh/files/misc/2025_state_of_ai_assisted_software_development.pdf) (not read directly).
20a. [O'Reilly Radar, "The Mythical Agent-Month"](https://www.oreilly.com/radar/the-mythical-agent-month/) — Wes McKinney, 2026-03-23; primary commentary checked in cross-review.
21. [Gloaguen et al., "Evaluating AGENTS.md"](https://arxiv.org/html/2602.11988v3) — 2026-09-29 revision, primary paper.
22. [Meyer, "A theorem of software engineering"](https://bertrandmeyer.com/2019/11/01/theorem-software-engineering/) — November 2019.
23. [Google Research, "Towards a science of scaling agent systems"](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/) — arXiv 2512.08296, December 2025.
24. [Cemri et al., "Why Do Multi-Agent LLM Systems Fail?"](https://arxiv.org/abs/2503.13657v3) — arXiv March 2025, NeurIPS 2025.
25a. [Cognition, "Don't Build Multi-Agents"](https://cognition.ai/blog/dont-build-multi-agents) — June 2025 (excerpts). 25b: [Cognition, "Multi-Agents: What's Actually Working"](https://cognition.com/blog/multi-agents-working) — April 2026.
26. [Anthropic, "How we built our multi-agent research system"](https://www.anthropic.com/engineering/multi-agent-research-system) — 2025-06-13; figures checked against the primary post in cross-review.
27. [Leveson and Turner, "An Investigation of the Therac-25 Accidents"](https://www.se.rit.edu/~swen-342/resources/Leveson,%20Turner%20-%20An%20Investigation%20of%20the%20Therac-25%20Accidents%20-%20IEEE%20Computer%20v26n7%20-%201993-07.pdf) — IEEE Computer, July 1993 (via secondary summaries).
28. [Summary of Feathers, *Working Effectively with Legacy Code*](https://www.web-developpeur.com/en/library/working-effectively-legacy-code/) — secondary; book 2004.
29. [Dijkstra quotations](https://en.wikiquote.org/wiki/Edsger_W._Dijkstra) — "The Humble Programmer," CACM 15(10), October 1972. 29b: [Wayne, "Testing can show the presence..."](https://buttondown.com/hillelwayne/archive/testing-can-show-the-presence-of-bugs-but-not-the).
30. METR 2025 randomized trial (19% slower): see source 39 for the follow-up that restates it.
31. [Parnas and Clements, "A Rational Design Process"](https://bibbase.org/network/publication/parnas-clements-arationaldesignprocesshowandwhytofakeit-1986) — IEEE TSE 12(2), 1986 (bibliographic and summary).
32. [Reeves, "What Is Software Design?"](https://www.developerdotstar.com/mag/articles/reeves_design.html) — C++ Journal, Fall 1992.
33. [Kleppmann, "Prediction: AI will make formal verification go mainstream"](https://martin.kleppmann.com/2025/12/08/ai-formal-verification.html) — December 8, 2025.
34. [Hoare, "Null References: The Billion Dollar Mistake"](https://www.infoq.com/presentations/Null-References-The-Billion-Dollar-Mistake-Tony-Hoare/) — QCon London, 2009.
35. [Estler et al., "Contracts in Practice"](https://arxiv.org/abs/1211.4775v6) — FM 2014. 35b: [AdaCore critique](https://blog.adacore.com/studies-of-contracts-in-practice).
36. [Neamtiu, Xie, Chen, Lehman's laws on open source](https://www.cs.kent.edu/~jmaletic/cs63902/Papers/jsme11neamtiu.pdf) — J. Software: Evolution and Process, 2013; nine projects.
37. [Systemantics (Wikipedia)](https://en.wikipedia.org/wiki/Systemantics) — Gall, 1975 (secondary).
38. [Derek Jones on DORA](https://blogs.accu.org/category/dora/) — blog, undated in search result.
39. [METR uplift update](https://metr.org/blog/2026-02-24-uplift-update/) — 2026-02-24; primary update checked in cross-review.
40. [Shaw, "Prospects for an Engineering Discipline of Software"](https://www.sei.cmu.edu/library/prospects-for-an-engineering-discipline-of-software/) — IEEE Software 7(6), 1990.
41. [NCEES, discontinuing PE Software Engineering exam](https://ncees.org/ncees-discontinuing-pe-software-engineering-exam/) — announced 2018, last exam April 2019. 41b: [FBPE](https://fbpe.org/ncees-ending-software-engineering-discipline-exam/).
42. [MIT Technology Review, review of Petroski](https://www.technologyreview.com/1997/08/01/237228/the-engineers-multifaceted-world/amp/) — August 1997. 42b: [Groce, review of *To Engineer Is Human*](https://www.cefns.nau.edu/~adg326/passages/PetroskiReview.pdf) — undated.
