# Exact reference-fault coverage by inspection count

Frozen 2026-11-17 before inspecting the normalized matrices or calculating coverage results. This is a descriptive extension on the same eight public human requirements-inspection matrices, using their declared study faults. It introduces no estimator, fitted parameters, optimal-round rule or live review.

For each matrix with M inspectors, enumerate all subsets at every size k from 1 through M. Report the exact mean discovered-reference-fault count, expected marginal discovery from the kth inspector, minimum/maximum and 5th/95th percentiles across teams, and reference faults never found by any inspector. Every unordered subset receives equal weight. Pools mix the study's documented reading techniques; do not interpret these curves as a controlled comparison of techniques.

Independently check each mean against the combinatorial expression: a fault found by d inspectors is missed by a random k-person subset with probability choose(M-d,k)/choose(M,k). Sum one minus this probability over declared reference faults. This needs no independence assumption about individual detection behavior; it describes the finite supplied matrix. It cannot infer faults outside its reference list or predict a new reviewer.

Keep matrices separate. Team subsets overlap and are not independent samples. Team percentiles describe variation within this finite pool, not confidence intervals about a general reviewer population. Do not turn a nominal coverage target into a production review count. These are independent preparations on a fixed artifact, not sequential code-repair rounds. Retain every curve and all limitations, even if coverage fails to approach the declared reference total.
