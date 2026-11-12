# Research brief — agentic practice, moldable tools, review, craft (2026-11)

Shared conventions for every agent writing into this directory. Read this
whole file before starting.

## The user and their setup

- Runs a NixOS flake (`/home/mini/Documents/repos/phoe-nix`) across three
  hosts. Read `AGENTS.md` at the repo root first.
- Their agent practice is encoded as skills in
  `scout-modules/agent-integration/skills/` (build-loop, question-everything,
  technical-excellence, test-quality, rg-implement, manual-keepalive, vigil,
  tea, plain-writing, unslop, uw-agent, ...). Most came from well-known
  practitioners; the point of this research is to find **where the user
  differs from the popular approaches, and what evidence each side has**.
- Main projects to keep in mind: `diff-core` (code review tool, mid-rewrite,
  newer draft only on an offline host), `residual-cli`, T3 Code (TypeScript),
  Rust scout modules (vigil, tea, apk-builder).
- The analysis ran on nixed, not sonic (an earlier version of this brief said
  sonic). The void host is offline; its transcripts and newest diff-core/residual work
  are missing. Say so where it limits a conclusion.

## Writing rules

- Plain, direct prose. No throat-clearing, no hype, no "delve", no "it's not
  X, it's Y" constructions. Define jargon once. Address the reader as "you".
  Do not guess anyone's pronouns; use they/them or the person's name.
- Every factual claim about research or a person cites a URL and the
  source's date. Mark claims you could not verify as `[unverified]`.
- Grade evidence for every practice you report:
  - **A** controlled study or benchmark with published data and method
  - **B** large-scale telemetry or observational data (n stated)
  - **C** practitioner report with concrete numbers or a reproducible demo
  - **D** opinion, anecdote, vibes
- Prefer 2025–2026 sources; older work is fine when it is the foundation.
  Note when a finding was measured on models that are now obsolete.
- Each file opens with **Top findings** (5–10 bullets, each with its grade),
  then the body, then **Where your setup differs** (compare against the
  skills directory; name the skill), then **Candidate actions** (ranked by
  expected value / cost, each with a one-line rationale), then **Sources**.
- Do not open issues, PRs, posts or any outreach anywhere. Read only.
- Do not edit anything outside this directory and your scratch dir.
  Write your file(s) only at the path your task names.
