---
name: publishing-scrub
description: >-
  Use before pushing to any public repository or fork the owner already
  publishes (mstack, vigil, agentpace fork, usagewindow, edge, …), before a
  publish branch or release, and when private names are found in something
  already public. Covers what to scrub, how, and what still needs the owner.
---

# Publishing and scrubbing (owner, 2026-11-21)

The owner said: scrub and publish "as to not have to ask me again generally".
Inside the limits below, act and report afterwards; do not ask.

## What counts as private

Run `publish-scan`; it is the list. It checks built-in patterns (this user's
home path, Boat sandbox ids `bx_…`, tailnet names `*.ts.net` and 100.64/10
addresses, `/tmp/claude-…` scratch paths) and the owner's denylist at
`~/.config/mstack/publish-denylist` (installed from phoe-nix, which is
private: edit it there, never copy its contents into a public repo).
Beyond the scanner, scrub by judgement: private repo and project names
(check `gh repo view <owner>/<name> --json visibility`), device names,
people's names from private work, private email addresses, tokens or keys.

Two tiers. **Generic** (the default): forks of other people's projects (the
agentpace fork) and anything meant for outside users get the full scrub.
**Toolbox**: the owner's own repos (mstack, vigil, usagewindow) name hosts and
home paths by design; there only secrets and denylist lines marked `!`
(private projects, people, private email) are scrubbed.

## How

1. Before every push to a public remote: `publish-scan [--tier toolbox] --base <remote>/<branch> <ref>`.
   It checks the tree at `<ref>` and every new commit (added lines, messages,
   author emails). Exit 0 is clean; any hit blocks the push until fixed.
2. Replace, don't delete meaning: hosts → `laptop`, `desktop`, `remote`;
   sandbox products → "remote sandbox"; private project → "project"; home
   paths → `~` or `/repo`. Keep examples realistic.
3. Code that matched a private name (a hard-coded host list, a project
   path) becomes configuration the user supplies (a file under
   `~/.config/<tool>/`, an env var), with the owner's values installed from
   phoe-nix. Add a test that the package has no built-in names.
4. Scrub the private source of truth too (e.g. agentpace `local/robust`),
   or the next publish brings the names back.
5. Already public: if the leaked names are not secrets, rewrite the history
   of the owner's own repo or fork **only** when nobody depends on it (no
   forks, stars, open PRs or other branches built on it: `gh api repos/<r>`
   for `forks_count`/`stargazers_count`, `git ls-remote`), with
   `--force-with-lease=<branch>:<old sha>`. Otherwise add a forward commit.
   Then bump every lock that pinned the old SHA (phoe-nix root and scout
   modules; `scout-module-locks`). Say in the report that GitHub keeps
   unreachable commits fetchable by SHA until it garbage-collects them.

## Still ask the owner first

- A **secret** (token, key, password, private email) is public: tell the
  owner at once, before or while scrubbing, since it needs rotation or
  GitHub support, not just a rewrite.
- Making a private repo public, creating a new public repo, publishing a
  package or release.
- Anything reaching other people's projects: issues, PRs, comments
  (`no-unsolicited-upstream`).
- A history rewrite on a repo others depend on.
