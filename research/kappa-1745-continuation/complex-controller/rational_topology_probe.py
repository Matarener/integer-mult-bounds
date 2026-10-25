#!/usr/bin/env python3
"""A single non-integral controller topology, with an exact acceptance gate.

Continuous least squares searches one SL3 x SL2^4 parameter chart. It is a
construction attempt, not a coefficient-bounded enumeration or obstruction.
Only an exactly zero rational endpoint is accepted. Apache-2.0; OpenAI.
"""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
from time import monotonic

import numpy as np
from scipy.optimize import least_squares


K = 4
N = 8
NVAR = 20


def recipe():
    operations = [('F', 0), ('R', 0)]
    interfaces = [
        [(0, 1), (1, 0), (0, 1), (1, 2), (2, 1), (1, 2), (0, 2), (2, 0)],
        [(0, 1), (1, 0), (0, 1)],
        [(0, 3), (3, 0), (0, 3)],
        [(0, 3), (3, 0), (0, 3)],
        [(0, 2), (2, 0), (0, 2)],
    ]
    calls = [[('F', 0)], [('R', 0), ('F', 0)], [('R', 0)],
             [('F', 0), ('R', 0)], [('F', 0)]]
    index = 0
    for interface, local in zip(interfaces, calls):
        for dst, src in interface:
            operations.append(('B', dst, src, index))
            index += 1
        operations.extend(local)
    assert index == NVAR
    return operations


OPERATIONS = recipe()


def float_endpoint(values):
    matrix = np.eye(N)
    derivative = np.zeros((NVAR, N, N))
    for op in OPERATIONS:
        kind = op[0]
        if kind == 'B':
            _, dst, src, index = op
            coefficient = values[index]
            derivative[:, dst, :] += coefficient * derivative[:, src, :]
            derivative[index, dst, :] += matrix[src, :]
            derivative[:, K + src, :] -= coefficient * derivative[:, K + dst, :]
            derivative[index, K + src, :] -= matrix[K + dst, :]
            matrix[dst, :] += coefficient * matrix[src, :]
            matrix[K + src, :] -= coefficient * matrix[K + dst, :]
        else:
            pair = op[1]
            dst, src, coefficient = (K + pair, pair, 1) if kind == 'F' else (pair, K + pair, -1)
            matrix[dst, :] += coefficient * matrix[src, :]
            derivative[:, dst, :] += coefficient * derivative[:, src, :]
    residual = np.concatenate((matrix[:K, :K].ravel(), matrix[K:, K:].ravel()))
    jacobian = np.concatenate((derivative[:, :K, :K].reshape(NVAR, -1),
                               derivative[:, K:, K:].reshape(NVAR, -1)), axis=1).T
    return residual, jacobian


def exact_endpoint(values):
    matrix = [[Q(int(i == j)) for j in range(N)] for i in range(N)]
    def add(dst, src, coefficient):
        matrix[dst] = [x + coefficient * y for x, y in zip(matrix[dst], matrix[src])]
    for op in OPERATIONS:
        if op[0] == 'B':
            _, dst, src, index = op
            add(dst, src, values[index])
            add(K + src, K + dst, -values[index])
        else:
            pair = op[1]
            if op[0] == 'F':
                add(K + pair, pair, Q(1))
            else:
                add(pair, K + pair, Q(-1))
    residual = [matrix[i][j] for i in range(K) for j in range(K)] + [
        matrix[K + i][K + j] for i in range(K) for j in range(K)]
    return matrix, residual


def run(seeds, nfev):
    started = monotonic()
    trials = []
    accepted = None
    for seed in range(seeds):
        rng = np.random.default_rng(seed)
        initial = rng.normal(0, 0.7, size=NVAR)
        if seed == 0:
            initial = np.array([1, -0.5, 1, 1, -0.5, 1, 1, -1] + [1, -0.5, 1] * 4, dtype=float)
        result = least_squares(lambda x: float_endpoint(x)[0], initial,
                               jac=lambda x: float_endpoint(x)[1],
                               max_nfev=nfev, ftol=1e-12, xtol=1e-12, gtol=1e-12)
        values = [Q(float(x)).limit_denominator(4096) for x in result.x]
        matrix, exact = exact_endpoint(values)
        row = {'seed': seed, 'nfev': result.nfev,
               'maximum_diagonal_block_error': float(np.max(np.abs(result.fun))),
               'squared_error': float(np.dot(result.fun, result.fun)),
               'maximum_coefficient': float(np.max(np.abs(result.x))),
               'rounded_rational_coefficients': [str(x) for x in values],
               'exact_rational_endpoint': not any(exact),
               'all_denominators_powers_of_two': all(q.denominator & (q.denominator - 1) == 0 for q in values)}
        trials.append(row)
        print(json.dumps({k: v for k, v in row.items() if k != 'rounded_rational_coefficients'}), flush=True)
        if not any(exact):
            accepted = {'coefficients': [str(x) for x in values],
                        'matrix': [[str(x) for x in row] for row in matrix]}
            break
    return {'status': 'EXACT_RATIONAL_SCALAR_CONTROLLER' if accepted else 'NO_EXACT_CONTROLLER_IN_THIS_NUMERICAL_ATTEMPT',
            'K': K, 'local_count': 9, 'interface_dimensions': [3, 2, 2, 2, 2],
            'parameter_count': NVAR, 'operations': OPERATIONS,
            'idle_events': [[1, -1, 1], [2, -1, 1], [1, 1, 2], [3, -1, 4], [3, 4, 5], [2, 1, 7],
                            [1, 2, 8], [3, 5, 8], [2, 7, 8]],
            'idle_profile': [1, 1, 1, 2, 2, 3, 5, 6, 6],
            'solver': 'scipy.optimize.least_squares; analytic forward Jacobian; unrestricted real parameters',
            'max_nfev_per_seed': nfev, 'trials': trials, 'accepted': accepted,
            'seconds': monotonic() - started,
            'scope': 'One fixed clock topology and one full-dimensional SL3 x SL2^4 shear chart. '
                     'Numerical failure is not a real, rational, or dyadic impossibility result. '
                     'A scalar endpoint would still require standard-flag and full hosting checks.'}


def main():
    ap = ArgumentParser(description=__doc__)
    ap.add_argument('--seeds', type=int, default=12)
    ap.add_argument('--nfev', type=int, default=1000)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    result = run(args.seeds, args.nfev)
    result['source_sha256'] = sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('trials', 'operations')}), flush=True)


if __name__ == '__main__':
    main()
