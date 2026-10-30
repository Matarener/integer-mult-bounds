#!/usr/bin/env python3
"""Refine the single independent-bridge topology and measure degeneration.

Only exact rational zero is admission. Conditioning is retained so a small
floating residual is never mistaken for a finite exact controller.
"""
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
from time import monotonic
import numpy as np
from scipy.linalg import qr
from scipy.optimize import least_squares


HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'independent_topology_probe.py'
RECEIPT = HERE / 'INDEPENDENT-TOPOLOGY-PROBE.json'
spec = importlib.util.spec_from_file_location('independent', SOURCE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
old = json.loads(RECEIPT.read_text())
best = min(old['trials'], key=lambda row: row['squared_error'])
values = np.array(best['floating_coefficients'])
rows = []
started = monotonic()


def record(label, vector, nfev=0):
    residual, jacobian = mod.endpoint(vector)
    matrix, _ = mod.endpoint(vector, exact=True)
    rounded = [Q(float(x)).limit_denominator(65536) for x in vector]
    exact_matrix, exact_residual = mod.endpoint(rounded, exact=True)
    sv = np.linalg.svd(jacobian, compute_uv=False)
    row = {'step': label, 'nfev': nfev,
           'squared_error': float(np.dot(residual, residual)),
           'maximum_error': float(np.max(np.abs(residual))),
           'coefficient_l2_norm': float(np.linalg.norm(vector)),
           'maximum_coefficient': float(np.max(np.abs(vector))),
           'full_matrix_condition_number': float(np.linalg.cond(np.array(matrix, dtype=float))),
           'jacobian_singular_values': sv.tolist(),
           'floating_coefficients': vector.tolist(),
           'rounded_rational_coefficients': [str(x) for x in rounded],
           'exact_rational_endpoint': not any(exact_residual)}
    if not any(exact_residual):
        row['exact_matrix'] = [[str(x) for x in rr] for rr in exact_matrix]
    rows.append(row)
    print(json.dumps({k: v for k, v in row.items() if k not in
                      ('floating_coefficients', 'rounded_rational_coefficients',
                       'jacobian_singular_values', 'exact_matrix')}), flush=True)
    return not any(exact_residual)


record('initial', values)
for epoch in range(2):
    result = least_squares(lambda x: mod.endpoint(x)[0], values,
                           jac=lambda x: mod.endpoint(x)[1], x_scale='jac',
                           max_nfev=10000, ftol=1e-13, xtol=1e-13, gtol=1e-13)
    values = result.x
    if record(f'jac_scaled_{epoch + 1}', values, result.nfev):
        break
else:
    _, jacobian = mod.endpoint(values)
    _, _, pivots = qr(jacobian, pivoting=True)
    selected = np.array(pivots[:32])
    fixed = values.copy()
    def expand(x):
        answer = fixed.copy()
        answer[selected] = x
        return answer
    result = least_squares(lambda x: mod.endpoint(expand(x))[0], values[selected],
                           jac=lambda x: mod.endpoint(expand(x))[1][:, selected],
                           method='lm', max_nfev=10000,
                           ftol=1e-13, xtol=1e-13, gtol=1e-13)
    record('fixed_eight_coordinates_lm', expand(result.x), result.nfev)

result = {'status': 'EXACT_ENDPOINT_FOUND' if any(row['exact_rational_endpoint'] for row in rows)
          else 'NO_EXACT_ENDPOINT_AFTER_CONTINUATION',
          'rows': rows, 'seconds': monotonic() - started,
          'source_sha256': {p.name: sha256(p.read_bytes()).hexdigest()
                            for p in (Path(__file__), SOURCE, RECEIPT)},
          'scope': 'One fixed topology and one numerical continuation. Nonzero rational residual rejects admission; '
                   'this is not a general impossibility result.'}
(HERE / 'CONTINUATION-PROBE.json').write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
