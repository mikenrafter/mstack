# mstack

Skills, helper scripts and research from my work with coding agents. Start with a skill you need, or read the [research index](research/00-index.md) for the evidence and its limits.

mstack is the source of truth for my shared coding-agent skills, workflow helpers and global instructions. The skills encode my own tools, hosts and preferences; adapt those assumptions before using them. The research preserves dated observations. The original 2026-11-12 snapshot remains available as the v0.1.0 release.

## How I approach agent work

People say agent work is more art than science. I read that as science nobody has worked out yet, which makes it a list of open questions and a reason to keep measuring. This repo holds what I have so far: the skills I run coding agents with, and the research I did to see where my habits match published evidence and where they have none. Every claim in the research carries a grade from A, a controlled study, to D, opinion. The research index says outright that no result in it measures my escaped defects, production impact or learning.

A review bar fixed for the whole life of a project does damage. One of my tools spent eight review rounds on concurrency races that no real user would hit for a long time, while it was still a prototype. So the bars here follow the project. Early on they run high on whether the thing fits its purpose, on architecture that is expensive to change later, on security boundaries and on test quality, and low on concurrency hardening, performance and polish. Once the project has users and stored data, the curve flips. Maturity is judged per region of the code, and I can override what the tool computes.

I want to test practices against things that really happened. The plan is to take real bugs, reverts and decisions I later undid in my own repositories, hide how each one ended, and see whether a given prompt, skill or piece of advice from a well-known practitioner leads an agent to the good outcome. Security gets a written threat model for each project, covering who can reach it, what strangers can feed it and what it holds, and findings are weighed against that model. Two agents sending the same request in the same millisecond goes on a list for the hardening phase.

The tools that work best in agent work have a deterministic core that the agent reads to see its situation: a clock, a ledger, a measurement, an index, a test. Around the core sits a mushy edge of judgement, where inference earns its cost, and beyond that the chaos of reality. Code alone is fast but can't adapt. Inference alone adapts but is slow and imprecise. Agents misjudged time and cache expiry until vigil and agentpace showed them both, and the same pattern runs through residual (what a change does next), paneweft (architecture) and a layout-shift measure for UI that is otherwise judged by eye. It is a twist on the bitter lesson. More compute keeps improving the models, but anyone, human or model, who can't see the state still guesses. So I look for guesses a program could replace, and the [legible-cores](skills/legible-cores/SKILL.md) skill has agents raise the ones big enough to build a company on.

Views of code should produce insight. A component earns its place by answering a question about the code that the reader would otherwise guess at, and decoration gets cut. The record of a decision keeps its dead ends, because the paths I dropped explain the one I took. I want views to make tests, invariants and their coverage visible, so that a wrong change looks wrong. paneweft, linked below, is where I try this, starting from the moldable development ideas in Glamorous Toolkit.

I also work under two limits, money and my own attention. Keepalive ticks alone drove about a quarter of my estimated Claude spend in the data I measured, so I run one working subagent at a time, push heavy builds to cloud sandboxes, and plan to move work to another model provider when a usage window runs low. For attention, I want short lessons at build-loop phase boundaries and ten questions before a pull request ships, so I can keep up with code I did not type. Those teaching steps remain planned work. Agents need my approval before opening issues, forks, pull requests or posts.

## Try a skill

Clone the repository, then ask your coding agent to read the relevant `SKILL.md` and its referenced files:

```sh
git clone https://github.com/mikenrafter/mstack.git
cd mstack
```

| If you need to… | Start with |
|---|---|
| Question a feature before building it | [question-everything](skills/question-everything/SKILL.md) |
| Assess whether tests prove useful behavior | [test-quality](skills/test-quality/SKILL.md) |
| Review interfaces, naming and design | [technical-excellence](skills/technical-excellence/SKILL.md) |
| Run a phased implementation and review | [build-loop](skills/build-loop/SKILL.md) |
| Write plainly | [plain-writing](skills/plain-writing/SKILL.md) and [unslop](skills/unslop/SKILL.md) |
| Split work into small PRs labelled by how hard they are to revert | [pr-stacks](skills/pr-stacks/SKILL.md) |
| Turn repeated review findings into checks | [retro](skills/retro/SKILL.md) |
| Cut comments that hide problems, keep the ones that carry facts | [comment-audit](skills/comment-audit/SKILL.md) |
| Track what other engineers publish about their practice | [practice-watch](skills/practice-watch/SKILL.md) |
| Write or audit a README | [readme](skills/readme/SKILL.md) |
| Add a rule that only gets stricter, or roll out a new tool | [ratchets](skills/ratchets/SKILL.md) |
| Find guesses a measurement could replace | [legible-cores](skills/legible-cores/SKILL.md) |

Copy an entire skill directory if you install it into your agent's skill directory. `build-loop` needs its `references/` and `scripts/` subdirectories. Referenced companion skills must also be available. Installation paths and tool names vary by agent.

`build-loop` assumes specific model roles and T3 Code orchestration tools. `boat`, `low-ram-hosts`, `vigil`, `manual-keepalive` and `uw-agent` describe my own environment. The `boat-run` wrapper, qex executable, NixOS installation hooks and usagewindow service are not bundled. Reading a skill does not install those tools.

## Helper scripts

The build-loop scripts use Python 3 and its standard library. Git is needed for ledger operations on repositories; live bot triage also needs an authenticated GitHub CLI (`gh`). `review-ledger` maintains review state and briefs; `bot-triage` tracks review-bot findings. `ui-brief-check` fails a UI brief that names no mock-up, original screen or prior pilot. Inspect their commands with:

```sh
python3 skills/build-loop/scripts/review-ledger --help
python3 skills/build-loop/scripts/bot-triage --help
python3 -I -m unittest discover -s skills/build-loop/scripts/tests
```

The script tests check helper behavior, not whether the workflow improves software outcomes. Run them from the repository root; some hook tests also need Bash, jq and grep.

## Research and open work

[research/00-index.md](research/00-index.md) starts the literature review and analysis of my own agent usage. Evidence is graded A through D, from controlled studies to opinion. My usage analysis covers one person on one host; it does not establish reductions in escaped defects or improvements in learning. Raw transcripts, private usage artifacts and Readwise material are excluded. Citations to those artifacts are marked as private evidence unavailable in this release.

[RELEASE.md](RELEASE.md) separates publication checks from the open research questions. [research/PLAN.md](research/PLAN.md) preserves the dated workstream plan, including work in other repositories. Its queued items are not promises for this release. [Related projects](related.md) lists the neighboring tools.

`research/site/index.html` is an optional dossier reader for sections 00–09. It fetches sibling Markdown files and external rendering libraries, so it needs HTTP hosting and network access. The Markdown files are the primary reading path.

## For agents and contributors

- Edit shared skills in `skills/`, workflow helpers in `bin/`, and global instructions in `global-instructions.md` here. phoe-nix consumes a locked `mstack` source input and installs these files through its agent-integration scout module and Kasetto. There is no second editable copy in phoe-nix.
- To test unpublished changes in phoe-nix, stage new files here and build the consumer with `--override-input mstack path:/absolute/path/to/mstack`. After publishing, update the named `mstack` lock and deploy `nix-scout switch agent-integration` without the override.
- Read the matching skill and its companions before applying a workflow. User instructions and available tools determine what can actually run.
- Do not open issues, forks, pull requests, discussions or other outreach without the owner's explicit request. See [no-unsolicited-upstream](skills/no-unsolicited-upstream/SKILL.md).
- Before pushing to a public repo or fork, run `bin/publish-scan`; [publishing-scrub](skills/publishing-scrub/SKILL.md) says what to scrub without asking.
- Keep transcripts, credentials, personal highlights and session handoffs out of this repository.
- For research, follow [BRIEF.md](research/BRIEF.md): date sources, grade evidence and mark unverified claims.
- Keep changes focused and report the checks actually run. Run the helper-script tests when changing those scripts.

### Writing a skill

Almost every skill I use lives here. Write a new skill in `skills/` and
install it from this repository; edit the copy here, never an installed copy
(`~/.claude/skills`, `~/.codex/skills`), which the next install overwrites.
The one exception is a skill that documents a tool and has to change in step
with it; that skill lives in the tool's own repository:

| Skill | Lives in |
|---|---|
| `qex` | the qex repository |
| `usagewindow-status` | usagewindow |
| `babeltele` | babeltele |

Some installed skills are other people's and stay theirs: `file-pr`,
`babysit-pr` and `leaving-pr-comments` come from Theo Browne's
[tstack](https://github.com/t3dotgg/tstack). Install them from there. When I
want one to behave differently, the change goes in an mstack skill, not in a
copy of theirs. `practice-watch` follows tstack for changes.

Every skill is model-invocable. Do not set `disable-model-invocation`.
Write its description as conditions saying when to invoke it, because the
model reads that description as a prose hook.

## License

[MIT](LICENSE), copyright 2026 Tyler Slaughter. The license covers original material in this repository. Cited publications and third-party material retain their own rights.
