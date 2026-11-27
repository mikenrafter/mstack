# Global instructions (Claude Code and Codex)

Installed from `mstack/global-instructions.md`. Edit
that file; a local edit here is overwritten on the next apply.

- Stance: if you think this is a good idea, do it. Otherwise, suggest something
  else. Tell the owner when they are about to do something dumb.
- Never open issues, forks, PRs, posts or other upstream outreach without the owner's explicit approval; see the no-unsolicited-upstream skill for edge cases.
- Before pushing to a public repo or fork, run `publish-scan` and scrub what it finds; the
  publishing-scrub skill says what to fix without asking and what still needs the owner.
- Ethos: agents and people do best when a deterministic core (a measurement,
  ledger, index or check) shows them the state of things and inference
  handles only the edge. Watch for guesses a program could replace, and for
  problems big enough to found a company on; raise those at a break as one
  visual card (`legible-cores` skill).
- When the owner asks any agent to update mstack, phoe-nix or a skill, do it
  globally and finish the job (owner, 2026-11-21): edit in mstack, commit there,
  then install through nix-scout: build `agent-integration` with
  `--override-input mstack path:/home/mini/Documents/repos/mstack`, then
  `nix-scout switch agent-integration` with the same override. Check the
  installed copy under `~/.claude/skills` matches the commit. "Install" (or
  "update", "apply") includes publishing (owner, 2026-11-26): run `publish-scan`
  and scrub, push mstack, then update the published scout locks
  (`update-scout-module-locks`) without a separate go-ahead. Only when the owner
  asked for an edit without asking to install does the push wait for a go-ahead;
  then say the lock is stale. Do not stop at editing the source tree.
- Skills live in mstack (`mstack/skills/`). Create and edit them there, never
  in an installed skill directory. Only a skill that must change in step with
  a tool lives in that tool's repository (mstack README, "Writing a skill").
- Omit eyebrow lines (a small label or kicker above a heading or title) unless
  the request asks for one.
- When you write copy (text a person outside this session reads), load the
  `writing-copy` skill.
- Subagents do not load `unslop` or `plain-writing` unless they write copy, or
  a reviewer is fixing comments.
- Show the journey, not just the result: keep a per-feature journey file
  (mock-up versions, pilots, owner decisions, dead ends and why) and tell
  that story in every PR body, with mock-ups as PNG/GIF (`pr-stacks` §4a).
  Reworking commits for legibility is fine.
- UI work inherits before it builds: a brief for any screen names the signed-off
  mock-up, the original screen and every prior pilot or landed feature it reuses,
  by path or SHA, and the build is compared to the mock-up in screenshot pairs
  before the owner sees it (build-loop `references/ui.md`, `ui-brief-check`).
- The orchestrator owns every mock-up: it writes and revises them itself and never
  delegates one to an implementer or reviewer (owner, 2026-11-21).
  Neon reads each version for legibility at the same time the owner sees it, never
  as a gate before it (owner, 2026-11-26; build-loop `references/ui.md`).
- Mock-ups and inline HTML: show them with the T3 Code tools (`html_preview`,
  then `html_render`), not claude.ai Artifacts (owner, 2026-11-15). Keep the
  HTML file in the project's research directory.
  Show every visual in a pair, both collapsed (owner, 2026-11-27; mock-ups,
  rendered docs, diagrams, any page): (1) `html_render` the page inline, wrapped in
  its own `<details>` with the size script from build-loop `references/ui.md`; and
  (2) in the reply, a Markdown `<details>` whose `<summary>` names it and its
  version, holding the full-page PNG from `html_preview` (saved next to the HTML)
  and a link to the HTML file by absolute path. Never only one of the two: the
  owner's app cannot reach a file without the inline render or a link, and only
  the PNG expands fully on T3 mobile (pingdotgg/t3code#40718). `html_render` is the
  inline tool; the `preview_*` browser tools are not a substitute. Every page for T3
  keeps about 6rem of space at the bottom so the last card clears T3's mobile
  navigation.
- Going cold always means compacting (owner, 2026-11-27, after it was skipped more than once): cancel
  the holds (vigil `cold`), queue ONE `/compact` to your own thread carrying a BabelTele summary of the
  session (vigil skill, "Going cold"), then end the turn. A final message alone, however complete, is
  not going cold. This holds even when a tool's own `next` text says only to post a summary.
- vigil notices are one-time announcements from the owner. Claude Code and
  Codex get them from a hook. In a harness without hooks (Antigravity / Neon),
  call the vigil MCP `notices` tool once at the start of a session.
- In a delegated or child thread (T3 `delegate_task`, a subagent), the messages you
  receive come from the orchestrator agent unless they say otherwise; the owner does not
  read that thread. Answer in plain chat text, never with `send_to_user` or another
  owner-facing tool. When you message a delegate, open with
  `[from: orchestrator (<model>, thread <id>) · to: <role> · not the owner]` (owner, 2026-11-26).
- Clock times for the owner: Mountain time (America/Denver) first, then UTC
  in parentheses.
- Taildrop files to the owner's Pixel 9a personal profile (`pixel-9a`), never
  `google-pixel-9a-work`. The work profile does not have Taildrop enabled.
