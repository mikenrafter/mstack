# Wake-pr external review corpus

The frozen family contains 51 files. Five code-review chains have paired prompts or an explicit saved round ledger, yielding 23 observed rounds and 113 finding entries. Their later rounds provide 13 positive reported-consequential outcomes, one negative and four unknowns after conservative scope checks. This dataset offers a small transport check for frozen models. It cannot validate a stopping policy.

The pool was selected and hashed before its contents were inspected and before model results were seen. It is separate from the frozen structured-ledger corpus. No model was fitted, selected or evaluated during extraction.

| Chain | Rounds | Actual code project | Chronological anchors |
|---|---:|---|---|
| T12 | 5 | Edge | Paired prompts name rounds and previous replies; saved ledger anchors round 1 |
| T3 | 5 | Edge | Saved ledger anchors first reply and code range; later prompts link prior replies |
| P8a | 5 | Edge | Round-2 prompt explicitly identifies first reply; subsequent prompts name rounds |
| CLS1 | 5 | Edge | Round-2 prompt explicitly identifies first reply; subsequent prompts name rounds |
| HMM-code | 3 | Analytics | Code-review prompts explicitly name rounds, target checkout and prior replies |

The four Tracks-related Edge chains share code and successive merges. Their group IDs represent distinct review scopes, not independent changes. HMM-code's evidence is stored under Edge research but reviews Analytics code. Two report-only pairs, harness-spec and HMM-repin, remain inventory-only because the selected family lacks paired prompts or explicit round identities sufficient for the same extraction rule. The remaining unused file is a redundant supporting T12 ledger. Exclusions follow evidence availability, not outcomes. This corpus does not reproduce the earlier usage report's nine-change or 164-finding aggregate.

## Labels and compatibility

The primary `documented_consequential_discovery` field means a newly recorded blocker/should report in the reviewed scope. It counts finding entries, with explicit repeated IDs excluded. It does not establish independent defect mechanisms, valid findings, or code quality. `true_new_valid_consequential` remains null. Final statuses and resolution evidence are outcomes, never features.

Every retained reply has one explicit verdict and a matching prompt or ledger anchor. Discovery IDs are separate from later CLOSED/OPEN statements. An accepted positive additionally requires a later matched CLOSED statement about an earlier consequential ID. The resolution event records its exact source and line. Such statements remain reviewer evidence, not independently executed fixes. The final observed successor is always right-censored.

The four Tracks round-5 prompts emphasize shipping blockers and regressions under a final review budget. Their reply format still allows should findings, and three prompts repeat the ordinary severity definitions. Nevertheless, the reporting threshold may have changed. Their zero-consequential primary labels are conservatively unknown, even where a reply says “No new findings.” Raw tagged counts and the unmasked report observation are retained for descriptive inspection. They must not silently replace the primary labels.

CLS1's last reply says only that no new regressions or shipping blockers were found. That is narrower than an unqualified no-new-findings statement and remains unknown even in the raw observation. T12's last reply contains one nit, and T3/P8a explicitly report no new findings. All four remain unknown for the common target because of final-budget focus.

HMM-code round 3 retains a should-enabled reply format and has no final-budget instruction. It reports no new code regressions and enumerates only two documentation nits. It supplies the single negative for the documented blocker/should proxy in that reviewed code scope. This is weak negative evidence for transfer and cannot establish absence of material defects.

`documented_new_blocker` is a separate narrow descriptive label. It is not a replacement training target. `scope_compatible_for_negative`, `prompt_final_budget_round`, `negative_evidence_kind` and the pinned prompt source preserve the coverage decision.

The existing model loader can read `rounds.jsonl` directly. Group/project/ordinal, both documented outcome fields, and `features_before_round` use the existing schema. All numerical scores, tiers and approaches are unknown. They are not inferred from verdicts. The safe feature record contains only prior observed scores, verdicts, reviewer/revision fields and counts. A model's existing missing-score behavior should remain frozen. It would be inappropriate to invent scores or tune missingness handling on this corpus.

There are 18 later-round observations in five scopes across two code projects. Only 14 have known common-target labels, 13 positive and one negative. Four of the five groups belong to the same intertwined Tracks effort. Severity meanings, review focus and missing scores also differ from the structured corpus. Report external results as an exploratory compatibility check, including these limitations.

## Artifacts and verification

`source-manifest.json` pins all 51 input paths and hashes. Extraction fails if a source changes. `inventory.jsonl` records used and excluded sources, `mapping.jsonl` records chronology and snapshot anchors, `rounds.jsonl` provides model-compatible observations, and `findings.jsonl` records discoveries and resolution events. `summary.json` contains counts, and `run.json` binds source/result fingerprints and queue jobs.

Eight focused tests cover prompt exclusion, discovery/resolution separation, censoring, partial approval, lagged features, repeated IDs, original severity categories, invalid chronology and final-budget scope uncertainty. Three deliberately broken parsers are detected: dropping should findings, treating approval alone as negative, and ignoring final-budget scope changes.

```sh
qex submit --follow --cpu 1 --mem 256MB -- python3 -m unittest discover -s research/elo-code-health/review-budget/external-corpus -p 'test_extract.py'
qex submit --follow --cpu 1 --mem 256MB -- python3 research/elo-code-health/review-budget/external-corpus/extract.py
qex submit --follow --cpu 1 --mem 256MB -- python3 research/elo-code-health/review-budget/external-corpus/check_mutations.py
```
