---
name: readme
description: Write or revise a project README in the owner's house style (one-line opening, status stated plainly, a usage path someone can follow end to end, limits, credits, MIT license) and audit existing READMEs against it. Use when creating, rewriting or reviewing a README, before publishing a repository, or when the owner asks to bring READMEs into line. Loads writing-copy.
---

# readme

Load `writing-copy` first; its rules apply. This skill adds what is specific
to READMEs, from a scan of the owner's own READMEs (2026-11-18). Where
`unslop` and these rules disagree, these win for READMEs, and §4 says where.

## 1. Order

1. `# <repo name>`, then one sentence: what it is, in plain words. No
   rebuttal opening ("Most tools try to...").
2. Status, when it is not ready for use, as a blockquote: `> Early draft. Not
   ready for use.` Say what does not work yet.
3. Why it exists, in one to three short paragraphs for a person. Concrete:
   the problem, what it costs, what this does about it. First person is
   right when the repo states how the owner works (mstack, phoe-nix); tools
   may stay impersonal. When the name or core terms are unfamiliar, explain
   them here.
4. Install, then usage that an operator or an agent can follow end to end.
   Nix first, then the plain route ("Without Nix:"). Commands in fenced
   blocks; a trailing `# comment` says what a line does. Test that the
   commands run; where cheap, a test runs them.
5. Limits: what it does not do, what is unproven, what it depends on.
6. `## For agents and contributors`: build, test, layout, pointers to
   `docs/`. Reference material lives in `docs/`, not in the README.
7. Credits: whose ideas or code it builds on, with links.
8. `## License`: one line, `MIT; see LICENSE.` A `LICENSE` file must exist.
   Split licenses when data or assets differ, and say what the license does
   not cover.

Aim for under about 1,200 words. A README that needs more is carrying
reference material.

## 2. Form

- Sentence-case headings. No Title Case.
- No badges, no emojis. A store button is fine for a store listing.
- No em or en dashes, no `→` chains, no curly quotes.
- No bold-label lists (`**Term** — text`). Use a table for lookups (terms,
  commands, status, "if you need to... start with") and prose otherwise.
- Define each term on first use and reuse the same word after.
- Point to other files (`docs/`, `AGENTS.md`, `CHANGELOG.md`) instead of
  copying them.

## 3. Honesty

- State status and limits where a reader decides whether to use it, not at
  the bottom.
- Scope every claim: what the tests prove and what they do not; what was
  measured, on what, and when.
- Counts match lists ("three modes" lists three).
- No promises about the future except a dated plan.

## 4. Where this overrides unslop

- **Parentheses** around commands, flags, paths and values are allowed:
  "(`nix develop`)". Parentheses as a stand-in for a dash are not.
- **Negations that limit a claim** are allowed: "the tests check the
  parser, not the protocol". The ban on rebutting claims nobody made still
  applies.
- **The owner's own voice lines** stay ("Because innovation is desirable.").
  Do not cut a line only because it carries personality.

## 5. Auditing READMEs

For each README report: last commit date, word count, and gaps against §1 to
§4, each with a line reference and an effort (S, M, L). Check that `LICENSE`
exists when the README claims a license. Propose edits; apply them only when
the owner asks, one commit per repo, never pushed without approval.
