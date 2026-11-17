# build-loop reference: review schedule v2 (§6)

Applies to ledgers with `"schema": 2` (every new `init`). `review.md` has the
shared rules (score and bar, stashes, briefs, checkpoint, answering); this file
has who reviews which round and the commands that enforce it.

## Schema 2 and legacy ledgers

- `init` writes `"schema": 2`. A ledger without it keeps the legacy schedule for
  its whole life: Sol rounds 1-3, tier 2 fresh Opus, no ARGUE, no cull, `--author`
  optional. Never mix the two in one ledger.
- A schema-2 `round` needs `--author` (exit 2 without it).

## Authors

`--author sonnet,sol` is a comma list of every model that wrote code in the diff
this round reviews: round 1 and tier 2, everything since base; later rounds,
everything since the last reviewed sha. Models: sonnet, sol, opus, fable. The
ledger keeps the union. `round` exits 2 when the reviewer is in the list: a
reviewer never reviews code it wrote. `next` names the expected reviewer
(`reviewer: sol or opus, not the author of the fixes since <sha>`, or
`reviewer: fable`). It cannot name a model: the next author is whoever wrote
those fixes, so you pick a reviewer who did not.

## Schedule

| Round | Reviewer | If it passes | If not |
|---|---|---|---|
| Pilot: 1, then 2 | 1: Sol or Opus, not author; 2: Fable | All agreed concern bars met plus owner build thumbs-up: CHECKPOINT, NIT-CULL, FIX-KEPT, STOP-AGREED | Round 2: ARGUE, then STEP-BACK; normal caps after that |
| 1-2 | Sol or Opus | CHECKPOINT, then tier 2 | next round |
| 3 | Fable (`--reviewer fable`) | CHECKPOINT, NIT-CULL, FIX-KEPT, STOP-AGREED | ARGUE, then STEP-BACK |
| 4-5 (after a pivot) | Sol or Opus | same as round 3 | ARGUE (round 4), then next round; STOP-STUCK after round 5 (the owner decides) |

Pilot bars are agreed before starting with `init --pilot --bar concern=N` (repeatable)
and `--bars-agreed "<owner quote or note>"`. Defaults: durability 7, others 6;
`--touches-data` makes durability 9 when the pilot writes stored data, changes schema
or migrations, or sends notifications or other outward messages.
Only named concerns block; other concerns and findings not needed for the bars go to
`HARDENING-STASH`, reviewed at normal bars before an upstream PR opens/goes ready
or a project release. Owner-run integration branches need only normal structural review.
Record the build thumbs-up with `owner-ok "<quote>"`; no CHECKPOINT or STOP-AGREED
without it. A passing pilot round 1 still goes to Fable at round 2. Pilot init
leaves `bars.json` untouched. Structural and later reviews keep the table above.

Outside pilot mode, tier 2 is a fresh Opus pass; Fable if Opus is among the authors. After any
passing round 3, 4 or 5 there is no tier 2. The caps of `review.md` stay: 3
rounds per approach, 5 tier-1 rounds per phase, then STOP-STUCK.

## Fable runs (B3)

In pilot mode, every round-3 rule below applies at round 2 instead. Round 4 and
later caps stay unchanged. Opening hardening restores the normal bars and schedule.

Fable is a T3 `delegate_task` child at effort high, version from
`orchestrator_capabilities` (Fable 5.2 or later; the Agent tool's `fable` alias
returns 404 here). Never swap versions silently; tell the owner. Keep its task identity. Fresh T3 dialogue tasks receive the prior review and ledger;
never use `t3_thread_send` for review or rechecks. Every brief to Fable (round 3 review, pivot, cull, and
a tier 2 Fable pass) starts with the ledger's line "Fuck me up, fam. Balls to
the wall: say what you actually think, torch a wrong approach, and say ship it
when it is good enough. No hedging, no asking permission." Sol and Opus briefs do not get it.

## Argue (every round)

Every new schema-2 round requires at least one orchestrator/reviewer exchange,
including clean approvals and tier-2 reviews. Every Fable round requires at least
two. The existing two-exchange minimum on non-clean tier-1 round 4 remains.
The ledger captures `exchange_minimum`; outcomes and later scores cannot waive
it. Historical completed rounds without that field retain their previous rules.

Read `dialogue.md`. `next` returns ARGUE until the minimum is met. An exchange
challenges a material assumption, checks a proposed fix, or explains why the
simplest approach is enough. It need not manufacture disagreement. Save both
speakers as `Orchestrator:` and `Reviewer:` sections, then run
`review-ledger -l LED argue --note FILE`. Empty, one-sided and exact duplicate
notes cannot count. More exchanges remain possible when useful.

For T3 reviews and rechecks, start a fresh `delegate_task` containing the review,
focus, objection and ledger. Do not continue a delegate with `t3_thread_send`.
For native agent dialogue, use its supported messaging route. Each answer must
explain whether the challenged scenario applies. A reproduction or clear causal
path decides facts; scores alone do not.

Only revised reviewer SCORE and VERDICT lines belong in the note; do not quote
old score lines, because the first match wins. These revisions replace the
round's scores/verdict while preserving originals. Close settled findings with
`outcome`. Parent verification of small final fixes still applies.

## Step-back

Round 3 below the bar: `next` returns STEP-BACK and `brief` prints a pivot
question. Send it to a fresh Fable dialogue task with the review and objections: "You rejected this. What should I pivot to instead?
At most 15 lines." Take the answer to the owner if it changes scope, then run
`new-approach`.

## Nit cull

After a passing round 3+ and its checkpoint, `next` returns NIT-CULL when open
nit findings or nit-stash items exist. `brief` lists each with its id (`S<n>`
finding, `N<n>` stash item) and text, and asks for one line of reason per kept id.

```sh
review-ledger -l LED brief > cull.txt        # send to the Fable thread
review-ledger -l LED cull --reply reply.txt  # reply holds "KEEP: S2, N1" or "KEEP: none"
review-ledger -l LED outcome N1 fixed        # stash ids work like S ids
```

At most 2 ids (more: exit 2, ledger unchanged). The rest become `discarded`, a
closed outcome still listed by `status` and `stash`. While a kept item is
neither fixed nor declined, `next` returns `FIX-KEPT: <ids>`: fix them yourself,
no new round. When all are closed, or KEEP was empty: STOP-AGREED.

## Comment fixups (A7)

Reviewers are review-only except comments. If comments need it, the reviewer
rewrites comments only (no code, no docs), with `unslop` loaded, and lists each
under `COMMENT-FIXUPS:` as `- <file>:<line> <what changed>`. Sol returns a patch
(`.git` is read-only). `round` stores the section; `status` shows it. Check the
patch touches only comments before you apply it. No new round is needed. Comment-only fixups do not count as authorship for R2, so their writer need not go in the next round's `--author` list.

## Ledger commands

```sh
$RL -l $LED round --tier 1 --reviewer fable --author sol,sonnet --sha <sha> --reply reply.txt
$RL -l $LED argue --note note.txt
$RL -l $LED cull --reply reply.txt
$RL -l $LED outcome N1 fixed|declined --evidence "..."
$RL -l $LED next    # ROUND | ARGUE | STEP-BACK | CHECKPOINT | NIT-CULL | FIX-KEPT: <ids> | STOP-AGREED | STOP-STUCK
```
