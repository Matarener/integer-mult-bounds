"""Check the complete basis compiler and the pinned caller witnesses.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import itertools
import json
from pathlib import Path
from fractions import Fraction as Q
from random import Random
from basis import compile_basis, inverse, apply, dyadic, unit, need

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def matrix(ops, n):
    rows = [[Q(i == j) for j in range(n)] for i in range(n)]
    for op, r, s, c in ops:
        need(0 <= r < n and 0 <= s < n and dyadic(c), 'Legal operand')
        if op == 'ADD':
            need(r != s, 'Distinct ADD operands')
            rows[r] = [x + c*y for x, y in zip(rows[r], rows[s])]
        else:
            need(op == 'SCALE' and unit(c), 'Unit SCALE')
            rows[r] = [c*x for x in rows[r]]
    return rows


def check(a, b, p):
    a, b = list(map(Q, a)), list(map(Q, b))
    ops = compile_basis(a, b, p)
    n = len(a)
    r, inv = matrix(ops, n), matrix(inverse(ops), n)
    need([sum(a[i]*r[i][j] for i in range(n)) for j in range(n)] ==
         [Q(j == p) for j in range(n)], 'Row identity')
    need([r[i][p] for i in range(n)] == b, 'Column identity')
    for i in range(n):
        for j in range(n):
            need(sum(r[i][k]*inv[k][j] for k in range(n)) == (i == j),
                 'Independent dense inverse')
    return ops


def main():
    sources = json.loads((HERE/'SOURCES.json').read_text())
    inputs = [x for x in sources['files'] if x['usage'] == 'input']
    for source in inputs:
        data = (ROOT/source['path']).read_bytes()
        need(hashlib.sha256(data).hexdigest() == source['sha256'], 'Pinned source bytes')
    source = ROOT/'research/p104-coupled-helper-bases'
    need("q = next((h for h in sorted(a) if unit(a[h])), None)" in
         (source/'construct.py').read_text(), 'Source unit-entry restriction')

    source_cases = 0
    for step in json.loads((source/'WITNESS.json').read_text())['steps']:
        if step['kind'] != 'coupled_handoff':
            continue
        for left, right in [('v', 'u'), ('source_functional', 'output_direction')]:
            a, b = dict(step[left]), dict(step[right])
            keys = sorted(set(a) | set(b) | {step['pivot']})
            av, bv = [Q(a.get(i, 0)) for i in keys], [Q(b.get(i, 0)) for i in keys]
            pair = sum(x*y for x, y in zip(av, bv))
            need(unit(pair), 'Source pairing')
            check([q/pair for q in av], bv, keys.index(step['pivot']))
            source_cases += 1
    need(source_cases == 18, 'All nine source handoffs, at both boundaries')

    cases, no_unit = 0, 0
    for a in itertools.product(range(-5, 6), repeat=2):
        for b in itertools.product(range(-5, 6), repeat=2):
            if sum(x*y for x, y in zip(a, b)) != 1:
                continue
            no_unit += not any(unit(Q(q)) for q in a)
            for p in range(2):
                check(a, b, p)
                cases += 1
    check([3, 5], [2, -1], 0)
    need(no_unit > 0, 'Old restriction omits legal pairs')

    rng, larger = Random(20261025), 0
    for n in range(1, 13):
        for trial in range(8):
            p = trial % n
            ops = []
            for _ in range(2*n):
                if n > 1 and rng.randrange(3):
                    r, s = rng.sample(range(n), 2)
                    ops.append(('ADD', r, s, Q(rng.choice([-5, -3, 1, 3, 5]), 2**rng.randrange(3))))
                else:
                    r = rng.randrange(n)
                    ops.append(('SCALE', r, r, Q(rng.choice([-2, -1, 1, 2]), 2**rng.randrange(3))))
            r, ri = matrix(ops, n), matrix(inverse(ops), n)
            check(ri[p], [r[i][p] for i in range(n)], p)
            larger += 1

    rejected = 0
    for a, b, p in [([3, 5], [1, 1], 0), ([Q(1, 3)], [3], 0),
                    ([3], [Q(1, 3)], 0), ([1], [1], 1), ([1, 0], [1], 0)]:
        try:
            compile_basis(a, b, p)
        except ValueError:
            rejected += 1
        else:
            raise ValueError('Invalid basis accepted')
    good = compile_basis([3, 5], [2, -1], 0)
    bad = good[:]
    op, r, s, c = bad[-1]
    bad[-1] = (op, r, s, -c)
    need(matrix(bad, 2) != matrix(good, 2), 'Sign mutation changes the output')
    need(apply(good, [1, 0]) == [2, -1], 'Literal counterexample channel')
    result = dict(source_interfaces=source_cases, exhaustive_compilations=cases,
                  omitted_primitive_pairs=no_unit, larger_presentations=larger,
                  rejected_inputs=rejected, sign_control=True,
                  counterexample_operations=[[op,r,s,str(c)] for op,r,s,c in good])
    need(result == json.loads((HERE/"RESULT.json").read_text()), "Committed receipt")
    print(json.dumps(result, sort_keys=True))
    print('PASS_DYADIC_HELPER_BASIS_COMPLETION')


if __name__ == '__main__':
    main()
