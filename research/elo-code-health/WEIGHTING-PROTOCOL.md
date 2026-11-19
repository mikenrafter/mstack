# Elo block weighting diagnostic

Written before this diagnostic runs, 2026-11-16. This is an exploratory analysis of already-inspected historical windows. None of its windows provide fresh validation. The original protocol, results and report remain the primary experiment.

Use the saved broad labels, histories, prediction revisions and five cutoffs for Edge, Analytics, Qex and Diff-core. Keep K=32, initial rating 1500, scale 400 and 25-commit blocks. Use the existing eligibility filter, fractional tie selection and future fix-touch metric. Reuse original sequential Elo results as arm 1 and existing baselines for context.

Within a block of n distinct touched files, define q_i=(fixes_i+1)/(touches_i+2), S_ij=1 when q_i>q_j, 0 when lower, and 1/2 when equal. E_ij=1/(1+10^((R_j-R_i)/400)).

- Arm 1, sequential: the original online update R_i += 32(S_ij-E_ij), updating both players immediately for each pair.
- Arm 2, simultaneous sum: freeze ratings at block start and apply R_i += 32 sum_j(S_ij-E_ij) after all comparisons.
- Arm 3, simultaneous average: freeze ratings at block start and apply R_i += 32/(n-1) sum_j(S_ij-E_ij) after all comparisons. Blocks with fewer than two files do not update ratings.

Arm 2 separates frozen simultaneous updates from sequential order. Arm 3 changes the per-file update budget relative to arm 2. Its absolute per-file block update is bounded by 32 regardless of block size. All comparisons in a block reuse the same observations. Averaging does not make them independent. It also reduces effective learning speed, so improvement cannot identify normalization alone as causal.

Compute logistic expectations with a sign-stable exponential to avoid overflow in the summed arm. Record block sizes, pair counts, per-file comparison exposures and ratings' range. Report all arms and existing baselines across all windows. Pool the original final two windows only as a descriptive comparison on reused data, weighting by eligible future fix touches. Select no winning setting for deployment from this diagnostic.

Before replay, test hand-computed two-file and three-file updates, zero-sum conservation, inactive files, empty/singleton blocks, simultaneous order invariance, stable extreme expectations and training/future separation. Check the runner's two new arms against hand-computed one-block scores. Run tests and replay through qex with one CPU and 256MB. No subject builds or source edits are required. A useful result would justify a prospective frozen comparison with independently adjudicated defects and measured inspection time.
