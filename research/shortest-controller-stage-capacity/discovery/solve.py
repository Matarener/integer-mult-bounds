"""Search the common-stage simplex with exact binary polynomial equations.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The simplex and rank-two projector parametrization are due to Cinna Davis.
"""
import argparse
import json
from pathlib import Path
import z3


def search(n, seconds, factor):
    solver = z3.Solver()
    solver.set(timeout=seconds * 1000)
    zero = z3.BitVecVal(0, n)

    def bit(v, k):
        return z3.Extract(k, k, v) == 1

    def parity(v):
        terms = [bit(v, k) for k in range(n)]
        out = terms[0]
        for t in terms[1:]:
            out = z3.Xor(out, t)
        return out

    def dot(rows, selector):
        out = zero
        for k, row in enumerate(rows):
            out = out ^ z3.If(bit(selector, k), row, zero)
        return out

    def fresh(label, depth):
        return [[z3.BitVec(f'{label}_{depth}_{d}_{i}', n) for i in range(n)]
                for d in range(depth + 1)]

    a = [[z3.BitVecVal(1 << i, n) for i in range(n)]]
    b = [[zero for _ in range(n)]]
    projectors = []
    for stage in range(n + 1):
        u = (1 << stage) if stage < n else (1 << n)-1
        v = ((1 << n)-1) ^ u if stage < n else u
        av = z3.BitVec(f'a_{stage}', n)
        bv = z3.BitVec(f'b_{stage}', n)
        solver.add(parity(av & v), parity(bv & u), z3.Not(parity(av & bv)))
        solver.add(z3.Not(bit(av, (u & -u).bit_length()-1)))
        projectors.append((u, v, av, bv))
        aa, bb = fresh('A', stage+1), fresh('B', stage+1)
        ca = [[zero for _ in range(n)] for _ in aa]
        cb = [[zero for _ in range(n)] for _ in aa]
        for d in range(stage+1):
            va, vb = dot(a[d], z3.BitVecVal(v, n)), dot(b[d], z3.BitVecVal(v, n))
            ba, bb0 = dot(a[d], bv), dot(b[d], bv)
            for i in range(n):
                pa = (ba if (u >> i) & 1 else zero) ^ z3.If(bit(av, i), va, zero)
                pb = (bb0 if (u >> i) & 1 else zero) ^ z3.If(bit(av, i), vb, zero)
                ca[d][i] = ca[d][i] ^ a[d][i] ^ pa
                ca[d+1][i] = ca[d+1][i] ^ pa
                cb[d][i] = cb[d][i] ^ b[d][i] ^ pb
                cb[d+1][i] = cb[d+1][i] ^ pb ^ (va if (u >> i) & 1 else zero)
        solver.add([aa[d][i] == ca[d][i] for d in range(len(aa)) for i in range(n)])
        solver.add([bb[d][i] == cb[d][i] for d in range(len(bb)) for i in range(n)])
        a, b = aa, bb
    solver.add([a[d][i] == b[d][i] for d in range(n+2) for i in range(n)])
    if factor:
        # The balanced target has n-2 jobs of degree two and two of degree three.
        left = [z3.BitVec(f'left_{i}', 2) for i in range(n)]
        right = [z3.BitVec(f'right_{i}', n) for i in range(2)]
        for i in range(2):
            for j in range(2):
                terms = [z3.And(bit(right[i], k), bit(left[k], j)) for k in range(n)]
                value = terms[0]
                for term in terms[1:]:
                    value = z3.Xor(value, term)
                solver.add(value == (i == j))
        for i in range(n):
            p = z3.If(bit(left[i], 0), right[0], zero) ^ z3.If(bit(left[i], 1), right[1], zero)
            for d in range(n+2):
                solver.add(a[d][i] == (p if d == 3 else (p ^ (1 << i) if d == 2 else zero)))
    result = solver.check()
    receipt = {'n': n, 'full_calls': n+1, 'balanced_target': factor,
               'z3_version': z3.get_version_string(), 'timeout_seconds': seconds,
               'solver_result': str(result), 'scope': 'finite binary model, not a physical caller'}
    if result == z3.sat:
        model = solver.model()
        receipt['projectors'] = [[(model.eval(bv).as_long() if (u >> i) & 1 else 0)
                                 ^ (v if (model.eval(av).as_long() >> i) & 1 else 0)
                                 for i in range(n)] for u, v, av, bv in projectors]
        receipt['coefficients'] = [[model.eval(x).as_long() for x in rows] for rows in a]
    elif result == z3.unknown:
        receipt['reason_unknown'] = solver.reason_unknown()
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--n', type=int, required=True)
    parser.add_argument('--seconds', type=int, default=60)
    parser.add_argument('--factor', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.n < 2 or args.n % 2:
        parser.error('n must be positive and even')
    receipt = search(args.n, args.seconds, args.factor)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print(json.dumps(receipt, sort_keys=True))
