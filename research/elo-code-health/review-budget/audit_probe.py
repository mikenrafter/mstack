"""Synthetic-only numerical audit; never reads a corpus."""
import importlib.util
import json
import math
from pathlib import Path
import sys
import tempfile

MODELS = Path(__file__).parent / 'models'
sys.path.insert(0, str(MODELS))
import forecast

raw = []
for i in range(8):
    raw.append({'group_id': f'g{i}', 'project': 'synthetic', 'ordinal': 2,
                forecast.LABEL: bool(i % 2),
                'features_before_round': {'previous_score': 10 if i % 2 else 0,
                                          'previous_verdict': 'CHANGES'}})
rows, _ = forecast.observations(raw)
with tempfile.TemporaryDirectory() as scratch:
    fixed_path = Path(scratch) / 'audit_fixed.py'
    source = (MODELS / 'forecast.py').read_text()
    broken_line = 'weights[index] -= 0.5 * (gradient[index] + (penalty * weights[index] if index else 0))'
    assert source.count(broken_line) == 1
    fixed_path.write_text(source.replace(broken_line, 'weights[index] -= (0.5 / (1 + penalty)) * (gradient[index] + (penalty * weights[index] if index else 0))'))
    spec = importlib.util.spec_from_file_location('audit_fixed', fixed_path)
    fixed = importlib.util.module_from_spec(spec)
    sys.modules['audit_fixed'] = fixed
    spec.loader.exec_module(fixed)
    for penalty in forecast.LAMBDA_GRID:
        captured = {}
        def trace(frame, event, arg):
            if event == 'return' and frame.f_code is forecast.fit_predict.__code__:
                captured['weights'] = list(frame.f_locals['weights'])
            return trace
        sys.settrace(trace)
        actual, _ = forecast.fit_predict(rows, rows, 'logistic', penalty)
        sys.settrace(None)
        corrected, _ = fixed.fit_predict(rows, rows, 'logistic', penalty)
        weights = captured['weights']
        loss = sum(max(z, 0) + math.log1p(math.exp(-abs(z))) - r.outcome * z
                   for r in rows for z in [sum(w*x for w,x in zip(weights, r.predictors))]) / len(rows)
        objective = loss + penalty / 2 * sum(w*w for w in weights[1:])
        print(json.dumps({'penalty': penalty, 'actual_first_two': actual[:2],
                          'corrected_first_two': corrected[:2],
                          'actual_brier': forecast.brier([r.outcome for r in rows], actual),
                          'corrected_brier': forecast.brier([r.outcome for r in rows], corrected),
                          'actual_max_abs_weight': max(map(abs, weights)),
                          'actual_penalized_objective': str(objective),
                          'intercept_only_objective': math.log(2)}))
