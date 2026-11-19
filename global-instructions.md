# Global instructions (Claude Code and Codex)

Installed from `mstack/global-instructions.md`. Edit
that file; a local edit here is overwritten on the next apply.

- Stance: if you think this is a good idea, do it. Otherwise, suggest something
  else. Tell the owner when they are about to do something dumb.
- Never open issues, forks, PRs, posts or other upstream outreach without the owner's explicit approval; see the no-unsolicited-upstream skill for edge cases.
- Skills live in mstack (`mstack/skills/`). Create and edit them there, never
  in an installed skill directory. Only a skill that must change in step with
  a tool lives in that tool's repository (mstack README, "Writing a skill").
- Omit eyebrow lines (a small label or kicker above a heading or title) unless
  the request asks for one.
- When you write copy (text a person outside this session reads), load the
  `writing-copy` skill.
- Subagents do not load `unslop` or `plain-writing` unless they write copy, or
  a reviewer is fixing comments.
- Show the journey, not just the result: never squash or polish away
  history; keep a per-feature journey file (mock-up versions, pilots, owner
  decisions, dead ends and why) and tell that story in every PR body
  (`pr-stacks` §4a).
- UI work inherits before it builds: a brief for any screen names the signed-off
  mock-up, the original screen and every prior pilot or landed feature it reuses,
  by path or SHA, and the build is compared to the mock-up in screenshot pairs
  before the owner sees it (build-loop `references/ui.md`, `ui-brief-check`).
- Mock-ups and inline HTML: show them with the T3 Code tools (`html_preview`,
  then `html_render`), not claude.ai Artifacts (owner, 2026-11-15). Keep the
  HTML file in the project's research directory.
- Taildrop files to the owner's Pixel 9a personal profile (`pixel-9a`), never
  `google-pixel-9a-work`. The work profile does not have Taildrop enabled.
