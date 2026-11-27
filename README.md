# mstack

The skills, helper scripts and research I use to work with coding agents.

mstack is the source for my agent skills and global instructions. The skills are written for my own tools, hosts and habits, so adapt them before you use them. The research keeps dated observations and grades every claim from A (a controlled study) to D (opinion). Agents working in this repository should read [AGENTS.md](AGENTS.md) instead of this page.

## How I work with agents

People call agent work more art than science. I read that as science nobody has worked out yet, so I keep measuring. Two ideas run through everything here: make the state of things **legible**, and keep my own **mastery** of code I did not type.

### Legibility: a solid core, a soft edge

![Three rings: a deterministic core in the middle, judgement around it, the chaos of reality outside](docs/legible-cores.svg)

The tools that work best have a deterministic core the agent reads to see where it stands. So I look for guesses a program could replace:

| Agents kept guessing at | The core that replaced the guess |
|---|---|
| How long a wait takes, and when the prompt cache expires | vigil (holds and keepalives) and agentpace (estimates from past runs) |
| Whether a test proves anything | tq, a linter for hollow tests, scored on 30 public repos with a model judging samples of its findings |
| Which test failures are real | a separate judge model; the model that wrote a rule was too generous grading its own output |
| What a change will do next | residual |
| How the code is shaped | paneweft, views inside the code |
| Whether a layout shifts | a layout-shift measure instead of judging by eye |

When a guess is big enough to build a company on, the [legible-cores](skills/legible-cores/SKILL.md) skill has the agent raise it with me as one card.

### Mastery: keep up with code I did not type

Agents write most of the code, and I still have to own it. These are the habits that keep me able to:

| Habit | What it does | Status |
|---|---|---|
| Review check | Every pull request ends with ten questions; if I can answer 24 of 30 points without looking, I have reviewed it | In use ([pr-stacks](skills/pr-stacks/SKILL.md)) |
| Journey file | Each feature keeps its mock-ups, my decisions and its dead ends, because the paths I dropped explain the one I took | In use ([build-loop](skills/build-loop/SKILL.md)) |
| Question first | An interview on states, edges and precedence before any spec | In use ([question-everything](skills/question-everything/SKILL.md)) |
| Sliced red and green | One model writes a few failing tests and the mutants they must kill; a different model writes the code. Each slice has one real flip, not just "delete the button" | In use since 2026-11-27 ([build-loop](skills/build-loop/references/slices.md)) |
| Assumption review | Ten questions about what a module assumes about its inputs, each with the evidence that would settle it | Pilot on one module |
| Views that teach | A benchmark for whether a view makes a fresh agent understand the code better than reading it | Proposed ([research 13](research/13-research-direction-views-that-teach.md)) |

### What changed my mind lately

| Finding | Where it lives now |
|---|---|
| A broken run can come out as a good score: a failed build counts every mutant as killed, a dropped exit status reads as a pass | test-quality failure mode 14 |
| A check that cannot run must fail, and every gate gets watched failing once before it is trusted | [ratchets](skills/ratchets/SKILL.md) |
| A rule's precision differs a lot by language, so each rule blocks or only warns per language, decided by a vote of repos with enough judged findings | tq gates, being measured |
| Reading a new rule back to three fresh agents finds wording they would misread | a pilot over ten skill edits |
| A row of substring checks over one text hides drift; one golden of the whole text does not | test-quality failure mode 13 |

Review bars also follow the project. Early on they run high on fit, architecture that is expensive to change, security boundaries and test quality, and low on concurrency hardening and polish. Once a project has users and stored data, the curve flips.

I work under two limits, money and attention. I run one working Claude agent at a time, push heavy builds to cloud sandboxes, and switch providers when a usage window runs low. Agents need my approval before they open issues, forks, pull requests or posts.

## Skills

Clone the repository and ask your agent to read the `SKILL.md` you need and the files it points to:

```sh
git clone https://github.com/mikenrafter/mstack.git
```

These are the ones worth starting with:

| If you want to | Use |
|---|---|
| Question a feature before building it | [question-everything](skills/question-everything/SKILL.md) |
| Check that tests prove behavior | [test-quality](skills/test-quality/SKILL.md) |
| Review interfaces, naming and design | [technical-excellence](skills/technical-excellence/SKILL.md) |
| Run a feature through spec, red, green and review | [build-loop](skills/build-loop/SKILL.md) |
| Split work into small pull requests | [pr-stacks](skills/pr-stacks/SKILL.md) |
| Make a rule only ever get stricter | [ratchets](skills/ratchets/SKILL.md) |
| Turn repeated review findings into checks | [retro](skills/retro/SKILL.md) |
| Find guesses a measurement could replace | [legible-cores](skills/legible-cores/SKILL.md) |
| Write plainly | [plain-writing](skills/plain-writing/SKILL.md), [unslop](skills/unslop/SKILL.md), [writing-copy](skills/writing-copy/SKILL.md) |

Everything else:

| Area | Skills |
|---|---|
| Review and cleanup | [adaptive-hardening](skills/adaptive-hardening/SKILL.md), [comment-audit](skills/comment-audit/SKILL.md), [deliberate-changes](skills/deliberate-changes/SKILL.md), [readme](skills/readme/SKILL.md) |
| Publishing safely | [no-unsolicited-upstream](skills/no-unsolicited-upstream/SKILL.md), [publishing-scrub](skills/publishing-scrub/SKILL.md) |
| Waiting and budgets | [vigil](skills/vigil/SKILL.md), [manual-keepalive](skills/manual-keepalive/SKILL.md), [uw-agent](skills/uw-agent/SKILL.md) |
| My hosts and tools | [boat](skills/boat/SKILL.md), [low-ram-hosts](skills/low-ram-hosts/SKILL.md), [iterating-with-nix](skills/iterating-with-nix/SKILL.md), [scout-module-locks](skills/scout-module-locks/SKILL.md), [tea](skills/tea/SKILL.md), [tailcook](skills/tailcook/SKILL.md), [github-stars](skills/github-stars/SKILL.md) |
| Keeping up | [practice-watch](skills/practice-watch/SKILL.md) |
| Special cases | [cyber-build-loop](skills/cyber-build-loop/SKILL.md) (a clean-room firmware project), [handling-ambiguous-work](skills/handling-ambiguous-work/SKILL.md) (recovering a thread after a provider error) |

Copy a whole skill directory when you install one; `build-loop` needs its `references/` and `scripts/`. The host and tool skills describe my environment, and reading them does not install those tools.

## Limits

The research covers one person on one host. Nothing in it measures escaped defects, production impact or what I learned. The tq precision numbers come from a model judging samples of findings, not from people. Several habits above are pilots, and their status says so.

## Research

[research/00-index.md](research/00-index.md) starts the literature review and the analysis of my own agent usage. Raw transcripts and private usage data are left out; citations to them are marked as private. [RELEASE.md](RELEASE.md) lists publication checks and open questions, [research/PLAN.md](research/PLAN.md) the dated plan, and [related.md](related.md) the neighboring tools.

## For agents and contributors

[AGENTS.md](AGENTS.md) covers editing and installing skills, the helper scripts and their tests, and the rules for publishing.

## License

[MIT](LICENSE), copyright 2026 Tyler Slaughter. The license covers original material in this repository. Cited publications and third-party material keep their own rights.
