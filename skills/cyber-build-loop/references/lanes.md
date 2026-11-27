# cyber-build-loop reference: the firewall in practice

How to keep the clean lane verifiably clean: admitting inputs, constructing a
clean agent, sandbox hygiene, and the retrieval + audit gates. Read this before
launching a clean sandbox, admitting an input, or deleting any sandbox.

## What may cross from dirty to clean

Only a **frozen spec/brief with a SHA manifest**, owner-frozen. The spec states
each fact as established / inferred / unknown, carries its provenance (which
public datasheet, which already-admitted public protocol library, which oracle
observation), and includes golden fixtures the clean side reproduces
bit-for-bit. Raw vendor artifacts, decompiles, emulator traces, BLE snoops and
the working notes taken while reading them never cross.

Already-admitted public inputs may also be admitted directly: public datasheets
(cited by URL), the public WHOOP-protocol libraries the owner has admitted, the
pinned Flutter/Dart SDK and locked public dependencies, and prior **clean**
firmware/spec outputs. Each admitted file is admitted individually and verified
by SHA before launch.

An agent that has seen vendor bytes is contaminated: it writes the spec, not
the kept code. If a prior agent's context touched mixed research notes or a
vendor artifact, its output is excluded regardless of whether vendor code was
actually read — host context that cannot be certified clean does not enter the
clean lane (this happened once: an agent read a mixed research ledger and its
work was quarantined).

## Clean-agent construction rule (owner, 2026-11-23)

Every clean implementer runs as a fresh CLI process entirely inside a fresh
Boat `--no-snapshots --no-env` sandbox. No T3 host delegate with access to the
research tree. The coordinator (Opus 4.8):

1. Installs the CLI in the fresh sandbox (record CLI version and model identity).
2. Uploads **only** individually admitted inputs and a fresh brief — nothing
   inherited from any prior conversation, session or host config/rules.
3. SHA-verifies every admitted input remotely before launch; a verify that
   runs while the upload is still in progress fails, so verify only after the
   upload completes.
4. Copies authorized CLI auth without logging its content, mode 0600.
5. Arms EXIT cleanup (shred auth/config on exit) **and** an independent timed
   auth overwrite/delete safeguard (e.g. a systemd timer ~125 min), so
   credential safety never depends on the coordinator being re-invoked.
6. Releases the agent only after the collector is armed (below).

Use no host config, no host rules, no inherited conversation, no resumed
session. Keep SDK, caches and build output outside the clean workspace from
first use (set a cache prefix outside the workspace) so later retrieval of the
workspace cannot drag in out-of-lane files.

## Sandbox hygiene

- **Dirty sandboxes:** `--no-snapshots`, auth-scrubbed, `boat delete`d only
  after the work AND its traces pass retrieval verification.
- **Clean sandboxes:** `--no-snapshots --no-env`, same deletion gate.
- The collector **never deletes a VM before audit.** Deletion is a separate
  manual `boat delete` that follows the gates below, in order. Never delete a
  sandbox before a verified retrieval.
- Leave untracked same-name sandboxes you did not create alone; confirm
  ownership before touching one.

## Retrieval and audit gates (owner, 2026-11-23)

Before accepting any output or deleting any sandbox, in order:

1. **Retrieve everything** — the entire workspace (admitted inputs unchanged,
   final source, tests, fixtures, failed attempts, verification logs, generated
   manifests) AND the complete agent/runtime traces (the run log, final report,
   run script, EXIT and auth-scrub markers, the wrapper's stdout/stderr, and the
   CLI session transcripts). Inventory the trace paths before packaging. Never
   collect auth.json, config.toml or any credential store.
2. **Build a remote SHA256 manifest** covering all retrieved work and trace
   files; transfer it with the archive.
3. **Verify locally** — the archive and every listed file hash; confirm the
   admitted inputs are unchanged and the delivery hashes match. Re-pull on any
   mismatch; do not delete.
4. **Audit the trace** — inspect the complete trace for reads, downloads or
   tool calls beyond the admitted inputs and permitted public dependencies.
   Record audit scope, findings, and any missing or truncated evidence. A
   generic read outside the ledger (e.g. the sandbox's own Boat skill) is
   disclosed and the file reviewed; a project/vendor/mixed-research read is a
   breach and excludes the output.
5. **Confirm auth is gone** — auth/config absent and the scrub marker present —
   then `boat delete`, then confirm the sandbox is gone from `boat list`.

A clean input bundle alone does not prove the run stayed clean: trace
completeness and observed compliance are checked **separately**. Logs do not
prove unobserved behavior; claim only what the trace shows. Retain the raw
traces. Outputs stay **pending acceptance** until the audit is complete. Never
resume a clean implementer with dirty audit context.
