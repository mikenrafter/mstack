#!/usr/bin/env python3
"""Choose parameters from structured training only, before external labels open."""
import hashlib
import json
from pathlib import Path
from forecast import choose_config, observations

HERE = Path(__file__).parent
content = (HERE / 'structured-training.jsonl').read_bytes()
rows, excluded = observations([json.loads(line) for line in content.splitlines() if line.strip()],
                              'documented_consequential_discovery')
if len({row.outcome for row in rows}) < 2:
    raise SystemExit('Reported-discovery training has fewer than two classes')
result = {'training_sha256': hashlib.sha256(content).hexdigest(),
          'label': 'documented_consequential_discovery', 'training_rows': len(rows),
          'training_groups': sorted({row.group for row in rows}),
          'logistic_penalty': choose_config(rows, 'logistic'),
          'elo_config': choose_config(rows, 'anchored_elo'),
          'excluded': excluded,
          'freeze_reason': 'Select on structured corpus only before opening external prose-chain labels.'}
(HERE / 'external-locked-settings.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
print(json.dumps(result))
