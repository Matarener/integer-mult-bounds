"""Test the shortest-query pairing equations in characteristic zero.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import json
from pathlib import Path
import z3


def search(n, seconds):
    solver = z3.SolverFor('QF_NRA')
    solver.set(timeout=seconds*1000)
    us = [[int(i == j) for j in range(n)] for i in range(n)]
    us.append([(-1)**(i+1) for i in range(n)])
    vs = [[(1 if j < i else -1 if j > i else 0) for j in range(n)] for i in range(n)]
    vs.append([1]*n)

    def dot(a, b):
        return sum(x*y for x, y in zip(a, b))

    av, bv = {}, {}
    for s in range(1, n):
        av[s] = [z3.Real(f'a{s}_{j}') for j in range(n)]
        bv[s] = [z3.Real(f'b{s}_{j}') for j in range(n)]
        solver.add(dot(av[s], vs[s]) == 1, dot(bv[s], us[s]) == 1,
                   dot(av[s], bv[s]) == 0, av[s][s] == 0)
    for transpose in (False, True):
        for first in range(n-1):
            coeff = [vs[first] if transpose else us[first]]
            for last in range(first+2, n+1):
                s = last-1
                out = [[0]*n for _ in range(len(coeff)+1)]
                for d, x in enumerate(coeff):
                    if transpose:
                        px = [dot(x, us[s])*bv[s][k]+dot(x, av[s])*vs[s][k] for k in range(n)]
                    else:
                        px = [dot(x, bv[s])*us[s][k]+dot(x, vs[s])*av[s][k] for k in range(n)]
                    for k in range(n):
                        out[d][k] += x[k]-px[k]
                        out[d+1][k] += px[k]
                coeff = [[z3.Real(f'x{int(transpose)}_{first}_{last}_{d}_{k}') for k in range(n)]
                         for d in range(len(out))]
                solver.add([x == y for xx, yy in zip(coeff, out) for x, y in zip(xx, yy)])
                target = us[last] if transpose else vs[last]
                value = dot(vs[first], us[last]) if transpose else dot(vs[last], us[first])
                for d, x in enumerate(coeff):
                    solver.add(dot(x, target) == (value if d == len(coeff)-1 else 0))
    result = solver.check()
    receipt = {'n': n, 'full_calls': n+1, 'solver_result': str(result),
               'timeout_seconds': seconds, 'z3_version': z3.get_version_string(),
               'scope': 'real common-stage query equations; no endpoint or dyadic admission'}
    if result == z3.sat:
        model = solver.model()
        receipt['a'] = {str(s): [str(model.eval(x)) for x in av[s]] for s in av}
        receipt['b'] = {str(s): [str(model.eval(x)) for x in bv[s]] for s in bv}
    elif result == z3.unknown:
        receipt['reason_unknown'] = solver.reason_unknown()
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--n', type=int, required=True)
    parser.add_argument('--seconds', type=int, default=60)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.n < 2 or args.n % 2:
        parser.error('n must be positive and even')
    result = search(args.n, args.seconds)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, sort_keys=True))
