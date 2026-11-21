# build-loop reference: estimates and ETAs (§2)

Answer every ETA with `agentpace` (its `agentpace` skill is the manual). Never quote agent work by
feel: models estimate at human-team pace and overshoot agent work 2–5× (vigil history, 2026-11).

- **One plan per deliverable** (`<project>.research/plans/<deliverable>.json`): agent runs, machine
  steps (suites, builds, Boat round trips) and waits. Update it as work moves (`plan start|done|scope`);
  answer an ETA from its current state, never from the original guess. Most ETA error comes from
  not knowing what remains or what changed in scope, not from per-run numbers.
- **Clock times:** Mountain time (America/Denver, the owner's zone) first, then UTC.
- **Relay three times:** commit (a Parkinson cut under the median, set by each task's risk appetite),
  P50, and the slip line (P80). State the trade-offs the commit assumes, so the owner can override
  any of them.
- **Research has no reliable duration** (`reliable: false`): say "research: all bets are off", give
  the historical range, and keep it out of the committed total.
- **Never buy the deadline with spend.** High-cost trade-offs (extra agents past the cap, fast modes,
  large or extra sandboxes) are suggestions marked `needs_owner`. Apply one only on the owner's
  words (`--owner-grant "<quote>"`). Max effort is not a speed lever.
- **Vigil:** dispatch, then register the hold right after it with
  `vigil hold add <hold> --for none --label <run> $(agentpace estimate-run --model <M> --kind <K> --vigil-meta)
  --meta run=<taskId>` (the taskId `delegate_task` or `t3_thread_send` returned: exact, one run; a
  childThreadId also works but is windowed, and a stopped or follow-up run beside it leaves the hold
  unscored. Add `--meta task=<plan>/<task>` for a plan task; an Agent needs its agentId). The flags carry the
  run P80 as `--expect-s` and the estimator's p50/p80 as meta; `run` ties the hold to its run exactly, so
  agentpace learn scores that estimate. Vigil's ledger then closes plan tasks. A hand-typed `--expect-s` is
  only a ceiling, reported apart from P80 coverage.
- **Machine time:** record suites and builds with `agentpace record` (it replaces hand-written
  `TIMINGS.md` rows; `agentpace timings import` converted the old files).
- An iteration build's estimate holds no review rounds. Give the review loop its own line.
- Owner deadline: plan to it. Time-box the implementer, ship what is green at the box, list the rest.

