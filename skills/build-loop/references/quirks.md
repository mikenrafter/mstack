# build-loop reference: model quirks (§2c, §7)

A quirk is a repeatable behaviour that costs time or quality unless handled. Each entry gives
what it does, how to detect it, and the defined response. Briefs carry the brief line; the
orchestrator carries out the orchestrator response. Add an entry when a quirk shows up twice, or
once with a written report from someone the owner follows. Remove one when two trials in a row
no longer show it. Record the date and source.

| Field | Meaning |
|---|---|
| Quirk | What the model does |
| Detect | The signal: a vigil note, a report pattern, a transcript check |
| Brief line | Text every brief to this model includes |
| Orchestrator | What the orchestrator does when it is detected |
| Evidence | Source, date, own use or collective |

## Sol (every gpt-*-sol version unless noted)

**Prints its verdict, then keeps running.** A review child writes its `VERDICT:` line, then works
on for hours. The parent waits on a run that has finished in substance.
- Detect: vigil `item overdue` on a Sol review item.
- Brief line: "End your turn right after the VERDICT line."
- Orchestrator: on the first overdue note, read the child once (`t3_thread_read`, small limit).
  If a `VERDICT:` line is there, take it, record it in the ledger, and `task_cancel` the child.
  Otherwise let it run and check again at `item far overdue`.
- Evidence: tstack issue (practice-watch 2026-11-20, 9–10 h waits five times in one night),
  collective, unverified here. Measure the overdue Sol rounds and the verdicts recovered.

**Builds heavy toolchains wherever it stands.** It runs `nix develop` / `cargo` / `nix build` on
the local host, which filled `/` on nixed (2026-11-19).
- Brief line: "Heavy builds run on Boat (or qex); keep ≥1 GB free on /."
- Orchestrator: before launching, name the build host in the brief. On a disk-full report,
  `nix-store --gc` and resume, never restart.
- Evidence: own use, 2026-11-19 (usagewindow).

**Never writes the press release.** This is a role rule, not a quirk (`front.md` §1b).

**Version 6.2 returns HTTP 400 here.** Use 6.1 until a probe succeeds.
- Evidence: own use, 2026-11-18.

**Commits fail in T3 sandboxes.** Codex mounts `.git` read-only (`sol.md` §4).
- Orchestrator: bundle-and-unbundle, as written there.

## Gemini Neon (trialled 2026-11-21, `roles.md` §2c)

**Ends its turn while background work is still running.** It stopped while a data fetch ran and
resumed only when prompted.
- Brief line: "Never end your turn while work is in flight."
- Orchestrator: a completion without a deliverable gets one "continue until <deliverable>" send.
- Evidence: Theo review, 2026-11, collective. Not seen in three trial runs carrying the brief line,
  which waited on Boat jobs correctly (own use, 2026-11-21).

**Reports work as done before it is measured.** In the owner's thread it said it had "implemented
60fps optimizations" before any profiling ran.
- Brief line: "Every performance or completion claim names the measurement behind it."
- Orchestrator: ask for the profile, timing or test output before relaying the claim.
- Evidence: own use, 2026-11-21 (T3 thread f360e6a4).

**May miss the prompt cache more often than other models (owner, 2026-11-21; re-evaluate weekly).**
Antigravity sets the cache server-side; no setting changes its TTL. Long threads also get expensive
anyway: Antigravity bills cached reads against the subscription pool, and the owner's thread reached
504k of a 512k context in 53 calls (17M cached tokens).
- Rule: start a fresh Neon agent instead of continuing one past ~100k context. Brief it from files
  (report, diff, state file), not from thread history.
- Detect: `mstack/bin/neon-usage <conversation.db>...` reads each conversation's cached and new input tokens from
  Antigravity's conversation DBs; a miss is a call whose cached tokens fall below half the previous
  context. `mstack.research/neon-trial/ttl-probe.sh` measures how long the cache survives idle gaps.
- Orchestrator: keepalive windows for a Neon session stay at 270 s until the probe shows a longer
  lifetime.
- Evidence: 2026-11-21, five Neon threads, 170 calls: 90-97% of input tokens cached, 2 misses (own
  use). The owner's suspicion is not confirmed yet; the weekly vigil reminder `neon-quirks` re-checks it.

**Answers check-ins in the final report, not in chat.** One of two runs did.
- Brief line: "Answer orchestrator check-ins in chat, then continue."
- Evidence: own use, 2026-11-21.

**Misses a skill named in passing.** It did not trigger a skill named in a longer sentence.
- Brief line: name each skill on its own line, with the instruction to load it.
- Evidence: Theo review, 2026-11, collective.

**Analysis claims are often wrong; implementation claims less so.** 10 of 72 architecture claims
were wrong, yet its changes verified their claims.
- Orchestrator: treat analysis output as unverified until checked (`roles.md` §2b, mistake gravity).
- Evidence: Theo review, 2026-11, collective.
