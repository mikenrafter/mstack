---
name: deliberate-changes
description: Make warranted deletions, replacements, and simplifications when a requested refactor or redesign is being held back by attachment to existing code. Use for explicit requests to reconsider an approach or work more boldly within scope; ordinary edits do not need it.
---

# Deliberate changes

Optimize for the requested behavior. Existing code, tests, abstractions, and an
agent's earlier plan are candidates for replacement when they obstruct it.
Permission to complete the task includes necessary reversible source edits
within its scope, including deletion. Do not ask again merely because a change
is large or removes code. This skill does not expand the task or authorize
deleting user data, breaking promised external contracts, publishing, or deploying.

## Establish what must survive

Use the request, callers, documented contracts, and existing project decisions
to identify the desired result and the behavior that must remain. Separate
those requirements from incidental implementation choices. Prefer a brief
statement in the task over a new document when the distinction is straightforward.

If uncertainty is about the implementation, investigate and choose. If it is
about a product requirement, preserve the existing contract where possible and
ask only when the answer changes the result. Give a concrete option and the
consequence. Do useful independent work while awaiting a required answer.

## Make the warranted change

- Delete obsolete paths and their wiring together. Search callers, exports,
  registrations, reflection, config references, generated entry points, and
  relevant consumers. An empty text search alone does not prove no consumers.
- Replace a weak approach when a simpler one meets the requirements. Do not
  retain parallel implementations, feature flags, compatibility layers, or
  fallback branches merely to avoid choosing. Preserve them when a real
  consumer, rollout requirement, or failure mode needs them.
- Remove a test only after identifying its claimed protection. Check that it
  runs and can reject a relevant broken implementation. Repair a broken test
  for a valuable requirement; keep unique regression coverage or replace its
  protection before deleting it. Test count and coverage percentage alone do
  not justify removal. Use `test-quality` for a test audit.
- Change internal interfaces and update consumers in one coherent batch.
  Public APIs, stored formats, migrations, and external consumers need their
  established compatibility or migration contract.
- Reject a review suggestion when its premises are disproved or its benefit
  falls outside the task. Cite the evidence. Do not implement it to appease a
  reviewer, and do not dismiss a small fix merely because it is small.
- Undo your own unhelpful work. Preserve unrelated working changes and a
  recoverable version of valuable experiments. Git recovers committed source,
  not untracked work or deleted production data.

When hesitating, name the concrete potential loss. Inspect the evidence that
could settle it. If the change is authorized, recoverable, and verifiable,
proceed. If it threatens a requirement, resolve that requirement first.

## Verify and stop

Judge confidence from observed behavior: a reproduction, relevant checks,
consumer checks, or an end-to-end exercise. Keep proof proportional to the
change. Do not weaken assertions or redefine requirements to obtain green
checks. Report unexercised boundaries explicitly.

Stop when the intended behavior and preserved contracts have adequate evidence.
No further change is a valid result. Review scores and enthusiasm are not
proof, and a spend limit is not approval. Existing project review requirements
still apply. For speculative findings, model-specific review adjustments, and
purpose comments, read [references/review-scope.md](references/review-scope.md).
