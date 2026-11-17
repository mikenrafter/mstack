---
name: nix-test-rebuild-override
description: If you need to test an unpublished or unpushed repo as a flake input, use this.
agent-invocable: true
---

# Nix Test Rebuild Override

Two paths depending on whether the producer flake (the thing you're testing changes to) has been pushed to its remote yet.

## Unpushed Updates

Testing unpushed updates is easier since you don't have to do an extra step for a flake lock hash.

1. Ensure the producer flake **fully builds** fine. Not `nix flake check`, but builds! Unless otherwise instructed.
2. `git add` any new/untracked files in the producer repo — `path:` flake refs only see git-tracked (including staged-but-uncommitted) files; a dirty working tree of already-tracked files is fine, but untracked new files are invisible until staged.
3. Use `--impure --override-input <input-name> path:<absolute-path-to-producer>` in your build command for the consumer flake. Both parts of `--override-input` are separate args (input name, then the flake ref) — use the **absolute** path, not relative.

```bash
nix build .#hostConfig --impure --override-input niri path:/home/v0id/Documents/repos/niri
# or, for a NixOS/home-manager rebuild:
nixos-rebuild build --flake .#host --impure --override-input niri path:/home/v0id/Documents/repos/niri
```

## Unpublished Updates

Testing unpublished updates is harder, since there is no correct remote to point at yet.

1. Ensure the producer flake **fully builds** fine. Not `nix flake check`, but builds! Unless otherwise instructed.
2. Point the consumer's flake input at `github:nixpkgs/unstable` and `nix flake lock --update <name-of-producer-input>` — this is a throwaway placeholder just to get a valid lock entry, not the real dependency.
3. Re-point the consumer's flake input to its true future source (typically `<user's git platform>:<user's handle>/<name of project>`, unless otherwise specified — e.g. `github:mikenrafter/safethrottle`).
4. Use `--impure --override-input <input-name> path:<absolute-path-to-producer>` in your build command for the consumer flake, same as above.

## Cleanup

`--override-input` and `--impure` are for local testing only — don't leave them in committed build scripts. Once the producer is actually pushed/published, drop the override and run a real `nix flake lock --update <input-name>` (or let CI do it) so the committed `flake.lock` points at the real commit.
