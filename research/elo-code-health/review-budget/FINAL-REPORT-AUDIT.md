# Final report consistency audit

2026-11-17. Independent review of REPORT.md and SCHEDULE.md against preserved outputs and protocols. No experiments, product tests, new research searches, implementation edits or model calls were run for this audit.

The main conclusion is supported: these experiments do not validate a predictive extra-review rule or an extra-round count. The collector, reproduced historical case and evidence graph have useful instrumentation scope independently of the failed forecasts. Their existence does not demonstrate defect prevention, a better architecture or improved review allocation.

## One correction required

REPORT.md line 70 and SCHEDULE.md step 3 call a **40–60-change/six-week** range a fixed endpoint. That is not a unique stopping rule and differs from advisory-design/DESIGN.md, which specifies the first of **60 independently observed eligible changes or the end of week 6**. Its 40-change requirement is minimum coverage for a ranking claim, not a selectable favorable endpoint.

Use: “a ten-assay feasibility checkpoint, followed by evaluation at the first of 60 independently observed eligible changes or the end of week 6; at least 40 independent changes and the other coverage criteria remain necessary for a ranking claim.” Keep the checkpoint restricted to feasibility stopping. The parent acknowledged this correction and is applying it consistently, including the looser power-results prose. This audit does not modify those documents.

## Scope wording to tighten

REPORT.md line 37 says “All 98 local rounds.” The underlying eligibility audit covers the **98 rounds in the two selected corpora**: 75 structured and 23 external rounds. It is not an exhaustive census of every local review. Replace with “All 98 rounds in the selected structured and external corpora.” The seven candidate pairs, zero eligible, six ineligible and one unknown are correct.

## Verified claims

- The four reported Brier losses match the saved accepted-proxy group-holdout results: prevalence 0.192399; selected Elo 0.192690; lag logistic 0.193023; augmented logistic 0.201659. All eight frozen K/schedule variants are worse than prevalence on that target. This is a bounded negative finding, not proof that all rating models fail.
- The primary denominator is 39 known later outcomes: 30 positive, nine negative, 16 group IDs and six projects. Fifteen additional observed later outcomes are unknown. Group IDs are not established independent changes.
- The external target is different: 14 reported-finding outcomes across five chains, with 13 positives and one negative. Its 4.2% logistic improvement, interval crossing zero and 2.8 versus 2.6 expected positive misses agree with the saved results. It does not pass the frozen gates.
- The 32,768 sensitivity completions apply to **fixed forecasts**, not refitting after acquiring labels. Some completions reverse the small loss ordering; none reaches the 10% threshold. REPORT.md correctly limits its claim to the fixed forecast.
- The public matrices retain eight matrices and 602 overlapping pairs. Saved coverage outputs sum to 65,528 nonempty teams; seven of eight full pools miss listed reference faults. These are finite combinatorial summaries, not independent trials or exhaustive natural-defect truth.
- The collector validation records 16 tests and three caught mutations. The 21-ledger smoke has 18 explicit unsupported-schema refusals and three supported captures, with no extra-review recommendation and no authentic historical optional-boundary claim. Current derived policy output is not recovered historical policy evidence.
- The real Paneweft CLI output preserves 11 edges and reports freshness `unverified` with `REPOSITORY_NOT_REGISTERED`. The misleading empty-freshness run remains separately preserved. The graph presents one corrected historical family, not a current defect or three independent causal cases.

All Markdown local links in REPORT.md and SCHEDULE.md resolved at audit time. Code-formatted protocol paths in SCHEDULE.md also refer to existing artifacts inspected in this research pass. No wrong numerical denominator or unsupported completed-experiment success claim was found beyond the wording issues above.

## Audit snapshot

The inspected REPORT.md SHA256 was `71f92ce45ec79cfbfc4b72feddabf0ff7d3457a2ded8c99b3335e9fcdaa9c4e7`; SCHEDULE.md was `ea97510caa14f22c89284044df8ee649d904f545ac2ed054a7093d42a0596708`. Parent corrections after this snapshot require updated integrity accounting; these hashes do not describe later edits.

The checks used models/RESULTS.md, models/EXTERNAL-RESULTS.md, models/fix-shape/RESULTS.md, missing-outcomes/RESULTS.md, advisory-design/DESIGN.md, power/RESULTS.md, capture-recapture/ELIGIBILITY.md, saved empirical/coverage/simulation JSON, advisory-prototype/VALIDATION.md, advisory-prototype/batch-smoke/RESULTS.md and evidence-graph/cli-checks.json. This audit checks their consistency, not a fresh reproduction of every underlying experiment or an authentication of historical reviewer claims.
