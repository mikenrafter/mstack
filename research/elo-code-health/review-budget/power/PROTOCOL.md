# Synthetic sampling and capture planning

Frozen 2026-11-17 before calculations. No fitted predictor, additional review execution, external validation, causal utility estimate, or optimal-round claim is authorized. This analytical planning exercise compares the prospective proposals in advisory-design/DESIGN.md and uncertainty/MEMO.md.

The decision question is whether a frozen trigger can prioritize ONE additional authorized standardized inspection after the mandatory process finishes. The assay checks a frozen snapshot. It does not identify the optimal number of review rounds.

## Frozen cases

Let q be the prevalence of independently supported material-positive ASSAY outcomes among eligible independent changes. This is not latent true-defect prevalence. Let s/f be the binary trigger's sensitivity/false-positive rate against that assay outcome. Set q=[0.1,0.3,0.6], N=[40,60,120], and trigger families null(s=.3,f=.3), moderate(.65,.15), strong(.8,.1). Use inspection budget b=.8. These assumed values are synthetic, not estimates from the retrospective corpus.

Trigger-positive share t=q*s+(1-q)*f. When t<=b, inspect all trigger-positive cases and sample trigger-negative cases with probability a=(b-t)/(1-t). Expected positive capture R=s+(1-s)*a. When t>b, sample trigger-positive cases with probability b/t and inspect no trigger-negative cases, giving R=b*s/t. This is population-level expected-budget allocation. A finite realized cohort's exact-budget tie allocation can differ.

Compute all nine population recall cases, expected supported positives and captured positives across all27(N,q,trigger) cases. The preregistered practical target is a10percentage-point gain over random80%capture, requiring R>=.9. Do not choose a favorable family or threshold after results.

For each N,q compute the exact binomial probability of at least10 observed positives, with independent complete outcomes and with90% follow-up independent of outcome and trigger. For enrolled N and coverage c, observed positive count M follows Binomial(N,q*c). Missing observations never become negatives. Also report expected observed positives and probability at least one observed negative.

Provide a separate, explicitly SIMPLIFIED power reference: M~Binomial(N,q*c), and, conditional on M, independently captured positives X~Binomial(M,R). Require M>=10 and the smallest X meeting BOTH X/M>=.9 and an exact one-sided null-tail P[Binomial(M,.8)>=X]<=.025. Sum the alternative probabilities over M. Report c=1 for all27 cases;90%coverage sensitivity only for the strong family. This is not the power of the proposed fractional-allocation paired change-bootstrap statistic. It assumes population allocation probabilities are known and independent capture indicators, and ignores estimated trigger share, missingness selection, project dependence, and adjudication error. The exact arithmetic is a reference planning model, not a sample-size guarantee.

For project dependence, illustrate N60 balanced across3 or6projects and within-project correlation rho=[0,.05,.1]. Derive design effect1+(m-1)*rho from equal-variance exchangeable within-project covariances, with m=N/projects. Report variance-equivalent N/design effect. This is a hypothetical sensitivity calculation; it does not establish actual project correlation or enough project clusters.

## Checks and interpretation

Independent oracles: null trigger gives R=.8 for every q; q=.3,moderate gives t=.3 and R=.9; q=.6,strong gives R=11/12; an oversubscribed branch q=.9,s=1,f=0 gives R=8/9; Binomial(N10,q=.5) P(M>=10)=1/1024; with16positives even all captured has null tail.8^16>.025, while17positives permits.8^17<.025; N60,3projects,rho.05 gives design effect1.95 and effective N400/13.

Do not infer that40or60changes provide adequate power. Distinguish enrollment limits, complete outcomes, independently grouped changes, positive count, and project clusters. Resolve the conflicting prospective schedules with one standardized assay per sampled change and a feasibility checkpoint; paired extra reviews require separate justification and owner authorization. No new review is launched by this exercise.
