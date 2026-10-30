"""Search shortest-query words with one relation among interior stages.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import json
from pathlib import Path
import z3


def search(n, seconds, supplied_labels=None):
    solver = z3.Solver()
    solver.set(timeout=seconds*1000)
    zero = z3.BitVecVal(0, n)
    mask = (1 << n)-1
    us = [(1 << i) if i < n else mask for i in range(n+1)]
    vs = [mask ^ (1 << i) if i < n else mask for i in range(n+1)]
    labels = {s: 1 << (s-1) for s in range(1, n-1)}
    labels[n-1] = (1 << (n-2))-1
    if supplied_labels is not None:
        if len(supplied_labels) != n-1 or any(x <= 0 for x in supplied_labels):
            raise ValueError('one positive label is required for each interior stage')
        labels = dict(enumerate(supplied_labels, 1))

    def parity(x):
        out = z3.Extract(0, 0, x) == 1
        for k in range(1, n):
            out = z3.Xor(out, z3.Extract(k, k, x) == 1)
        return out

    av, bv = {}, {}
    for i in range(1, n):
        av[i], bv[i] = z3.BitVec(f'a{i}', n), z3.BitVec(f'b{i}', n)
        solver.add(parity(av[i] & vs[i]), parity(bv[i] & us[i]),
                   z3.Not(parity(av[i] & bv[i])), z3.Extract(i, i, av[i]) == 0)
    for transpose in (False, True):
        for first in range(n-1):
            coeff = {0: z3.BitVecVal(vs[first] if transpose else us[first], n)}
            expected_label = 0
            for last in range(first+2, n+1):
                s = last-1
                expected_label ^= labels[s]
                out = {}
                for label, x in coeff.items():
                    if transpose:
                        px = z3.If(parity(x & us[s]), bv[s], zero) ^ z3.If(parity(x & av[s]), z3.BitVecVal(vs[s], n), zero)
                    else:
                        px = z3.If(parity(x & bv[s]), z3.BitVecVal(us[s], n), zero) ^ z3.If(parity(x & vs[s]), av[s], zero)
                    out[label] = out.get(label, zero) ^ x ^ px
                    other = label ^ labels[s]
                    out[other] = out.get(other, zero) ^ px
                coeff = {label: z3.BitVec(f'x{int(transpose)}_{first}_{last}_{label}', n) for label in out}
                solver.add([coeff[label] == value for label, value in out.items()])
                target = us[last] if transpose else vs[last]
                solver.add([parity(x & target) == (label == expected_label) for label, x in coeff.items()])
    result = solver.check()
    receipt = {'n': n, 'full_calls': n+1, 'solver_result': str(result),
               'timeout_seconds': seconds, 'z3_version': z3.get_version_string(),
               'labels': labels, 'scope': 'binary query equations with involutive stages; no endpoint or rank admission'}
    if result == z3.sat:
        model = solver.model()
        receipt['interior_projectors'] = {
            str(s): [(model.eval(bv[s]).as_long() if (us[s] >> i) & 1 else 0)
                     ^ (vs[s] if (model.eval(av[s]).as_long() >> i) & 1 else 0)
                     for i in range(n)] for s in range(1, n)}
    elif result == z3.unknown:
        receipt['reason_unknown'] = solver.reason_unknown()
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--n', type=int, required=True)
    parser.add_argument('--seconds', type=int, default=60)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--labels', help='Comma-separated nonzero group labels for interior stages')
    args = parser.parse_args()
    if args.n < 4 or args.n % 2:
        parser.error('n must be even and at least four')
    result = search(args.n, args.seconds, list(map(int, args.labels.split(','))) if args.labels else None)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, sort_keys=True))
