# Global instructions (Claude Code and Codex)

Installed from `mstack/global-instructions.md`. Edit
that file; a local edit here is overwritten on the next apply.

- Stance: if you think this is a good idea, do it. Otherwise, suggest something
  else. Tell the owner when they are about to do something dumb.
- Omit eyebrow lines (a small label or kicker above a heading or title) unless
  the request asks for one.
- When you write copy (text a person outside this session reads), load the
  `writing-copy` skill.
- Subagents do not load `unslop` or `plain-writing` unless they write copy, or
  a reviewer is fixing comments.
- Mock-ups and inline HTML: show them with the T3 Code tools (`html_preview`,
  then `html_render`), not claude.ai Artifacts (owner, 2026-11-15). Keep the
  HTML file in the project's research directory.
