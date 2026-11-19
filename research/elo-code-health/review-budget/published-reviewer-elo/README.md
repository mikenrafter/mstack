# Published reviewer Elo example

## Top findings

- [C, vendor report] HeyDeer published a directly relevant use of Elo for reviewer comparison on 2026-11-10.
- [C, reproduced arithmetic] All 43 accounting and graph checks in `audit.py` pass against the downloaded aggregate.
- [D, application] This is a candidate design for comparing reviewers on matched snapshots; it does not validate a code-quality rating or a review-round recommendation.
- [C, data limit] The public aggregate cannot support a chronological K replay.
- [D, next step] Collect executable evidence and review cost before considering reviewer allocation.

HeyDeer reports 752 eligible internal review rounds producing 1,001 comparisons. Its scoring rewards accepted and exclusive findings and penalizes explicit false positives. It uses K=32 and applies summed pair updates together after each round. Adjudication is model-assisted, and the raw code and findings are private. The report does not establish recall, cost-effectiveness, or causal multi-round benefit. [Article, 2026-11-10](https://heydeer.ai/blog/code-review-evaluation).

The aggregate identifies six configurations; some have no direct matchup, and one has only three scored rounds. Its own timestamp says published 2026-09-19, with a 2026-09-14 snapshot. These dates differ from the article date. [Aggregate](https://heydeer.ai/research/code-review-evaluation-2026-09-19.json), retrieved 2026-11-17.

The local audit reconstructs per-model wins, ties, losses and comparison counts from pair records. It also verifies graph connectivity and computes a descriptive constant-rating gap for each nonempty pair. These checks establish internal arithmetic consistency. They cannot authenticate private outcomes, adjust for shared-round dependence, or recover chronology. No additional model ranking was fitted.

## Where your setup differs

Your `build-loop` already changes reviewer context and requires fresh review in specified cases. The decision here concerns another inspection after those gates. A relative reviewer leaderboard does not answer that decision. Its scoring weights would also need an explicit local materiality and triage-cost contract.

## Candidate actions

1. Preserve matched code snapshots and finding adjudications; otherwise reviewer comparisons mix changing tasks.
2. Keep reviewer-comparison ratings separate from code risk and round-count recommendations.
3. Leave K sensitivity unresolved when only aggregates are available; do not invent a replay order.

## Sources

The linked first-party article and aggregate, retrieved 2026-11-17; unchanged `aggregate.json`, `source.json`, `audit.py`, `audit.json` and the frozen `PROTOCOL.md` in this directory.
