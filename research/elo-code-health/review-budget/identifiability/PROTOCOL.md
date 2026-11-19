# Synthetic identifiability demonstration

Frozen 2026-11-17 before executing the arithmetic. This is an analytical demonstration, not another fitted predictor or an empirical gain claim. No repository source, review policy, model provider, or external dataset is involved.

## Two synthetic worlds

A fresh reviewed change has a binary material-defect state D. In world A, P(D=1)=p=1/5 and reviewer sensitivity s=1. In world B, p=4/5 and s=1/4. There are no false positives. The initial finding probability q=p*s=1/5 in both worlds.

Show equality of the exact finite likelihood of k findings among n independent FIRST reviews of fresh changes. Freeze (n,k) to (0,0),(1,0),(1,1),(4,2),(20,4). These are not repeated reviews of the same evolving change. Use rational arithmetic and include the binomial coefficient for count likelihood. A particular ordered sequence has no binomial coefficient.

## Review and repair transition

A review detects a present defect with sensitivity s. On detection, a repair succeeds with probability r. Conditional on successful repair, a fix-induced defect appears with probability h. No finding means no repair and no repair-induced hazard. No other defect births occur. The binary loss counts whether a material defect is present; it does not count several simultaneous defects. The transition is p_next=p-r*(1-h)*q.

Use only r=1, h=1/10, material-defect loss L=100, and review cost c=5 for the decision cases. A review's expected avoided loss is L*r*q; its repair-hazard cost is L*r*h*q. Net utility is L*r*(1-h)*q-c. These are arbitrary synthetic policy units, not estimated costs or calibrated rates.

With identical initial q,r,h,L,c, the IMMEDIATE review utility is identical. Do not manufacture a different immediate decision from p alone. Compare the NEXT review under three explicitly different information states after one first review:

1. Marginal first-review result not observed: residual p_next from the transition.
2. First review found a defect: post-repair risk is 1-r*(1-h)=h for r=1.
3. First review found no defect: posterior risk is p*(1-s)/(1-q), and no repair occurs.

For each information state, next finding probability is s times its updated defect probability. Calculate utility using the same fixed costs and repair parameters. The actual owner decision is conditional on the observed first result; the marginal example is explanatory only. All next-review detections are newly discoverable in these r=1 examples: any first detected defect was repaired, and a subsequent present defect is either previously missed or newly fix-induced.

## Elo and checks

Use the fixed ordered initial-screen observations [0,1,0,0,1] with starting rating1500, fixed benchmark1500, logistic scale400. Show trajectories for K8, K32, K64, and K32/(1+t/4), where t counts prior initial-screen observations. Each deterministic rule receives the same observations in both worlds, so it returns identical world-specific ratings. Changing K changes response speed but supplies no identifying information. This is a consequence of equal input distributions, not a performance experiment.

Independent checks: q arithmetic; binomial n4,k2 likelihood96/625; repair and conditioning probabilities; immediate utility13 in both worlds; marginal next utilities-3.2 and8.95; finding-positive next utilities4 and-2.75; finding-negative next utilities-5 and11.875; expected first-round risk equals the finding/no-finding mixture. Validate all probabilities and input parameters. Mark every output synthetic. End without parameter search.
