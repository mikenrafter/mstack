# Review-budget research result

## Top findings

- [C, retrospective experiment] No tested Elo/K variant beats the simple prevalence baseline on accepted-finding proxies. A calibrated number of extra rounds is not justified.
- [C, sensitivity] All 32,768 assignments of the missing labels leave the fixed forecast below the predeclared 10% improvement requirement.
- [C, behavioral replay] One review fix introduced a cancellation interaction; identical targeted tests fail before and pass after its correction. This supports tracking changed contracts, not a universal extra-round count.
- [C, prototype] A research collector now preserves policy, code and finding evidence with explicit unknowns. It never executes or approves a review.
- [C, published methods and reproduction] Capture–recapture directly addresses residual defects, but existing local records fail its sampling requirements; a fixed estimator also performs poorly on the public human-inspection matrices examined here.
- [D, recommendation] Keep risk evidence and a conservative inspection preference separate. Collect authentic stopping-boundary data before fitting another rating or round policy.

## What changed about K

K is the update gain, not an uncertainty distribution. Logistic Elo supplies an expected-outcome curve; a Bayesian rating model separately supplies uncertainty about latent quantities. Glicko and TrueSkill offer useful precedents, but their assumptions do not automatically describe code changes or reviewer misses. [Primary-source memo](uncertainty/MEMO.md).

The original file-pair replay multiplied one historical block into many correlated comparisons. The corrected review-yield experiment uses one genuine observed outcome per update. It tested K8/16/32/64 with fixed and evidence-decayed schedules, holding complete changes out. Larger K worsened the descriptive result; this does not prove that every possible Elo formulation fails.

| Accepted-finding proxy forecast | Change-held-out Brier loss; lower is better |
| --- | ---: |
| Training-only prevalence | 0.192399 |
| Nested-selected Elo, K8/decay | 0.192690 |
| Lag-score logistic | 0.193023 |
| Logistic with revision-shape features | 0.201659 |

There are 39 labeled later rounds, 30 positive and nine negative, across 16 group IDs and six projects. Group independence is not established; some revisions overlap. Fifteen other observed later-round outcomes remain unknown. These are selected observed reviews, including mandatory rounds, and accepted findings are proxies rather than independently proved defects. [Forecast results](models/RESULTS.md), [feature diagnostic](models/fix-shape/RESULTS.md), [missing-label bounds](missing-outcomes/RESULTS.md).

The separate external check has only 14 known reported-finding outcomes across five chains, with one negative. Logistic loss improves descriptively by 4.2%, its uncertainty interval includes zero, and its matched-budget misses increase. This does not satisfy the frozen improvement gates. No external retuning followed. [External results](models/EXTERNAL-RESULTS.md).

An unstable logistic optimizer was found, corrected and tested with an independent arithmetic/descent fixture. Invalid outputs remain quarantined. The corrected negative results above are the ones to use. [Amendment](models/OPTIMIZER-AMENDMENT.md), [independent audit](MODEL-AUDIT.md).

## Research that is closer to the decision

The [search-scope note](LITERATURE-SCOPE.md) distinguishes competition-code ratings, reviewer comparisons, defect-focused review and the optional-round question. No validated Elo-to-round-count rule was established by this search.

HeyDeer reports Elo comparisons of AI reviewers on matched pull-request snapshots. That is a use for reviewer comparison; its report does not measure causal multi-round benefit. Public aggregates cannot reconstruct a K replay. [First-party article, 2026-11-10](https://heydeer.ai/blog/code-review-evaluation), [local accounting audit](published-reviewer-elo/README.md).

Older software-inspection research uses capture–recapture: overlap between private defect detections helps estimate what remains unseen. Published empirical and simulated studies also show sensitivity to inspector count, defect difficulty and dependence. This is a closer conceptual target than a generic quality leaderboard, with substantial transfer limits. [Literature memo](capture-recapture/MEMO.md).

All 98 rounds in the selected structured and external corpora were checked for fixed-snapshot opportunities. Seven candidate pairs produced zero eligible pairs, six ineligible pairs and one unknown. Different scopes, prior-finding context and repeat suppression defeat a closed-population interpretation. [Eligibility audit](capture-recapture/ELIGIBILITY.md).

The public UMD human requirements-inspection matrices allow a limited reproduction. All eight matrices and 602 pairs were retained. The simple Chapman estimate underestimates mean remaining reference faults in every matrix. Exact coverage curves across 65,528 finite teams show that seven full inspector pools still miss listed study faults. These results concern reference faults in historical requirements documents, not current LLM code-review accuracy. [Empirical diagnostic](capture-recapture/EMPIRICAL-RESULTS.md), [coverage data](capture-recapture/coverage-results.json), [independent audit](capture-recapture/MATRIX-AUDIT.md).

Synthetic checks explain possible mechanisms. Equal finding rates cannot identify code risk and reviewer sensitivity separately. Shared blind spots can make overlap-based estimates reassuring while defects remain; edits also violate a fixed-population assumption. No synthetic success is counted as empirical improvement. [Identifiability](identifiability/RESULTS.md), [frozen stress test](capture-recapture/SIMULATION-PROTOCOL.md).

## A concrete integration now exists

The [collector](advisory-prototype/README.md) runs the pinned canonical `review-ledger next` against byte-identical ledger evidence and binds the named Git object. It distinguishes pending required work, caps, unknown coverage and a shadow candidate for extra inspection. Trigger category and acceptance remain supplied assertions; hashes prove bytes and reachability, not truth. Every result disables execution. Live dirty-worktree coverage and parent-verified final-fix coverage are unsupported.

Sixteen focused tests, three deliberate mutations and independent review support the prototype's stated scope. The review caught duplicate/reordered history falsely creating a boundary; that defect is corrected. A real-corpus smoke verifies all 21 pinned ledgers: 18 legacy schemas are explicitly refused, while three supported captures preserve pending work, insufficient evidence or cap escalation. No unperformed review becomes a negative label. [Validation](advisory-prototype/VALIDATION.md), [audit](advisory-prototype/AUDIT.md), [batch results](advisory-prototype/batch-smoke/RESULTS.md).

The [Paneweft graph](evidence-graph/paneweft.bundle.json) traces one historical finding → fix → new cancellation interaction → behavioral replay → correction. A pinned real CLI round trip preserves all 11 edges. An empty freshness list initially yielded misleading `fresh` presentation; the export now supplies genuine historical fingerprints and correctly remains `unverified` in an unregistered session. The original output is preserved. [Integration evidence](evidence-graph/cli-checks.json).

Residual mappings remain proposed component/outcome links. The old bug is fixed; it was not filed as a stressor. A stage-aware cancellation owner is an architectural hypothesis requiring a behavioral comparison, not an automatic rerouting recommendation. Ratings alone cannot establish a better architecture. The [architecture research note](ARCHITECTURE.md) gives more direct structural/history precedents and a proposed controlled Edge retention comparison; that implementation experiment has not run.

A focused two-version source challenge also exercised private reports and adjudication. One parent follow-up shared a new hypothesis between arms; post-follow-up findings are therefore excluded from independent detection claims. The exercise yields no accuracy estimate. [Adjudication and deviation](blind-challenge/ADJUDICATION.md).

## Where your setup differs

Your `build-loop` already requires fresh review in specified cases, meaningful exchanges and caps. Later findings in those required rounds do not justify adding rounds beyond the actual stopping policy. Final historical ledgers contain later dispositions; truncating their rounds cannot recover authentic earlier decisions.

Your `test-quality` practice provides stronger evidence than accepted reviewer comments alone. The cancellation replay uses the same assertions against the broken and corrected implementations. Its Qex/Cargo peers are fakes, so it is not a full interoperability result. [Reproduction](REPRODUCTION.md).

The practical longitudinal object is a versioned record of contracts, reviewed code, fixes, private findings and subsequent outcomes. Shared hypotheses and changed scopes belong in that record. A single scalar score currently hides too much of it.

## Candidate actions

1. **Use the collector passively on ten new decisions.** Start with phoe-nix for modern ledger compatibility and Paneweft for fast executable cases; include Edge as its decision capture becomes compatible.
2. **Test one fixed additional-inspection trigger in shadow mode.** Keep execution and caps separate, measure supported findings and effort, and observe trigger-negative samples too. The trigger is a policy hypothesis, not a learned gain.
3. **Stop retrospective K searching on this sample.** Revisit a probability model only after authentic eligible outcomes and adequate positive counts exist.
4. **Keep architectural proposals tied to contracts and reproductions.** Use Paneweft to inspect evidence and Residual for explicitly proposed mappings; do not refactor to improve a rating.

The [consolidated schedule](SCHEDULE.md) proposes one additional authorized assay per sampled change, with a ten-assay feasibility checkpoint and a fixed endpoint at 60 independently observed eligible changes or six weeks, whichever comes first. Power calculations show those are feasibility caps, not assurance of a conclusive result. No future review or automation was launched. [Sampling limits](power/RESULTS.md).

## Sources

Frozen protocols, source manifests, outputs, counterexamples and audits are linked above. A [final explanation audit](FINAL-EXPLANATION-AUDIT.md) checked the added K response-speed table and architectural evidence boundaries. A [mathematical spot check](MATH-SPOT-CHECK.md) verified the stated examples and clarified net repair risk. The [reproduction guide](REPRODUCE.md) separates integrity checks, component tests and product replays. A final [consistency audit](FINAL-REPORT-AUDIT.md) checked the consolidated claims; [cross-artifact verification](artifact-integrity.json) checks the current byte bindings without rerunning subjects or refitting models. All local experiments and inspections are dated 2026-11-17. External sources have publication dates and applicability limits in `METHODS.md`, `uncertainty/MEMO.md`, `published-reviewer-elo/README.md` and `capture-recapture/MEMO.md`. Subject repositories were read-only; research files remain local and uncommitted. No Claude models, paid model APIs or upstream actions were used.
