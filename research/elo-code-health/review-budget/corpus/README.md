# Saved review evidence corpus

This corpus records what saved review artifacts say about additional review rounds. It supports descriptive yield analysis. It cannot establish the defects that an unperformed review would find, or identify an optimal stopping policy.

The census found 21 reviewed change ledgers with 75 explicit rounds across six projects. The original ledger snapshots contain 240 finding entities. Thirteen manually verified reply mappings add 24 omitted findings and support nine reports with no new blocker/should discovery. The resulting 264 entities include 165 reported blocker/should findings and 99 nits. These classifications come from reviewers and ledgers. Independent validity remains unknown. A newly observed empty ledger remains in the inventory, outside the reviewed groups.

The source inventory includes 444 candidate artifacts at the final extraction. Only `*.ledger.json` contributes primary round sequences. Supplemental prose chains, filename numbers and archived derived reports do not create additional rounds. No review round is inferred from a test filename, a numerical suffix, a score, or absence of a later report. This avoids counting duplicate copies of earlier analyses as independent reviews.

## Files

| File | Meaning |
|---|---|
| `sources.jsonl` | Candidate paths, content hashes, size, extraction/exclusion status |
| `groups.jsonl` | One saved ledger per change group; independence is unestablished |
| `rounds.jsonl` | Explicit chronological round observations and lagged features |
| `findings.jsonl` | One entity per explicit discovery ID and round, with disposition provenance |
| `disposition-events.jsonl` | Explicit later resolution statements from verified replies |
| `summary.json` | Counts, parser fingerprint and errors |
| `mutation-results.json` | Tests against deliberately broken in-memory parser versions |
| `run.json` | Source/result fingerprints and queue job IDs |
| `source-manifest.json` | Frozen 21 ledgers and 13 reply hashes; changed inputs fail extraction |

Each observation records its source path and SHA-256, source JSON pointer or line, change group, round, tier, approach, reviewer, score, verdict and reviewed commit where present. Timestamps are null because these ledgers do not record review timestamps. File modification times and dates embedded in filenames are not substituted. Reviewed commit IDs identify code snapshots, not review times.

The frozen source manifest binds the 34 inputs that contribute observations. New ledgers remain inventory-only. A changed contributing ledger or reply aborts extraction rather than silently changing this dataset. The broad supplemental candidate inventory may grow independently.

`features_before_round` contains only earlier recorded rounds' scores, verdicts, tiers, approaches, reviewers and code revisions, plus prior round counts. Current-round scores and final finding dispositions are outcomes. Final ledger metadata, including paths, checks, score bars and gates, is explicitly separated because it may have changed later. Prior finding classifications are provided separately as retrospective reconstruction, with a warning that their online availability is unverified.

## Labels and missingness

`new_recorded_findings` and related counts describe saved evidence and may be incomplete. `recorded_consequential_lower_bound` counts reported blocker/should discoveries. `recorded_accepted_consequential_lower_bound` additionally requires a final `fixed` or `resolved` disposition and removes exact duplicated claims. Neither is an adjudicated defect count. A `should` item may concern unnecessary complexity, documentation or a contract amendment. `needed_for_bar`, severity, class and disposition remain separate so an audit can distinguish these.

`documented_consequential_discovery` is true when any blocker/should discovery is recorded. It is false only for a manually mapped complete structured reply with none. Otherwise it is null. `documented_accepted_consequential_discovery` is true when a fixed/resolved consequential report exists. It is false only when that complete reply reports no new blocker/should, and otherwise null. `true_new_valid_consequential` is always null. A missing findings object or an empty round in a partial ledger never establishes a clean review.

Final statuses distinguish fixed/resolved, declined/disagree/pre-existing, open and unknown. A declined report is not automatically a false positive. A resolved report is an acceptance proxy, not proof of an independently reproduced defect. Exact repeated claim text is flagged; semantic duplication remains unknown. Findings appear once at their explicit discovery round. Later resolution statements do not become new discoveries.

The largest verified omissions were all tier 2: Residual round 3, disk-full round 4 and Paneweft v1 rounds 6–7. Their raw replies contain consequential findings absent from the ledgers. The disk-full round 5 reply adds two nits and records earlier resolutions. Round 3 explicitly reports no new finding. Source score/verdict agreement is checked before accepting these manual mappings. The independent audit supplied these mappings and they were checked against the reports' contents.

Additional negative mappings use phoe-nix W49 round 2 and W47 round 4's explicit no-new-findings statements; W46 rounds 2–3, W47 round 2 and Edge database split round 2's complete only-nits replies; and Paneweft round 6's complete resolution-only reply. Disk-full rounds 3 and 5 complete the nine documented negatives. These are negatives for reported blocker/should discovery in the reviewed scope. They do not establish absence of material defects, and audit may challenge the severity assigned to a nit. No mixed Edge execution logs were parsed to create negatives.

The Edge graphs ledger has only per-round needed/fixed/deferred lists and no findings object. Its three rounds remain unknown rather than being assigned zero. Other rounds with no discovery rows also remain unknown unless a complete reply was verified. Detailed round extras are retained for later audit.

The final observed round in each group is right-censored. We do not label its unobserved successor negative. Observed later rounds were selected by people and previous review results. Groups share projects, code and review practices, so independent sampling is not established. This creates selection bias for any yield prediction.

Current build-loop policy already requires tier 2 after tier 1 passes. A later tier-2 discovery does not establish a benefit beyond that mandatory schedule. `policy_role` remains unknown until the historical schedule is inspected. This corpus alone supports an advisory forecast, with extra review under uncertainty, rather than an optimized stopping recommendation.

## Reproduction

```sh
qex submit --follow --cpu 1 --mem 256MB -- python3 -m unittest discover -s research/elo-code-health/review-budget/corpus -p 'test_extract.py'
qex submit --follow --cpu 1 --mem 256MB -- python3 research/elo-code-health/review-budget/corpus/extract.py
qex submit --follow --cpu 1 --mem 256MB -- python3 research/elo-code-health/review-budget/corpus/check_mutations.py
```

Nine focused tests cover discovery versus repetition, missingness, censoring, lagged features, status uncertainty, exact duplication, invalid chronology, verified supplementation and changed mapping rejection. The mutation checks require failures when current-round data leaks into prior features, missing findings become zero, or old findings are recounted in later rounds. Extraction reads subject artifacts and Git-free local files only; it runs no product builds and changes no subject repositories.
