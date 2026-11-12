---
name: boat
description: >-
  Use Boat (boat.dev) cloud sandboxes from this machine: what Boat is, how to
  reach a sandbox (only through the `boat` CLI), run long jobs, copy files and
  source, and the gotchas seen here. Use whenever a task mentions Boat, a
  sandbox id (`bx_...`), "Box"/ascii, a remote x86_64 build or test host, or
  when local RAM/CPU or architecture (aarch64) is not enough.
---

# Boat

Boat (boat.dev) rents full Linux VMs ("sandboxes"): x86_64 Ubuntu, user
`user`, home `/home/user`, passwordless `sudo`, Docker and common toolchains,
billed per second while running. Older docs and third-party skills call it
**Box** (`box` CLI, `box.ascii.dev`, `on.ascii.dev`): same product, stale
names. Use `boat`. Inside a sandbox, agents get Boat's own `boat` skill; this
one is for driving sandboxes from here.

## Access

- The CLI is `boat` (on `PATH`; `~/.ascii/bin/boat`) and is already signed in:
  `boat status`. Never run `boat login`, `boat onboard` or an install script;
  if it says signed out, ask the user.
- A sandbox is reachable **only through the CLI** (`exec`, `ssh`, `scp`,
  `forward`). It is not on Tailscale and has no entry in `~/.ssh/config`.
- Always pass the explicit `bx_...` id. `current` and `self` do not work from
  a non-interactive shell here.
- Which sandbox: read `<project>.research/boat.md` (id, purpose, size, what
  secrets it holds). Update it when you create, trim or retire one.

## Commands

| Need | Command |
|---|---|
| State, size, TTL | `boat info <id>` (JSON; fields under `.sandbox`), `boat list` |
| Start / stop | `boat resume <id>`, `boat stop <id>` |
| Short command | `boat exec <id> --timeout 120 -- bash -lc '<cmd>'` (default timeout 30 s) |
| Long job | `boat exec <id> --detach -- bash -lc '<cmd> > ~/job.log 2>&1'` → prints `pid` |
| Wait for it | `boat exec <id> --attach <pid>` as a background Bash command (the harness notifies you); `--status <pid>`, `--kill <pid>` |
| Files | `boat scp ./f <id>:/home/user/f`, `boat scp <id>:/home/user/f ./f` |
| Source | `git bundle create x.bundle <branch>`, `scp` it, `git clone x.bundle` inside: no Git credentials enter the sandbox |
| Plan and hours | `boat limits`, `boat usage <id>`; never quote prices from memory |

`exec` prints one JSON line (`stdout`, `stderr`, exit code). Parse it, for
example `| python3 -c 'import json,sys; d=json.loads(sys.stdin.readline()); print(d["stdout"])'`.

## Gotchas seen here

- **Nix socket after resume.** The first Nix call after `resume` fails with
  "Permission denied" on the daemon socket. A plain restart can leave the
  socket at mode 0644, and a `chmod 666` alone later gives "Connection refused"
  once a detached job starts. What works (one `exec`): `sudo systemctl stop
  nix-daemon.service nix-daemon.socket; sudo rm -f
  /nix/var/nix/daemon-socket/socket; sudo systemctl start nix-daemon.socket
  nix-daemon.service; sleep 3; sudo chmod 666
  /nix/var/nix/daemon-socket/socket; nix store ping`. Then run detached jobs
  under `setpriv` (below). Source
  `/nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh` in each `exec`.
- **Capabilities.** `exec` processes carry ambient capabilities that break
  FHS/bubblewrap tools. Wrap detached runs:
  `--detach -- setpriv --ambient-caps -all --inh-caps -all bash -lc '...'`.
- **Nothing survives a stop** except the disk: relaunch services after
  `resume`. The IP changes on each resume.
- **Size.** Boat counts allocated disk; a sandbox past the default limit needs
  `--type large` to resume (2× cost). Trim or `nix-store --gc` instead of
  upsizing, and ask before choosing a paid size.
- **Memory.** Sandboxes have their own RAM (the qex queue is for this host),
  but default size is ~8 GB: one Gradle or emulator job at a time.

## Rules

- **Secrets stay put.** Never copy keys, tokens or signing keystores into a
  sandbox, and never print them, unless the user said so for that sandbox.
  `holdsCreatorLogins` in `info` shows whether account logins are on it; a
  sandbox made with `--no-env` has none.
- **Costs.** Stop a sandbox when the work is done. Create one only when the
  task needs it; never delete one unless the user asks.
- **Docs.** `https://docs.boat.dev/llms.txt` lists every page; fetch any page
  as `.md`. `boat <command> --help` is authoritative for flags.
