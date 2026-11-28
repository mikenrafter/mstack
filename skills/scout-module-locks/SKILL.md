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
GitHub. Do not infer push approval from approval to edit files alone. An owner
request to install, update or apply the change is that confirmation (owner,
2026-11-26): it covers `publish-scan`, the push, the lock update, and committing
and pushing the updated lock files, with no second ask.

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

4. Review the lockfile diff. Other `flake.lock` changes already in the phoe-nix
   working tree go in too (owner, 2026-11-28): stage and push them with yours,
   and list each one under an "Addenda:" heading in the commit body, one line
   per input: file, input, old and new revs (first 8 characters). Do not leave
   lock changes behind, and do not ask about them. The one exception is a
   change that moves an input to a different owner, repository or branch: that
   is a retarget, so stop and ask as in step 2. Files that are not tracked lock
   files (an untracked module, even one holding a `flake.lock`, or an edited
   `.nix`) stay out unless the owner says otherwise; name them in your report. Commit and push phoe-nix (after
   `publish-scan` if it is public) when the owner asked to install or update;
   otherwise wait until they ask.

Do not update a lock from an unpublished local branch, silently retarget a flake
input, or run a broad lock update when named inputs and modules are sufficient.
