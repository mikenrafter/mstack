<!-- DRAFT: the first five paragraphs below (the ethos) were drafted by an agent from the owner's decisions in research/PLAN.md. They await the owner's edit. Delete this comment when they are final. -->
# mstack

People say agent work is more art than science. I read that as science nobody has worked out yet, which makes it a list of open questions and a reason to keep measuring. This repo holds what I have so far: the skills I run coding agents with, and the research I did to see where my habits match published evidence and where they have none. Every claim in the research carries a grade from A, a controlled study, to D, opinion. The research index says outright that no result in it measures my escaped defects, production impact or learning.

A review bar fixed for the whole life of a project does damage. One of my tools spent eight review rounds on concurrency races that no real user would hit for a long time, while it was still a prototype. So the bars here follow the project. Early on they run high on whether the thing fits its purpose, on architecture that is expensive to change later, on security boundaries and on test quality, and low on concurrency hardening, performance and polish. Once the project has users and stored data, the curve flips. Maturity is judged per region of the code, and I can override what the tool computes.

I test practices against things that really happened. The plan is to take real bugs, reverts and decisions I later undid in my own repositories, hide how each one ended, and see whether a given prompt, skill or piece of advice from a well-known practitioner leads an agent to the good outcome. Security gets a written threat model for each project, covering who can reach it, what strangers can feed it and what it holds, and findings are weighed against that model. Two agents sending the same request in the same millisecond goes on a list for the hardening phase.

Views of code should produce insight. A component earns its place by answering a question about the code that the reader would otherwise guess at, and decoration gets cut. The record of a decision keeps its dead ends, because the paths I dropped explain the one I took. I want views to make tests, invariants and their coverage visible, so that a wrong change looks wrong. paneweft, linked below, is where I try this, starting from the moldable development ideas in Glamorous Toolkit.

I also work under two limits, money and my own attention. Keepalive ticks alone drove about a quarter of my estimated Claude spend in the data I measured, so I run one working subagent at a time, push heavy builds to cloud sandboxes, and plan to move work to another model provider when a usage window runs low. For attention, the build loop is meant to teach me in short lessons at phase boundaries, and a pull request ends with an agent asking me ten questions, so I can keep up with code I did not type. Nothing reaches outside this machine without my approval. No issues, forks, pull requests or posts go out on an agent's own initiative, and this repo stays local until I say otherwise.

## For agents

This repo is the home for the owner's agentic workflow: skills, the research behind them, and the plan that tracks what is next. Read this section, then the skill that matches your task.

### Layout

- `skills/` holds 13 skills in the [agentskills.io](https://agentskills.io) format, one directory each with a `SKILL.md`. `skills/build-loop/` also has `scripts/` (`review-ledger`, `bot-triage`) and their tests.
- `research/` holds the numbered research docs (`00-index.md` first), `PLAN.md` (the workstream table with owner decisions), `BRIEF.md` (conventions the research followed), and `15-bars-by-maturity-spec.md`. `research/site/index.html` is a rendered dossier of the same material.
- `related.md` lists the neighbouring repos.

### How the skills are installed today

These are copies. [phoe-nix](https://github.com/mikenrafter/phoe-nix) keeps the originals in `scout-modules/agent-integration/skills/` and installs them into each agent CLI (Claude Code, Codex and others) through kasetto (KST). Until the owner says otherwise, edit the phoe-nix copy and treat this repo as a mirror. A change made only here will not reach any agent.

### The main workflow

Use `build-loop` for any multi-phase feature. An orchestrator writes the spec and red tests, a cheaper implementer writes the code, a scored review loop fixes findings, and one fresh pass reviews the stable result. The companions are `question-everything` (interrogate the spec before code), `technical-excellence` (design and code standards), `test-quality` (what a test is worth) and `vigil` (stay alive while work runs; `manual-keepalive` is the backup). `rg-implement` is the smaller single-model red/green variant. After any context compaction, reread `build-loop` and `vigil` before doing anything else.

`low-ram-hosts` and `boat` cover where heavy work runs. `uw-agent` covers compaction and resume against a usage limit. `plain-writing` and `unslop` apply to all prose you write.

Run the build-loop script tests with `python3 -I -m unittest discover -s skills/build-loop/scripts/tests`. They were copied together with the scripts; confirm they pass here before relying on them.

### Rules of conduct

- Do not open issues, forks, pull requests, discussions or any other outreach without the owner's explicit approval (`skills/no-unsolicited-upstream`). A draft in chat is fine.
- This repo is local only. Do not push it or create a remote.
- Write plainly. Load `plain-writing` and `unslop` before writing prose a person will read.
- Keep private data out. Readwise highlights, third-party transcripts, session logs and handoff notes were left out on purpose and stay in phoe-nix.
- Research docs follow `research/BRIEF.md`: cite sources with dates, grade evidence A to D, mark anything unverified.
- Future research directions are filed under `research/`. Open ones are listed in `research/PLAN.md` (W40, veil against jj for landing many agent changes, has its first write-up in `research/16-veil-vs-jj.md`).

### Not included

The research docs link to `data/` (usage analysis scripts and session extracts) and to the Readwise-derived upskilling material. Those links are dead here on purpose.

### License

None yet. The owner decides. Until then, treat the contents as all rights reserved and do not redistribute them.
