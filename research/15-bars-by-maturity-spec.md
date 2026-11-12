# Spec: review bars by lifecycle shape and maturity (build-loop), 2026-11-11

Owner direction (this session): PLAN W23, W35, W35a, W35b. Encode into build-loop's
`references/bars.md`, `references/review.md`, `SKILL.md` §6 summary, and `scripts/review-ledger`.

## Why

paneweft v1 spent 8 review rounds mostly on concurrency/durability races no real user would hit
yet. The bar was an automatic 9 for `concurrency`/`durable-state` regardless of the project's
age, and the ledger's threat model was empty, so reviewers assumed hostile multi-writer use.
Early in a project, finding the direction (legibility) and the costly-to-change architecture
matter most; robustness matters later. Bars must follow the project's life.

## Claims

- **B1 range.** Every bar is an integer 6..10. Most bars are 7 or 8. 6 is the taper floor (a
  concern that has stopped mattering for this region); 10 is rare.
- **B2 ramp cap.** A rising concern reaches at most 9. Exceptions that may reach 10: (a)
  `architecture` at its peak (owner rule, automatic, no extra approval); (b) an owner floor in
  `<project>.research/review/bars.json`. Known recurring bug classes keep the existing +1, capped
  at 9 (10 only via the exceptions).
- **B3 inputs.** `review-ledger init` takes `--shape` (one of the nine below) or the declared
  facts it is derived from: `--direction-known yes|no`, `--users-at-start yes|no`,
  `--formats reversible|costly`, `--lifespan short|long`, `--throwaway`. Plus `--stage
  prototype|beta|production` (per region; the computed or owner-set stage). Existing
  `--category` stays and selects which concerns the diff touches.
- **B4 shapes** (each a table: concern × stage → bar, within B1/B2):
  1. explore-first: legibility high early; architecture rises to a late peak (10 at beta), then tapers.
  2. port/recast (direction borrowed from prior art): architecture peaks at prototype (10).
  3. rewrite/replacement: architecture and compatibility/migration high from prototype; robustness rises a stage earlier than explore-first.
  4. accretion in a mature codebase: a new region uses its own stage (usually prototype) even when the repo is production.
  5. pivot: an owner-declared reset of a region to prototype (exploration resurges).
  6. spike/throwaway: all bars 6; output is knowledge; the ledger notes "no review needed" unless the owner asks.
  7. integration/glue: architecture low throughout (6–7); wiring (`prod-wiring`), rollback and blast radius 8–9.
  8. research/measurement: measurement validity high early (9); code quality 6–7.
  9. library with outside consumers: API/compatibility steps to 9 at the first outside user (stage beta or later).
  Concerns in the tables: legibility, architecture, security, testability, concurrency, durability/recovery, performance, compatibility/migration, observability, error-paths, docs. Map the existing categories onto them; keep `permissions`/`consent`/`pii`/`signing`/`egress` (security) at ≥8 at every stage — security does not wait for maturity.
- **B5 the diff's bar** = max over the concerns its categories touch (as today), then recurrence +1 (cap 9), then owner floors. `init` prints the shape, stage, each touched concern's bar and why.
- **B6 usage and threat model required.** `init` requires `--usage-model` (who calls it, how many at once, which inputs are untrusted). The brief prints it. Empty or `-` is refused.
- **B7 realistic reproduction.** The brief tells reviewers: a blocker/should needs a realistic reproduction under the usage model (who does what, how often). Findings without one go to the **hardening stash** (`HARDENING-STASH:` section of the reply), not the round.
- **B8 nit stash (W23).** While any blocker/should is open, reviewers put nits under `NIT-STASH:`. The ledger stores both stashes; `brief` hides them; `stash` prints them; the nit stash opens at the §6c checkpoint; at that point fix only nits solvable by ONE central change that maps to a code practice or feature facet, decline the rest with a reason.
- **B9 hardening phase.** The hardening stash opens only in a separate hardening phase: at a stage change (prototype→beta→production), or by owner call (`review-ledger hardening`), never as part of an ordinary quality round. A hardening phase uses the next stage's bars.
- **B10 ratchet.** The stage a region uses only rises automatically; lowering it needs the owner (recorded in bars.json). Shape and stage are recorded in the ledger so later loops reuse them.
- **B11 compatibility.** Existing ledgers without these fields still load; `init` without `--shape`/`--stage` defaults to the declared-facts default (explore-first, prototype) and prints that it did so.

## Tests (red first)

Script tests in `scripts/tests/test_review_ledger.py`: range and caps (B1/B2) for every shape ×
stage; architecture 10 only at its peak and via owner floors; security ≥8 everywhere; recurrence
cap; usage model required; both stashes parsed and hidden from `brief`; `stash` and `hardening`
subcommands; ratchet refuses an automatic downgrade; old ledgers load. Keep `test_skill_size.py`
passing (SKILL.md stays small: §6 gets one or two lines; detail lives in references/bars.md).

## Defaults taken

- D1 shapes are a fixed list of nine for now; adding one is an owner call.
- D2 maturity signals (releases, users, stored data, escapes, residual churn) are documented in
  bars.md as how to choose `--stage`; computing them automatically is later work (W35a).

## Amendment A1 (owner, 2026-11-11, during review r1): security follows the real threat model

Replaces "security ≥8 at every stage" (B4) and the spike security floor.

- **B12 threat model drives security.** The security bar comes from the project's threat model,
  not from a fixed floor. Inputs per region: who can reach it (local single user / other local
  users or agents / network / public), what is untrusted (none / files or captured data /
  network input / third-party code), what it holds (nothing / the owner's data / secrets /
  others' data).
  Bars: no reachable untrusted input and nothing held → 7 (6 in a spike); local untrusted data → 8; network-reachable, secrets, or others' data → 9;
  10 only by owner floor.
- **B13 upfront, from the owner, held in residual.** The threat model is asked of the owner at
  the start (build-loop §1 discussion) and stored with the project's residual data (or
  `<project>.research/review/threat-model.md` when residual is not set up), so every loop and
  every brief reuses it. If the owner has not given one, the agent derives a default from the
  project's kind (CLI tool, local service, network service, library, browser extension, Nix
  host config) and marks it `inferred` in the ledger and brief until the owner confirms.
- **B14 findings respect it.** A security finding needs an attacker the threat model includes. Anything outside it goes to the hardening stash. `init --usage-model` (B6)
  becomes `--threat-model FILE|TEXT`, covering usage and threats together.
