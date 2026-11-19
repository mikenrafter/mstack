#!/usr/bin/env python3
"""Summarize the single frozen fix-shape diagnostic without selecting new models."""
import json
from pathlib import Path

here = Path(__file__).parent
result = json.loads((here / 'results.json').read_text())
lines = ['# Fix-shape diagnostic results', '',
         '2026-11-17. Adding the frozen revision-shape features did not improve the forecast. This ends the diagnostic without another feature or threshold search.', '',
         'This is a post-hoc exploratory analysis of the already examined structured corpus. No external chain outcomes enter fitting or evaluation. The accepted-finding target remains an acceptance proxy, not independently verified defects.', '',
         f"Inventory: {json.dumps(result['inventory'], sort_keys=True)}.", '',
         'All 39 labeled later rounds have observed pinned snapshot comparisons. The join verifies source identity, project, round, and recorded revision prefixes. Missing snapshots would use explicit missing flags; none were needed here.', '']
for key in ('loco', 'project_holdout'):
    block = result[key]
    lines += [f"## {block['partition']} holdout", '',
              '| Model | Brier loss | Change-average Brier | One-class fallback rows |',
              '| --- | ---: | ---: | ---: |']
    for name, metrics in block['metrics'].items():
        lines.append(f"| {name} | {metrics['brier']:.6f} | {metrics['change_average_brier']:.6f} | {metrics['fallback_rows']} |")
    augmented = block['metrics']['augmented_logistic']
    best = block['best_simple_descriptive']
    intervals = augmented['paired95_vs_each_simple'][best]
    group_interval, project_interval = intervals['group']['percentile95'], intervals['project']['percentile95']
    lines += ['', f"The strongest simple descriptive baseline is {best}. Relative Brier improvement is {augmented['relative_improvement_vs_best_simple']:.1%}; a negative value means worse loss.", '',
              f"Paired baseline-minus-augmented Brier interval: change-group resampling [{group_interval[0]:.6f}, {group_interval[1]:.6f}], project resampling [{project_interval[0]:.6f}, {project_interval[1]:.6f}]. These use 16 group IDs and six project clusters; independence is unestablished.", '',
              '### Within-change allocation', '',
              '| Forecast or fixed rank | Expected reviews | Expected captured positives | Expected missed positives |',
              '| --- | ---: | ---: | ---: |']
    for name, allocation in block['within_change_allocation80'].items():
        lines.append(f"| {name} | {allocation['expected_reviews']:.3f} | {allocation['captured_positives']:.3f} | {allocation['missed_positives']:.3f} |")
    lines += ['']
lines += ['## Interpretation', '',
          'No frozen augmented forecast meets the 10% improvement threshold. The within-change allocations are descriptive. Every change receives an 80% expected budget, with uniform random selection at tied scores. They do not determine which changes deserve an additional review. Always continuing uses every observed opportunity.', '',
          'The fixed ranks use source churn and stateful path names without fitted thresholds. A stateful path name is a scope hint. It does not prove a defect, dangerous architecture, or that a review fix caused an observed defect. Source churn can also describe legitimate complexity or review effort already selected for difficult changes.', '',
          'The model adds five bounded revision features and five missing flags to the lag-score features. Both logistic models use the original regularization grid with nested training-only parameter selection and the corrected bounded gradient step. All observations share the same label coverage. No discarded fold or new outcome-derived feature improves the reported numbers.', '',
          'Seven feature-boundary tests pass. Three deliberate mutations are caught: erasing unknown indicators, removing the source cap, and ignoring snapshot identity fields. The logarithm fixture uses an independent 40-digit Decimal oracle. Fixed 400-step optimization is the specified approximation, not a convergence guarantee.', '',
          'The data do not establish independent change sampling. Project-cluster intervals are a sensitivity check with only six clusters. Historical observed reviews include mandatory reviews and selected difficult changes. This experiment does not identify causal benefit at a valid optional stopping boundary. No live policy or review cap changed.', '',
          f"Input hashes: `{json.dumps(result['input_sha256'], sort_keys=True)}`.", '']
(here / 'RESULTS.md').write_text('\n'.join(lines))
print('\n'.join(lines))
