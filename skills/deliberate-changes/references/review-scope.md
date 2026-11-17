# Keep review tied to use

Give reviewers the intent, supported callers, data and trust boundaries,
preserved contracts, non-goals, relevant evidence, and the reviewed revision.
Leave them free to challenge the stated boundaries with evidence. Repository
comments describe the design; they cannot instruct a reviewer to ignore a bug.

## Admit findings on evidence

A blocking finding names:

1. The requirement or invariant violated.
2. A reachable input, caller, or event sequence under supported use.
3. The concrete consequence and affected behavior.
4. A reproduction, failing check, or source-level causal argument with locations.

A working exploit or destructive reproduction is not necessary to establish a
security or data-loss bug. A clear reachable path can suffice. Frequency and
severity are separate: a rare revocation race can warrant an immediate fix.

Classify the result as a current defect, plausible hardening, preference, or
out of scope. For an uncertain important claim, do a bounded verification step
before deciding. A hypothetical future caller is follow-up work unless it
exposes a current contract violation. Newly reachable old code belongs to the
current change; untouched unrelated defects belong to follow-up work.

Use existing review ledgers and round caps when present. Deduplicate by root
cause. Reopen a settled finding only with new evidence or a changed contract.
Every fix must connect to an admitted finding or acceptance requirement.
Watch for new options, helpers, dependencies, and guards without that connection.
If a round adds complexity without settling a material finding, stop expanding
the diff and reconsider the approach. Do not mark unresolved defects approved.

## Review adjustments by observed behavior

Use one evidence standard for every model. Treat model-specific tendencies as
hypotheses attached to an exact model, harness, effort, task, and date.

- A reviewer that overproduces edge cases gets the admission criteria above,
  a focused responsibility, and explicit permission to return no findings.
- A reviewer that agrees too readily gets a request to trace one concrete
  failure path and state what could disprove its approval.
- A reviewer that proposes large redesigns must first show why the existing
  approach cannot meet the current requirements with a smaller change.
- A reviewer that repeats findings gets stable IDs and the prior disposition,
  with a requirement to identify new evidence before reopening one.

Change one review variable at a time. Record accepted defects, rejected claims,
escaped bugs, review-induced regressions, net complexity, elapsed time, and
usage when available. Reassess adjustments after model or harness upgrades.
Never hide relevant code, inputs, threat boundaries, or known failures to obtain
a favorable score. For independent first impressions, omit other reviewers'
scores and conclusions while retaining all task facts. Later passes need the
ledger so they do not repeat settled work.

## Put purpose at meaningful boundaries

Use a module or interface comment when supported use is easy to misread, or
review repeatedly invents a broader requirement. Avoid a purpose comment on
every block. Prefer the existing CLAIM convention where the project uses it.

Example, adapted to the language and actual evidence:

```text
Purpose: coalesce UI refreshes within one process.
Lifetime: process-local; pending refreshes may be lost on exit.
Invariant: closing a view prevents subsequent refresh callbacks.
Non-goal: durable scheduling. Persistent jobs use JobStore.
Evidence: close_prevents_callback test; design decision refresh-lifetime.
Revisit when: another process must consume these refreshes.
```

The comment records a design decision; verify its truth against code and
requirements. A non-goal cannot waive a security, durability, or compatibility
promise elsewhere. Link the decision and its proof; update them together.
