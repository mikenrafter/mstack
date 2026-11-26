# build-loop reference: nitpicks (owner, 2026-11-26)

Audits, retros and research find defects in code no review ledger covers. They go to
`<repo>.research/nitpicks.md`, one entry each, never fixed in passing:
```
## N<yyyymmdd>-<n> · <one-line title>
- where: <path:line> @ <sha>
- kind: test-gap | bug | security
- fails when: <the wrong version that still passes, or the input that breaks it>
- fix: <concrete input, oracle or change>
- proven by: reading | mutation | run
- source: <report path>
- status: open | stashed <ledger> | fixed <sha> | dropped <why>
```
`security` entries are also listed to the owner in the reply that files them. When a pilot or
hardening phase starts in that repo, copy the open entries it touches into its `HARDENING-STASH`
and mark them `stashed`.
