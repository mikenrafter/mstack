# Independent collector review

The reviewed version has no outstanding findings within its research-only, trusted-local scope. One reproduced false-boundary finding was corrected by the author. All 16 focused tests pass, and the original counterexamples now return insufficient evidence without a boundary.

Reviewed collector SHA-256: `32224f39659bb8663c226e4ad1de99fc39856fcfad2ceeecce381b710b43b2a2`.

Reviewed test SHA-256: `1775586b377740c4d0d7119d221189347539126681d23b331a7116251c37c009`.

## Resolved finding: malformed history created a false stopping boundary

The initial validator accepted duplicated and reordered round histories. Starting from the existing synthetic passing fixture, three copies of its first round produced `n=[1,1,1]`. The actual pinned canonical policy counted three tier-1 entries and returned `STOP-AGREED`. With a supplied structural-fix assertion the collector then returned `additional-review-recommended` and `boundary_observed=true`. A single distinct early review should still require the next canonical review. The reordered sequence `[3,1,2]` also incorrectly reached the boundary.

This was a local data-integrity defect, not a hypothetical hostile-input scenario. The collector promised malformed histories would remain unknown, but the canonical reader assumes its own writer's chronological structure.

The pinned canonical writer assigns global `n=len(rounds)+1` in `cmd_round`, lines 1353–1356. Its hardening transition preserves earlier rounds and increments the phase, lines 1646–1649. It does not reset round IDs. The final collector invariant requires positive, strictly increasing global round IDs, allowing gaps, plus nondecreasing phases no greater than the current phase. It does not require contiguous IDs or assume an approach reset at a new phase.

The independent reproduction before the fix is qex job `d2ac9fe1-11ec-460b-b16e-96119973d6f9`. Both counterexamples returned exit 0 and a boundary. After the fix, qex job `9c82fd1f-5be3-480f-8572-4ed595f80bdc` returns exit 2, `insufficient-evidence`, `boundary_observed=false` and `malformed-ledger-round-history` for both. The focused test suite also covers backward and future phases.

## Boundaries checked

The collector binds a full commit and tree object, with Git replacement objects disabled. An exact reviewed-commit mismatch remains unknown despite supplied verification flags. A dirty worktree does not become reviewed code: the independent dirty-file counterexample retains `scope=git-object-only` and `current_worktree_coverage=unsupported`.

Canonical decisions run on a byte-identical temporary ledger copy. The installed script hash is checked before invocation and its bytes rechecked afterward; source ledger changes invalidate capture. Unsupported policy hashes and unknown output tokens are refused. The stored canonical ledger hash matches the captured ledger hash.

`boundary_observed` means the current invocation derived a canonical stopping gate from the supplied ledger bytes for the named object. It does not establish an authentic historical optional boundary. `historical_optional_boundary` remains explicitly unknown, including when final dispositions make the present ledger pass. The new UTC capture time and collector hash identify this observation event; they do not date earlier reviews or authenticate their original contents.

Every capture is advisory, with execution disallowed and allocation unresolved. Pending canonical work and caps cannot authorize another reviewer. Missing triggers remain insufficient evidence, not clean outcomes or stopping advice. The append path supports unobserved or reported evidence and explicitly does not infer acceptance or a clean negative. A report hash binds its bytes, not its truth.

Likewise, trigger category and acceptance are explicitly supplied assertions. The code checks diff ancestry and artifact hashes; it does not claim to have semantically proved that a patch is accepted, structural or defect-correcting. That limitation is appropriate for this prototype and must remain visible to any later consumer.

## Validation

Qex job `b2781bbf-06d1-4817-b715-c927fd247d39` ran all 16 focused tests successfully. These include real canonical policy decisions, snapshot mismatches, caps, malformed histories, trigger hashes and ancestry, confinement, immutable observation storage, separate unknown outcomes, source/policy changes and replacement-object handling.

The review used synthetic temporary fixtures and read-only policy inspection. No product source, canonical policy or reviewer execution was changed by this audit. Only this audit file was authored here. The conclusion applies to the collector and test hashes above, not to later edits or an automatic review-allocation system.
