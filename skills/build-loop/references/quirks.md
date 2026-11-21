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

## Gemini Neon (untrialled here)

**Ends its turn while background work is still running.** It stopped while a data fetch ran and
resumed only when prompted.
- Brief line: "Never end your turn while work is in flight."
- Orchestrator: a completion without a deliverable gets one "continue until <deliverable>" send.
- Evidence: Theo review, 2026-11, collective.

**Misses a skill named in passing.** It did not trigger a skill named in a longer sentence.
- Brief line: name each skill on its own line, with the instruction to load it.
- Evidence: Theo review, 2026-11, collective.

**Analysis claims are often wrong; implementation claims less so.** 10 of 72 architecture claims
were wrong, yet its changes verified their claims.
- Orchestrator: treat analysis output as unverified until checked (`roles.md` §2b, mistake gravity).
- Evidence: Theo review, 2026-11, collective.
