# 06 — Claude Code usage on nixed: where the tokens and the failures go

Data: 504 Claude Code transcripts from `~/.claude/projects/` on nixed (20 main sessions, 484 subagent
transcripts), 50,563 API calls, 47,879 tool calls. Retained timestamps span
2026-10-17T16:58:40.533Z to 2026-11-11T00:32:31.753Z, ending on November 10
in America/Denver. The analysis ran on nixed (confirmed by `hostname`, 2026-11-10); the brief
mislabeled the host as sonic, and the extractor's hardcoded `sonic` label in
`sessions.jsonl` is wrong. Sonic's transcripts were not analyzed.
The void host is offline, so its transcripts are missing. So are the newest
diff-core and residual-cli sessions, and nearly all Nix work on void. Read
every number below as your edge/polara-port corpus on nixed. Edge and polara-port make up 98.8% of the estimated cost.

Grades follow BRIEF.md. Numbers measured from your transcripts are **B**: telemetry
with n stated, though from one user on one host over 25 days. Numbers that rest on
hand labels or fewer than ~20 cases are **C**.

## Top findings

1. **Turns triggered by keepalive ticks carry about a quarter of estimated cost.**
   Main-session writes are predominantly 1-hour: 20.36 M tokens versus
   0.036 M 5-minute writes. Seventeen of 18 main sessions with writes use
   1-hour writes for at least 95% of their cache creation. Yet ticks fire
   every 270 s. 5,178 main-session tick launches were associated with 10,656 API calls, 2.06 calls per tick, each
   re-reading a mean 337 k-token context. That is 24.9% of estimated cost
   (≈ $798). One tick costs $0.154, so an hour of ticking costs $2.05, while
   letting the cache expire and rebuilding it once costs $2.70. A proportional model puts the gross reduction from 50-minute ticks at
   ≈ 22.6% of total cost. Avoided work, recovery cost and transport behavior
   were not tested. **B** for attribution; **D** for the intervention.
2. **Subagents are half the cost, and 11% of all cost is subagent cache rebuilds.**
   Subagents use the 5-minute cache. 562 times a subagent's next call came 5–60
   minutes after its last one and made a cache write exceeding half its context.
   - 297 of those rebuilds (6.4% of cost) came when the parent sent a follow-up
     to a subagent that had sat idle.
   - 265 (4.6%) followed 5–60 minute gaps without a parent-message trigger.
     Some examples are long foreground
     `until grep -q DONE …; do sleep 10; done` waits. **B**
3. **Main-session context is very large.** Median 274 k tokens per call, p90 560 k,
   max 815 k. A quarter of main-session cache reads (24.9%) sit above 300 k
   tokens. Compacting at ~300 k would cut at most 10.1% of total cost.
   Compaction cost little in this data (finding 5). **B**
4. **Bash output, not file reads, fills the context.** Tool results that stay
   in context and get re-read on later calls account for ≈ 13.4% of cost. Bash
   is 91.9% of that, and `cat`/`sed -n`/`head` file views alone are 27.5%.
   Agents ran 5,555 shell file views against 1,595 Read calls. 336 file/transcript pairs had
   more than two views. A file occurring in several transcripts is counted again. The top three were
   `derivation_engine.dart` (152 views), `play.rs` (140) and the inter-agent
   chat file `chat-cls-merge.md` (87). **B**
5. **Post-compaction records often lack the required rule-recovery steps.** There were 44
   compactions, all manual, at a mean of 419 k tokens.
   - In the first 15 tool calls afterwards the agent read 24.4 k chars on
     average, against 15.0 k at random points (1.6×). Re-reads of
     already-seen files rose from 1.26 to 1.9 per 100 tool calls.
   - The keepalive chain was not restarted within 60 tool calls after 7 of 44
     compactions.
   - No summary carried the `REREAD the build-loop…` first line (0 of 44).
     build-loop was explicitly re-read after 2 of 44. The harness re-attached
     rg-implement and manual-keepalive after 19 of 44. **B**
6. **Review replies contain half their finding entries after round 1, and about a third of
   those late entries are in stored data.** Across 9 wake-pr changes reviewed
   by Sol, new findings per round went 81 → 52 → 19 → 12 (rounds 1, 2, 3, 4+).
   Blockers went 19 → 13 → 4 → 3. Four changes needed 5 rounds. 50.6% of
   finding entries arrived after round 1. The separate 25/55 same-file figure
   is hardcoded in `analyze.py`, with no retained derivation [unverified]. "Stored data / migration / export" is the largest
   kind: 47 of 164 findings overall and 28 of 83 in rounds 2+. **C** (9 changes)
7. **A third of tool errors come from three fixable patterns, mostly in subagents.**
   1,175 tool errors in 47,879 calls (2.5%).
   - 182 calls were `sleep N; cat file` waits that the harness blocked, across
     136 transcripts. 167 of the 182 came from subagents.
   - 59 called a tool named `bash`.
   - 47 called Monitor without its required `description` parameter.

   Sonnet 5.5 subagents made all 106 of the wrong-name and Monitor errors.
   **B**
8. **Your corrections are rare, and most are about budget and blocking.**
   Hand-labelled, 14 of 723 unique prompts (1.9%) correct the agent: 5 about
   parallelism or cost, 4 misread references, and 3 about the question tool
   stalling work ("You got stuck for 30 minutes because of this"). Another
   46 prompts (6.4%) ask for keepalive or "stay in cache", and 5 complain
   about T3 restarts, an OOM or a hung connection. **C** (hand labels)
9. **No secrets found.** Eight secret patterns (Anthropic, OpenAI/OpenRouter,
   GitHub, AWS, private-key blocks, age keys, Slack, bearer headers) matched 0
   times across prompts, tool inputs, tool results and assistant text. **B**
   (pattern scan only)

## 1. What burns the tokens

Totals: 10.92 B cache-read tokens, 212.8 M cache-write tokens, 32.1 M output
tokens, 0.12 M uncached input. At list prices, cache reads are 60.8% of cost,
cache writes 24.0% and output 15.2%. Total ≈ $3,207. The harness's own
`cost-state` records sum to $3,007 for the main sessions that have them, a 7%
gap. A free least-squares fit of those records recovers Opus 5.5 cache reads
at $0.207/MTok against the published $0.20, which checks the extraction.

**By project.** edge main 44.2%, edge subagents 30.8%, polara-port subagents
18.2%, polara-port main 5.6%, everything else 1.2%.

**By what started the turn.** Each API call is charged to the event that
began its turn.

| Turn trigger | Share of cost | Calls |
|---|---:|---:|
| Subagent's own work (first prompt onward) | 35.5% | 24,023 |
| Keepalive tick completed | 24.9% | 10,656 |
| Parent's follow-up message to a subagent | 14.1% | 4,939 |
| Background command completed | 8.8% | 3,679 |
| Your prompt | 8.3% | 3,881 |
| Subagent completed | 7.4% | 2,897 |
| Other task notifications | 1.1% | 488 |

Your own prompts start turns carrying 8.3% of estimated cost. Other turns
include substantive subagent work as well as waiting and notifications;
this attribution does not measure avoidable work.

**Cache misses.** In main sessions, rebuilds are negligible: 50 rebuilds,
0.3% of cost. Observed main-session writes are almost all 1-hour writes. This does not
isolate how much activity or keepalive ticks caused cache hits. In
subagents, 562 rebuilds after 5–60 minute gaps cost 11.0%. They split into
297 parent resumes of an idle subagent (6.4%) and 265 waits inside the
subagent (4.6%). Of the 265 non-parent-triggered cases, not every gap was a wait loop.
Across all 562, the tool result before the gap was a
`sleep`/`until` wait loop in 191 cases and a Nix command in 26.
Representative wait commands:
`until grep -q DONE /tmp/hb/run3.log; do sleep 10; done; cat /tmp/hb/run3.log`
(600 s), `until grep -q "^DONE" /tmp/p8a-r4-all.out …` (600 s).

**Keepalive economics.** These are trigger-attributed costs, not a causal
measurement of waste. The tick (`sleep 270 && echo keepalive`) was sized for
a 5-minute cache. On these sessions the cache lasts an hour, and it is
refreshed for free on every hit ([prompt caching docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching),
read 2026-11-10). Each tick costs two API calls: one to relaunch the sleep and
one to end the turn. Its result and notification text also stay in context
(0.7% of cost). At $2.05 per hour of ticking against $2.70 for one full
rebuild, ticking every 270 s costs more than doing nothing as soon as a wait
runs past ~80 minutes.

**Subagent fan-out.** 482 subagents were spawned, averaging 60 calls each.
Their context is smaller than the parent's (median 127 k, p90 323 k), and
first-call writes are cheap (0.6%). The cost is in how long they run and in
idle resumes, not in starting them. Opus subagents (134 that requested or
inherited Opus) cost 20.8% of the total. Sonnet subagents cost 31.3%.

**Tool results.** Result size: p50 421 chars, p90 5.3 k, p99 18 k, max 67 k
(the harness caps it). Results over 10 k chars hold 32.6% of result chars.
Re-read on later calls, though, the part above 10 k is worth only 1.3% of
cost. Small outputs read many times outweigh big outputs read once.

**Hooks.** The tea PostToolUse hook fired on 5,872 slow Bash commands. Its
≈ 230-character note costs ≈ 0.2%. The rtk PreToolUse hook already rewrites
Bash commands (you can see `[+N hidden: rtk recall …]` in outputs), so output
filtering already happens. More filtering has little left to win.

## 2. Compaction and context loss

All 44 compactions were manual, through `/compact` or uw-agent. They ran with
the BabelTele PreCompact hook. Mean pre-compaction size was 419 k tokens,
mean summary 13.9 k chars, and mean cache write on the first call afterwards
21 k tokens.

What happens next, compared with 184 random points in the same sessions:

| After compaction | Post | Baseline |
|---|---:|---:|
| Re-views of files read earlier, per 100 tool calls | 1.9 | 1.26 |
| Chars read in the first 15 tool calls | 24.4 k | 15.0 k |
| Keepalive restarted within 5 tool calls | 21 of 44 | — |
| Keepalive not restarted within 60 tool calls | 7 of 44 | — |
| build-loop re-read within 40 calls | 2 of 44 | — |
| Summary first line is the REREAD line | 0 of 44 | — |
| Harness re-attached invoked skills | 19 of 44 | — |

Reading the stretches shows one pattern. The agent rehydrates by `cat`/`sed`-ing
`RULES.md`, the BabelTele plan and the chat file in 7–15 k-char chunks. That
works but is wasteful, because the same files were read before compaction. In one sampled stretch
(1459dd51, 2026-10-19) you had to step in right after the compaction:
"please pull a large amount of the context from the Babeltele plan. I need for you to understand the project direction, most recent action items, and particularly the rules and mode of conduct."
In another (1459dd51, 2026-10-24), the agent restarted keepalive in the
same turn and carried on. In a third (polara-port 57eea103, 2026-11-06),
your "continue" led the agent straight to `SendMessage`-resuming a subagent
that had sat idle through a spend-limit pause. That is the 5-minute-cache
rebuild pattern from section 1. It then ran a second `sleep 270; tail …`
chain next to the keepalive, which manual-keepalive's "exactly one chain"
rule forbids.
The sampled post-compaction windows show some repeated reading and missing
recovery steps. No independent task-outcome audit measured lost work. The SessionStart(compact) REREAD hook
appears only once in this data (it is newer than most of these sessions).

Separately, T3 restarts replay old transcript records. 45,059 records,
about 25% of main-session records, are exact uuid repeats. 131 prompts
appear 2–5 times. The model may or may not see them again; check one restart
by hand before drawing a conclusion.

## 3. Review-loop churn

Two sources sit outside the transcripts: Sol's review replies on disk, and
the review-ledger files.

**Rg-implement era (edge wake-pr, 9 changes, findings `R<round>-<n> [severity]`):**

| Round | Findings | Blockers |
|---:|---:|---:|
| 1 | 81 | 19 |
| 2 | 52 | 13 |
| 3 | 19 | 4 |
| 4+ | 12 | 3 |

- 4 of 9 changes needed 5 rounds: cls1, p8a, t12, t3. Typical series ran
  t3 13 → 11 → 7 → 3 → 0 and t12 12 → 10 → 5 → 4 → 1.
- The 25/55 same-file recurrence figure lacks a retained derivation [unverified].
  The round totals count finding IDs within each reply, not deduplicated
  defects across replies. They do not establish that fixes introduced new bugs.
- Kinds, tagged by keyword (58 of 164 untagged):
  - stored data / migration / export: 47 (28 of them in rounds 2+);
  - caller or contract drift: 18 (11);
  - time / date / DST: 12 (7);
  - invalid input: 12 (4);
  - UI / layout / l10n: 12 (5).
- Spec reviews also took two rounds with many findings: cls2 20 → 14,
  hmm 18 → 7.
- One edge workstream reached "round-14 green (review fixes)" in an
  agent description.

**Build-loop era (6 ledgers, scored):**

- 35 findings: 2 blockers, 12 should, 21 nits. 22 were raised after round 1
  or in tier 2.
- In appkind (fauxx, bar 9), tier 1 went from 4 to 9 in two rounds. The fresh
  tier-2 pass then scored 7 and raised 10 new findings, including a
  "tautology" test.
- In home (edge) the score went 4 → 6 → 7.5, and in graphs 6 → 8 → 8.
- Observed score sequences include 2–3 rounds. Ten of the 35 ledger findings
  remain open. This is not evidence that every loop completed or that the cap
  caused convergence (**C**, six ledgers).

Example recurring finding (wake-pr cls1 round 3):
"`R3-2 [should] lib/data/db.dart:2230 The new alcohol sum uses amounts rejected by the reader … The invalid-state checklist answer is false.`"
The project checklist existed, but the implementer's answer to it was wrong.

## 4. Recurring failure points

1,175 tool errors in 47,879 tool calls (2.5%).

| Family | Errors | Transcripts | Representative excerpt |
|---|---:|---:|---|
| grep/test/diff returned non-zero (mostly "no match", benign) | 241 | 136 | `Exit code 1` |
| Harness blocked `sleep N; read` | 182 | 136 | `Blocked: sleep 45 followed by: head -c 1500 …/green-p1.log` |
| Other non-zero exit | 121 | 79 | (mixed; test assertions inside scripts) |
| Inline script failed + Python traceback (heredoc edits) | 155 | ≤ 93 | `Traceback … File "<stdin>", line 6` |
| Process management (`pgrep`/`pkill` hunting codex runs) | 87 | 49 | `pkill -f 'codex exec -m …'` → `Exit code 144` |
| git failed | 80 | 45 | — |
| Wrong tool name `bash` / `bash_placeholder` | 59 | 58 | `No such tool available: bash. Tool names are case-sensitive: call Bash instead.` |
| File missing / bad path | 49 | 33 | `ls: cannot access '~/.android/debug.keystore'` |
| Monitor called without `description` | 47 | 47 | `InputValidationError: Monitor failed … The required parameter description is missing` |
| Test run failed | 43 | 32 | — |
| Command not found (NixOS PATH) | 25 | 20 | `sqlite3: command not found` |
| Worktree isolation block | 25 | 3 | `This agent is isolated in the worktree …, but this command runs …` |
| You rejected the tool call | 8 | 7 | `until grep -q DONE …; do sleep 10; done` |

Other failure signals:
- 51 API connection errors and 15 Bash timeouts.
- 112 Bash commands ran more than 10 minutes, mostly wait loops and
  `flutter test` runs that hit the 600 s cap.
- 44 times the same command succeeded right after failing.
- 15 user interrupts.

The failures AGENTS.md warns about are rare here, because these sessions are
mostly Flutter and Rust work:
- 1 evaluation of another host on nixed;
- 2 `nix flake check` runs;
- 8 builds piped into `tail`/`head`/`grep`;
- 0 checks of a `result` link.

The void data, where most Nix work happens, would test these properly.

**Your corrections** (hand-labelled, 14 of 723 unique prompts):
- "Do not use the Ask User Question tool unless I have said something in very recent history. You got stuck for 30 minutes because of this."
- "tell that opus sub agent to stop and relaunch a sonnet sub agent it doesn't need to be that expensive"
- "No, and once these three subagents filter down to fewer, I would like for you to not run so many things in parallel for budget reasons."
- "stop, no compiling, no testing, agg is running performance tests."
- "No, I mean the babeltele-plan file within the research directory."

Infra complaints: "Keepalive, it restarted again, ugh", "did we reach an OOM
state just now? T3 restarted again", "The connection hung again."

The brief's keyword list ('no', 'stop', 'wrong', 'again', …) flags 65
prompts, but only 14 are corrections (about 22% precision). Many flags are
about the app ("it called all of it deep sleep, which is definitely wrong").
The `user_correction_msgs` field in `sessions.jsonl` is that raw regex count;
read it as an unvalidated keyword signal. It can miss differently worded
corrections, so it is not a mathematical upper bound on all corrections.
The 65 candidates use deduplicated main-session prompts; the per-row regex
counts sum to 192 across all 504 retained transcripts.

## 5. Small injections and what each would remove

Shares are of total estimated cost (≈ $3,207 over the period) or of the
1,175 tool errors. These are modeled addressable buckets, not measured savings.
They overlap and do not add up. A fresh child also incurs briefing, cache-write
and rediscovery costs; a removed notification turn may contain useful work.

| Injection | Removes | How it was estimated |
|---|---:|---|
| Keepalive tick every ~50 min (`sleep 3000`, background timeout ≥ 3,300,000 ms) when the session's cache is 1 h | **22.6% of cost** | tick cost × (1 − 270/3000) |
| …or keep 270 s but make each tick one API call (relaunch with no closing message) | 12.8% of cost | tick cost × (1 − 1/2.06) |
| Compact main sessions at ~300 k tokens (uw-agent threshold) | ≤ 10.1% of cost | main cache reads above 300 k; ignores re-read cost, measured at 1.6× chars post-compaction |
| Compare a fresh short brief with resuming a child idle beyond its 5-minute cache | ≤ 6.4% of cost | rebuilds triggered by a parent message after a 5–60 min gap |
| Subagents never block a foreground call > 270 s (`qex`, or background + Monitor) | 4.1% of cost; 15.5% of errors (blocked sleeps) | rebuild cost minus one cache read per 270 s leg |
| Two lines in the implementer prompt template: "tool is `Bash` (capital B)"; "Monitor needs `description`" | 9.0% of errors | 59 + 47 errors, all Sonnet subagents |
| PID-based runner for codex/Sol jobs (`qex` or `$!` + `tail --pid`) instead of `pgrep`/`pkill -f` | 7.4% of errors | process-management family |
| PreToolUse gate on AskUserQuestion unless your last prompt is < 2 min old | 3 of 14 corrections, plus the 30-min stall | hand labels |
| PreToolUse gate on Agent when in-flight subagents ≥ build-loop §9 cap | 5 of 14 corrections | hand labels |
| SessionStart(compact) hook that restarts the tick and requires the REREAD line | 7 of 44 lost keepalive chains; 42 of 44 missing build-loop re-reads | compaction table |
| PostToolUse on exit 127: suggest `nix shell nixpkgs#<pkg>` | 2.1% of errors | command-not-found family |
| Cap tool results at 10 k chars with a spill file | 1.3% of cost | excess re-read cost |
| Fire the tea hook only when a pipeline truncated output | 0.2% of cost | hook text × later calls |

## Where your setup differs

- **manual-keepalive / build-loop §10.** The skill says ticks keep the
  session in prompt cache, and it fixes 270 s. That is right for the default
  5-minute cache. Your main sessions run on the 1-hour cache, where Anthropic's
  docs say each hit refreshes the entry for free. The data says the tick is
  11× more frequent than the cache needs, at about a quarter of spend. One
  caveat: if ticks also keep T3 sessions alive or act as a clock (budget.md
  §10 uses "every ~5 ticks"), that need is separate from cache. Measure it on
  its own.
- **build-loop §9 (concurrency) and §2 (Sonnet implements).** Subagents are
  50% of cost. The two subagent behaviours the skills do not cover cost more
  than the parallelism they do: resuming idle subagents, and long foreground
  waits inside a subagent. Together that is 11% of spend. budget.md warns
  about `while pgrep` loops but not about `until grep -q DONE; sleep` waits
  outliving a 5-minute cache.
- **rg-implement / build-loop implementer prompts.** They carry no tool-name
  guardrails. Sonnet 5.5 subagents made 106 avoidable tool-name or parameter
  errors.
- **question-everything §3 (turn recurrence into checklists).** The data backs
  it. Stored-data / migration / export findings recur in round 2+ (28 of 83).
  The cls1 round-3 reply shows a checklist that existed but was answered
  wrongly. The skill asks the implementer to answer each line. It does not
  ask the reviewer to check the answers.
- **build-loop §6b (cap 3 tier-1 rounds).** The wake-pr changes predate it and
  ran to 5 rounds. The scored ledgers show some 2–3-round sequences, with ten findings still
  open across the six ledgers. Changed tasks, models and workflow prevent
  attributing convergence to the cap (**C**).
- **build-loop "after compaction, reread".** The summaries never carried the
  REREAD line, and the agent re-read build-loop after only 2 of 44
  compactions. The skill text alone did not change behaviour. The new hook
  is the right layer.
- **AGENTS.md "evaluate only the host you are on".** It shows up once in this
  data (1 evaluation of another host on nixed). It does no harm, but it is
  not exercised here.

## Candidate actions (ranked by expected value / cost)

1. **Pilot tick length against cache TTL and transport needs.** Test
   `sleep 3000` with a background timeout ≥ 3,300 s where the main cache is
   1 hour. The modeled gross reduction is 22.6% of estimated spend; net
   savings are unmeasured. Verify completion delivery, liveness and recovery
   before changing the general rule.
2. **Implementer prompt template: three lines.** No foreground wait over 270 s
   (use `qex` or background + Monitor). The tool is `Bash`. Monitor needs
   `description`. About 4% of spend and ~25% of tool errors for a template edit.
3. **Compare a fresh child with resuming an expired child.** The observed
   cache-write bucket is 6.4% of spend. A replacement has its own writes and
   rediscovery costs; no net saving or universal 4.5-minute cutoff is established.
4. **SessionStart(compact) hook that restarts the tick** and injects the
   REREAD line (partly built). Fixes 7 of 44 dead chains and the missing re-reads.
5. **PreToolUse gates for AskUserQuestion and the subagent cap.** These are
   the two most frequent correction themes (8 of 14). Skill text has not held
   either rule.
6. **Compact main sessions at ~300 k tokens through uw-agent.** Up to 10% of
   spend. Test it on one workstream first, because the rule-loss cost after
   compaction (finding 5) is real.
7. **Reviewer brief line: "check each checklist answer; a false 'done' is a
   blocker".** Targets the largest recurring review family.
8. **Low value; skip unless free:** result caps (1.3%) and tea hook narrowing
   (0.2%).

## Method

Scripts are in `data/claude/scripts/`. All are Python stdlib, run with
`python3 -I`, and stream one transcript line at a time (peak RSS 35 MB).
`run_all.sh` rebuilds everything. Bulky intermediate tables (commands,
prompts, per-call rows) go to `$DERIVED`, outside the repo; for this run that
was the session scratchpad.

- `survey.py`, `survey2.py`, `survey3.py`, `survey4.py`: schema surveys
  (record types, fields, enumerations); they print no content.
- `extract.py`: per-transcript metrics into `sessions.jsonl`, plus `calls`,
  `results`, `human`, `compactions`, `reviews` tables and a secret-pattern
  count. Dedupes API usage by message id, tool calls by tool_use id, and
  every record by uuid (T3 replays).
- `fit_prices.py`: least-squares fit of the harness `cost-state` USD, used
  as a cross-check.
- `compaction.py`: post-compaction windows (60 tool calls) against 184
  random baseline windows.
- `postcompact_sample.py`: prints redacted post-compaction stretches for
  reading by hand (3 stretches read, from 2 sessions).
- `reviews.py`, `review_rounds.py`: parse review ledgers and Sol reply files
  in `~/Documents/repos/*.research` and `/tmp` (read only).
- `failures.py`: error families, host and build patterns, retries, restarts.
- `analyze.py`: headline numbers and injection estimates into
  `aggregate.json`.

Rules and limits:

- **Cost.** Each API call is priced at list price per model (Opus 5.5:
  $4 input, $5 5-minute write, $8 1-hour write, $0.20 read, $20 output per
  MTok; Sonnet 5.5 half that; [pricing](https://platform.claude.com/docs/en/about-claude/pricing),
  read 2026-11-10). This is an estimate, not your bill; subscription usage
  is not billed this way.
- **Carry cost** of a tool result = chars ÷ 4 × the calls left before the
  next compaction × the read price. That is an approximation; it ignores
  segments preserved across compaction.
- **Rebuild** = a call whose cache write is more than half its context, with
  context over 20 k.
- **Exclusions.** The four phoe-nix sessions of this research batch
  (a7647621, 4040da30, 111b1b75, f005328e) are excluded from aggregates but
  kept in `sessions.jsonl`.
- **Prompt counts.** "Human prompts" = SDK prompts plus mid-turn queued
  prompts, minus delegate-task completions and context handoffs.
- **Error families and finding kinds** are regex-tagged. The correction
  themes are my hand labels.
- **`repeated_reads`** counts Read calls plus shell views
  (`cat`/`sed -n`/`head`/`tail`/`nl`).
- **Missing data.** The void host is missing, and so is Codex usage (a
  sibling file covers it). Sol review replies were found only where saved to
  disk.

## Sources

- Anthropic, "Prompt caching" (5-minute default, 1-hour option, write
  multipliers 1.25× and 2×, refresh on hit), read 2026-11-10:
  https://platform.claude.com/docs/en/build-with-claude/prompt-caching
- Anthropic, "Pricing" (Opus 5.5, Sonnet 5.5, Haiku 5.5 rows; 0.05× cache
  reads on Opus 5.5 and Sonnet 5.5; long-context rules), read 2026-11-10:
  https://platform.claude.com/docs/en/about-claude/pricing
- Your transcripts: `~/.claude/projects/` on nixed, 2026-10-17 to 2026-11-10.
  Review ledgers and replies: `~/Documents/repos/{edge,fauxx,polara-port}.research/`.
