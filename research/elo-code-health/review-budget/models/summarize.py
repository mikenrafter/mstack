#!/usr/bin/env python3
"""Render only the valid corrected model outputs into a compact research report."""
import json
from pathlib import Path

HERE = Path(__file__).parent
lines = ['# Forecast results', '', '2026-11-17. Historical accepted-finding proxies; no live policy changes.', '']
for filename, title in [('accepted-results.json', 'Accepted material finding proxy'),
                        ('reported-results.json', 'Reported material finding sensitivity')]:
    path = HERE / filename
    if not path.exists():
        continue
    result = json.loads(path.read_text())
    lines += [f'## {title}', '', f"Input SHA256: `{result['input_sha256']}`.", '',
              f"Inventory: {json.dumps(result['inventory'], sort_keys=True)}.", '']
    if 'loco' not in result:
        lines += [result['reason'], '']
        continue
    for key in ('loco', 'project_holdout'):
        if key not in result:
            continue
        block = result[key]
        lines += [f"### {block['partition']} holdout", '',
                  f"Strongest simple baseline by descriptive outer Brier is `{block['best_simple_descriptive']}`.", '',
                  '| Model | Brier | Change-average Brier | Relative improvement vs best simple | Paired group 95% interval, baseline minus model | Expected misses at 80% budget | Fallback rows | Meets numeric gates |',
                  '| --- | ---: | ---: | ---: | --- | ---: | ---: | --- |']
        for name, metrics in block['metrics'].items():
            interval = metrics['paired_group_bootstrap95']
            lines.append(f"| {name} | {metrics['brier']:.6f} | {metrics['change_average_brier']:.6f} | {metrics['relative_brier_improvement']:.1%} | [{interval[0]:.6f}, {interval[1]:.6f}] | {metrics['allocation80']['missed_positives']:.3f} | {metrics['fallback_test_rows']} | {metrics['meaningful_by_numeric_gates']} |")
        lines += ['', f"Always continue: {json.dumps(block['always_continue'], sort_keys=True)}.",
                  f"Random 80% allocation: {json.dumps(block['random_allocation80'], sort_keys=True)}.", '']
grid_path = HERE / 'accepted-grid-results.json'
if grid_path.exists():
    grid = json.loads(grid_path.read_text())
    lines += ['## Frozen K grid sensitivity', '',
              '| K and schedule | Accepted-proxy Brier |', '| --- | ---: |']
    lines += [f"| {name} | {metrics['brier']:.6f} |" for name, metrics in grid['metrics'].items()]
    lines += ['', 'Every frozen K/schedule is worse than training-only prevalence on these observed rounds. These are sensitivity diagnostics; no candidate was selected from outer scores.', '']
lines += ['## Limits and verification', '',
          'The folds contain selected observed reviews, including mandatory rounds. They do not estimate the causal benefit of adding reviews after the current mandatory path stops. Final acceptance is a weak outcome proxy; no result is an independently established defect reduction.', '',
          'The first logistic implementation had an unstable fixed step for lambda10. Its outputs are quarantined under invalid-optimizer-v1. The corrected runs use the derived gradient bound in OPTIMIZER-AMENDMENT.md. Thirteen boundary and arithmetic tests pass; five specified incorrect implementations are caught, including the original optimizer defect.', '',
          'The parameter grid was fixed before fitting. Nested training folds select parameters; all held-out rows remain evaluated, including one-class training fallback. Bootstrap intervals resample complete changes. Group independence and future transfer remain unproven.', '',
          'The 16 group IDs do not establish 16 independent changes. Some phoe-nix groups share reviewed revisions. Project holdout has only six project clusters. No numerical gate alone establishes meaningful improvement under this unresolved dependence.', '',
          'Pooling leave-one-group-out forecasts for allocation creates a ranking artifact. Each held-out group receives a different training-prior intercept. Holding out a mostly negative group raises its remaining-training prevalence, which can assign higher risks to that negative group. The cross-fold allocation columns are descriptive and cannot establish deployment allocation performance. Fixed-training external forecasts avoid that particular artifact.', '',
          'The K distribution interpretation is analytical. A Beta(a,b) posterior for review yield has mean a/(a+b), and its log-odds rating is R=1500+400log10(a/b). A positive outcome changes R by400log10(1+1/a); a negative changes it by-400log10(1+1/b). The equivalent Elo K depends on the outcome as well as evidence strength. A single pre-outcome K generally cannot reproduce both Bayesian updates exactly. The lag-bucket baseline already uses this form of probability shrinkage. This derivation adds no new fitted model or performance claim.', '']
(HERE / 'RESULTS.md').write_text('\n'.join(lines))
print('\n'.join(lines))
