---
name: iterating-with-nix
description: >-
  Use when iterating on Nix builds (nix build / nixos-rebuild while fixing
  failures, first build of a new host config), when changing another repo this
  flake consumes (local path: input loop), when testing an unpublished or
  unpushed repo as a flake input, or when adding an input for a repo with no
  remote yet.
---

# Iterating with Nix

When a build may fail in several independent places (a new host config, a
`buildEnv` bundling many packages, a large closure), pass `--keep-going`.

Without it, Nix stops at the first failed derivation. Each fix-and-rerun then
reveals only the next failure. With it, Nix builds everything that doesn't
depend on a failure, so:

- all independent failures show up in one pass, and
- more of the closure is already in the store when you rerun.

A single rebuild of a known-good config doesn't need it.

On small hosts, pair it with job limits so one pass doesn't OOM: check the
host's `nix.settings.max-jobs`/`cores` in `hosts/<host>.nix`, and pass
`--max-jobs`/`--cores` lower on the command line if a heavy derivation still
exhausts memory.

## Offloading to nixed

sonic is small (4 cores, 8GB RAM, 110GB disk). Push heavy work to nixed
(aarch64-linux, 8 cores, ~7GB RAM, larger disk):

- **x86_64 Nix builds:** nixed is a `nix.buildMachines` entry with qemu-user
  binfmt, so the daemon sends x86_64 derivations there automatically.
  Exception: pnpm/node native-addon builds (t3code) crash under qemu; those
  carry `preferLocalBuild = true` and stay on sonic.
- **Architecture-independent dev work** (e.g. a Rust crate's `cargo test`):
  run it natively on nixed as `mini` (sonic's `ssh nixed` logs in as mini).
  Sync the tree with its `.git`, but not build output, and keep cargo's
  build directory outside the tree:

  ```sh
  git add -A   # nix sees only tracked files in a git flake
  rsync -a --delete --exclude target ./ nixed:Documents/repos/<repo>/
  ssh nixed 'cd ~/Documents/repos/<repo> && env CARGO_TARGET_DIR=$HOME/.cache/<repo>-target nix develop -c cargo test'
  ```

  mini's login shell is fish, so use `env VAR=value` (not `VAR=value cmd`)
  and `$HOME` (not `~`) in ssh commands, or wrap them in `bash -c`.
  Without `.git`, the copy is a plain `path:` flake: every `nix develop`
  copies the whole directory into the store, build output included. With an
  in-tree `target/`, that once left 25 dead copies (66GB) on nixed. Root on
  nixed is only for the daemon's remote-builder connection; don't use it
  otherwise.
- Cross-compiling (`pkgsCross`) on nixed is also an option when a native
  build there doesn't fit.

## Autonomy

Small, recoverable problems while iterating (an OOM-killed build, job or
substitution limits, retrying a step with adjusted flags) don't need the
user's go-ahead: keep iterating on your own judgement and report what you
changed. Ask first before pushing (and which repo or branch to push to),
reverting a deliberately chosen version pin, or any destructive git
operation.

## Iterating on another repo you also control

To change a repo this flake consumes (nix-scout, t3code, a fork), point the
input at your local checkout instead of pushing every attempt. It avoids a
push and an API-backed relock per try, so iteration is faster.

1. Switch the input to `path:/absolute/path/to/checkout` in the root
   `flake.nix`, keeping any `follows`. `git add` new files in that checkout:
   `path:` only sees tracked (including staged) files.
2. `nix-scout update all` so the scout modules that declare the same input
   pick up the same URL and lock (it syncs module inputs from the host).
3. Build and test until you're confident.
4. Commit and push the other repo (ask first, see Autonomy).
5. Point the input back at its real ref: the existing branch, or a new branch
   pointer if you pushed one. Run `nix flake update <input>` for the new
   commit (often not needed if the branch didn't change), then
   `nix-scout update all` again.

`path:` inputs are for testing only; never commit them.

## Testing an unpublished or unpushed input once

Use `--override-input` for a one-off consumer build without editing
`flake.nix`:

1. Unless instructed otherwise, fully build the producer flake first.
   `nix flake check` alone is not enough.
2. Stage new files in the producer with `git add`. Already-tracked files may
   stay dirty; untracked files are invisible to the input until staged.
3. Pass `--impure --override-input <input-name> path:<absolute-path-to-producer>`
   to the consumer build. The input name and flake ref are separate arguments;
   use an absolute path.

```sh
nix build .#hostConfig --impure --override-input niri path:/absolute/path/to/niri
nixos-rebuild build --flake .#host --impure --override-input niri path:/absolute/path/to/niri
```

For a producer with no remote yet, seed its lock entry as below, then point
the consumer input at its intended future source and build with the override.
The placeholder is only for creating a valid lock entry.

Keep `--override-input` and `--impure` out of committed build scripts. After
the producer is pushed or published, drop the override and run
`nix flake update <input-name>` so the committed lock points at the real commit.

## Bootstrapping an input for a repo with no remote yet

`flake.lock` needs a locked node for every input before the input can point
anywhere real. To seed it for a new project:

1. Add the input under its final name, temporarily pointed at nixpkgs
   (e.g. `github:NixOS/nixpkgs/nixos-unstable`), and run
   `nix flake update <input>`.
2. Point it at `path:/absolute/path/to/new-repo` (with any `follows` it
   needs) and iterate as above.
3. Once it works, point it at the proposed upstream, typically
   `<the user's primary forge>:<their account>/<project name>`. Confirm the
   location with the user, and let them create the remote unless they
   explicitly ask you to. Then relock as in step 5 above.
