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
  installed copy under `~/.claude/skills` matches the commit. Pushing, and
  updating the published locks afterward, still needs the owner's go-ahead
  (`update-scout-module-locks`); say that the lock is stale until then. Do not
  stop at editing the source tree.
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
  Show every mock-up collapsed (owner, 2026-11-22): in the reply, a Markdown
  `<details>` block whose `<summary>` names the mock-up and version and holds a
  full-page PNG screenshot from `html_preview` (saved next to the HTML). That is the
  only form that expands fully on T3 mobile. When interaction matters, also
  `html_render` the page wrapped in its own `<details>` with the size script from
  build-loop `references/ui.md` (web resizes to fit; mobile does not yet,
  pingdotgg/t3code#40718). Every page for T3 keeps about 6rem of space at the bottom
  so the last card clears T3's mobile navigation.
- vigil notices are one-time announcements from the owner. Claude Code and
  Codex get them from a hook. In a harness without hooks (Antigravity / Neon),
  call the vigil MCP `notices` tool once at the start of a session.
- Clock times for the owner: Mountain time (America/Denver) first, then UTC
  in parentheses.
- Taildrop files to the owner's Pixel 9a personal profile (`pixel-9a`), never
  `google-pixel-9a-work`. The work profile does not have Taildrop enabled.
