---
name: low-ram-hosts
description: Use on sonic and nixed (both have only ~8GB RAM) before running tests, builds, emulators, or anything memory-hungry (flutter test, cargo, gradle, pnpm/node, nix build), and when a command dies with "Killed" / exit 137. Heavy work goes to Boat via boat-run; local jobs (one or two quick runs, or when the boat-budget advisory says Boat is low) go through the shared qex queue so agents don't collide.
---

# Running on RAM-constrained hosts (sonic and nixed)

**Both sonic and nixed need this.** Neither is a big machine:

| Host | RAM | Swap |
|------|-----|------|
| sonic (CF-19, x86_64) | 8GB | zram + disk swap partition |
| nixed (M1, aarch64) | ~7.4GB | zram (3.7GB) + 8GB swapfile |

void has plenty of memory; this skill is not for it.

Agents here (t3, Claude Code, Codex sessions) share the same memory as
whatever test or build they launch. One runaway test can use 6GB on its own,
and the machine then swaps hard or the kernel OOM killer fires.

## Why it matters

The kernel kills the biggest process, which is usually the runaway test, not
the agents. On nixed, `flutter_tester` (~6GB) was killed three times on
2026-10-18. Before `OOMPolicy=continue` was set on `t3.service`, systemd then
stopped the whole unit and every agent session in it died too. That setting
is now in `scout-modules/t3`, but the box is still thrashing the whole time
before the kill. Keep tests small and capped so it never comes to that.

## Heavy work goes to Boat first

**Prefer Boat (cloud sandboxes) for all heavy work**: test runs beyond one or
two files, suites, builds, APKs, long benchmarks. Use
`edge.research/bin/boat-run [--shell PREFIX] <worktree> -- <command>`: it syncs
the worktree, fixes the Nix socket, runs detached and returns the exit code and
the log (see the `boat` skill). Queuing heavy runs in qex on these 8GB hosts
cost 20 to 120 minutes of waiting on 2026-11-11, and Boat has no memory
problem. Briefs to subagents name `boat-run`, not a local runner.
Boat spends plan hours: use the boat skill's "Spend" table (cheap by default: `default`
size for test iterations, sandbox stops itself between batches; `large` and keep-up only under an
owner deadline).

Use qex on this host only:

- for one or two quick runs (a single test file, a small build), or
- when the `boat-budget` vigil advisory says Boat is low: Boat's remaining
  hours are at or below the threshold (default 10%). Read it with `vigil advice`
  (it is also in every `keepalive` result's `advice`). The threshold is
  `vigil advisory set boat-budget threshold=<percent>`. If the advice says it
  is unavailable, prefer Boat and check `boat limits` yourself.

## Queue the local jobs through qex

Whatever stays local (see above) goes through the queue. Agents can't see what
other agents are about to start. On 2026-11-10 two
sessions' Rust and Gradle builds plus a test run caused 8 OOM kills in 25
minutes on nixed. `qex` is the shared queue: a job claims cores and memory,
and qex starts it only when the claim fits the budget (75% of the machine,
less what other users hold). Load the `qex` skill, or run `qex help agents`.

```sh
qex list                 # who holds what now, and why anything waits
qex info                 # the budget and the load
qex submit --wait --cpu 2 --mem 3GB --id-file /tmp/<you>.id -- <command>
```

- Run `qex submit --wait` as a background command of your harness; the harness
  reports the end. Reattach with `qex status $(cat <id-file>) --wait`. No
  pgrep or sleep loops.
- Claim what the job really uses. Starting points on these hosts: `flutter
  test` 2GB, Gradle/APK build 3GB, `cargo build -j2` 2GB, `nix build` 2GB.
  qex learns from each run of the same command.
- A claim is a promise, not a limit. Put the scope cap below inside the job:
  `qex submit --wait --mem 3GB -- systemd-run --user --scope -q -p MemoryMax=4G -- <command>`.
- Never skip the queue because it is slow. A waiting job is cheaper than an
  OOM kill of someone else's work.
- But a job that has waited for memory for more than ~20 minutes should move
  to Boat instead (cancel it with `qex cancel <id>`). A queued job is still
  in flight: keep the keepalive tick live while it waits.

## Before starting heavy work

```sh
qex list                                  # jobs queued and running, by whom
free -h                                   # available, and swap in use
systemctl list-units --type=service | grep -E 't3|claude'   # what else is running
```

- If available memory is under ~3GB, or swap is mostly full, wait or stop
  something first.
- Check disk too: `df -h / /tmp`, and give a heavy job a disk claim:
  `qex submit --wait --cpu 2 --mem 3GB --disk 4GB -- cargo build`. The claim is
  a promise, not a limit. qex waits (`waits for disk` in `qex list`) when the
  free space of that filesystem, less 1GB in reserve and the claims of the jobs
  that run, is under the claim; `qex info` shows the free space. A job with no
  `--disk` is not held by it, and nixed's / reached 82 MB free twice on
  2026-11-12 before the claim existed. Under ~10 GB free, free space first:
  `qex submit --wait --disk 0 --lock nix-gc -- nix-store --gc` (`--disk 0` says
  that the job frees space, so no disk floor holds it), and clear your own
  /tmp files.
- If `qex submit --wait` or `qex run` exits **101**, the disk is full and the job
  did not run: it waited 60 s for space that something outside the queue holds,
  and qex cancelled it. stderr says the filesystem, the free space and how much to
  free. Free it (the `nix-store --gc` job above, `du -xsh` on the usual places,
  your own /tmp files), then submit the job again, or give a smaller `--disk`.
  `--disk-wait-limit 5m` waits longer.
- Run one heavy job at a time. Don't start a second test run while the first
  is going.

## Cap every heavy command in its own scope

Wrap test runs and builds in a memory-limited user scope. The limit applies to
that command alone, so if it blows the cap, only it is killed. Your agent
session and t3 keep running.

```sh
systemd-run --user --scope -q \
  -p MemoryHigh=3G -p MemoryMax=4G -p MemorySwapMax=2G \
  -- <command>
```

- `MemoryHigh` throttles the command before it hits the hard limit.
- `MemoryMax` is the hard limit: the command gets OOM-killed inside the scope.
- `MemorySwapMax` stops one process from filling the swap and slowing
  everything else.

Tested on both hosts (cgroup v2, user scopes enforce `memory.max`). On nixed
this works as `mini`; from sonic use `ssh nixed` (see `iterating-with-nix`
for the quoting rules: mini's shell is fish).

Inside a t3 session (agents run under `t3.service`) there is no user D-Bus,
so `systemd-run --user` fails with "Failed to connect to user scope bus". Use
`choom -n 900 -- nice -n 10 <command>` there instead: no cap, but the kernel
kills that job first, never an agent.

Scale the numbers to the host: 4G max is right for one job on either box.
Don't raise it to make a test pass; reduce the test's footprint instead.

## Reduce the footprint too

Lower parallelism, since each worker has its own memory:

| Tool | Setting |
|------|---------|
| `flutter test` | `--concurrency=1` |
| `cargo` | `-j2`, `CARGO_BUILD_JOBS=2` |
| `jest` / `vitest` | `--maxWorkers=2` |
| node | `NODE_OPTIONS=--max-old-space-size=2048` |
| `nix build` | `--max-jobs 1 --cores 2` (host defaults are already 2) |

Run a single test file or package before the whole suite.

## When something is killed

- `Killed`, exit code 137, or a test runner vanishing with no assertion output
  is an OOM kill, not a test failure. Don't report it as one and don't "fix"
  the test.
- Confirm: `journalctl -k --since "-1h" | grep -i "out of memory"`. The line
  names the victim and its size.
- Retry once with lower parallelism and a scope cap. If it still doesn't fit,
  move it: x86_64 builds go to nixed automatically, and architecture-neutral
  test runs can use whichever of sonic/nixed is idle (see `iterating-with-nix`).
- Never kill or restart `t3.service` to free memory. It holds every agent
  session.
