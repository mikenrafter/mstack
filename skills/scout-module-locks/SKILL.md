---
name: update-scout-module-locks
description: >-
  Use after pushing a change to a repo that a phoe-nix scout module pins,
  before rebuilding. Update the scout-module flake locks with fork/branch
  verification and an explicit push confirmation.
---

# Update scout-module locks

Use this skill when a change in a satellite repository needs to be reflected in a
phoe-nix scout module's `flake.lock` files.

Before any push, show the user the change and ask for confirmation to push it to
GitHub. Do not infer push approval from approval to edit files or update locks.

After the user confirms:

1. Commit the satellite repository change with a scoped message, then push the
   intended branch to GitHub.
2. Inspect every relevant `flake.nix` in phoe-nix, including the top-level
   `flake.nix` and affected `scout-modules/*/flake.nix` files. Confirm that each
   usage points to the intended fork, repository, and branch. If any reference is
   wrong or ambiguous, stop and ask before updating locks.
3. From the phoe-nix checkout, update the satellite input and all affected scout
   modules. For example, when updating usagewindow and agent-integration:

   ```sh
   cd ~/Documents/repos/phoe-nix
   nix flake update usagewindow
   nix scout update usagewindow agent-integration
   git add scout-modules/*/flake.lock
   ```

4. Review the staged lockfile diff. Stage only the affected scout-module lock
   files, verify that no unrelated files changed, and report the exact lockfiles
   updated. Do not commit or push phoe-nix unless the user separately asks for
   that.

Do not update a lock from an unpublished local branch, silently retarget a flake
input, or run a broad lock update when named inputs and modules are sufficient.
