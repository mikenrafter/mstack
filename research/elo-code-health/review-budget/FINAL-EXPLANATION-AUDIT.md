# Final explanatory audit

Reviewed 2026-11-17 08:58 UTC. Scope: ARCHITECTURE.md and uncertainty/MEMO.md, “What the tested gains mean numerically.” No fitting, new empirical experiments, source edits, model calls or delegation.

**No substantive defects found in the reviewed scope.**

The raw anchored Elo table agrees with the stated scale q=ln(10)/400 and fixed benchmark. Starting at p=0.5, one positive outcome moves the rating by K/2, yielding logistic(qK/2). Direct arithmetic gives 50.57562084%, 51.15108912%, 52.30095873% and 54.59219228% for K=8,16,32,64, respectively. The displayed rounded values are correct.

For a stationary Bernoulli mean of 0.5, linearizing the conditional expected rating-error update about the midpoint gives contraction factor 1−Kq/4. The displayed log(0.5)/log(1−Kq/4) half-lives round correctly to 59.9, 29.8, 14.7 and 7.2 updates. The note explicitly limits this to a local mean-error approximation and excludes correlated reports, changing K, changing buckets and two moving opponents. It does not present these values as effective sample sizes or uncertainty intervals.

The numerical table is explicitly marked RAW, with starting probability stated, and explicitly distinguished from the implemented prior shrinkage. Reading models/forecast.py confirms both the raw update and the deterministic decay schedule; the real pipeline additionally starts buckets at training-prior odds, shrinks by distinct bucket-group count, and averages update-order seeds. Nothing in this section claims the table reproduces those pipeline outputs.

ARCHITECTURE.md distinguishes published observational findings from proposed transfer. The Brightsquid values match the supplied verified primary-source record: DL 86%→83%, PC 6%→6%, crossings 29→6, and files affected by unstable interfaces 471→59. The note preserves the concurrent-change causality caveat and the single-system limit. The other two sources are explicitly restricted to the abstract/first-page scope actually inspected.

The Edge alternative is clearly a proposed controlled comparison with held-out behavioral assays. The note explicitly says that it has not run, no source rerouting occurred, and the existing evidence graph does not implement the comparison. Architectural comparison outcomes are explicitly separated from additional-review outcomes. No executed refactor, causal gain, or optimal-round model is implied.
