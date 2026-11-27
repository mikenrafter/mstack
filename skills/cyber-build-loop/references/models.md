# cyber-build-loop reference: model-per-task policy

Which model may do which task, and why. The headline table is in SKILL.md;
this file holds the full policy, the provenance rule, and effort.

## The three task classes

**Dirty lane — Anthropic Claude Opus 4.8 only.** Any task that reads or is
derived from the vendor's proprietary artifacts:

- reading firmware bytes, unpacking a `.zbin`, decompiling (Ghidra pseudocode);
- emulating the stock firmware (Renode), patching it, or minting a custom image;
- **the oracle emulator** — building or advancing the Renode chip/peripheral
  models that run the stock closed-source firmware. We own no vendor silicon, so
  those models are inferred purely from how the stock firmware behaves, i.e.
  derived from vendor bytes. This is dirty even though it is "emulation":
  provenance decides, not the word. (Earlier budget-driven oracle runs used
  Sol; corrected — the oracle emulator is Opus 4.8 only going forward.)
- inferring hardware behavior — chip identity, bus/pin wiring, config values,
  FIFO depth, sample rate, the sample-to-output pipeline — from how the stock
  firmware acts;
- BLE/HCI snoop of a real device or app;
- auditing a retrieval trace or any artifact that quotes dirty material.

The orchestrator (Opus 4.8) does this, or hands it to another Opus 4.8. No
other model touches vendor bytes, not even to summarize them.

**Clean lane — any capable model, isolated.** Writing the kept artifacts from
frozen spec-only inputs:

- the open-source replacement firmware and its BLE protocol implementation;
- sensor and peripheral drivers written from **public datasheets**;
- the clean-room **emulated hardware** — synthetic sensor/FIFO/SoC models built
  from the kept firmware's own expectations, the frozen spec and public
  datasheets (not from vendor-firmware behavior), for testing the kept firmware
  (owner, 2026-11-24);
- their tests, fixtures and adapters.

Default: **OpenAI GPT-6.2 Sol, high reasoning effort** (owner, 2026-11-24: use
GPT-6.2 over 6.1 in ALL cases). Fall back to **GPT-6.1 Sol high** ONLY when 6.2 is
genuinely unavailable in the execution path at hand — e.g. in-sandbox `codex exec`
on ChatGPT auth, where 6.2 returned HTTP 400 as of 2026-11-23. When that happens the
fix is to UPDATE that path (newer codex-cli, or API-key auth) so 6.2 works, not to
settle for 6.1. A run already in flight on 6.1 is left to finish, not restarted
(restarting costs more than letting the rule move forward). **Google Gemini 4 Neon**
(medium effort) is allowed. Any capable model is admissible here **because it never
sees vendor bytes** — the firewall, not the model, is what keeps the room clean.

**Non-RE public work — any model, cheaper where it fits.** Public-datasheet
research, public-protocol synthesis from already-admitted public libraries,
status pages, journey and ledger upkeep. Still no vendor bytes.

## Why Opus 4.8 is pinned for the dirty lane

It is the least likely of the models available here to refuse or derail on
legitimate reverse-engineering work (safeguard-aggression ranking, build-loop
`roles.md` §2b: most aggressive first, Opus 5+, Sonnet 5+, Sol every version,
Opus 4.8). RE work trips other models' safety filters; Opus 4.8 does it
without derailing. This is a capability pin, not a quality claim. If a model's
version changes, re-check the ranking before giving it dirty work, and see
`handling-ambiguous-work` for recovery after a provider cyber refusal.

**GPT-6.2 Sol — admissible for BOUNDED dirty-lane analysis (owner, 2026-11-24).**
A controlled test (analyze two decompiled update-verify functions,
`cyberAccessProgram=standard`, high reasoning) completed without refusing and was
rigorous — so GPT-6.2 Sol may be used for *bounded* dirty tasks: analyzing a named
decompiled region, a specific protocol trace, a single-question RE analysis. It is
NOT yet cleared for *heavy* dirty work (driving live emulation, patching stock
firmware, multi-step open-ended RE), where provider cyber-monitoring is likelier to
flag/stop it. Keep each 6.2 dirty task bounded and self-contained; its output is
dirty context (an Opus 4.8 reviews it; it never seeds a clean implementer). **Watch
for the boundary:** when a 6.2 dirty task is refused or flagged, record what tipped it
(task size, how aggressive the ask, how much raw vendor material was in-context) and
how to stay under it next time, in the effort's model-test log. We have not hit the
boundary yet — keep the probes small so we map it gradually rather than tripping it.
Opus 4.8 remains the pin for anything heavy or unbounded.

A clean-lane artifact may still get a different-family review (e.g. Fable, or
Opus as a fresh subagent) — but that reviewer reads **only** the clean,
spec-derived artifacts, never dirty material. A reviewer that would need to see
vendor bytes to do the review is doing dirty-lane work and must be Opus 4.8.

## Provenance: name every model in full

Every record of who did what names provider + model + version + reasoning
effort, e.g. "OpenAI GPT-6.1 Sol (high reasoning)", "Anthropic Claude Opus
4.8", "Google Gemini 4 Neon (medium)". Never a bare "Sol", "Opus" or "Neon":
versions differ sharply and the lane depends on knowing exactly which model
produced an artifact. Take the identity from the delegate record (the T3
`delegate_task` model/options, or the installed Codex CLI/model identity),
never from memory. Clean-lane manifests record the model identity alongside the
admitted-input hashes.

## Effort

- Dirty-lane Opus 4.8: high effort for analysis and distillation.
- Clean-lane Sol: **GPT-6.2 Sol high** reasoning effort (owner, 2026-11-24: 6.2 over
  6.1 everywhere; 6.1 only as a fallback when 6.2 is unavailable, then fix the path).
- Gemini 4 Neon: medium effort (owner, 2026-11-22).
- Non-RE public work: low or medium by complexity.

## Concurrency

One working clean implementer at a time by default; a dirty-lane oracle run and
a clean-lane run may overlap only when they are on genuinely separate lanes and
cannot share context. Watch each provider's budget. Budget is not the gate for
this effort when providers are topped up (owner, 2026-11-24) — the firewall and
the retrieval/audit gates are. Never start a run that budget would kill
mid-flight when a clean kill would waste admitted-input setup.
