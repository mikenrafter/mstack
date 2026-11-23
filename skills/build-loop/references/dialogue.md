# Argument, priorities, and behavior profiles

Implementers begin immediately and have a work-grounded check-in roughly five
minutes into the batch. Every reviewer round needs one substantive exchange,
even an approval. Fable needs two; non-clean tier-one round four keeps two.
Challenge a material assumption, consequence or simpler option without inventing
disagreement.

## Set the round focus

Store a JSON object containing arrays of strings:

```json
{
  "most_important": ["Revoking a share prevents subsequent content reads."],
  "invariants": ["Cached content must not bypass revocation."],
  "priority_concerns": ["security", "concurrency"],
  "lower_priority": ["Copy polish can wait."],
  "evidence": ["revoked_share_denies_read passed; device exercise unavailable."]
}
```

The first, second and fifth arrays must be nonempty. State uncertainty honestly
when proof is missing. Priorities weight attention; they cannot waive a real
contract, security or data-loss defect. `context` updates later briefs; each
recorded round keeps its own snapshot. Set context before any new schema-2 round.

```sh
review-ledger -l LED context --file focus.json
review-ledger -l LED brief --model EXACT_MODEL > review-brief.txt
```

The brief includes focus and the compact behavior mask. Optional `--family sol`
explicitly permits a family aggregate if the exact model has no profile. An
unknown model never silently inherits observations about earlier weights.

## Implementer check-in after work starts

Start implementation without waiting for proposal approval. Note the start time.
Roughly five minutes into actual work, the orchestrator reads 1–5 relevant files,
including the current edits, then asks 2–3 concrete questions. Ask what remains
ambiguous and point to questionable assumptions or implementation choices in
those files. The implementer answers from the work; the orchestrator challenges
the answers where needed and settles direction before the questioned work
continues. This checks implementation bias rather than repeating planning.

For example, after reading a handler and tests: What remains ambiguous? Why add
a second cancellation registry when the job already carries the state? Where
did the requirement to delete partial output come from? After the answers, the
orchestrator decides which state and behavior the implementation should use.

Use an available session timer to make the check eligible around five minutes;
do not sleep or hold the implementer idle. The orchestrator can read files while
the implementer works and must use the supported messaging route for that live
agent. For a batch finishing sooner, perform the exchange at handoff. Raise known
blockers immediately rather than waiting for the check-in.

Record implementer identity, batch/start time, the 1–5 inspected file paths,
2–3 actual questions and answers, orchestrator pushback, and the settled decision
with `review-ledger -l LED implementation-check --file checkin.json`.
The JSON fields are `agent`, timezone-qualified `started_at`, `inspected_files`,
`ambiguities`, `questions`, `pushback`, and `resolution`. Questions are 2–3 objects
with nonblank `question` and `answer` strings. Files are 1–5 distinct paths;
ambiguities is a string array, empty if none remain. Pushback and resolution are
nonblank strings. Explain why the current approach suffices if no correction is
needed. The ledger records elapsed time and rejects an exact duplicate. It accepts
a shorter batch's handoff exchange without making the agent wait. Recording
cannot establish that files were really read or that dialogue was substantive;
the orchestrator must do both.

The earlier `plan`, `plan-answer`, and `plan-status` commands remain available
for optional explicit planning records and compatibility. Their READY status is
not a prerequisite to starting implementation. Reviewer argument gates are
unchanged.

## Record review exchanges and findings

Let the reviewer write its reply to a research output file through its harness.
The existing round parser saves findings, nit stash, hardening stash and stable
IDs. Do not create a second manually maintained concern list.

```sh
review-ledger -l LED round --tier 1 --reviewer sol --author sonnet \
  --model EXACT_MODEL --requested-effort B6_EFFORT --author-effort AUTHOR=B6_EFFORT [--effort VERIFIED_EFFORT] --sha SHA --reply review.txt
review-ledger -l LED next
review-ledger -l LED brief --model EXACT_MODEL > argument-brief.txt
review-ledger -l LED argue --note exchange.txt
```

`exchange.txt` contains both `Orchestrator:` and `Reviewer:` sections with their
actual exchange. For T3, every new review or recheck uses a new delegate with
prior context and objections. Native agents can use supported messaging. A
summary records the real speakers; it is not permission to fabricate dialogue.
The ledger rejects one-sided/empty notes and exact duplicates. It blocks a new
round or phase transition while an earlier exchange remains unfinished.
Revised reviewer SCORE/VERDICT lines update the round and preserve originals.

`--requested-effort` (required, schema 2) records the B6 request separately from exposed `--effort`.
Record effective model and effort when exposed. Do not label a requested effort
as verified. Missing effort remains unknown. Observe priorities, finding classes,
review dispositions and source evidence when refreshing profiles.

## Maintain small behavior masks

`scripts/review-profile EXACT_MODEL` prints three strength and three weakness
slots, with evidence status. `--mask-only` prints the short adjustment sent to
agents. `--role implementation` selects the separate implementer observations.

The data is `references/reviewer-profiles.json`. Nicknames describe behavior;
dated mappings associate exact versions and roles with them. Sparse slots remain
unknown. Family aggregates identify their supporting versions and require an
explicit fallback. A declined nit is not automatically wrong, and an accepted
nit is not independently proven correct. Never suppress an important finding
because of a profile.

To refresh, extract original reviewer statements and dispositions from newly
recorded rounds, deduplicate copied replies, and cite source locators. Keep raw
history private in project research; commit only necessary observations and
pointers. Revise the mapping or mask when evidence changes. Do not rename the
archetype merely because a provider changes weights.

## Hourly check-in (owner, 2026-11-20)

Check in with every running subagent at
least once an hour, by steering it mid-run (SendMessage), not by queuing work for
later: read 1–5 of its files or commits, ask questions, redirect it if it is
drifting, and look for what is slow. Speed it up when that is reasonable;
otherwise have it write the slow part up as hardening work or an owner item.
Track it with a vigil item: `vigil hold add <hold> --for none --expect-s 3600
--label checkin-<run>`; its overdue event is the prompt. When the agent has not checked in for a
long time, open the message with "URGENT: stop and answer this before your next
step" and ask it to write its answers to its report before it continues.
