---
name: writing-copy
description: >-
  Use when writing text a person outside this session reads, including docs,
  READMEs, UI strings, PR bodies, release notes, explainers and messages to
  the owner.
---

# Writing copy

Load `unslop` and `plain-writing` first, then apply these six rules.

1. **No eyebrow lines.** Omit the small label or kicker above a heading or
   title unless the request asks for one.
2. **Question every piece of text.** Name the question it answers and whether
   anyone is really asking it. People usually are not. Cut it if not.
3. **Keep jargon out of explainers.** One word per idea, defined once. Reuse
   that word; do not cycle synonyms.
4. **One named audience.** Know who reads it before you write, and write for
   that person.
5. **No compliance narration.** Do not explain how an action follows a rule
   or why it does not break one, unless the reader asked or the action really
   sits on the rule's boundary; then state the decision in one clause and stop.
   Never explain a distinction the reader set up or plainly knows. After a
   correction, report what changed; do not reassure in later messages. The
   test: what would the reader misread without this sentence? If nothing, cut
   it.
6. **Three passes before sending.** Reread the whole draft three times, each
   pass with one question: is every claim correct; does every sentence answer
   something the reader is asking; is any sentence about the writer rather
   than the reader's subject (self-justification, reassurance, credit, effort).
   Take the most care with that last kind: it is the easiest to miss in your
   own writing. Fix and reread after each pass.

Subagents load `unslop` and `plain-writing` only when they write copy, or when
a reviewer fixes comments (build-loop A7).
