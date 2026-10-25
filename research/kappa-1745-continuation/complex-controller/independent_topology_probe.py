#!/usr/bin/env python3
"""One changed controller model: independent primal and dual scalar bridges.

This uses the fixed topology from rational_topology_probe.py but releases the
equality of each primal coefficient and its dual coefficient. An exact scalar
endpoint is mandatory for acceptance. Numerical failure is not an obstruction.
Apache-2.0; substantial OpenAI assistance.
"""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
from time import monotonic

import numpy as np
from scipy.optimize import least_squares


SOURCE = Path(__file__).resolve().with_name('rational_topology_probe.py')
PIN = 'cfb025c09f4a8384d87fc7a965ec5aaa8a775e4f0d068a25d8bccaf61d81960a'
assert sha256(SOURCE.read_bytes()).hexdigest() == PIN
spec = importlib.util.spec_from_file_location('paired_topology', SOURCE)
paired = importlib.util.module_from_spec(spec)
spec.loader.exec_module(paired)
OPERATIONS = paired.OPERATIONS
K = 4
N = 8
NVAR = 40


def endpoint(values, exact=False):
    if exact:
        matrix = np.eye(N, dtype=int).astype(object)
    else:
        matrix = np.eye(N)
        derivative = np.zeros((NVAR, N, N))
    for op in OPERATIONS:
        if op[0] == 'B':
            _, dst, src, index = op
            steps = [(dst, src, index, 1), (K + src, K + dst, 20 + index, -1)]
        else:
            pair = op[1]
            steps = [(K + pair, pair, None, 1)] if op[0] == 'F' else [(pair, K + pair, None, -1)]
        for dst, src, index, sign in steps:
            coefficient = sign if index is None else sign * values[index]
            if not exact:
                derivative[:, dst, :] += coefficient * derivative[:, src, :]
                if index is not None:
                    derivative[index, dst, :] += sign * matrix[src, :]
            matrix[dst, :] += coefficient * matrix[src, :]
    residual = np.concatenate((matrix[:K, :K].ravel(), matrix[K:, K:].ravel()))
    if exact:
        return matrix, residual
    jacobian = np.concatenate((derivative[:, :K, :K].reshape(NVAR, -1),
                               derivative[:, K:, K:].reshape(NVAR, -1)), axis=1).T
    return residual, jacobian


def main():
    ap = ArgumentParser(description=__doc__)
    ap.add_argument('--seeds', type=int, default=8)
    ap.add_argument('--nfev', type=int, default=2000)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    started = monotonic()
    trials = []
    accepted = None
    for seed in range(args.seeds):
        rng = np.random.default_rng(seed)
        initial = rng.normal(0, 0.7, size=NVAR)
        result = least_squares(lambda x: endpoint(x)[0], initial,
                               jac=lambda x: endpoint(x)[1], max_nfev=args.nfev,
                               ftol=1e-12, xtol=1e-12, gtol=1e-12)
        values = [Q(float(x)).limit_denominator(4096) for x in result.x]
        matrix, exact = endpoint(values, exact=True)
        row = {'seed': seed, 'nfev': result.nfev,
               'maximum_diagonal_block_error': float(np.max(np.abs(result.fun))),
               'squared_error': float(np.dot(result.fun, result.fun)),
               'maximum_coefficient': float(np.max(np.abs(result.x))),
               'floating_coefficients': result.x.tolist(),
               'rounded_rational_coefficients': [str(x) for x in values],
               'exact_rational_endpoint': not any(exact),
               'all_denominators_powers_of_two': all(q.denominator & (q.denominator - 1) == 0 for q in values)}
        trials.append(row)
        print(json.dumps({k: v for k, v in row.items()
                          if k not in ('floating_coefficients', 'rounded_rational_coefficients')}), flush=True)
        if not any(exact):
            accepted = {'coefficients': [str(x) for x in values],
                        'matrix': [[str(x) for x in row] for row in matrix]}
            break
    result = {'status': 'EXACT_INDEPENDENT_BRIDGE_SCALAR_CONTROLLER' if accepted else 'NO_EXACT_CONTROLLER_IN_THIS_NUMERICAL_ATTEMPT',
              'parameter_count': NVAR, 'interface_dimensions': [3, 2, 2, 2, 2],
              'idle_profile': [1, 1, 1, 2, 2, 3, 5, 6, 6],
              'trials': trials, 'accepted': accepted, 'seconds': monotonic() - started,
              'source_sha256': {SOURCE.name: PIN, Path(__file__).name: sha256(Path(__file__).read_bytes()).hexdigest()},
              'scope': 'One topology; independently parameterized SL3 x SL2^4 maps on the primal and dual sides. '
                       'No paired symplectic or mod2 obstruction is imported. No native construction or invoice asserted.'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'trials'}), flush=True)


if __name__ == '__main__':
    main()
