# Mathematical spot check

The inspected algebra and displayed numerical examples are consistent with their stated assumptions. They do not establish an optimal number of review rounds. One state-definition ambiguity in `uncertainty/MEMO.md` was identified and corrected during this check, preventing a reader from dropping repair-induced risk when connecting its transition model to the identifiability example.

This was a read-only inspection on 2026-11-17. The three requested notes were read, plus exactly three supporting local files: `identifiability/demonstration.py`, `power/planning.py`, and `power/results.json`. No model was fitted, script executed, new experiment run, or cited external paper independently checked.

## Recommended clarification

Disposition: the parent accepted the clarification and updated the memo. Reinspection confirms it now defines defect presence separately from discovery status, net clearance including introduced defects, dependence on actual patch action, no-patch a=b=0, and a=r(1-h) in the identifiability positive-result branch. This resolves the ambiguity without numeric or script changes. The discussion below records the original issue and the reasoning for the correction.

`uncertainty/MEMO.md:44` defines D as an undiscovered material defect, then conditions on a positive review and applies a patch transition at lines 53-56. After a positive report, that detected defect is known. D should refer to material-defect presence on the fixed snapshot when applying Bayes' rule, with the known/undiscovered distinction tracked separately. Otherwise a reader might incorrectly set D false merely because the reviewer reported the defect.

The transition

\[
p_{next}=p_{after}(1-a)+(1-p_{after})b
\]

is correct if a is the **net probability of a defect-free post-patch state given pre-patch defect presence**, and b is the probability of a defective post-patch state given pre-patch absence. Both depend on the observed review outcome and patch action. The current phrase "removes all remaining material defects" could be read as old-defect removal alone, which would omit new defects introduced during a successful repair.

Suggested replacement for the definition, leaving the formula unchanged:

> Let D indicate material-defect presence in the fixed snapshot, whether known or undiscovered. After observing review result Y and choosing patch action A, let a=P(D_next=0 | D=1,Y,A) be net clearance, including any newly introduced defects, and b=P(D_next=1 | D=0,Y,A). With no patch and no other code changes, a=b=0.

In the identifiability demonstration's positive-finding branch, a=r(1-h), not merely r. With r=1 and h=0.1, this gives residual risk 0.1 as its table states. Before observing the first finding and applying a patch only upon detection, the marginal clearance probability is s*r*(1-h). The two notes use compatible but differently parameterized models; no numerical correction is required.

## Verified algebra

| Claim | Check | Assessment |
| --- | --- | --- |
| Elo gain versus uncertainty | `uncertainty/MEMO.md:9-16` | With p=logistic(q(R_A-R_B)), the likelihood gradient in R_A is q(y-p). The Elo update is a gradient step with learning rate K/q. K therefore plays the role of update gain; it is not itself a distribution over latent uncertainty. The memo's wording is consistent with that constant rescaling. |
| One-step Gaussian-prior update | `uncertainty/MEMO.md:29-36` | At the prior mean m, the negative posterior Hessian is v^-1+q²p(1-p) and the gradient is q(y-p). One Newton step gives the displayed v' and mean shift q*v'*(y-p). This is a local curvature approximation, not an exact posterior variance or the full Glicko algorithm. The memo explicitly labels it illustrative. |
| Negative-review posterior | `uncertainty/MEMO.md:44-51` | Bayes' numerator is p(1-s) and the denominator adds (1-p)(1-f). For p=.5,f=.05, s=.8 gives .1/.575≈.174; s=.2 gives .4/.875≈.457. These are assumed example risks, not calibrated reviewer rates. |
| Equal first-screen likelihoods | `identifiability/demonstration.py:35-40`; `identifiability/RESULTS.md` opening | Both worlds have q=.2. Two findings among four independent first screens have probability 6*(.2²)*(.8²)=96/625; one ordered sequence has 16/625. The notes correctly restrict observational equality to initial screens, not the evolving repaired sequence. |
| Conditional repair hazard | `demonstration.py:43-61` | Marginal residual p-r(1-h)q, positive-result residual 1-r(1-h), and negative-result residual p(1-s)/(1-q) follow from the stated model. Hazard occurs only after successful repair. There is no unjustified hazard applied to a no-finding/no-edit branch. |
| Review utility | `demonstration.py:64-77`; `identifiability/RESULTS.md:24-39` | Utility is L*r*(1-h)*q-c. The initial worlds both give +13. After a positive finding and successful repair, q is .1 or .025 and utility is +4 or -2.75. After a negative finding, World B's posterior risk is .75, q=.1875, and utility=+11.875. The table is correct. These are one-proposed-review utilities under a binary loss model, not a fitted global round policy. |
| Expected-budget trigger allocation | `power/planning.py:20-33` | Trigger share t=q*s+(1-q)f. When t≤b, selecting negative triggers with (b-t)/(1-t) uses expected budget b and captures s+(1-s)a of positives. When t>b, positive-trigger selection b/t gives capture b*s/t. The notes distinguish population expected allocation from finite-cohort ties. |
| Positive counts with follow-up | `planning.py:36-47,62-74,106-113` | Independent outcome-blind follow-up yields observed-positive probability q*c and count Binomial(N,q*c). The report explicitly states the independence assumption and does not treat complete-case estimates as automatically unbiased. |
| Seventeen-positive reference | `planning.py:50-59`; `power/RESULTS.md` positive-count discussion | Full capture of 16 positives has random-80% null-tail .8^16≈.0281, above .025; 17 gives .8^17≈.0225. The threshold statement is correct. Tail≤.025 corresponds to the lower endpoint of a central 95% exact interval, or a one-sided 97.5% level. It must not be renamed a one-sided 95% test. The report names the .025 tail explicitly. |
| Simplified power calculation | `planning.py:62-74`; `power/results.json`; `power/RESULTS.md` reference section | The code sums P(M=m)*P(X≥critical(m) | M=m), with M~Binomial(N,q*c) and X~Binomial(m,R). This matches the report's simplified independent-positive model. It omits exact-budget coupling, estimated trigger share, project dependence, adjudication error, and selective eligibility, all explicitly disclosed. It is not power for the proposed paired-bootstrap assay. |
| Project design effect | `planning.py:77-84`; `power/RESULTS.md` dependence section | Equal cluster size m and common within-cluster correlation give 1+(m-1)rho. For N=60, three clusters and rho=.05 give effect1.95 and variance-equivalent N≈30.77; six clusters give effect1.45 and N≈41.38. The notes correctly avoid converting these into extra independent projects. |

## Interpretation boundaries to retain

The gain/uncertainty memo proposes assumptions; it has not estimated reviewer sensitivity, latent defect risk, or process variance from these repositories. A useful next-review-yield forecast would still not equal defect-absence probability.

The identifiability demonstration shows a limitation of finding rates, not impossibility of learning from richer longitudinal evidence. Its repair model allows one binary defect state, no false positives, no simultaneous defect count, and no defect birth without a successful repair. Its conditional examples cannot be transferred to a real stopping policy without validating those assumptions.

The power report is deliberately a reference calculation. Its effect-size requirement, binomial significance condition, and prospective bootstrap criterion are not interchangeable. The report already warns against this substitution. Assumed prevalence and trigger rates must not be presented as measured project rates or a sample-size guarantee.

The paired-review proposal in the uncertainty memo is labeled a more expensive later alternative and defers to the consolidated schedule. Preserve that precedence. Neither paired reviews nor a larger enrollment budget is authorized by a mathematical illustration.

This spot check found no algebraic change that would rescue the failed retrospective models or justify changing K again. The recommended clarification concerns state meaning and net repair risk, not an additional experiment or a new recommendation rule.
