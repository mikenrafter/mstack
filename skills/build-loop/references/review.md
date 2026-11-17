# build-loop reference: review rounds (§6a–§6d)

Read before round 1. SKILL.md §6 has the tier table; this file covers rules,
briefs and ledger.

## Ledger script

`scripts/review-ledger` stores JSON rounds and findings, parses replies, closes
repeats, applies caps and prints briefs. Keep ledgers outside the repo.

```sh
RL=<skill dir>/scripts/review-ledger; LED=/tmp/<change>.ledger.json
$RL -l $LED init --repo <abs path> --base <sha> --intent "..." --checks "..." \
    --threat-model "<FILE|TEXT: Reach, Untrusted, Holds lines>" | --project-kind <kind> \
    [--shape <shape> | <declared facts>] [--stage prototype|beta|production] [--category logic]
$RL -l $LED brief > brief.txt          # send to the reviewer
$RL -l $LED round --tier 1 --reviewer sol --author sonnet --sha <reviewed sha> --reply reply.txt
$RL -l $LED outcome S3 fixed|disagree|declined|pre-existing --evidence "file:line ..."
$RL -l $LED next                       # ROUND | ARGUE | CHECKPOINT | NIT-CULL | STEP-BACK | FIX-KEPT | STOP-*
$RL -l $LED checkpoint                 # after you answered §6c
$RL -l $LED owner-ok "<quote>"          # owner's pilot-build thumbs-up
$RL -l $LED new-approach               # after a step-back changed the approach
$RL -l $LED status                     # rounds, findings, next step (for the hand-off)
$RL -l $LED stash                      # nit stash (from the checkpoint); hardening stash (once opened)
$RL -l $LED hardening [--from <ledger>]  # open the hardening phase (new rounds, full brief)
$RL -l $LED threat-model --confirm     # the owner confirmed an inferred threat model
```

Argument minimums and focus: `dialogue.md`.

Who reviews which round, `--author`, `argue`, `cull`: `review-v2.md`. The text
below is the legacy (no `schema`) schedule where it names Sol rounds.

`next` is advice from the counts. You still verify every `needed for bar: yes`
finding against the source, and your own concerns still block.

## 6a. Score and bar

Rounds end on confidence, not on comment count. A PR with eighteen nits can be
a 9; a PR with one finding can be a 6, and that one matters more.

- Every reply carries `SCORE[concern]: n/10`, one line per concern the brief lists:
  the reviewer's confidence that the diff does the intent correctly and is safe to
  merge. Anchors: 10 = merge as is; 8 = only nits left; 6 = a real bug callers will
  hit; ≤4 = intended case wrong, or the approach is wrong. A lone `SCORE: n/10`
  counts for every concern.
- Set the **bars** before round 1 with `review-ledger init` and put them in the
  brief. Each concern has its own bar (6 to 10) from the region's shape and stage;
  security comes from the threat model. A round passes when each concern's score
  meets its own bar. Rules in `references/bars.md`.
- Every finding says `needed for bar: yes|no` (would the score reach its bar
  with this one left as is?) and may name its `[concern: x]`. Only `yes` findings must be fixed in this PR.
  `no` findings go to the feature's `HARDENING-STASH`; do not fix them this round.
- A score is the reviewer's claim, not a pass. You still check every `yes`
  finding against the source, and your own concerns still block.

## 6b. Rounds

- **Round 1** reviews the whole diff from the recorded base.
- **Round 2 on: diff-only.** Commit before each round and record the
  reviewed SHA. Later rounds see `git diff <last-reviewed-sha>`, the ledger,
  and only the still-open ids.
- **No repeats.** The reviewer gets the ledger and must not re-raise a
  resolved or declined id without new evidence; a repeat is closed unactioned.
- **Flag the class.** Each finding names its class and lists every instance
  in the diff (search for them), so one fix covers all of them. You fix the
  class, not the line.
- **Pre-existing** findings (code this diff did not touch or newly reach) are
  tagged `pre-existing`: follow-up list, not this PR.
- **Stashes.** A blocker or should needs a realistic reproduction under the
  threat model (who does what, how often); a security finding needs an attacker
  it includes. Without one it goes under `HARDENING-STASH:`. While a blocker or
  should is open, nits go under `NIT-STASH:`. The brief hides both. Hardening
  opens in its own phase (`review-ledger hardening`), at normal bars, before an
  upstream PR opens/goes ready or a project release. Owner-run integration branches
  need only structural review, Fable at round 3, no extra triage.
- **Cap and step back.** Tier 1 has at most 3 rounds. If round 3 is still
  below the bar, do not run a fourth on the same approach. Ask the reviewer for
  one step-back reply instead: is the approach wrong, is there a smaller
  design, should the PR split? Bring it to the user with your view if it
  changes scope. A changed approach starts over at round 1 (hard cap: 5 tier-1
  rounds per phase). The user can always ask for more.
- **Stop early** at the bar. Declined nits and comment, doc or format-only fixes need no new round.
- One reviewer at a time, no subagents.

**Do not edit scoped files while a round runs.** Wait for the reply. Do not
poll or start a second reviewer. A timeout or error is NOT
approval: cancel, verify it stopped, restart with the ledger.

**Ledger.** One row per finding: id, round, class, severity, needed-for-bar,
outcome (fixed / disagree / declined / pre-existing), evidence. Plus one row
per round: reviewer, reviewed SHA, score. Record reviewer model and effort if exposed. Never hardcode a model ID in a skill, prompt
template or report; say "<latest Sol model>".

**Brief (round 1, either tier).** `review-ledger brief` prints it: review-only
rules, repo, base, intent, bar with shape and stage, per-concern bars, the threat
model (marked `inferred` until confirmed), the diff command, and the reply format.
The reply has one `SCORE[concern]: n/10` per listed concern,
`VERDICT: APPROVE|CHANGES`, then one line per finding:

```
S1 [blocker|should|nit] [needed for bar: yes|no] [class: <slug>] [concern: <name>] <file>:<line>[, more instances] <claim>. Fix: <…>
```

Then the stash sections, one `- ` line per item:

```
NIT-STASH:
- <file>:<line> <nit>
HARDENING-STASH:
- <file>:<line> <what fails, and under what use the threat model does not expect>
```

**Later rounds.** Send the round-1 brief, the ledger, `git diff
<last-reviewed-sha>`, and the open ids. Tell the reviewer: mark each open id
`resolved` or `still open: <reason>`; raise new findings only on the new diff
or with new evidence.

**Tier 2 brief.** The round-1 brief plus the full ledger with outcomes, and:
"Tier 1 reached <score>. Do not re-raise ledger items. Look for what tier 1
missed: wrong approach, broken callers, intent mismatch, threat-model gaps."
After its fixes, at most one diff-only re-review. Disagreements after that go
to the user (Stop, below).

## 6c. Stability checkpoint (between tiers)

Once tier 1 reaches the bar, before tier 2, answer these yourself, in
writing, in the ledger. Raise any answer that changes scope with the user.

1. **Simpler intent.** Ask the §1 question again with what you now know: is
   the user's intent served by something simpler (do less, reuse, change the
   requirement)?
2. **Tests vs policy.** Is the amount and kind of testing in line with the
   repo's test policy (AGENTS.md, `test-quality`)? Cut tests the intent does
   not need; add only what the policy requires.
3. **Smaller or more structural.** Could the fix be smaller, or move up a
   level (a type, a module boundary, one owner for the value) so the
   per-site patches go away?
4. **Enforcement layer.** For each bug class found in this loop, which layer
   stops it from coming back? Go down this order and stop at the first layer
   that can hold it:
   1. **code**: types, structure, one source of truth (the bug cannot exist);
   2. **static analysis**: analyzer or lint rules, guard tests, CI checks;
   3. **prose**: AGENTS.md, a project checklist, a skill;
   4. **human review**: only for what the layers above cannot express.

   Try the first layers for real (a type change, a guard test) before a
   checklist line or "watch for it in review". Record the layer chosen per
   class, or why a higher layer could not hold it.

5. **Nit stash.** `review-ledger stash` shows the nits held back. Fix only a
   nit that ONE central change solves and that maps to a code practice or
   feature facet (a lint rule, a helper). Decline the rest with a reason.

If this cuts the diff, rerun the covering checks and give tier 2 the new diff.

## 6d. Answering findings

Make the minimum change that satisfies the finding, but do not dismiss
findings cheaply.

- **Never wave a finding off as "just a nit".** Judge it on its merits and
  against the threat model.
- **Question the security stance.** For each comment, ask: under this
  project's threat model, is this a real exposure, a hardening nicety, or out
  of scope? Say which, with the reason. Also ask the reverse: does the
  reviewer's silence mean the stance is sound, or never examined? If a project
  rule limits reviewer scope (for example "correctness findings only"), follow
  it for what you ask, but still judge security-relevant findings against the
  model and tell the user.
- **Threat model source.** The model `init` stores (residual's data, else
  `review/threat-model.md`). If it is `inferred`, say so and ask the user to
  confirm (`threat-model --confirm`). Leave any new file UNCOMMITTED unless told.
- Agree: smallest fix for every instance of the class, plus one focused test
  that fails without it. Prefer delete or narrow over a new lock, cache,
  helper or option. Prefer a type change over a new runtime check.
- Disagree: give evidence (file:line, test, output).
- Out of scope: decline in one line with the reason, and list it as follow-up.
- Re-check each severity and each `needed for bar` yourself. Another path,
  rare case or small cost is a nit only after you have checked it is not a
  threat-model issue.
- If review grew the diff, cut it back first. Never agree just to end the
  loop.

**Stop**
- Agreed: tier 2 at or above the bar on the current diff, no blocker or
  should open, no concern of your own.
- Stuck: an item is still disputed after two replies, tier 1 hit its cap, or
  the budget is spent. Show both sides in 2-3 lines each and let the user
  decide. Out of budget is not approval.
