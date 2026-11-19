# Published reviewer Elo audit

Frozen 2026-11-17 before downloading or calculating with the aggregate JSON. The source page and displayed aggregate contents have been read. This is a descriptive accounting and interpretation audit, not independent validation or model selection.

Source: HeyDeer's article dated 2026-11-10 and its separately dated aggregate snapshot. Download the linked JSON unchanged and retain its SHA256. Check run-status totals, model comparison totals against twice the pair count, each pair's wins/ties/losses, and per-model totals reconstructed from pairs. Record the nonzero comparison graph and each model's direct opponents.

For each nonempty pair, calculate its observed point share and the implied constant Elo gap `400 log10(points/(comparisons-points))`. These are descriptive summaries of those pair outcomes. They do not reproduce chronological Elo, estimate reviewer accuracy, establish statistical significance, or identify the best number of reviews. Do not fit another ranking or tune K on this aggregate.

The raw ordered rounds, code, and individual findings are private. No K replay, dependence adjustment, recall calculation, or causal multi-round estimate is possible from this file alone. A multi-reviewer round contributes several correlated pairs. A fixed K does not cap total per-round movement when pair updates are summed.

The local research record will distinguish the vendor's report from independently checked arithmetic and from proposed applications. No reviewer is called, no account is connected, and no upstream action occurs.
