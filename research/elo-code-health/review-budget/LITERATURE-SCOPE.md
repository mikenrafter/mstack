# Scope of the literature search

Retrieved 2026-11-17. The search found related uses of Elo and stronger precedents for measuring residual faults. It did not establish a published, validated rule translating Elo into the optimal number of architectural or code-review rounds. This is a scoped search result, not proof that no such work exists.

Queries included `Elo rating software defect prediction architecture code quality research`, `Elo rating automated code review defect detection research paper`, `Elo rating software architecture evaluation pairwise code quality`, `"Elo" "software architecture" quality`, `"Elo" "defect prediction"`, and `"CodeElo" arxiv`. Only primary papers and first-party methods are used below. The full mathematical and residual-inspection sources are in [METHODS.md](METHODS.md), [uncertainty/MEMO.md](uncertainty/MEMO.md), and [capture-recapture/MEMO.md](capture-recapture/MEMO.md).

| Source | What it establishes | Limit for this experiment |
| --- | --- | --- |
| Quan et al., [CodeElo](https://arxiv.org/abs/2501.01257), submitted 2025-01-02 | A competition-programming benchmark with Codeforces judging and human-comparable ratings. | Rates task-solving performance; it does not measure longitudinal repository quality, architectural improvement or optional-review benefit. |
| HeyDeer, [reviewer evaluation](https://heydeer.ai/blog/code-review-evaluation), 2026-11-10 | A first-party paired-reviewer Elo comparison on matched PR snapshots. | Reviewer ordering is a different target from defects remaining or useful round count. Local aggregate accounting is in `published-reviewer-elo/`. |
| Lu et al., [Towards Practical Defect-Focused Automated Code Review](https://proceedings.mlr.press/v267/lu25f.html), ICML 2025 | A repository-context industrial review study emphasizing bug inclusion, false alarms and workflow. | Abstract-level scope check here; no result is reproduced or used to support an extra-round policy. |
| Tufano et al., [Deep Learning-based Code Reviews: A Paradigm Shift or a Double-Edged Sword?](https://arxiv.org/html/2411.11401v1), v1 2024-11-18 | A controlled experiment with 29 professional developers and 72 selected reviews; supplied automated comments influenced where reviewers looked. | Small Java/Python programs, injected quality issues and human-assisted review; it does not estimate current Codex dependence or repeated-round yield. |

The last study gives an empirical reason to take context-sharing seriously. Its authors suggest showing automated comments after an initial manual inspection. Our proposed private-report-first assay is an inference from this concern, not a tested transfer. The historical two-version challenge in this work shared a hypothesis during parent feedback, so post-feedback reports cannot be called independent merely because the contexts began fresh.

No additional paid model calls or source-repository changes followed this final search. No new estimator or threshold was selected from these papers.
