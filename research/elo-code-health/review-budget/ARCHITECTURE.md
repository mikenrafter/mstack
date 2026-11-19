# Architectural hotspots and rerouting

## Top findings

[B, published observational evidence; D, proposed transfer] Combining structural dependencies with change history is a more direct starting point for architectural hotspots than treating files as Elo competitors. It still supplies candidates for investigation, not proof that moving an edge or extracting an interface improves behavior.

[Mo et al., Decoupling Level, ICSE 2016](https://www.cs.drexel.edu/~yc349/papers/2016/icse2016-DL.pdf) studies independently replaceable modules and reports measurements across 108 open-source and 21 industrial projects. Its abstract and first-page method description were verified here. This is a maintainability metric, not an optimal-review-round model; the metric itself was not reproduced in this pass.

[Mo et al., Architecture Anti-patterns, TSE, online 2019-04-14 / issue 2021-05](https://ieeexplore.ieee.org/document/8691586/) combines structural relations and revision history to detect recurring architectural problems, with analysis of 19 projects. The abstract-level evidence supports inspecting such patterns. It does not establish that every cycle, cochange pair or influential interface is a defect.

[Nayebi et al., longitudinal Brightsquid study, arXiv 2018 / ICSE-SEIP 2019](https://arxiv.org/pdf/1811.12904), sections III, V and VI, is especially relevant. Its before/after analysis distinguishes system-wide measures from localized flaws. Decoupling Level changes from 86% to 83% and Propagation Cost remains 6%, while crossings fall from 29 to six and files affected by unstable interfaces from 471 to 59. The authors report better maintenance outcomes but explicitly reject strict causality because other changes occurred concurrently. This is one industrial Java-system case, not an intervention estimate transferable to Edge. The useful inference is to retain localized evidence and outcomes alongside any scalar summary.

## A tool we could build

The following is our design hypothesis, not a finding from a fitted model:

1. Preserve a versioned dependency graph, an independently recorded change graph, and a contract/outcome graph. Keep missing edges and incomplete language resolution visible.
2. Identify recurrent cross-boundary changes, changing interfaces with many dependents, cycles and duplicated decisions. Keep their evidence separate; do not sum arbitrary weights into a quality number.
3. Inspect the implicated contracts and mixed commits. A dependency can be necessary; unrelated changes sharing a commit can create false coupling. The inspected Edge engine/database pair contains both phenomena.
4. Generate a small architectural alternative tied to one explicit outcome: for example, give one component authority over retention completeness or lifecycle cancellation. Preserve the original as the control.
5. Compare identical behavioral assays, then apply the same new requirement to both alternatives. Measure supported regressions, duplicated decisions, change effort and runtime constraints. File count and graph shape are secondary diagnostics.
6. Offer the measured alternative for architectural review. Until that comparison exists, label the rerouting unmeasured. Elo could eventually aggregate wins on repeated anchored tasks, but would summarize the experiment rather than replace it.

This can feed Paneweft with inspectable graph edges and provenance, and Residual with proposed component/outcome mappings. The implemented case graph already demonstrates the evidence format. It does not perform steps four or five.

## Candidate Edge experiment

The [original retention proposal](../residual-draft.json) already pins a concrete shared invariant at `c11f5cbac942969a410764e86d1a13bdd39a8651` and the current analysis object `cd64eaa89948409ccffbea19ee48d7bd22dcb808`.

Use the current paths as the control and one typed retained-window decision as the candidate. Require that incomplete retained input never overwrites a complete night, deletion and prune metadata commit atomically, the cursor never decreases, and every derive entry path agrees. Hold out DST, a forced window crossing the prune boundary, transaction failure, an older supplied cursor and an algorithm-version rederive.

After parity on these outcomes, vary a retention requirement identically in both implementations and record the required edits and regressions. An interface that merely hides a broken transaction or duplicates authority fails even if its dependency diagram looks simpler. A candidate with no demonstrated benefit should be discarded.

This experiment has not run. Dart is not available in the current shell, and no application build or toolchain installation was launched during final consolidation. It belongs in a separate bounded implementation experiment; no automated source rerouting or live review change follows from this note.

## Where this setup differs

The immediate build-loop question concerns one additional inspection after actual mandatory gates. The architectural experiment concerns changing a responsibility boundary and measuring later behavior. They can share evidence identifiers, but neither result should be used as the other's outcome label.

## Sources

Primary sources above were retrieved 2026-11-17. The Brightsquid full preprint was inspected; the other two papers were checked at abstract/first-page scope after direct PDF fetches timed out. No local architectural metric was newly fitted or claimed as a reproduced result.
