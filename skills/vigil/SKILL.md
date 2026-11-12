---
name: vigil
description: >-
  Wait on builds, logs, commands, ports, processes or URLs without polling by
  hand: create a vigil watch, then call keepalive until it fires. Hold the
  main session in prompt cache with `vigil hold`. Use when a task has to wait
  minutes to hours for something outside the session.
---

# vigil

`vigil` is an MCP server (`mcp__vigil__*`) and a CLI. A watch senses some
inputs every `interval_s` and fires on a rule. Nothing runs between calls:
ticks happen only inside `keepalive` (or `vigil wait`). State is in
`~/.local/state/vigil`, never in the repo.

## Loop

1. `watch_create` with inputs, `interval_s`, `deadline_s` and a fire rule.
2. `keepalive`. Read the envelope's `next`:
   - `"call keepalive again"`: nothing happened; call it again.
   - `"act on events"`: read `events` and `digest`, then act. The watch may
     still be live (see "Attention" below): check `status`.
   - `"watch ended; create a new watch if still needed"`: fired, expired or
     cancelled.
3. `watch_cancel` when you no longer need it.

`keepalive` with no `watch_id` covers watches this server process created.
Pass the id for watches from another session or from before a restart.

## Holds: stay in cache, even with nothing to watch

The main session holds itself in prompt cache with a vigil hold, always, even
when the only thing running is a subagent: every keepalive also returns
`advice` and checks usage limits. A hold is a watch on the work itself, so it ends when the
work ends, not on a short deadline like a dummy watch (it still ends when you
cancel it or after 7 days at most):

```sh
vigil hold --for qex:<job> --for pid:<pid> [--for file:<marker>] [--for until:<RFC3339>]
vigil hold --until-idle          # live until no qex job at or under this cwd runs
vigil hold                       # bare: live until cancelled (7 days at most)
```

Leave `--id` out: vigil returns a fresh `watch_id`, which you keep. (An id that
has ended or been cancelled stays reserved for seven days, so a replacement hold
needs a new one.) `qex:<job>` takes a job id, an id prefix or a unique name; the
hold stores the full id, and refuses a name that already names several jobs.
MCP: tool `hold` with `{for: ["qex:ID", "pid:N", ...], until_idle}`. Then
`keepalive` (no `watch_id` covers it with your other watches; it is already an
orchestrator watch, so the long window applies without a flag). While any work
is live the result is `pending` / "call keepalive again". When all of it has
ended you get one event, `hold released: <why>`, with `next: "act on events"`.

- Keep ONE hold for the session. Another watch firing does not touch it:
  act, then call `keepalive` again. Do not cancel it to "re-arm" it. When it
  releases (or expires at 7 days), make a new one before anything else.
- `--for file:<path>` ends when the path exists; `idle:<dir>` is `--until-idle`
  for another directory (a worktree outside your cwd). qex runs are in your cwd
  or below it only if you submitted them from there.
- A T3 delegate or a `boat exec` run cannot be sensed here: hold on the local
  `boat` pid, a marker file the work writes, or use a bare hold.
- A subagent passes its own `watch_id` to `keepalive`: a call with none also
  covers your hold and would take its long window.

## You never pick the tick length

Do not pass `max_s` / `--max-s`. vigil decides how long a call blocks.

- **Subagents and anything that is not the main session:** call `keepalive`
  with nothing extra. The call blocks 270 s.
- **The main (orchestrator) session only:** pass `orchestrator: true` on
  `keepalive` (CLI: `--orchestrator`; background wait: `vigil wait <id>
  --orchestrator`), or create the watch with `"orchestrator": true`. On a
  Claude session whose prompt cache is 1 hour, vigil then blocks up to 3300 s
  (55 minutes) per call, which costs about 11 times fewer model calls than
  270 s ticks. On a 5 minute or unknown cache it stays at 270 s. It decides
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
  the first call. For `vigil wait`, `clock` covers the whole wait.

## Attention: a job that looks stuck

Give a watch a budget and vigil wakes you early instead of at the deadline:

- `expect_s`: how long the job should take. When the watch has run
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
decide, then call `keepalive` again to keep the same watch, or `watch_cancel`.
`vigil wait` exits with code **5** for this (the watch is still live); 0 fired,
3 expired, 4 cancelled. An attention event the call did not manage to deliver
comes back, flagged `"redelivered": true`, with the same `event_id`; if the
watch fires, expires or is cancelled first, it comes back in front of the
final events, flagged the same way.

## Usage credits changed

An orchestrator call re-checks every 240 s whether the account started or
stopped using usage credits. When that changes, the call ends with one event of
`kind: "credit_state_changed"` (`on_credits`, `source`, `windows`, and `hook`
if the operator set `VIGIL_ON_CREDIT_CHANGE`, which vigil runs at least once
per change, so it must be safe to repeat). Read it, then call `keepalive` again;
the next call decides its window from the cache TTL the session now has.
`status` is still `pending`.

## Advisories: rules the operator set for you

Every blocking result (`keepalive`, `vigil wait`) carries an `advice` list when
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

## Going cold: the session is ending

vigil never wakes or revives a session. When you are told to end the session,
or your keepalive duty ends, do this before anything else: post ONE collapsed
BabelTele summary of the session in your final message, then stop calling vigil
(and cancel watches you will not need):

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

- Act on the envelope as usual, then keep calling `keepalive`. A tick that
  could not be saved is not saved, so the next call senses the change again.
  A quiet one (nothing to act on) makes the call wait one watch interval
  before it returns, so keep calling: that wait is the pacing.
- Free space (the state root is `~/.local/state/vigil`; the CLI names it on
  stderr). The next healthy call saves and rebuilds the reserve.
- Treat any event that follows an envelope with `persist.ok = false` as
  possibly repeated. The MCP server and `vigil wait` (the processes that failed
  to save) flag repeated events with `"redelivered": true`, and the same
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
vigil wait build                 # blocks until done; exit 0 fired, 3 expired, 4 cancelled, 5 attention (still live)
vigil wait build --orchestrator  # main session only: the long window and the credit checks
vigil keepalive build            # one call; add --orchestrator in the main session
vigil status build; vigil list; vigil cancel build
vigil advice [--json]            # the operator's current rules (see Advisories)
vigil hold [--id ID] [--for SPEC]... [--until-idle]   # see Holds
```

The CLI prints the envelope and then commits its delivery. If it cannot write
the envelope (stdout closed or full) it exits 1 and the next call returns the
undelivered events again, flagged `redelivered`.

## Client limits

- Claude Code moves a call longer than 2 min to a background task; the
  result still arrives, as a task notification. A 3300 s call (or a `vigil wait
  --orchestrator` run through Bash) needs a background timeout of at least
  3,600,000 ms; with the default 10 minute limit it is killed.
- Codex caps a tool call at 300 s by default, and keepalive returns by 270 s
  (vigil never exceeds 270 s when it sees Codex, or both Codex and Claude).
  Kasetto cannot set `tool_timeout_sec`; to raise it, add
  `tool_timeout_sec = 330` under `[mcp_servers.vigil]` in
  `~/.codex/config.toml` yourself.
