---
name: manual-keepalive
description: >-
  Backup only (vigil is the default hold): keep a session's turn open with a
  repeating background sleep+echo command when vigil is unavailable or
  failing, relaunched on each completion, instead of a bash while-loop. Use for TDD
  workflows, long-running commands, or subagent orchestration; keep
  relaunching until the work is complete. A near-constant effort: maintain it
  for as long as anything is in flight, and restart it after compaction.
---

# manual-keepalive

**vigil is the default hold, always.** Use the `vigil` skill for every wait,
including ones a watch cannot sense (subagents, a usage limit, a queue you
start yourself): hold a vigil watch anyway, because each keepalive also checks
usage limits and the operator's advisories. This manual tick is the BACKUP,
only for when vigil is unavailable or failing.

Use single-shot ticks so each completion gives the harness an observable
event. Run this in the background:

```
sleep 270 && echo keepalive
```

270 s is right for every case but one. If you are the orchestrator and know
that your prompt cache is 1 hour (the vigil envelope says `cache.ttl: "1h"`, or
your transcript shows a 1 hour cache write), use a 3300 s tick instead:

```
sleep 3300 && echo keepalive
```

and give that background command a timeout of at least 3,600,000 ms, or the
harness kills it before it ends. If the TTL is unknown or 5 minutes, or you are
a subagent, stay at 270 s.

Relaunch it after each completion while the work is still active. Do not use
a loop or a chain of sleeps in one command.

## A near-constant effort

Keepalive is not a one-off. Once started it runs, tick after tick, for as long
as any work is in flight: subagents (including ones paused on a usage
limit), background commands, waits on CI or a reset, and queued work you will
start yourself. Concretely:

- Relaunch every tick the moment it completes, without asking and without
  comment beyond at most "keepalive #<count>".
- Never end a turn while work is in flight unless a tick is live.
- After compaction, assume the chain died: restart it in the first turn.
- Keep exactly one chain; do not stack a second one.
- A completion notification is NOT a keepalive. Background commands, qex
  waits, `boat exec`, subagents and T3 delegates notify you when they END,
  which can be past the cache TTL (a 77-minute subagent, a qex job queued for
  memory). Keep a tick live while any of them runs or waits.
- After you cancel or consume a hold (a tick, a vigil watch), re-arm one in the
  same turn if anything is still in flight. Queued qex jobs count.

## Termination and Continuation

You may stop keepalive ONLY under these circumstances:

1. The user says so.
2. BOTH: *You, the agent* started the skill, and the work you started it for has been fully completed.

When the user or system requests this skill explicitly, it is for reasons that are opaque to you. Thus, patience here is greatly appreciated. If the harness lets you simply launch the command w/o user-facing acknowledgement, do so. Otherwise, "keepalive #<count>" suffices.

## Cursor harness

In the Cursor harness, run the tick in the foreground so its completion is
delivered as a blocking harness event (270 s; the 3300 s tick needs a
background timeout the foreground does not offer):

```
sleep 270 && echo keepalive
```

Relaunch it after completion while the work is still active. Do not
background Cursor ticks.

## Subagents

When launching subagents, start one keepalive in the same turn. If the
subagent finishes first, let that tick expire. Otherwise, relaunch it after
each completion until the full orchestration, including follow-up agents, is
complete. One keepalive chain covers all subagents in the orchestration.
