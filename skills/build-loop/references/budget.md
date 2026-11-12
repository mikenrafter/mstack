# build-loop reference: usage limits, concurrency, timing (§8–§10)

## 8. Usage limits

When a model hits its limit mid-run:
1. Save partial work: `git diff` to a patch; bundle any scratch-clone commits.
2. Read the reset time from the error. Set ONE background timer ending just
   after it, chaining legs if the wait exceeds the tool's background cap.
   Ticks alone do not track a deadline: check `date` against it each tick.
3. At the reset, probe with a tiny call before relaunching.
4. Relaunch with a "resume" prompt pointing at the partial work and report.
   Never restart from scratch.

## 9. Concurrency

- One implementer run at a time. At most two, and only at the start of a fresh
  usage window.
- The cap counts every working subagent, not only implementers: spec and red
  writers, researchers, investigators and integrators count too. Read-only
  reviewers (Sol in tier 1, the Opus subagent in tier 2) share their own cap:
  one run at a time, at most two and only at the start of a fresh usage
  window.
- Focus on one workstream: the one the user named as the priority. Do not
  start agents for other queued work just because you are waiting; queue it,
  log it, and start it when the focus work is done or the user redirects.
- Exception: when research is the only task in flight (no implementer,
  integrator or spec writer running), several research agents may run in
  parallel, preferably on a cheap model (e.g. Haiku).
- Before launching any agent, count what is already in flight. If the cap is
  reached, wait (keepalive) instead of launching.
- Wait on a run's process (`tail --pid=<pid> -f /dev/null`), not by grepping
  its log. Logs can quote old errors.
  Take the pid when you start the run (`$!`). Never wait with
  `while pgrep -f <pattern>` inside `bash -c`/`fish -c`: `pgrep -f` matches the
  waiting shell's own command line, so the loop never ends and spins on
  fork/exec (five such loops once held ~70% of an 8-core host for two days).
- Reviewer subagents never use keepalive or sleep loops. Implementers use
  single keepalive ticks only while their own long test runs are going (§7.6).
- Parallel implementers each get their own git worktree with disjoint file
  ownership, and every prompt names the worktree's absolute path. Forbid
  `git stash` in their prompts: the stash is shared by all worktrees of a
  repo, so one agent can pop another's work. Use a WIP commit instead.


## 10. Timing and low budget

**Is it taking too long?** Long keepalive chains are also a clock. Keep a
per-project `TIMINGS.md` (in the project's research dir): expected durations
for suites, single heavy files, builds and agent jobs, plus a log of actuals.
- Before a long job, note its start time and the expected duration from
  TIMINGS.md (or an estimate, marked as one).
- At each check-in (every ~5 ticks), compare elapsed time with the expectation.
  Once it is past 1.5x the expected time or more than 9 minutes over it,
  whichever comes first, investigate before waiting longer: `uptime`, `top -b -n 2 -d 3`,
  `/proc/pressure/{cpu,memory,io}`, `free -m`, and processes you did not start
  (long-running loops, orphaned test runners, another agent's suite).
- Ask what the underlying issue is and how to speed it up: contention, a test
  or step that is slow by design, work that could be cached or reused, too-wide
  test selection, serial work that could be batched.
- Surface host problems to the user early (one line with the evidence): rogue
  or orphaned processes eating CPU or memory, swap pressure, a stuck job. Do not
  kill processes you did not start without the user's OK.
- When the job ends, add a row to TIMINGS.md (took vs expected, contention).

A completion notification (background command, qex wait, `boat exec`,
subagent, T3 delegate) fires when the work ends, which can be past the cache
TTL. It never replaces the tick. After cancelling or consuming a hold, re-arm
one in the same turn while anything is in flight, queued qex jobs included
(2026-11-12: a polara-port session went ~1h35 without a hold this way).

When budget is low (either side):
- one-line status messages; no recaps;
- do not re-read large files; use `git diff --stat` and targeted ranges;
- delegate drafting (reports, prompts, boilerplate) to a subagent;
- while waiting on a long job, arm one completion watcher and relaunch ticks
  silently; check in every few ticks, not every tick.
