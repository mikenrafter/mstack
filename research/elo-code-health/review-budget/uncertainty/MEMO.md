# K, uncertainty and what an additional review measures

The principled next step is to model uncertainty about code and reviewer detection separately. Randomizing K would add noise to a learning rule. It would not explain why a reviewer missed a defect. The local negative results provide no reason to select another K retrospectively. This memo proposes a different observation model, not a demonstrated improvement.

## Three different mathematical choices

For binary logistic Elo,

\[
p=\operatorname{logistic}\{q(R_A-R_B)\},\quad q=\ln(10)/400,
\qquad R_A'=R_A+K(y-p).
\]

The logistic curve models outcomes given ratings; 400 sets its scale. K is an update gain. Elo's update is a stochastic gradient step on the Bradley–Terry likelihood, so K plays the role of a learning rate. A fixed or decreasing learning rate is not a probability distribution over rating uncertainty. [Olesker-Taylor and Zanetti, NeurIPS 2024, introduction](https://proceedings.neurips.cc/paper_files/paper/2024/file/f9db8bd38c36391ddc4ccc0d23effdbe-Paper-Conference.pdf).

A distribution such as \(R\sim N(m,v)\) instead expresses uncertainty about latent rating. Integrating the outcome curve over that distribution gives a predictive probability. Changing the gain and representing uncertainty solve different problems.

## What the tested gains mean numerically

The actual grid uses deterministic K8/16/32/64, either fixed or divided by `1 + preceding_training_groups/4`. There is no sampled K distribution. Different order seeds test update-order sensitivity; they are not independent observations or posterior draws.

For the RAW anchored update against a fixed benchmark, starting at p=0.5 and observing y=1:

| K | Probability after one positive outcome | Local mean-error half-life near p=0.5 |
| --- | ---: | ---: |
| 8 | 50.576% | 59.9 updates |
| 16 | 51.151% | 29.8 updates |
| 32 | 52.301% | 14.7 updates |
| 64 | 54.592% | 7.2 updates |

The first column follows exactly from `logistic(q*K/2)`. The half-life is an explanatory linearization: under a stationary independent Bernoulli stream near the calibrated midpoint, the expected rating error contracts per step by approximately `1-q*K/4`, giving `log(0.5)/log(1-q*K/4)`. It is not an effective sample size, a posterior interval, or a half-life under edits, bucket changes, changing K or correlated reports. Two moving Elo opponents require a different calculation. The implemented forecast additionally shrinks bucket predictions toward the training prior, so this table is not the full pipeline's output.

This gives K an understandable response-speed interpretation. It supplies no evidence about defects a reviewer never observes. Comparisons manufactured from one source observation cannot be counted as this many independent informative updates.

## What the established alternatives offer

| Method | Where uncertainty enters | Relevance here |
|---|---|---|
| Glicko | Rating mean and rating deviation; uncertain opponents contribute less decisive evidence | Adaptive update sizes and an explicit uncertainty estimate |
| Glicko-2 | Adds volatility governing changes in latent strength | A starting point for changes over time, with a new drift assumption to justify |
| TrueSkill | Gaussian beliefs over skill, separate Gaussian performance variation, approximate Bayesian updates | Separates what we do not know from outcome variability |
| Rasch / item response | Success depends on reviewer ability minus challenge difficulty | Separates reviewer detection ability from the difficulty of a known challenge |

Glickman's original model treats strengths as changing latent quantities rather than just point scores. In Glicko-2, uncertainty rises between rating periods through volatility and contracts through informative results; opponent uncertainty also changes the expected-result calculation. A gain therefore follows the model's uncertainty. Code edits would require a defensible transition model instead of borrowing chess inactivity rules unchanged. [Glickman, 1999](https://www.glicko.net/research/glicko.pdf), [Glickman, Glicko-2 worked specification, steps 3 and 6–7](https://glicko.net/glicko/glicko2.pdf).

For intuition, one Newton step with a Gaussian prior and a fixed known opponent gives this approximate binary logistic update:

\[
v'=(v^{-1}+q^2p(1-p))^{-1},\qquad
m'=m+\underbrace{qv'}_{K_{\mathrm{effective}}}(y-p).
\]

This is an illustrative derivation, not the full Glicko algorithm. Larger prior uncertainty permits a larger correction. A dynamic model could first add process variance, \(v^-=v+Q\), but the amount Q requires evidence about actual changes. Thousands of comparisons derived from one observation cannot justify thousands of independent variance reductions.

TrueSkill places Gaussian beliefs over skill and models per-game performance noise separately. In the simple no-draw two-player case this gives a Gaussian-CDF, or probit, outcome curve after integrating uncertainty. It is not logistic Elo with a randomly drawn K. The paper also describes adding variance when skill changes over time. Its gaming results do not establish validity for code reviews. [Herbrich, Minka and Graepel, NeurIPS 2006, §2](https://proceedings.neurips.cc/paper/2006/file/f44ee263952e65b3610b8ba51229d1f9-Paper.pdf).

An item-response formulation can use \(P(\text{known challenge detected})=\operatorname{logistic}(a_r-d_i)\). Here \(a_r\) is reviewer ability and \(d_i\) is challenge difficulty. Elo has already been applied to estimating student ability and item difficulty jointly. Transferring that structure to reviewers and executable defect challenges is our hypothesis. It requires overlapping reviewers and anchored tasks; adding the same constant to both latent parameters leaves predictions unchanged. [Pelánek, 2016, model and educational application](https://www.fi.muni.cz/~xpelanek/publications/CAE-elo.pdf).

## Reviews are imperfect tests on a changing object

The following is a proposed model for this project. Let D mean that a material defect is present in the fixed snapshot and assessed scope. Before review, that scope excludes previously known findings; after a positive report the same defect can be known and still present until repair. Let Y mean a review reports a material finding. Let p be the probability of D, s reviewer sensitivity, and f the false-positive probability when D is absent. Then

\[
P(Y=1)=sp+f(1-p),\qquad
P(D=1\mid Y=0)=\frac{p(1-s)}{p(1-s)+(1-p)(1-f)}.
\]

A clean report is weak evidence when sensitivity is low. For illustration, p=0.5 and f=0.05 leave posterior risk 0.174 after a negative review with s=0.8, but 0.457 with s=0.2. These are assumed numbers illustrating Bayes' rule, not measured reviewer performance.

For the actual patch action and observed review result, let a be the NET probability that no material defect remains after the patch when D was true, including the possibility of repair-induced defects. Let b be the probability a defect is present afterward when D was false. A simplified state transition is

\[
p_{\mathrm{next}}=p_{\mathrm{after\ review}}(1-a)+(1-p_{\mathrm{after\ review}})b.
\]

These transition probabilities are conditioned on whether a patch occurs and on the observed result; they are not constant repair parameters inferred from a finding rate. With no patch and no other change, a=b=0. In the separate identifiability example, a positive finding followed by repair success r and conditional introduction hazard h gives a=r(1-h), not r.

This explains why more rounds need not monotonically imply less risk. Repairs can create problems. Reviewers can also share blind spots, and supplied prior findings change what counts as undiscovered. A single scalar “volatility” cannot resolve these mechanisms by itself.

Identification is the limiting factor. One observed detection rate cannot identify p, s and f separately. More rounds on changing snapshots do not automatically add the missing information. Hui and Walter showed how multiple imperfect tests can become identifiable under specific population and conditional-independence assumptions. Johnson and colleagues demonstrated that Bayesian inference alone does not repair insufficient identification. Correlated LLM reviewers and selected review scopes make those assumptions especially consequential here. [Hui and Walter, 1980](https://pubmed.ncbi.nlm.nih.gov/7370371/), [Johnson, Gastwirth and Pearson, 2001](https://pubmed.ncbi.nlm.nih.gov/11323324/).

## One falsifiable prospective experiment

This paired-review design is a more expensive later alternative, not the initial pilot. The consolidated [`SCHEDULE.md`](../SCHEDULE.md) takes precedence for the proposed first experiment; no future reviews are authorized by this memo.

Preregister 20 calibration changes followed by 40 new evaluation changes. After all mandatory review gates, pin each revision, materiality definition, prior-known-finding set, reviewer configuration and equal review budget. Run two extra reviews independently on that same snapshot with separate contexts. Both receive the same prior-known findings; neither sees the other's extra report. Adjudicate every report with reproductions or explicit contract evidence, recording duplicates and review effort. No prediction determines which changes receive verification.

Use the calibration phase to specify reviewer detection assumptions, including fixed executable challenge fixtures with known failure outcomes. These fixtures anchor detection for their challenge families; their sensitivity is not assumed to transfer unchanged to natural code. Freeze one uncertainty-aware model and the existing simple baseline before evaluation. Forecast whether the first extra review finds an adjudicated material issue beyond the mandatory-review record. The second review supplies overlap and miss evidence, not a perfect ground truth. Record actual fix transitions separately; never count them as independent repeated tests of the original snapshot.

The hypothesis is that the uncertainty-aware model improves prospective next-review-yield probabilities over the frozen baseline. Evaluate paired Brier-score differences with intervals grouped by change and report calibration. Claim support only if the uncertainty interval favors the candidate; otherwise report failure or insufficient evidence. Forty changes may be underpowered. If inferred latent risk changes substantially under plausible sensitivity assumptions, report a range and keep additional review as the default. Do not infer defect absence, automate skipping, or select another K from these evaluation outcomes.
