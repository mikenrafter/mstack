#!/usr/bin/env python3
"""Render the frozen synthetic sampling plan without claiming actual study power."""
import json
from pathlib import Path

here = Path(__file__).parent
result = json.loads((here / 'results.json').read_text())
lines = ['# Sampling limits for one additional inspection', '',
         '2026-11-17. Forty or sixty changes are enrollment limits, not a promise of adequate power. These calculations use assumed synthetic rates. They do not estimate actual defect prevalence, model quality, or the causal value of another review.', '',
         'The proposed pilot should test prioritization of ONE additional standardized inspection on a frozen eligible snapshot. It cannot estimate the optimal number of review rounds. All mandatory gates and existing caps remain binding, and a separately valid allocation needs owner agreement before an inspection occurs.', '',
         '## What a trigger must achieve', '',
         'Let q be the proportion of independently supported material-positive assay outcomes. Trigger sensitivity s and false-positive rate f are measured against this assay outcome. They are different from the latent prevalence and reviewer sensitivity in the identifiability demonstration.', '',
         'With budget b=0.8, the trigger-positive share is t=q*s+(1-q)*f. If t<=b, inspect all trigger-positive changes and select trigger-negative changes with probability a=(b-t)/(1-t). Positive capture is R=s+(1-s)*a. If t>b, sample trigger-positive changes with probability b/t, giving R=b*s/t. These formulas allocate 80% in expectation at population trigger frequencies. Finite-cohort tie allocation can differ.', '',
         '| Assay-positive prevalence | Synthetic trigger | Trigger sensitivity / false-positive rate | Expected positive capture | Gain over random 80% | Meets 10-point population target |',
         '| ---: | --- | --- | ---: | ---: | --- |']
for row in result['population_capture']:
    lines.append(f"| {row['prevalence']:.0%} | {row['trigger']} | {row['sensitivity']:.0%} / {row['false_positive']:.0%} | {row['recall']:.2%} | {100*row['gain_vs_random']:.2f} points | {row['recall'] >= .9-1e-12} |")
lines += ['', 'The maximum possible gain above an 80% budget is 20 percentage points. A 10-point improvement requires at least 90% positive capture. Trigger sensitivity alone is insufficient; its false positives and the assay-positive prevalence determine how much budget remains for trigger-negative changes.', '',
          '## Positive counts and missing outcomes', '',
          'For enrolled N and independent follow-up coverage c, observed positive count is Binomial(N,q*c). The following probabilities use the exact binomial sum. The 90% column assumes missingness is independent of the outcome and trigger. This assumption must not be inferred from a high overall follow-up rate.', '',
          '| Enrolled changes | Assay-positive prevalence | Expected positives, complete / 90% follow-up | Chance of at least 10 positives, complete | Chance with 90% follow-up |',
          '| ---: | ---: | --- | ---: | ---: |']
lookup = {(r['enrolled'], r['prevalence'], r['coverage']): r for r in result['positive_count_coverage']}
for prevalence in (.1, .3, .6):
    for enrolled in (40, 60, 120):
        complete, missing = lookup[enrolled, prevalence, 1], lookup[enrolled, prevalence, .9]
        lines.append(f"| {enrolled} | {prevalence:.0%} | {complete['expected_observed_positives']:.1f} / {missing['expected_observed_positives']:.1f} | {complete['probability_at_least10_observed_positives']:.2%} | {missing['probability_at_least10_observed_positives']:.2%} |")
lines += ['', 'Ten positive changes are a minimum coverage check, not adequate evidence for the planned performance claim. Under an independent-positive binomial reference, even capturing every one of 16 positives cannot give a one-sided null-tail probability below 0.025 against random 80% capture. Seventeen out of seventeen can; observing less than perfect capture needs more positives.', '',
          'Both outcome classes are still needed to assess discrimination. At high positive prevalence, the negative class becomes scarce. The grid has expected negatives N*(1-q); a 60-change study at 60% prevalence expects 24 negatives, while at 90% prevalence it would expect only six. That latter value is explanatory arithmetic, not another evaluated case.', '',
          'At 90% follow-up, completing 40 or 60 outcomes needs about 45 or 67 enrollments in expectation, not with guaranteed completion probability. Missing positives can be concentrated in costly or trigger-negative changes. Report missingness by trigger and project; do not replace absent outcomes with negatives or report complete-case results as unbiased without support.', '',
          '## Simplified power reference', '',
          'These numbers are NOT the power of the proposed paired change-bootstrap assay. They use an independent-positive-capture reference: M~Binomial(N,q), and X conditional on M is Binomial(M,R). A successful reference trial requires at least 10 positives, observed capture >=90%, and an exact one-sided random-80% null tail <=0.025. The calculation averages over random positive counts. It ignores estimated trigger share, dependence induced by exact-budget selection, adjudication error, project dependence, and optional-boundary selection.', '',
          '| Assay-positive prevalence | Synthetic trigger | N=40 reference probability | N=60 reference probability | N=120 reference probability |',
          '| ---: | --- | ---: | ---: | ---: |']
power = {(r['enrolled'], r['prevalence'], r['trigger'], r['coverage']): r for r in result['simplified_reference_power']}
for prevalence in (.1, .3, .6):
    for trigger in ('null', 'moderate', 'strong'):
        values = [power[n, prevalence, trigger, 1]['reference_power'] for n in (40, 60, 120)]
        lines.append(f"| {prevalence:.0%} | {trigger} | {values[0]:.2%} | {values[1]:.2%} | {values[2]:.2%} |")
lines += ['', 'For the strong trigger with 90% independent follow-up:', '',
          '| Assay-positive prevalence | N=40 reference probability | N=60 reference probability | N=120 reference probability |',
          '| ---: | ---: | ---: | ---: |']
for prevalence in (.1, .3, .6):
    values = [power[n, prevalence, 'strong', .9]['reference_power'] for n in (40, 60, 120)]
    lines.append(f"| {prevalence:.0%} | {values[0]:.2%} | {values[1]:.2%} | {values[2]:.2%} |")
lines += ['', 'A true gain exactly at the 10-point target can still have a low probability of clearing both the observed effect-size threshold and the uncertainty requirement. More enrollment does not guarantee success for a weak trigger.', '',
          '## Project dependence', '',
          'For N observations in equal-sized project clusters of size m and common within-project outcome correlation rho, summing the within-cluster covariances gives variance inflation 1+(m-1)*rho. The variance-equivalent count is N divided by that design effect. These are hypothetical sensitivity values, not estimated correlations.', '',
          '| Enrolled | Projects | Assumed within-project correlation | Variance inflation | Variance-equivalent count |',
          '| ---: | ---: | ---: | ---: | ---: |']
for row in result['dependence_sensitivity']:
    lines.append(f"| {row['enrolled']} | {row['projects']} | {row['within_project_correlation']:.2f} | {row['design_effect']:.2f} | {row['variance_equivalent_sample']:.2f} |")
lines += ['', 'The variance-equivalent count does not create independent projects. Three or six project clusters remain too few for a strong portability claim. Related stacked changes and repeated snapshots must share a validation group, regardless of how many review records they produce.', '',
          '## One feasible prospective schedule', '',
          '1. Capture the first 10 eligible boundaries passively. Verify canonical gates, snapshot coverage, trigger evidence, and exclusions. This checks the collector and launches no review.',
          '2. If the owner approves a valid research allocation, run one standardized independent assay per sampled change. Start with 10 observed assays as a feasibility check for capture quality, effort, adjudication, and finding rate. The reviewer remains blind to the trigger. This checkpoint cannot establish predictive success.',
          '3. Keep the original frozen trigger and collect up to the agreed 40-60-change or six-week limit. Report raw positive counts, missingness, projects, and uncertainty. A limit reached with too few positives means insufficient evidence. An extension toward 120 changes requires a new explicit budget decision, not an automatic continuation.',
          '4. End with one fixed evaluation of prioritizing an optional assay. Retire the predictive claim if its criteria fail. Any learned uncertainty model, paired extra reviews, repair-utility trial, or optimal-round recommendation requires a separately scoped experiment.', '',
          'This replaces the conflicting suggestion of 20 calibration changes followed by 40 evaluation changes with TWO extra reviews per change. Paired reviewers may later help study detection overlap, but they cost more and still do not supply perfect ground truth. They are unnecessary for the first fixed-trigger feasibility question and are not authorized here.', '',
          'Freeze the evaluation endpoint before outcome collection. The feasibility checkpoint may stop an unworkable pilot; it cannot authorize repeated extensions until a favorable result appears. A later budget extension needs a separately specified analysis and independent confirmation or a valid sequential inference design.', '',
          'Inspecting every sampled snapshot is outcome collection for an offline allocation evaluation. It is not a causal comparison of extra review versus no review. Repair-induced harm, avoided shipped defects, inspection effort, and changes in architectural quality need their own outcomes and defensible comparison.', '',
          'Six arithmetic and boundary tests pass. Three deliberately wrong implementations are caught. Protocol and numeric outputs are preserved; no review or future automation was launched.', '']
(here / 'RESULTS.md').write_text('\n'.join(lines))
print('\n'.join(lines))
