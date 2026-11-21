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

## 8a. Subscription subsidies (Gemini, 2026-11-20)

Subsidised plans buy far more work than API billing at the same price. Know each one's shape
before planning around it.

- **Google AI plans** (Antigravity, which T3 drives): Pro $19.99, Ultra 5x $99.99, Ultra 20x
  $199.99 a month. Gemini models share one rate limit "drawn down according to API pricing"
  ([Antigravity plans post](https://antigravity.google/blog/changes-to-antigravity-plans/)). It
  refreshes every 5 hours, up to a weekly cap. Ultra 5x has 5× Pro's tokens, and 20x has 20×. Google
  publishes no absolute size. Past the cap, AI credit packs (2,500 / 5,000 / 20,000) bill at Gemini
  Enterprise rates. Bringing your own API key gives no extra plan quota.
- **Neon draws the pool fast:** $3 / M input, $15 / M output (cached input reportedly $0.15 / M).
  That is 4× Flash until 2026-12-31, then 2×.
- **Sizing a run** (our Sol runs as a proxy: 1,202 runs, P50 1.6 M tokens, P80 10 M, P90 23 M; assuming
  ~92% cached input, 7% fresh input, 1% output, about $0.50 per million): about $0.80 of API value for
  a typical run, $5 for a P80 run, $11 for a P90 run. The plan's window size is unknown, so measure
  it: on the first Neon run, read "Five Hour Limit Remaining" before and after, along with the
  run's tokens. That turns the plan into "runs per window" and "runs per week".
- Until measured, plan Neon as a scarce role (press release, coherency-critical reviews), not the
  default implementer.

## B5. Back to default roles

Read `vigil advice` by window, at a threshold of 15% left:

- Low `claude-budget-5h`: wait until its reset or shift work to Sol for now.
- Low `claude-budget-weekly`: switch Claude's roles for the rest of the week,
  until its weekly reset.
- Low `codex-budget-weekly`: switch Sol's roles for the rest of the week,
  until its weekly reset. This Codex plan has no 5-hour limit.
- Low `antigravity-budget-5h` or `-weekly` (20%): Neon's implementer and
  reviewer slots go back to Sonnet/Sol/Opus by their own budgets. The Pro plan
  carries about one busy Neon thread at a time.

Read `resets_at` with `usage-budget-probe ClaudeCode --window 5h`,
`usage-budget-probe ClaudeCode --window weekly`, or `usage-budget-probe Codex
--window weekly`. Do not infer weekly headroom from the combined `pct_left`.
Missing windows or adapter failures are unavailable, not recovered; keep current
roles when unknown.

Return to default roles, Sonnet and Sol alternating with Opus orchestrating,
at the next phase boundary once all relevant windows have recovered. A 5-hour
reset or `on_credits: false` alone does not clear a low weekly window. Say the
switch in the next phase's role statement. Replace the old combined
`claude-budget` and `codex-budget` advisories with the three named windows.

## Heavy work (§8-9)

Run test runs beyond one or two files, suites, builds and APKs with
`edge.research/bin/boat-run [--shell PREFIX] <worktree> -- <cmd>` (`boat`
skill). Briefs to subagents and Sol name `boat-run`, never a local runner. Use
the local queue only for one or two quick runs, or when the `boat-budget`
advisory says Boat's hours are at or below its threshold (default 10%; `vigil
advisory set boat-budget threshold=N`). Local jobs go through qex with a real
claim (`qex submit --wait --cpu 2 --mem 3GB --id-file <f> -- <cmd>`, in the
background); `qex list` first. Details: `low-ram-hosts`.

## 9. Concurrency

- The cap is in SKILL.md §2: one working Claude agent, reviewers a separate
  cap of one, Codex and Sol less strict. Only the owner raises it, by a logged
  exception with an end condition. When it ends, go back to one and count
  again before every launch, not only at the boundary.
- Focus on one workstream: the one the user named as the priority. Do not
  start agents for other queued work just because you are waiting; queue it,
  log it, and start it when the focus work is done or the user redirects.
- Before launching any agent, count the working Claude agents in flight (Codex/Sol
  runs and commands do not count; reviewers have their own cap). At the cap, wait
  (background `vigil keepalive --orchestrator`) instead of launching.
- Wait on a run's process (`tail --pid=<pid> -f /dev/null`), not by grepping
  its log. Logs can quote old errors.
  Take the pid when you start the run (`$!`). Never wait with
  `while pgrep -f <pattern>` inside `bash -c`/`fish -c`: `pgrep -f` matches the
  waiting shell's own command line, so the loop never ends and spins on
  fork/exec (five such loops once held ~70% of an 8-core host for two days).
- Subagents (reviewers and implementers) may use vigil but never orchestrator
  mode, and never sleep loops (owner 2026-11-14). Implementers call
  `keepalive` (270 s, foreground) only while their own long test runs are going.
- Parallel implementers each get their own git worktree with disjoint file
  ownership, and every prompt names the worktree's absolute path. Forbid
  `git stash` in their prompts: the stash is shared by all worktrees of a
  repo, so one agent can pop another's work. Use a WIP commit instead.


## 10. Timing and low budget

**Is it taking too long?** Long waits are also a clock. Keep a
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

Wait in the background (owner 2026-11-13): `vigil keepalive <watch_id>
--orchestrator` with `run_in_background` and a timeout of at least
3,600,000 ms; it returns within 50 minutes, so start the next call on each
return. Never a foreground `keepalive` call (every user message interrupts
it). Keep one session hold (a bare one is fine) and add each delegated run to
it as an item rather than making a hold per run: `vigil hold add <hold> --for
pid:N|file:<report>|none --label <run> $(agentpace estimate-run --model M --kind K --vigil-meta)
--meta run=<taskId>` (the pid or report file
when the run has one, else `none`; `--vigil-meta` always supplies `--expect-s`, so a stalled run raises
`item overdue: <run>`). The same keepalive covers every item; each one that
ends raises `item ended: <run>: <why>` and the hold stays live while other items remain (the last item's event comes with the release). When a `none`
run's completion notification arrives, `vigil hold done <hold> <run>`. Another
watch firing does not touch the session hold, and it is never cancelled. When
it releases (its last item ended) or expires, make a new one in the same turn
while anything is in flight (2026-11-12: a polara-port session went ~1h35
without a hold this way).

When budget is low (either side):
- one-line status messages; no recaps;
- do not re-read large files; use `git diff --stat` and targeted ranges;
- delegate drafting (reports, prompts, boilerplate) to a subagent;
- while waiting on a long job, keep one background wait and restart it
  silently; check in every few waits, not every one.
