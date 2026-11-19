# Independent matrix and finite-coverage audit

No numerical or parsing findings remain for the inspected artifacts. Six empirical tests and three coverage tests pass. An independent calculation also agrees with all 602 pair records, every saved empirical summary metric, and all 65,528 nonempty finite teams.

The conclusion is limited to a descriptive calculation on these supplied human-inspection matrices. It does not validate capture-recapture as a residual-code-defect estimator, calibrate an LLM reviewer, identify a causal inspection benefit, or establish an optimal number of review rounds.

## Source and manual oracle

The raw source SHA-256 is `696c9397d1213da986db451ab83c369e328e46d6d22afd9091c2ea066faffbcd`. Both Python programs read data files and perform ordinary numerical calculations. No C++ source is imported as executable code, compiled, evaluated or executed.

I inspected the original `atm_nov` rows independently of importing the empirical parser. After excluding ID and P, participant 1 has faults {2,3,4,5,8,13,18,21,25}, and participant 2 has {4,8,11,16,17,21,27}. Their intersection is {4,8,21}; union size is 13. This agrees with the separately recorded parent oracle. The 29 declared reference faults leave 16 unseen reference faults; Chapman gives total 19, remaining 6, and remaining error -10. Remaining relative error is -62.5%; total relative error is -10/29. These targets are distinct.

Source declarations and the original computation loops establish 35 columns per row, two metadata columns, then the declared reference columns and zero padding. The parser excludes ID and P and does not infer the reference denominator from detections. The `pg_jun` header's 29 printed labels contradict its declared 27 reference faults. The explicit amendment permits only that exact header in the pinned source. All six values after its declared fault columns must remain zero. A changed source hash cannot inherit the exception.

For a separate complete check, I removed comments from each literal initializer, flattened its integers and split them into 35-column rows. I did not import `empirical.py` for that calculation. All eight resulting ID-to-detection-set mappings match `normalized-matrices.json`, with the expected row counts and checked zero padding.

## Pair arithmetic and summary targets

For every source pair I independently computed overlap m and union U. Instead of repeating the implemented total-minus-union expression, I used the equivalent remaining-count identity

\[
\widehat N_{\mathrm{remaining}}=\frac{(n_A-m)(n_B-m)}{m+1}.
\]

Exact rational calculations agree with all 602 saved remaining estimates. Adding U agrees with each estimated total. Actual remaining reference faults are N-U, using the declared source N. No reference fault unseen by every inspector disappears from the denominator.

The saved means, medians, remaining-error RMSE, total-population relative errors and their RMSE all agree with an independent aggregation. Less-than-half frequency uses only pairs with positive remaining reference counts. The zero-estimate-with-unseen frequency is correctly provided with both all-pair and positive-remainder denominators. Zero-overlap pairs and subset captures are retained; subset captures can estimate zero while known reference faults remain unseen.

## Exact finite-team coverage

I independently enumerated teams using `itertools.combinations` and direct set unions, rather than the implementation's bitmask recurrence. For every matrix and team size k, these results agree with the saved mean, minimum, maximum and nearest-rank 5th/95th team percentiles.

I also calculated exact rational means from the fault detection frequencies d:

\[
E[\text{found by a uniform k-person subset}]
=\sum_{f=1}^{N}\left(1-\frac{\binom{M-d_f}{k}}{\binom{M}{k}}\right).
\]

When M-d is less than k, its numerator is zero. This agrees with each direct-enumeration mean. Dividing by the declared N agrees with every reference-coverage value. Successive means define expected marginal gains under a uniformly random ordering of this finite pool; they do not measure the effect of hiring another reviewer or running another sequential repair round.

Even the complete supplied pools leave reference faults unseen in seven matrices: ATM November 4, ATM June 5, PG November 4, PG June 1, NASA A November 6, NASA B November 5 and NASA B June 1. NASA A June is the only pool reaching its declared reference total. These are reference-list statements, not exhaustive natural-defect counts.

## Sampling and interpretation limits

There are 102 matrix rows but only 26 distinct cohort-plus-ID keys across the supplied arrays. Keys repeat across documents. A cross-cohort person crosswalk is unknown, so neither 102 rows nor 26 keys establishes that many independent people. Fault IDs are local to artifact/version; matching a column number across documents does not establish the same fault.

The 602 pairs overlap in inspectors and faults. The 65,528 teams overlap even more extensively. Neither count supplies independent replication or population confidence intervals. Team quantiles describe variation in the finite pool. Reading techniques are mixed, document versions differ across replications, and the supplied reference list may omit natural defects.

The empirical underestimation pattern challenges using these two-list estimates as stopping evidence. It does not isolate whether heterogeneous detectability, dependent reviewers, selected preparation techniques or other study features caused the pattern. The code appropriately preserves all eight matrices and fits no parameters or thresholds. Any transfer to changing code snapshots or LLM reviewers needs separate evidence.

## Verification record

- Empirical tests: qex `57640550-ab12-4b53-9395-7c3002feb133`, six passing.
- Coverage tests: qex `a1575e84-1b3f-4291-bf02-92ff380682b1`, three passing.
- Independent source, pair and exact team calculations: qex `c65b3f93-50b4-49f1-9d90-1f00f1e13eb4`.
- Independent complete summary-metric check: qex `6e899936-d3e9-4ee1-a704-78067a746448`.

Inspected SHA-256 fingerprints:

| Artifact | SHA-256 |
|---|---|
| `empirical.py` | `6e45272bd73e0cf7828bb928b22418f62dc5dc89a8ee8d9c7eb6a4e02d98cc80` |
| `coverage.py` | `cedeef932166c046f54292d28bfdda36452e3daa9002d37574ba0d370971b5ca` |
| `normalized-matrices.json` | `b8b5cea1c423e88c4e65363eed3c7b37abc07750c2ae8b009003c8da85239dec` |
| `empirical-results.json` | `89413f84f13385c4c7d46207066b6bad6dd3564dd4714a3658e0524370edd76a` |
| `coverage-results.json` | `5a660191704c9e410dd3555bdbd177ce2db438686be7d111df8e3f1ff45877a1` |

Only this audit document was authored. No product tests or raw C++ program ran, and no matrix, estimator, protocol or result artifact was edited by this review.
