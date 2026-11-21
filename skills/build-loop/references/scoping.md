# build-loop reference: scope, pilots, estimates, fast iteration (§1, §2, §4, §8–9)

Source: edge "live guides r2" (2026-11-13) and "no-spinners" (2026-11-15).

## The scope question (§1)

Ask the owner which kind of change this is:

- **Pilot**: try it on a few cases, gather data, then decide.
- **Structural fix**: change how the thing works everywhere.
- **Hardening**: strengthen the structural design before an upstream PR or project release.

**Default: pilot.** Owner: "The answer is typically launch things as pilots first, because then we're
able to gather more data and that data is able to inform implementations that are correct the first
time." Ask inline with that default and keep working (§1a). A bug fix is not a pilot; skip the
question when the kind is obvious.

## Pilot rules

- **Scored, agreed before starting (owner, 2026-11-15).** Agree the feature's scored concerns and
  bars with the owner, typically four: data safety (`durability`), correctness (`error-paths`), the
  feature goal (`legibility` for UX, `performance` for layout shift), maintainability (`architecture`).
  Record exactly those concerns at init, for example `init --pilot --bar durability=9 --bar wiring=7
  --bars-agreed "<owner quote or note>"`. Concern names come from `bars.md`.
  Without an agreement, touched concerns default to 6, except durability at 7. If the pilot writes
  stored data, changes schema or migrations, or sends notifications or other outward messages,
  pass `--touches-data`: durability
  defaults to 9 and is included automatically. `durable-state`/`migration` categories also select it.
  Init prints the default applied. Pilots never record or constrain a region's shape/stage in
  `bars.json`. Structural and later stages keep the normal shape × stage bars.
- **Review schedule.** Round 1: Sol or Opus, never the author. Round 2: Fable, including ARGUE,
  STEP-BACK, NIT-CULL and FIX-KEPT; later rounds keep the normal caps. Every named concern must
  meet its bar, and the owner must approve the pilot build. Record `review-ledger -l L owner-ok
  "<quote>"`; without it the ledger refuses CHECKPOINT and STOP-AGREED.
- **Hardening list.** Use the existing `HARDENING-STASH`, not a second list. Review briefs send
  findings outside the agreed concerns, or not needed for the current bars, there. Do not fix them
  this round. Typical items: pixel/frame tests and sweeps, stricter measurement, micro-performance,
  screen readers, translations of changing copy, maintainability tidy-ups.
- **Tests cover the pilot's own cases only.** No sweeps over every item, no catalogue-wide guards,
  until the owner decides to go structural. Size check: pilot test code stays under about twice the
  expected change. Over that, cut tests before writing more.
- **No full test runs (owner, 2026-11-15).** The pilot stage runs targeted tests and gates for what
  it touches. Full runs belong to the structural and hardening stages.
- **One red round.** The spec review (§4a) may run alongside green, not before it. Its findings go to
  the first fix round.
- **Ship iteration builds early.** An iteration build, preview or screenshot set goes to the owner as soon as the
  targeted tests pass. The pilot's scored review (§6) follows the owner's feedback.
- **Feature flag, always.** Put pilot behaviour behind a flag (or a per-item field), so the pilot
  build changes only the pilot's cases and turning it off is a two-way door. Choose where the
  flag lives from what kind of feature it is:
  - *user-facing behaviour in an app*: a setting the owner can toggle inside the product (a
    debug or labs screen), so the pilot can be compared on and off on a real device;
  - *services, daemons, CLIs*: an environment variable or config key read at start-up, with the
    flag's state logged on boot;
  - *changes that alter what gets built* (new dependencies, codegen, schema, native code): a
    build-time flag (a Cargo feature, a Gradle property, a Nix option), off by default;
  - *data shape changes*: a flag that gates writes, with reads accepting both shapes until the
    structural round.
  Name the flag in the pilot report, say how to flip it, and say what happens to data written
  while it was on. The structural round decides whether the flag stays, becomes a setting, or
  goes.
- **Own branch, kept as a reference (owner, 2026-11-15).** Keep the pilot branch as a reference.
  Start the structural stage fresh from the base on a new branch, carrying over only the code,
  tests and evidence the owner endorsed. Pilot tests encode the pilot design; rebuilding avoids
  spending the structural round undoing it.
- **Shared pilot branch, on request (owner, 2026-11-18).** Several pilots may share one branch
  (`pilot/<a>+<b>`) to reuse pieces both need; two day-timeline adjustments piloted separately
  duplicated one shared timeline change. Not the default: when two or more pilots are still being
  evaluated, or are requested around the same time, and they overlap, ask the owner inline
  (default: separate branches) before starting. Each pilot on a shared branch keeps its own
  opt-in, its own red tests and its own report section.
- **End with evidence** for the owner's decision: before/after shots, counts, what broke.

Structural and hardening stages use the normal bars and review schedule (§4–§6).

## Stages and what to test (§1, §3)

The work stages are pilot → structural → hardening:

- **Pilot**: a few cases, opt-in; tests cover the pilot's own cases only (above).
- **Structural**: the owner says go wide. One design check per fix; looser on edge cases.
- **Hardening**: before an upstream PR opens or goes ready, or a project release, review the
  hardening stash at normal bars. Add symptom tests, catalogue sweeps, pixel/frame tests, edge cases.

Before a structural round lands on an integration branch the owner runs: the structural review
at normal bars, Fable at round 3, no extra triage. Before an upstream PR or a project release: hardening.

**Test the design, not the symptom, until hardening.** When a fix rules a bug out by construction,
one assertion that the construction is in place is the test. Symptom tests (frame stepping, pixel
sampling, timing, sweeps over every item) are hardening work.

**30-minute flag.** An implementer that spends more than 30 minutes on one problem (the same failing
test or symptom across 3 or more runs) flags it to the orchestrator in its report and keeps working on
the rest. The orchestrator cuts it (defers it to hardening) or asks the owner. Put this rule in every
implementer brief, next to: "You may use vigil, but never orchestrator mode (`orchestrator: true` /
`--orchestrator`); that is only for the main session that talks with the user."

## Estimates (§2)

In `references/estimates.md`: every ETA comes from `agentpace` plan state.

## Developer releases: deadlines (owner, 2026-11-20)

A developer release is anything the owner is waiting on: a pilot APK, an upstream PR, a fork release. These get a
deadline; slow-burn work nobody is waiting on does not (an artificial date thins review and burns budget).

- **Give an estimate when asked, then plan to it.** State it in the owner's time zone and in UTC, and say what
  would make it slip. Report a slip when it becomes likely, not at the deadline.
- **Internal cutoffs in every brief:** "pushed by HH:MM UTC", with the priority order inside the run ("naps before
  the log storm") and "push what is done and list the rest" if the cutoff hits. Leave at least one hour between the
  last cutoff and the promised delivery for the merge, the combined tests and the build.
- **Integrate early:** merge and test each branch as it lands, not all at the end; parallel branches conflict where
  they share a widget or painter, and early merges leave time to resolve them.
- **Scope freeze at the cutoff (Parkinson's law):** a request that arrives after the cutoff goes to the next build
  by default. Say so in one line and offer the exception; take it only when the owner says it must make this build.
  When the owner moves the deadline out, do not refill the slack with new scope unless they ask.
- **Keep the independent check:** a deadline may move fidelity review to the orchestrator, but never skips it.
  Write follow-ups for the flaws you let through.
- **Budget:** parallel runs under a deadline spend the weekly windows faster; check them at each cutoff and move
  work between providers before one runs out.

## Faster iteration (§8–9)

- **Many runs on ephemeral compute:** keep a checkout in one ephemeral compute sandbox for the
  stage, so repeated runs do not upload the whole worktree. Upload once for a one-off run.
- **Batch checks** into one run (analyze, codegen, tests). While iterating, run the targeted files only.
- **Warm build:** start an iteration build on the base while the implementer works, so the final build
  recompiles only the change.
- **Shard on one ephemeral compute sandbox:** split independent test files across processes in
  that sandbox. Keep files sharing mutable fixture state together. Give each shard its own copy of
  the checkout (separate build and compiler caches, unique temp and database paths), stagger the
  starts and put each under a timeout. Shards sharing one directory corrupted incremental compiler
  caches and collided on database names; a killed test run can leave a cache half-written, so clear
  it before rerunning.
- **Failing files only while iterating:** rerun failing files on ephemeral compute; run the stage's
  full gate once at the end. The pilot stage keeps its targeted scope.
- **Keep working during a run:** run checks on ephemeral compute in the background and fix the
  next independent failure while they run.
- **No parallel ephemeral compute sandboxes** unless the owner sets a deadline (owner, 2026-11-15).
  A second sandbox increases the stage's compute spend.

## Handoffs under a time box (B1)

Under an owner deadline, the red author may continue into green in the same run (no re-reading), unless
its budget is low. B1 alternation resumes at the fix rounds. R2 is unchanged: no reviewer reviews code
it wrote.
