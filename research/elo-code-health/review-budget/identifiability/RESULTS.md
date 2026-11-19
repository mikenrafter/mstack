# Synthetic review-identifiability example

2026-11-17. These are assumed worlds and exact arithmetic, not empirical rates, fitted models, or a demonstrated improvement in defect detection.

A finding rate combines how often code contains a defect and how often the reviewer detects it. With no false positives, q=p*s. The same 20% finding rate can describe either world:

| Synthetic world | Defect prevalence p | Reviewer sensitivity s | Initial finding probability q |
| --- | ---: | ---: | ---: |
| A | 20% | 100% | 20% |
| B | 80% | 25% | 20% |

For n independent first reviews of fresh changes, the exact likelihood of observing k findings is choose(n,k)*q^k*(1-q)^(n-k). It is identical in these worlds for every finite n and k. For example, two findings among four first reviews have probability 96/625 in both worlds. An ordered four-review sequence with two findings has probability 16/625. The distinction prevents counting permutations twice.

The equality concerns independent first reviews. It does not say that the entire evolving sequence after repairs is observationally identical. Those later observations can supply the information the first-screen rate lacks.

## Review and repair assumptions

The state records whether one material defect is present. A review detects it with sensitivity s. After detection, repair succeeds with probability r. Conditional on successful repair, a fix-induced defect appears with probability h. No finding means no repair or fix-induced hazard. There are no other defect births.

Under these assumptions, residual defect probability is p_next=p-r*(1-h)*q. Hazard h is conditional on successful repair; it is not an independent defect birth applied to every code change. Binary defect loss does not represent the number of simultaneous defects.

The following arbitrary synthetic policy values are fixed: repair success r=1, conditional fix hazard h=0.1, defect loss L=100, review cost c=5. All initial detected defects are repaired. A later defect is either previously missed or newly introduced by a fix, so these cases do not count unresolved known findings as new discoveries.

For a proposed review, expected avoided loss is L*r*q, expected fix-hazard cost is L*r*h*q, and net utility is L*r*(1-h)*q-c. Review when this utility is positive.

Identical current q and identical repair, hazard, and costs give identical IMMEDIATE utility. Both worlds give 20 avoided-loss units minus 2 hazard units minus 5 review-cost units, or +13. Different latent prevalence alone cannot manufacture a different immediate decision under this loss model.

## The next review depends on what was observed

| Synthetic information state | World | Defect risk before next review | Next finding probability | Net utility of next review | Decision |
| --- | --- | ---: | ---: | ---: | --- |
| First result not observed, marginal illustration | A | 2% | 2% | -3.20 | Stop |
| First result not observed, marginal illustration | B | 62% | 15.5% | +8.95 | Review |
| First review found a defect, repair completed | A | 10% | 10% | +4.00 | Review |
| First review found a defect, repair completed | B | 10% | 2.5% | -2.75 | Stop |
| First review found no defect | A | 0% | 0% | -5.00 | Stop |
| First review found no defect | B | 75% | 18.75% | +11.875 | Review |

The owner normally decides after observing the first result, so the conditional rows are the relevant examples. A positive first finding establishes that the old defect existed; the remaining risk is the assumed 10% fix hazard. A no-finding result leaves risk p*(1-s)/(1-q). It eliminates risk only in the assumed perfect-sensitivity world.

These worlds give the same probability to the first observed finding or no-finding outcome. They nevertheless imply different conditional next-review decisions. The observation alone does not tell us which world applies.

## What K can and cannot supply

The demonstration applies four predetermined rating rules to the same ordered initial-screen outcomes [0,1,0,0,1]: K=8, K=32, K=64, and K=32/(1+t/4). Each uses initial rating 1500, benchmark 1500, and logistic scale 400.

Each rule returns the same rating trajectory in world A and world B because its inputs are identical. Changing K changes the reaction to an observation. It supplies no evidence that separates prevalence from reviewer sensitivity. This is a consequence of the equal likelihoods, not a benchmark result or a claim that ratings are useless once richer evidence is available.

## Data that would help choose extra rounds

- Independently inspect representative findings and no-finding cases. Finding acceptance alone does not establish residual defect prevalence or false-positive rate.
- Measure reviewer sensitivity on representative independently supported defects and clean controls. Seeded mutations can test a specific detection capability, but do not automatically represent natural defects or architectural failures.
- Preserve defect identities and before/after revisions. Verify repair outcomes and distinguish missed old defects from newly introduced fix defects.
- At eligible stopping boundaries, assign bounded extra review independently of the score. Record the observed prior outcome, reviewer, scope, cost, fixes, and common independent final checks.

A randomized extra-review study can estimate the net benefit directly without separately identifying every latent p and s. The demonstration shows why finding rates alone are insufficient for the stronger stopping-policy claim. Adding false positives or changing reviewer behavior would introduce further unknowns.

Exact rational calculations and rating trajectories are in results.json. Six arithmetic and boundary tests pass. Three deliberately incorrect implementations are caught. The protocol was frozen before execution. No empirical data or live review policy changed.
