---
name: github-stars
description: If you need to know what the user recently starred on GitHub, use this instead of guessing or trying to browse GitHub.
agent-invocable: true
---

# GitHub Stars

There is no live GitHub API access from an agent session by default. Recent-stars
data already exists on-disk because `modules/github-stars.nix` runs a daily scan —
read that instead of fabricating repo names or trying to reach the network yourself.

## Where the data comes from

`modules/github-stars.nix` defines a systemd timer (`github-stars-scan`, daily at
09:30) that calls the GitHub REST API directly, per watched user:

```
https://api.github.com/users/$user/starred?sort=created&direction=desc&per_page=50
Accept: application/vnd.github.star+json   # needed to get starred_at timestamps
```

Watched users are configured via `v0id.githubStars.watchUsers` — currently set in
`hosts/void.nix`:

```nix
v0id.githubStars.watchUsers = [ "mikenrafter" ];
```

Optional `GITHUB_TOKEN` (via `githubTokenSecret`, sops) raises the rate limit from
60 to 5000 req/hr; without it unauthenticated calls still work for occasional scans.

## Where the results live

- `/var/lib/github-stars/tracker.json` — canonical state, one entry per starred repo:
  `starred_at`, `starred_by`, `description`, `html_url`, `language`, `stars`,
  `status` (`new` → `pending_direction` → `noted`/`implementing`/`done`/`skipped`),
  `discovered`, `direction`, `notes_file`.
- `/var/lib/github-stars/pending-notification.md` — human-readable digest of
  repos not yet covered.
- `/var/lib/hermes/.hermes/starred-repos-pending.md` — copy for Number One's 6pm
  review pickup.

Per-repo user notes, once given: `knowledge/starred-repos/notes/<owner>-<repo>.md`.

## Answering "what have I starred recently"

Query the tracker directly — it's already scanned, no network call needed:

```bash
# Everything starred in the last N days (e.g. 21 for "last 3 weeks")
jq --arg cutoff "$(date -u -d '21 days ago' +%Y-%m-%dT%H:%M:%SZ)" '
  .repos | to_entries
  | map(select(.value.starred_at >= $cutoff))
  | sort_by(.value.starred_at) | reverse
  | map({repo: .key, starred_at: .value.starred_at, desc: .value.description,
         lang: .value.language, url: .value.html_url})
' /var/lib/github-stars/tracker.json

# Filter further by keyword (e.g. nix-related) with jq's test()
jq --arg cutoff "..." '
  .repos | to_entries
  | map(select(.value.starred_at >= $cutoff))
  | map(select((.key + " " + .value.description) | test("nix|flake"; "i")))
' /var/lib/github-stars/tracker.json
```

If `/var/lib/github-stars/tracker.json` doesn't exist on the current machine (the
service is host-specific, `void`), say so — don't invent star data. A manual scan
can be triggered with `sudo systemctl start github-stars-scan` if the service is
enabled and reachable.

## Assessing whether a starred repo fits this repo

1. Look it up: `jq '.repos["owner/repo"]' /var/lib/github-stars/tracker.json`.
2. Fetch its README (`curl -sf https://raw.githubusercontent.com/owner/repo/HEAD/README.md`)
   to check it's a real, current project — don't trust the tracker description alone.
3. Judge "trivial to include" by what this repo actually supports: a flake input
   pinned in `flake.nix` + a `scout-modules/<name>/flake.nix` wrapper + a
   `modules/<name>.nix` NixOS module is the standard shape here (see any existing
   `scout-modules/*`). Anything needing new packaging, unpackaged deps, or a
   language toolchain not already vendored is not trivial.
4. Full lifecycle handling (recording direction, handoff to implementation) is
   covered by the Dax/Number One agent skills at
   `knowledge/agents/dax/skills/github-stars.md` and
   `knowledge/agents/number-one/skills/starred-repos.md` — use those for the
   scan/tracker-management workflow, this skill is for read-only lookups.
