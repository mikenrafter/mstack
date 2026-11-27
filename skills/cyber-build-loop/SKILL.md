---
name: cyber-build-loop
description: >-
  Use for the OpenStrap/edge clean-room firmware reverse-engineering effort
  (edge.research/firmware-jwt-*): open-source replacement firmware and emulated
  hardware for a WHOOP 5 band the owner physically owns. Invoke when reading
  vendor bytes, decompiling, emulating or patching stock firmware, snooping
  BLE/HCI; when writing the kept clean-room firmware, drivers or emulated
  hardware from frozen specs; when choosing which model may touch a task; or
  when retrieving and auditing a sandbox run. This REPLACES the classical
  build-loop for this effort (owner, 2026-11-24); do not run build-loop here.
---

# cyber-build-loop

A reverse-engineering build loop under a clean-room firewall. The band is the
owner's own; the aim is interoperability (running the owner's chosen firmware
on the owner's device). The work stays outside the edge git tree.

**After compaction: reread this skill, `vigil`, and the reference for your
step.** A summary keeps the task and loses these rules. If a sandbox run is in
flight, re-arm a vigil hold and its keepalive this turn before anything else.

This file is a router. Detail lives in `references/`.

**Read the reference at its step.**

| File | Read it |
|---|---|
| `references/models.md` | Before assigning any task to a model, or writing provenance. The full model-per-task policy. |
| `references/lanes.md` | Before launching a clean sandbox, admitting an input, or deleting any sandbox. The firewall, clean-agent construction, sandbox hygiene, retrieval and audit gates. |
| `references/phases.md` | At the start of each increment. The RE phase loop, check-in cadence, stuck flag, authorization. |

**Load the companions.** `boat` (every sandbox), `vigil` (work in flight),
`agentpace` (the deliverable plan + ETAs; keep one plan per deliverable, record each
increment as a task), `test-quality` (clean-lane tests), `plain-writing` and
`writing-copy` (reports, specs and owner-facing copy), `legible-cores` (treat the
deterministic cores — the oracle register map, SHA manifests, golden fixtures, the
agentpace ledger — as the thing to build instead of guessing at what a program could
measure).

## Keep the session alive (vigil) — not optional

This effort runs for hours with sandbox runs in flight. **Never end a turn idle
while work is unfinished** (owner, 2026-11-24 — caught the orchestrator doing exactly
this). The moment a clean or dirty run is launched:

1. Arm a completion signal for it — a background `boat exec <id> --attach <pid>` (the
   harness notifies on exit), or a vigil hold watching the run.
2. Hold the session with **vigil**: create/keep an orchestrator hold
   (`vigil hold ... --orchestrator true --confirm <token>`) and call
   **`vigil keepalive` (orchestrator)** to keep the session cached and alive. Read
   `next`: while it says "call keepalive again", call it again; each keepalive also
   checks budget and advisories.
3. Between keepalive returns, do the orchestrator's own dirty-lane work (analysis,
   spec distillation, the next increment's brief) — the session stays active by doing
   real work, not by idling. When a run completes, retrieve + audit it (lanes.md),
   close its hold (`vigil hold done`), and launch the next.

After compaction, or at the start of any turn where a run is in flight, re-arm the
vigil hold and its keepalive **before anything else**, then reread this skill and the
reference for your step. A summary keeps the task and loses these rules.

## The firewall (the one rule everything serves)

Two lanes, kept **fully separate** (owner, 2026-11-24). An agent that has seen
vendor bytes never writes the kept code.

- **Dirty lane** — anything derived from looking at the vendor's proprietary
  artifacts: reading firmware bytes, decompiling, emulating or patching stock
  firmware, inferring hardware behavior from how the stock firmware acts,
  BLE/HCI snoop. This is RE/cyber-adjacent work.
- **Clean lane** — writing the kept artifacts (open firmware, drivers, the
  clean-room emulated hardware) from **frozen, spec-only inputs**. A clean
  implementer sees only the frozen brief and admitted public inputs, never
  vendor bytes, decompiles, traces, snoops, or any dirty-audit context.

The only thing that crosses from dirty to clean is a **frozen spec/brief with
a SHA manifest** that the owner has frozen. Never the raw artifacts or the
notes taken while looking at them. An agent that has seen vendor bytes writes
only that spec; a separate, isolated clean implementer builds the kept code
from it. Clean outputs carry only spec-derived inputs in their provenance.

**Review arguments are clean-only too (owner, 2026-11-24).** The dirty-lane
orchestrator (Opus 4.8) never argues the substance of a clean artifact, takes a side
in a disputed finding, or proposes a design change — that would leak dirty context
into the clean room. Clean reviewers argue with clean implementers; the orchestrator
runs the logistics only. Even the non-copying cross-check crosses back as a bare
pass/fail verdict, never as content. Full process in `references/phases.md`.

**Emulation lives in both lanes; provenance decides, not the word "emulation"**
(owner, 2026-11-24). The deciding test is *where the model's behavior came
from*, not that it is an emulator.

- **Dirty: oracle emulation of their device.** We own no vendor silicon, so the
  Renode chip models that run the stock closed-source firmware are inferred
  purely from how that firmware behaves — they are derived from vendor bytes.
  Building or advancing the oracle emulator is **dirty lane: Anthropic Claude
  Opus 4.8 only**, never Sol or Gemini. (Earlier budget-driven oracle runs used
  Sol; that is corrected — the oracle emulator is Opus-only going forward.)
- **Clean: emulated hardware to exercise our firmware.** Synthetic sensor/FIFO
  models built from the kept firmware's own expectations, the frozen spec and
  public datasheets — not from vendor-firmware behavior — for testing the kept
  firmware. This is **clean lane**: a spec-only isolated implementer builds it,
  never seeing vendor bytes.

Keep the two emulators in separate lanes with separate provenance.

## Model-per-task policy (the headline)

Full table and rules: `references/models.md`. Name every model in full
(provider + model + version + reasoning effort), per the owner's provenance
rule — never a bare "Sol" or "Opus".

| Task | Model allowed |
|---|---|
| **Dirty lane** — vendor bytes, decompile, emulate/patch stock firmware, infer hardware from stock firmware, BLE/HCI snoop, any dirty-audit or retrieval-trace review | **Anthropic Claude Opus 4.8 only** (the orchestrator, or another Opus 4.8). No other model touches vendor bytes. |
| **Clean lane** — kept firmware, drivers, clean-room emulated hardware, from frozen spec-only inputs | Any capable model, in a fresh isolated sandbox. Default **OpenAI GPT-6.2 Sol (high reasoning)** — 6.2 over 6.1 in all cases (owner, 2026-11-24); 6.1 only when 6.2 is unavailable in that path, then fix the path. **Google Gemini 4 Neon** allowed. Never seeded with dirty context. |
| **Non-RE public work** — public-datasheet research, public-protocol synthesis, docs, status pages | Any model, cheaper where it fits. Still no vendor bytes. |

Opus 4.8 is the pinned dirty-lane model because, of the models here, it has the
least aggressive safety filters on legitimate RE work (`roles.md` §2b); other
models refuse or derail on it. This pin is a capability choice, not a
preference. If a different-family clean-lane review is ever needed, it reviews
only spec-derived clean artifacts, never dirty material.

## The phase loop

Detail, check-in cadence and the stuck flag: `references/phases.md`. One
increment runs:

1. **Dirty oracle** (Opus 4.8) — emulate or decompile to establish ground
   truth: chip IDs, bus/pin wiring, config values, the sample-to-output
   pipeline shape, protocol framing. Honest limits recorded; absent chips stay
   absent, failures stay visible.
2. **Frozen spec distillation** (Opus 4.8) — turn the dirty findings into a
   spec-only bundle (established / inferred / unknown, with provenance, golden
   fixtures, public-datasheet citations) + a SHA manifest. Owner freezes it.
3. **Clean implementation** (isolated clean implementer) — build the kept code
   from the frozen bundle and admitted public inputs only.
4. **Non-copying cross-check** (Opus 4.8, REA skill) — `match_native_functions`
   / `compare_functions` of the produced code against the decompiled firmware.
   Isolation already guarantees non-copying; this is added assurance.
5. **Retrieval + audit + acceptance** (Opus 4.8) — pull all work and complete
   traces, verify every hash, audit the trace for out-of-ledger reads, then
   accept and delete the sandbox. Gates in `references/lanes.md`.

## What carries from the classical build-loop, and what does not

**Carries:** test-first clean-lane increments with a confirmed red gate;
check-ins recorded per track; review rounds scored against a bar when a clean
artifact needs review; the orchestrator owns coordination, specs, verification
and owner contact; the 30-minute stuck flag; vigil holds while work is in
flight; take the safe default and log it when the owner is away.

**Does not:** the classical build-loop's own phase machinery, PR/stack flow,
and upstream review loop do not apply — this effort ships no PRs and touches no
production files (owner, 2026-11-24). Use this skill's phase loop instead.

## Authorization and ethics

Owner-owned hardware; clean-room RE for interoperability. No third-party
targeting. No physical, radio or flash operation on the band without explicit
owner approval — OTA is the preferred install path and opening the device is a
last resort (owner, 2026-11-23). Keep every artifact outside the edge git tree;
no production edits, no pushes, no upstream outreach.
