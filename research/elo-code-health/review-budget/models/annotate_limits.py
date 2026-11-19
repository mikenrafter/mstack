"""Attach interpretation limits without changing predictions or fitted parameters."""
import json
from pathlib import Path

here = Path(__file__).parent
for name in ('accepted-results.json', 'reported-results.json'):
    path = here / name
    result = json.loads(path.read_text())
    result['independent_change_sampling_established'] = False
    result['meaningful_improvement_demonstrated'] = False
    result['interpretation_limits'] = [
        'Group identities do not establish independent changes; some reviewed revisions overlap.',
        'Pooled cross-fold allocation has varying training priors and is descriptive only.',
        'Per-model meaningful_by_numeric_gates is a descriptive check; independence remains unestablished.',
    ]
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
print('Attached dependence and allocation limits; predictions and parameter choices unchanged.')
