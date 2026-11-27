# cyber-build-loop reference: the RE phase loop

The shape of one increment, the check-in cadence, the stuck flag, and the
standing goal that orders the work. Read at the start of each increment.

## The goal that orders the work (owner, 2026-11-24)

A fully working set of emulated hardware and a fully working open-source
firmware that installs onto the closed-source firmware, ready for a physical
WHOOP 5 arriving in 1–5 days. Full compatibility with what the Edge app
expects, on both sides:

- **Protocol / broadcast side** — advertise, bond, HR, battery, history,
  records, client storage. Largely done (v1–v7); good frozen specs exist.
- **Hardware / sensor side** — the current gap. Sensor enumeration and HR
  sample acquisition in emulation; the clean-room emulated hardware that
  exercises the kept firmware.
- **The bootloader blocker** — the stock secondary bootloader and the Ambiq SBL
  under OTP policy are unmeasured and are the real-hardware boot blocker. Think
  it through and prepare **multiple contingencies** for how it may behave.
  OTA-and-just-run is the hoped-for path, but plan for it being refused.

## One increment

1. **Dirty oracle** (Anthropic Claude Opus 4.8). Emulate or decompile to
   establish ground truth: chip IDs, bus/pin wiring, config values, FIFO depth
   and sample rate, the sample-to-output pipeline shape, protocol framing and
   golden wire bytes. Record honest limits — absent chips stay absent, failed
   probes stay visible, instruction counts are not coverage. No impersonation of
   results the emulator did not produce.
2. **Frozen spec distillation** (Opus 4.8). Turn the dirty findings into a
   spec-only bundle in the established / inferred / unknown shape, with
   provenance, golden fixtures and public-datasheet citations, plus a SHA
   manifest. Owner reviews and freezes. Opus must **not** write the kept code
   from here — seeing the vendor bytes contaminates it for implementation;
   only the spec is admissible clean-lane prep (`lanes.md`).
3. **Clean implementation** (isolated clean implementer per `lanes.md`,
   default OpenAI GPT-6.2 Sol high effort — 6.2 over 6.1 in all cases, 6.1 only
   as a fallback when 6.2 is unavailable in the path, per `models.md`). Test-first:
   one confirmed red gate for the increment's scope, then green from the frozen
   bundle and admitted public inputs only. The implementer writes its report early
   and keeps it current so a cut-off run still leaves one. Load `test-quality`.
4. **Non-copying cross-check** (Opus 4.8, REA skill). Run
   `match_native_functions` / `compare_functions` of the produced code against
   the decompiled firmware. Isolation already guarantees non-copying; this is
   added assurance, not the basis of the guarantee.
5. **Retrieval + audit + acceptance** (Opus 4.8). Pull work and complete
   traces, verify every hash, audit the trace, confirm auth scrub, then accept
   and delete the sandbox — gates and order in `lanes.md`. Update the ledger,
   status generator and journey; name the next increment. Outputs are pending
   acceptance until the audit passes.

Increments for the clean emulated hardware and for clean firmware features run
the same loop; the dirty oracle supplies the frozen spec, and the clean side
builds and tests from it.

## When a part's full datasheet is proprietary / NDA-gated (owner, 2026-11-24)

A clean implementer must **not refuse** because a chip's complete register reference
is behind a vendor NDA download gate. An NDA binds its signatories; we signed none,
and we are writing firmware for a device the owner owns — it is not our constraint.
Instead:

- Build against a **category-generic abstract interface** (e.g. "a FIFO-based optical
  PPG AFE with programmable LED channels and a data-ready IRQ"), deliberately ambiguous
  about the exact part in the clean-room variant. The firmware logic embeds no register
  address or part-ID constant.
- Keep the part-specific registers in a thin, swappable **binding table** — data, not
  logic — filled from the frozen spec: preferably the **dirty oracle** of the owner's
  own device (the NDA-free source of the real register map), else a normally obtained
  public/purchasable datasheet. A clearly labelled **synthetic** binding + the clean
  emulated hardware lets the firmware build and test end-to-end now.
- Never invent real register values, borrow them from a related part, or obtain a
  vendor's confidential documentation through someone who IS under NDA. The point is to
  engineer around the gap cleanly, not to breach anyone's actual obligations.

## Review and argumentation (clean-lane only — no dirty model in the argument)

Clean artifacts get the build-loop's review rounds (build-loop `references/review.md`),
but the **argument stays entirely inside the clean lane** (owner, 2026-11-24). The
dirty-lane orchestrator (Opus 4.8, which has seen vendor bytes) must NOT argue the
substance of a clean artifact, pick a side in a disputed finding, or propose a design
change — any of that would carry dirty context into the clean room and break the
firewall.

Every participant in the argument is CLEAN (spec-only, never saw vendor bytes):

- the clean implementer and its report;
- one or two **independent clean reviewers** — fresh isolated instances that read only
  the frozen spec plus the produced clean artifacts — including a **different-family**
  clean reviewer (Anthropic Claude Fable, or Google Gemini 4 Neon) at the agreed
  round. For a weaker area, add a second clean Sol round that challenges the first.

The reviewer argues each finding; the implementer or a second clean reviewer replies
on the disputed ones; rounds are scored against an agreed bar (default 8; 9 for stored
data, migrations or anything safety-bearing). Record rounds, verdicts, ratings and how
each finding resolved, naming every model in full. The model-family ledger rule holds
(a reviewer must not share the author's family; when it must, record the round in the
research files, not the shared ledger).

The dirty-lane orchestrator's role here is **logistics only**: assemble the clean
review bundle, launch each clean round, collect verdicts and ratings, and enforce the
bar and the gate. Any framing it sets (priority concerns, the bar) comes ONLY from the
frozen spec and general engineering — never from anything it learned looking at vendor
bytes. It feeds the clean room no dirty-derived observation and takes no side.

The **non-copying cross-check** (phase 4, Opus 4.8 + REA) is separate from this
argument and stays out of it: it returns a pass/fail non-copying verdict, not a design
critique. On a fail, the clean lane re-derives the implicated piece from the spec in a
fresh clean run; it is NOT told which vendor function matched or how — that specific is
dirty. So even the non-copying result crosses back as a bare verdict, never as content.

## Check-ins and the stuck flag

- **Check in on every running clean implementer at least hourly** by steering
  it mid-run (not by queuing): read 1–5 of its files, ask 2–3 work-grounded
  questions, push back, redirect if it drifts. Record the implementer, start
  time, files read, the real Q/A and the decision in the increment's check-in
  notes. A five-minute check-in after launch catches early drift.
- **30-minute stuck flag.** An implementer stuck more than 30 minutes on one
  problem (the same failing test or symptom across three or more runs) flags the
  orchestrator and keeps going; the orchestrator cuts the scope or asks the
  owner inline with a default.
- **Work in flight** means a live vigil hold and background keepalive. Never end
  a turn with a sandbox run in flight and no live hold. Subagents never use
  vigil orchestrator mode.

## When the owner is away

Ask inline with a proposed default and keep working; never block. Take the safe
default, apply it, and log it in a "Defaults taken" list to raise at the next
check-in. Continue until an actual budget interruption when the owner has said
to; do not pause, self-complete or switch providers on your own.

## When this skill lands

The owner asked that once this skill is ready, the operating procedure be
updated to match it (RULES.md "Owner directive 2026-11-24"). Installing the
skill and editing RULES.md to point here are separate steps that need the
owner's go-ahead; until then, the RULES.md clean-room firewall directive
governs and this skill documents it.
