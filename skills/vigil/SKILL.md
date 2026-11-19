---
name: vigil
description: >-
  Use when a task has to wait minutes to hours for a build, log, command,
  port, process, URL or other event outside the session.
---

# vigil

`vigil` is an MCP server (`mcp__vigil__*`) and a CLI. A watch senses some
inputs every `interval_s` and fires on a rule. Nothing runs between calls:
ticks happen only inside `keepalive`. State is in
`~/.local/state/vigil`, never in the repo.

**Subagents and delegated implementers may use vigil, but never orchestrator
mode** (`orchestrator: true` / `--orchestrator`; owner 2026-11-14). That mode
is only for the main session that talks with the user. (A Sonnet implementer
once sat 40 minutes in a 50-minute orchestrator keepalive, unable to see the
orchestrator's messages.)

## Loop

1. `watch_create` with inputs, `interval_s`, `deadline_s` and a fire rule.
2. Wait in the background (owner 2026-11-13): run `vigil keepalive <watch_id> --orchestrator` as a background shell command
   (timeout at least 3,600,000 ms). It returns
   within one window (at most 50 minutes), and its completion notification
   wakes you. Act, then start the next call. Never wait in the foreground:
   a foreground `keepalive` MCP call blocks the turn and every user message
   interrupts it. Only a main session whose harness cannot run background
   commands calls the `keepalive` MCP tool. The envelope's
   `next` says the same in both forms:
   - `"call keepalive again"`: nothing happened; wait again.
   - `"act on events"`: read `events` and `digest`, then act. The watch may
     still be live (see "Attention" below): check `status`.
   - `"watch ended; create a new watch if still needed"`: fired, expired or
     cancelled.
3. `watch_cancel` when you no longer need it.

`keepalive` with no `watch_id` covers watches this server process created.
Pass the id for watches from another session or from before a restart.

## Holds: stay in cache, even with nothing to watch

Keep one background session wait while work is in flight, including a bare
hold when nothing specific can be sensed. Every return carries advice and
keeps the prompt cache warm. Holds expire after 7 days at most.

The work goes into the hold as **items**. Each `--for` is one item, and
`vigil hold add` puts more into a live hold:

```sh
vigil hold                                   # bare session hold: live until cancelled (7 days at most)
vigil hold --for qex:<job> --label build --expect-s 1200
vigil hold --until-idle                      # one item: no qex job at or under this cwd runs
vigil hold add <hold> --for pid:<pid> --expect-s 900 --label <run>
vigil hold add <hold> --for file:<report> --expect-s 900 --label <run>
vigil hold add <hold> --for none --expect-s 900 --label <run>   # nothing to sense (a T3 delegate)
vigil hold done <hold> <run>                 # ends a `none` item
```

Item specs: `qex:<job>` (a job id, an id prefix or a unique name; the hold
stores the full id and refuses a name that names several jobs), `pid:<pid>`,
`file:<path>` (ends when the path exists), `until:<RFC3339>`, `idle:<dir>`
(no qex job at or under that directory runs; `--until-idle` is the form for your cwd, `idle:<dir>` the form for another directory, such as a worktree), and
`none`. A `none` item needs `--label`, and only `vigil hold done <hold> <label>`
ends it. A label names the item in every event; without `--label` it is the
spec as you wrote it. Labels are unique per hold. `--label` goes with one
`--for` only; `--expect-s` applies to every item it is given with.

Leave `--id` out: vigil returns a fresh `watch_id`, which you keep. (An id that
has ended or been cancelled stays reserved for seven days, so a replacement hold
needs a new one.) MCP: `hold {for: ["qex:ID", ...], label?, expect_s?,
until_idle?}`, `hold_add {watch_id, for, expect_s?, label?}`, `hold_done
{watch_id, label}`. The main session runs this in the background:

```sh
vigil keepalive --session --brief --orchestrator
```

`--session` covers all owned holds across CLI and MCP processes, discovers new
holds within five seconds, and skips delivered terminal results. Session identity
comes from the harness; without it, pass a hold id. Old holds without ownership
also need their id. MCP: `keepalive {session: true, brief: true}` plus the main
session's orchestrator flag. JSON remains the default; `--brief` prints actions,
notes, next step, cache pacing, and every advisory message in two lines.

Confirm each hold by id first, or create it with `--orchestrator true --confirm
TOKEN` after answering the challenge. A session wait never confirms holds. A new
unconfirmed hold makes an orchestrator session wait refuse; confirm it and
restart the wait. Subagents never use orchestrator mode.

What the keepalive returns:

- Autonomous `item ended` events wake the wait. Explicit `hold done` completions
  are durable `kind: "note"` events delivered with the next return, even when
  the last item releases the hold. They never interrupt its cache window.
- A sensed job can revive before more work is added. Adding work retires
  completed inputs; add a new item to watch a later retry.
- `item overdue: <label>` is a quiet note after
  `min(1.5 x expect_s, expect_s + 9 minutes)`. At twice `expect_s`,
  `item far overdue: <label>` wakes the wait once. A PID exit still wakes at
  the next sensing tick. These clocks start when each item is added.
- `hold released: <N> items ended (<labels>)` with `next: "act on events"`:
  every item has ended (each one's `item ended` comes with it). A hold that
  never had items does not release.

Rules for the main session:

- Keep one session hold. Add each delegated run (T3 delegate, background agent,
  build) to it as an item: `--for pid:N` or `--for file:<report>` when the run
  has one, else `--for none`. Always pass `--expect-s` set to its time
  estimate, so a stalled run raises overdue notes and then attention, and `--label <run>`. When a
  `none` run's completion notification arrives, `vigil hold done <hold> <run>`.
  A hold takes 16 live items; ended items free capacity. The most recently
  added 64 ended items stay in history. Undelivered events survive history
  pruning. Labels remain reserved while retained. `vigil status <hold>` lists
  live items and retained history. One session wait covers additional holds.
- An envelope with `cap_error` means the agent-cap file cannot be read, and
  `--cap` adds are refused: tell the owner, who fixes it with
  `vigil cap reset` (MCP has no cap setter).
- Another watch firing does not touch the session hold: act, then wait on it
  again. Never cancel the session hold to "re-arm" it. When it releases (its
  last item ended) or expires at 7 days, make a new one before anything else.
- `hold add` and `hold done` on a released, cancelled or expired hold fail with
  "has ended": make a new hold and add the item there.
- qex runs are in your cwd or below it only if you submitted them from there.
- A `boat exec` run cannot be sensed here: add the local `boat` pid, a marker
  file the work writes, or a `none` item.

## You never pick the tick length

Do not pass `max_s` / `--max-s`. vigil decides how long a call blocks.

- **Subagents and anything that is not the main session:** call `keepalive`
  with nothing extra, never orchestrator mode. The call blocks 270 s.
- **The main (orchestrator) session only:** pass `orchestrator: true` on
  `keepalive` (CLI: `vigil keepalive <id> --orchestrator`, run in the
  background), or create the watch with `"orchestrator": true`. The first
  such call on a watch returns a challenge instead of blocking: answer its
  question honestly. Only the main session repeats the call with the
  `--confirm` (MCP `confirm`) value the challenge gives; the watch then stays
  confirmed. Confirm a watch by naming its `watch_id`: a no-id orchestrator
  call requires every covered pending watch already confirmed and never
  confirms new ones. A subagent drops the orchestrator flag. On a
  Claude session whose prompt cache is 1 hour, vigil then blocks up to 3000 s
  (50 minutes, owner 2026-11-13) per call, which costs about 11 times fewer
  model calls than 270 s ticks. On a 5 minute or unknown cache it stays at 270 s. It decides
  again at every call, so a cache that shortens is noticed at the next call.
  Codex is always 270 s.

Every blocking result says what it chose and how long it has been:

- `cache`: `{ttl: "1h" | "5m" | "unknown", source, interval_s}`. `interval_s`
  is the window of this call. `credit_check` appears after an orchestrator's
  usage-credit check: `{at, source, on_credits}` (`on_credits: null` means no
  source could say). The check is made on every return of an orchestrator
  call that is due for one (about every 4 minutes), a fire included.
- `clock`: `{waited_s, watch_age_s, since_last_call_s, summary}`. `summary` is
  one line such as `waited 55m 0s this call; watching for 2h 10m; last call 55m
  ago`. Read it: a long window hides time, and `since_last_call_s` is `null` on
  the first call.

## Attention: a job that looks stuck

Give a watch a budget and vigil wakes you early instead of at the deadline:

- `expect_s`: how long the job should take. (On a hold it is per item, see
  Holds.) When the watch has run
  `min(1.5 x expect_s, expect_s + 9 minutes)` it raises one `attention` event
  (`reason: "overdue"`).
- `stall_s`: how long inputs may stay unchanged while a `process` input still
  runs. Then one `attention` event (`reason: "stalled"`). With neither field
  set, a long window (over 270 s) applies 900 s to file, glob and cmd changes
  of a watch that has a running `process` input, so a hung build is noticed
  within about 15 minutes.

Both are optional and need between 1 second and 7 days (604800). Each reason
fires once per watch. An
`attention` event is not the end: the envelope has `status: "pending"` and
`next: "act on events"`. Look at the job (read the log, check the process),
decide, then wait again to keep the same watch, or `watch_cancel`. An attention event the call did not manage to deliver
comes back, flagged `"redelivered": true`, with the same `event_id`; if the
watch fires, expires or is cancelled first, it comes back in front of the
final events, flagged the same way.

## Other calls in your session

A `foreign_orchestrator` event means another same-session call is using
orchestrator mode without confirmation for all its watches. Read its watch
ids, transport, pid and start time, identify the delegated agent, and stop
that agent with `TaskStop` or T3 `task_cancel`. Never kill the MCP pid: it is
the session's shared vigil server. After handling the event, follow `next`;
if it says the watch ended, create a replacement only if still needed.

`peers` lists other same-session waits as information. Each entry names the
watch, kind, `mode`, expected time, time waited and input summary. `plain`
means an ordinary wait; `orchestrator` means a confirmed call on watches this
call does not cover. Entries in `peers` do not end the call and do not alone
justify stopping an agent. There is no caller identity within a session, so a
subagent that explicitly confirms cannot be distinguished from the main
session's own other calls. Calls in the same MCP process are not listed.

## Usage credits changed

An orchestrator call re-checks every 240 s whether the account started or
stopped using usage credits. When that changes, the call ends with one event of
`kind: "credit_state_changed"` (`on_credits`, `source`, `windows`, and `hook`
if the operator set `VIGIL_ON_CREDIT_CHANGE`, which vigil runs at least once
per change, so it must be safe to repeat). Read it, then wait again;
the next call decides its window from the cache TTL the session now has.
`status` is still `pending`.

## Advisories: rules the operator set for you

Every blocking result (`keepalive`) carries an `advice` list when
advisories are on: `[{id, kind, message, checked_at, value?}]`. **Read it and
follow it.** The messages are the operator's current rules, computed from live
facts, for example `boat-budget`:

- Boat has more than the threshold of its hours left: prefer Boat for heavy
  work (builds, test runs, suites) through `edge.research/bin/boat-run`; run
  `qex` on this host only for one or two quick runs.
- Boat is at or below the threshold (default 10%): run heavy jobs through
  `qex` on this host instead.

`kind: "unavailable"` means the rule could not be evaluated; the message says
why (`advisory boat-budget unavailable: probe exited with 127: ...`). Do not
guess its value. Fall back to the default: prefer Boat, qex for quick runs.
`advice` is `[]` when no rule is configured and absent when advisories are off.

Look without waiting, from a script or hook: `vigil advice` (one
`id: message` line each) or `vigil advice --json`, and the MCP tool `advice`.
Answers are cached for the advisory's `cache_s` (default 600 s), so asking often
is cheap; a new answer needs no restart.

Change a rule at runtime (the owner may ask you to):

```sh
vigil advisory list                          # ids, params, condition
vigil advisory show boat-budget              # full spec and current evaluation
vigil advisory set boat-budget threshold=15  # Boat is "low" at 15% or less; applies at once
vigil advisory set boat-budget cache_s=60    # also: condition=, message_when_true=, message_when_false=
vigil advisory add ID '<json>' [--replace]   # a new rule; vigil advisory rm ID
```

MCP: `advisory_list`, `advisory_show {id}`, `advisory_set {id, settings:
{"threshold": 15}}`, `advisory_add {id, spec, replace?}`, `advisory_rm {id}`.
Unknown ids, unknown parameters and bad expressions are errors that say what is
wrong and change nothing. An advisory is `{probe, extract, params, condition,
message_when_true, message_when_false, cache_s}`: the probe (`cmd`/`url`/`file`)
runs, `extract` takes one number out of its output (`json` path, optional `of`
and `scale`, or `regex`), and `condition` (`pct <= threshold`) picks the
message; `{pct}` and `{threshold}` in a message print the number and the param.
Only add a probe you would run yourself: it is a command that reruns, cached, on
every later call until removed. The rules live in
`~/.config/vigil/advisories.toml` (re-read on every call; hand edits count).
Do not edit `boat-budget` unless the owner asked; a deleted default is not
brought back.

### Claude and Sol budget

Read each window separately. Claude has a 5-hour and a weekly limit; this
Codex plan currently has only a weekly limit. Use three advisories, each low
at 15% left or less:

- `claude-budget-5h`: wait for its reset or shift work to Sol for now.
- `claude-budget-weekly`: switch Claude's build-loop roles for the rest of the
  week, until the weekly reset.
- `codex-budget-weekly`: switch Sol's build-loop roles for the rest of the
  week, until the weekly reset.

`usage-budget-probe ClaudeCode --window 5h`, `usage-budget-probe ClaudeCode
--window weekly`, and `usage-budget-probe Codex --window weekly` report the
selected window's `pct_left`, `on_credits`, and `resets_at`. `windows` preserves
uw's window descriptor and duration. Without `--window`, the original keys
still describe the tightest window across the provider, so a combined reading
cannot tell you how long a role switch should last.

The owner or orchestrator adds these only when asked. Retire `claude-budget`
and `codex-budget` after adding the replacements to avoid contradictory role
advice. Probe argv accepts `--window` directly. Vigil message placeholders are
numeric, so name the window in the message and read reset timestamps from the
probe. Exit 3 means unavailable, including `no such window` when uw does not
report the requested duration. Treat unavailable as unknown and keep current
roles. A healthy 5-hour window never overrides a low weekly window; return to
default roles at a phase boundary only when every relevant window has recovered.
See build-loop's `references/budget.md`, B5.

## Going cold: the work is done

There is always a session to keep warm while work is in flight. The only cold
path is going from working or waiting to done. vigil never wakes or revives a
session, so when the work is done (or you are told to end the session), post
ONE collapsed BabelTele summary of the session inline in your final message and
end the turn. Call the MCP tool `cold` (or run `vigil cold ID...`) to cancel
your watches and holds; it replies with this instruction and the ids still
pending. Then stop calling vigil.
Never start a long cold wait instead: no background command that only waits for
something that may come much later, no sleeping until a result might arrive.

```
<details><summary>Session state (BabelTele)</summary>
task and its progress; work in flight (ids, paths, watch ids); tools in use
(MCP servers, CLIs such as vigil and qex); the user's standing rules for this
session; skills loaded
</details>
```

Use the `babeltele` skill to write it compactly.

## Fire rules

- `"change"`: any input changes from the baseline taken at create.
- `"condition"`: every input with a `want` meets it. Only `port`
  (`"open"`/`"closed"`) and `process` (`"exited"`/`"running"`) take `want`.
- `"judge"`: a Laya judge answers `judge_questions` and `judge_rule` decides.
  Needs `VIGIL_JUDGE_URL` and a reachable Laya (only on void).

```json
{"id": "build", "prompt": "Tell me when the build finishes or fails.",
 "inputs": [{"kind": "file", "path": "/tmp/build.log"},
            {"kind": "process", "pid": 4242, "want": "exited"}],
 "interval_s": 20, "deadline_s": 3600, "fire": "condition"}
```

Input kinds: `file`, `glob`, `cmd` (`argv`, `timeout_s` 0.1-19), `url`
(http only), `port`, `process`. Up to 16 inputs.

A glob input takes `pattern`, not `path`, and reports matches that appeared
since the last tick: `{"kind": "glob", "pattern": "/tmp/out/result*", "report": "created"}`.

A watch fires once. After a `change` (or `condition`, or `judge`) watch fires
it is finished: to keep watching, create a new watch with a fresh id. Ids of
finished watches cannot be reused until they are pruned (7 days).

## When the disk is full

vigil keeps its state on disk. If a write fails (usually a full disk), the
call still gives you the whole answer: `events`, `digest`, `status` and `next`
are the same as on a healthy disk. What changes is the `persist` field, which
a healthy call never has:

- `"persist": {"ok": false, "kind": "disk_full" | "io", "error": "...", "path": "..."}`:
  the result was NOT saved. `"redelivery": true` means events or a final status
  are at risk. `"first_error"` appears when a retry failed too.
- `"persist": {"ok": true, "used_reserve": true, "kind": "disk_full"}`: it was
  saved, but only by spending vigil's 256 KiB emergency reserve. The disk is
  full; free space soon.
- `"persist_failures": [{"watch_id", "kind", "error", "path"}]`: with several
  watches, other watches whose save failed in this call.

What to do:

- Act on the envelope as usual, then keep waiting. A tick that
  could not be saved is not saved, so the next call senses the change again.
  A quiet one (nothing to act on) makes the call wait one watch interval
  before it returns, so keep waiting: that wait is the pacing.
- Free space (the state root is `~/.local/state/vigil`; the CLI names it on
  stderr). The next healthy call saves and rebuilds the reserve.
- Treat any event that follows an envelope with `persist.ok = false` as
  possibly repeated. The MCP server (the process that failed to save) flags
  repeated events with `"redelivered": true`, and the same
  `event_id` can come back with different content, so do not deduplicate by
  `event_id`. A fresh CLI process (a new `vigil keepalive`) cannot know about the
  earlier failure, so its events are not flagged.
- `status` may lag: after a failed save `watch_status` can still say `pending`
  while `keepalive` answered `fired`. Trust the envelope.
- `watch_create` on a full disk fails with an error that names the state root
  and says `disk full`. Nothing is left behind, so retry with the same id once
  space is free.

What survives is best effort. `file` inputs redeliver what was appended since
the last saved tick, the newest `tail_bytes` of it (default 4096, never more
than 64 KiB; past 64 KiB the oldest bytes are skipped and the text says
`[truncated]`). `glob`, `cmd`, `url`, `port` and `process` report what they
see at the next tick (a glob its current matches), so a change that has
already reverted is not repeated. A watch that another process saved as expired or cancelled wins over
a redelivery. The reserve cannot help when the disk is out of inodes, a quota
is hit by a write bigger than 256 KiB, or the filesystem compresses zeros.

`VIGIL_TEST_FAULT` makes vigil's writes fail on purpose. It exists for vigil's
own tests and assumes a trusted environment: never set it, and be aware that
if it is inherited it disables writes (or, if malformed, stops vigil from
starting).

## Without MCP

```sh
echo '{...}' | vigil create      # prints the watch id
vigil keepalive build            # one call; add --orchestrator in the main session
vigil status build; vigil list; vigil cancel build
vigil advice [--json]            # the operator's current rules (see Advisories)
vigil hold [--id ID] [--for SPEC]... [--label L] [--expect-s N] [--until-idle]   # see Holds
vigil hold add ID --for SPEC [--label L] [--expect-s N]; vigil hold done ID LABEL
```

The CLI prints the envelope and then commits its delivery. If it cannot write
the envelope (stdout closed or full) it exits 1 and the next call returns the
undelivered events again, flagged `redelivered`.

## Client limits

- Claude Code moves a call longer than 2 min to a background task; the
  result still arrives, as a task notification. A 3000 s call (a background
  `vigil keepalive --orchestrator` run through Bash) needs a background timeout
  of at least 3,600,000 ms; with the default 10 minute limit it is killed.
- Codex caps a tool call at 300 s by default, and keepalive returns by 270 s
  (vigil never exceeds 270 s when it sees Codex, or both Codex and Claude).
  Kasetto cannot set `tool_timeout_sec`; to raise it, add
  `tool_timeout_sec = 330` under `[mcp_servers.vigil]` in
  `~/.codex/config.toml` yourself.

## Project reminders

For the owner's periodic technical reviews and comment audits, initialize the
current project once per session with adaptive-hardening's
`scripts/review-maintenance ensure --project ABS` (resolve the script relative
to that skill). It discovers new repositories as single-repository projects and
resolves configured multi-repository products to shared technical review history.
Each project gets `review-<key>` and `comment-audit-<key>` reminders with identical
scopes, split after 16 entries with matching `-2` and later ids. Rerun `ensure`
after scope or membership changes to refresh both kinds and retire obsolete
reminders. Grouping retires the former independent reminders too.
Use that skill's `group` command to associate additional repositories with a
product; do not infer membership from directory names.
Technical review reminders do not authorize paid work.

Comment audits deliver weekly on Saturday or Sunday, 09:00-21:00 in
America/Denver, the technical review reminder's timezone. Load `comment-audit`
and check headroom with `adaptive-hardening`. Audit files changed since the last
audit, or the whole repo once a month. Report only; edits need the owner. The
reminder authorizes at most lean work. It has no probe; each id's done state
suppresses its own weekly reminder.

Reminders deliver a project instruction only inside vigil calls you already
make. They never wake a session. Read `reminders` in keepalive/wait results and
`vigil advice --json` or MCP `advice`. Each due entry has an id and message;
`unavailable` means the check failed, so do not assume the reminder is due.
The list is absent outside the configured directory scopes, and empty within
scope when nothing is due. `reminders_error` reports an unreadable config file
whose scope cannot be established. Long main-session keepalives may return early with
`kind: "reminder_due"`, once per reminder per local day/week across sessions.
A reminder event leaves the watch live. Act on the message and follow `next`.

```sh
vigil remind list
vigil remind show ID          # spec plus current evaluation
vigil remind done ID          # suppress until the local day/week ends
vigil remind snooze ID 2h     # pause for an absolute duration, up to 7d
vigil remind rm ID
```

MCP: `remind_list`, `remind_show {id}`, `remind_add {id,spec}`,
`remind_done {id}`, `remind_snooze {id,duration}`, `remind_rm {id}`.
Configuration is `~/.config/vigil/reminders.toml` or the XDG config path,
re-read on calls. Suppression and cached probe output live under vigil's state
root. CLI scope follows the process cwd. MCP scope follows the server startup
cwd; roots and later client directory changes are not tracked. Use the CLI from
the project or restart the MCP server there.

An operator can install a scoped reminder. Use one timezone for its schedule
and probe:

```sh
reminder_tz=America/Denver
vigil remind add weekly-review \
  --scope /work/project --days wed,thu,fri --window 09:00-21:00 \
  --tz "$reminder_tz" --period week \
  --probe '["/work/project/bin/review-due"]' \
  --message 'A project review is due. {output}' --cache-s 21600 --timeout-s 19
```

Reminder delivery and the PreToolUse hook use the cache only. Cold/expired
results say unavailable while one spawned task refreshes eligible probes
concurrently within a single five-second deadline. Terminal watches and
outboxes are checked first. A short CLI may exit before refresh completes;
`vigil remind show ID` explicitly warms the cache. Failures last 60 seconds;
cache-only successful snapshots also have a 60-second minimum delivery lifetime.
The hook labels project reminders separately from operator advice.

`--window 09:00-18:00` optionally limits local delivery to that interval;
start is inclusive, end exclusive. Overnight windows are not supported in the
pilot. Omit `--tz` for host local time. Probe argv is JSON, with exit 0 due,
1 not due, other exits unavailable. Reserve exit 1 for a successful false
predicate, not a command error; it runs from the first scope. For a numeric
probe add `--condition 'value >= 100'`, optionally `--extract '<JSON>'` using
advisory extraction. `{output}` and `{value}` interpolate its result. Probes
have a timeout and cached results; add only commands you would run yourself.
