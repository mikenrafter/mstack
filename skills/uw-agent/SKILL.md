---
name: uw-agent
description: >-
  Use when your context is getting large, you are near a usage limit, or you
  want to continue a task later through usagewindow.
---

# uw-agent: compact yourself, resume yourself later

`uw-agent` wraps the `uw` command. It starts a private usagewindow daemon on
first use, with the T3 and Paseo credentials read from the host's secret files,
so you never handle a token. Use it instead of plain `uw` for anything that
changes state.

## Find your session id

```sh
uw-agent self           # active sessions, newest first, with titles
uw-agent self --id      # just the id, only if exactly one session is active
```

Check the title against your own task before using an id. If several sessions
are active and you cannot tell which is yours, ask the user.

## Compact

In T3 Code, compact yourself natively with TWO queued messages to your own
thread (T3 tool `t3_thread_send`, `mode: "queue"`, thread id in
`$T3CODE_THREAD_ID`), then end the turn:

1. `/compact next: <first step after the boundary>`. Text after the command
   steers the summary.
2. A resume message, e.g. `Resume: read <state file>, then <first step>`.

The compaction runs when your turn ends, but it does not start a new turn. Without
the second message the session stays idle until someone writes to it. Send
both, in that order, before ending the turn.

Outside T3 Code, ask usagewindow instead. Delivery waits for its next policy
pass, so expect a delay:

```sh
uw-agent compact ask <session-id> --reason "context at 80%, finishing the migration next"
uw-agent compact status <session-id>
```

Either way, do not claim the compaction happened until you see it: a
`/compact` record in your context, or a status message like
`compacted from X to Y tokens` (see the usagewindow-status skill).

usagewindow still compacts sessions that sit idle: at five sixths of the
cache TTL it reads from your transcript (50 minutes on a 1 hour cache), so a
long idle session is summarised before its cache expires.

## Resume later

```sh
uw-agent resume <session-id> --message "Continue the APK queue work; start with uw-agent status"
uw-agent resume <session-id> --at 2026-10-24T14:00:00Z --message "..."
uw-agent resume cancel <session-id>
```

Without `--at`, the resume is scheduled for when the provider's usage window
resets. `--at` takes an RFC 3339 UTC time. You see `will auto resume at <time>`
when it is scheduled, and `auto resume canceled` after a cancel. Put what you
need to remember in `--message`: the resumed session starts from that and the
compacted context.

## Check and troubleshoot

```sh
uw-agent status          # usage and daemon state (read-only, needs no daemon)
uw-agent doctor          # checks binaries, secret files, T3, competing service; starts nothing
uw-agent daemon-status
uw-agent daemon-stop     # stops the private daemon (scheduled resumes then wait)
```

If `doctor` prints a FAIL about hooks, do not use compact or resume: the daemon
only learns about your session from the hooks, and they are not yet pointed at
it. Tell the user it needs `v0id.usagewindow.hookDaemonUrl` set and the host
rebuilt.

Notes:

- The daemon keeps running after your shell exits. Scheduled resumes only fire
  while it runs, so do not stop it with resumes pending.
- It refuses to start while the system `usagewindow.service` is active, because
  two daemons would resume a session twice. Then use plain `uw`.
- It listens on 127.0.0.1:7879 only, with no web login.
- Reads (`status`, `sessions list`) work even with no daemon.
