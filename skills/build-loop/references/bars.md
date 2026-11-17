# Choosing the bar

Set bars at `review-ledger init`, before round 1. It prints each touched concern's
bar and why. Normal bars follow shape × stage; robustness rises later. Bars are
integers 6–10, usually 7–8. Ramps stop at 9; 10 needs an architecture peak or owner floor.

**Each concern has its own bar.** Scores and findings are judged against their own
concern's bar. The highest bar is only a summary line.

## Pilots

`init --pilot --bar concern=N` (repeatable) with `--bars-agreed "<owner quote or note>"`
records the feature's agreed concerns/bars before starting. Defaults: durability 7,
others 6; `--touches-data` selects durability 9 when the pilot writes stored data,
changes schema or migrations, or sends notifications or other outward messages.
Other concerns go to the hardening stash. Pilots leave `bars.json`
untouched; normal stage bars and schedule resume at hardening. See `scoping.md`.

## Shape (`--shape`, or the facts it comes from)

Name the shape with `--shape`, or declare facts and the script derives it (first
match wins; unset facts: direction no, users no, formats reversible, lifespan long).
Give one or the other, not both.

| Facts | Shape |
|---|---|
| `--throwaway`; or `--lifespan short`, formats reversible, no users, no outside consumers | `spike` |
| direction known, users yes, `--outside-consumers no` | `rewrite` |
| direction known, users yes, consumers yes or unset | refused (`rewrite` or `library`?): pass `--shape` |
| `--outside-consumers yes`; or users yes, costly formats, consumers unset | `library` |
| direction known | `port` |
| otherwise | `explore-first` |

- `explore-first`: greenfield, direction unknown. Legibility first (9/8/7);
  architecture peaks late (10 at beta).
- `port`: direction borrowed from prior art. Architecture peaks at once (10 at prototype).
- `rewrite`: replaces a system with users. Architecture and compatibility high from
  prototype; robustness rises a stage earlier than `explore-first`.
- `accretion`: a new region in a mature codebase, with its own stage (usually
  prototype) and its own `--region`.
- `pivot`: an owner-declared reset of a region to prototype; legibility 9/8/7.
- `spike`: throwaway, all bars 6. The ledger notes "no review needed" unless the
  owner asks or the diff touches security.
- `glue`: integration and host config. Architecture 6-7; wiring, rollback and blast
  radius 8-9.
- `research`: measurement. Validity 9 from the start; code quality 6-7.
- `library`: outside consumers. API and compatibility reach 9 at the first outside user (beta).

Only these nine. `accretion`, `pivot`, `glue` and `research` are never derived:
name them.

## Stage (`--stage`, per region)

`prototype`, `beta` or `production`. A region is a module or path (`--region`;
default the whole repo). Choose it from these signals; the script does not compute it.

- prototype: nobody depends on it; no release, no data worth keeping.
- beta: first outside users, data the owner cares about, or a first release.
- production: released; others rely on it; stored data; defects have escaped.

If signals disagree, take the later stage and say why.

### Ratchet

A region's stage only rises on its own. `init` records region, shape and stage in
`<project>.research/review/bars.json` and reuses them when the flags are absent. It
refuses a lower stage or different shape (exit 2). Only the owner lowers a stage
or changes a shape, with an entry:

```json
{"stages": [{"region": ".", "stage": "prototype", "shape": "pivot", "reason": "...", "date": "..."}]}
```

An entry applies once; then the stage rises on its own again. An entry without
`shape` keeps the recorded shape: a stage reset does not unlock a shape change.
A new `pivot` needs an entry with stage `prototype`.

## The table (bar by prototype/beta/production)

| Concern | explore-first | port | rewrite | accretion | pivot | spike | glue | research | library |
|---|---|---|---|---|---|---|---|---|---|
| legibility | 9/8/7 | 7/7/7 | 7/7/7 | 8/7/7 | 9/8/7 | 6/6/6 | 7/7/7 | 7/7/7 | 7/7/7 |
| architecture | 7/10/8 | 10/8/8 | 9/10/8 | 7/10/8 | 7/10/8 | 6/6/6 | 7/7/6 | 6/6/6 | 8/9/9 |
| testability | 8/8/8 | 8/8/8 | 8/8/8 | 8/8/8 | 8/8/8 | 6/6/6 | 7/7/7 | 7/7/7 | 8/8/8 |
| concurrency | 7/8/9 | 7/8/9 | 8/9/9 | 7/8/9 | 7/8/9 | 6/6/6 | 7/8/8 | 6/6/7 | 7/8/9 |
| durability | 7/8/9 | 7/8/9 | 8/9/9 | 7/8/9 | 7/8/9 | 6/6/6 | 8/9/9 | 6/7/7 | 7/8/9 |
| performance | 7/7/8 | 7/7/8 | 7/8/8 | 7/7/8 | 7/7/8 | 6/6/6 | 7/7/7 | 6/6/7 | 7/7/8 |
| compatibility | 7/8/9 | 7/8/9 | 9/9/9 | 7/8/9 | 7/8/9 | 6/6/6 | 8/8/9 | 6/6/7 | 7/9/9 |
| observability | 7/7/8 | 7/7/8 | 7/8/8 | 7/7/8 | 7/7/8 | 6/6/6 | 7/8/8 | 6/7/7 | 7/7/8 |
| error-paths | 7/8/8 | 7/8/8 | 8/8/8 | 7/8/8 | 7/8/8 | 6/6/6 | 8/8/8 | 6/7/7 | 7/8/8 |
| docs | 7/7/8 | 7/7/8 | 7/7/8 | 7/7/8 | 7/7/8 | 6/6/6 | 7/7/7 | 6/7/7 | 7/8/8 |
| wiring | 7/8/8 | 7/8/8 | 8/8/8 | 8/8/8 | 7/8/8 | 6/6/6 | 8/9/9 | 6/7/7 | 7/8/8 |
| measurement | 7/7/7 | 7/7/7 | 7/7/7 | 7/7/7 | 7/7/7 | 6/6/6 | 7/7/7 | 9/9/9 | 7/7/7 |

Architecture is the only concern that reaches 10, and only at its peak stage.
Every other concern stops at 9. Security is not in this table.

## Security: the threat model sets the bar

Security has no fixed floor; its bar comes from the threat model. Ask the owner for
one at the start (§1). `--threat-model FILE|TEXT` (alias `--usage-model`) states
three facts as `Label: value` lines; a list takes its worst value.

| Fact | Values, mildest first, with the bar each gives |
|---|---|
| `Reach:` | local-single-user 7, other-local-users 8, network 9, public 9 |
| `Untrusted:` | none 7, local-data 8, network-input 9, third-party-code 9 |
| `Holds:` | nothing 7, owner-data 8, secrets 9, others-data 9 |

The security bar is the highest of the three. A spike's 7 becomes 6. 10 comes
only from an owner floor. A model that omits a fact stays at 9 and `init` says so.

- **Stored once.** `init` writes it to `residual/threat-model.md` with inline metadata, else to
  `<project>.research/review/threat-model.md`, and reads it back when the flag is absent.
- **Inferred until confirmed.** With none, pass `--project-kind` (cli-tool,
  local-service, network-service, library, browser-extension, nix-host). The script
  stores a guess marked `inferred`; ledger and brief say so. Ask the owner, then run
  `review-ledger threat-model --confirm`. `--threat-model` replaces any stored model.
- **Findings respect it.** A security finding needs an attacker the model includes;
  anything else goes to the hardening stash.

## Categories (`--category`, repeatable)

A category names the concerns the diff touches. Each touched concern keeps its own
bar. No category means `logic`. A concern name also works as a category.

| Category | Concerns |
|---|---|
| `logic` (default) | legibility, error-paths |
| `ui` | legibility |
| `test` | testability (a test that weakens an assertion also needs `logic`) |
| `docs`, `tooling` | docs |
| `permissions`, `consent`, `pii`, `signing`, `egress` | security |
| `durable-state`, `migration` | durability, compatibility (respectively) |
| `concurrency` | concurrency |

Data the owner cannot recreate: add `--category security`. Split a mixed diff when
its high-bar part separates cleanly.

**Scoring.** The reviewer gives `SCORE[concern]: n/10`, one line per touched
concern. Each must meet its own bar. A lone `SCORE: n/10` counts for every
concern. A finding names its concern (`[concern: x]`, or the class implies it).
`--bar N` (an integer 6 to 10) sets every touched concern to N.

## Recurrence: +1, capped at 9

A class (canonical slugs; `review-ledger` lists them) is hot for a diff when, in the
last three ledgers, it has two or more findings in the changed paths, or one marked
`escaped` (it shipped). A hot class adds 1 to each touched concern and the brief
names it. A bar of 9 or 10 stays. It lasts until §6c moves the class to a structural
layer (type, lint rule, wiring test) and a later loop finds no instance.

Order: table (security from the threat model), recurrence, owner floors. An owner
floor in `bars.json` (`owner`: `paths`, `bar`, `reason`) is an integer 6 to 10;
anything else is ignored with a warning.

## Stashes

- A blocker or should needs a **realistic reproduction** under the threat model: who
  does what, how often. A finding without one goes under `HARDENING-STASH:` in the
  reviewer's reply, not into the round.
- While any blocker or should is open, nits go under `NIT-STASH:`.
- The ledger stores both; `brief` hides them; `review-ledger stash` prints them.
- The nit stash opens at the §6c checkpoint. Fix only nits that ONE central change
  solves and that map to a code practice or feature facet (a lint rule, a helper, a
  convention). Decline the rest with a reason.
- Open hardening with `review-ledger hardening` (`--from` imports earlier stashes),
  before an upstream PR opens/goes ready or a project release. Owner-run integration
  needs structural review only. A new phase: fresh round caps, checkpoint, full-diff brief,
  at the bars of the stage after the one the items were filed in.

## Residual

If residual is set up (`residual/` or its sidecar), use it as evidence: components
name regions, `residues.csv` force counts measure coupling, attractor negative states
give the cost of a miss. Cite them in the bar reason. The script prints residual
evidence and never applies it. If it is not set up, do not set it up just to rate a diff.

## Ask the user

- The threat model (reach, untrusted inputs, what it holds), then confirm an inferred one.
- Any 10 outside architecture's peak. Propose candidates (irreversible, large state
  space: egress fail-closed, signing keys, the consent gate); record each decision
  under `owner` in `bars.json` as a floor.
- Lowering a stage, changing a shape, a `pivot`, or a new shape.
- Work leaving their control (upstream PRs, releases, public repos); disputes after
  two replies (§6d); legal or third-party exposure.

`init` refuses a lower bar, or an unasked 10, without `--bar-reason`. `--bar 10` caps non-peak concerns at 9.
