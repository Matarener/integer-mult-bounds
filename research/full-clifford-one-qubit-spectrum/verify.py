#!/usr/bin/env python3
"""Exact one-qubit Clifford tensor spectrum; Python3.12/standard library.

Prepared for MatShep with substantial OpenAI Codex assistance. Apache-2.0.
The 2U representation/enumeration follow MatShep's PR5549. Ali Romman's
PR5526 supplies the general Gram/error framework. No predecessor is loaded.
"""
from fractions import Fraction as F
import argparse
import json
from pathlib import Path

Z = (0, 0)
ONE = (1, 0)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def add(a, b):
    return a[0]+b[0], a[1]+b[1]


def neg(a):
    return -a[0], -a[1]


def conj(a):
    return a[0], -a[1]


def mul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def power(a, n):
    out = ONE
    for _ in range(n):
        out = mul(out, a)
    return out


def gscale(a, s):
    return s*a[0], s*a[1]


def mm2(a, b):
    c = tuple(add(mul(a[2*i], b[j]), mul(a[2*i+1], b[2+j]))
              for i in range(2) for j in range(2))
    need(all(x % 2 == y % 2 == 0 for x, y in c), '2U closure')
    return tuple((x//2, y//2) for x, y in c)


I2 = ((2, 0), Z, Z, (2, 0))
S = ((2, 0), Z, Z, (0, 2))
V = ((1, 1), (1, -1), (1, -1), (1, 1))
PAULIS = ((Z, (2, 0), (2, 0), Z), (Z, (0, -2), (0, 2), Z),
          ((2, 0), Z, Z, (-2, 0)))


def adj2(a):
    return conj(a[0]), conj(a[2]), conj(a[1]), conj(a[3])


def census():
    group, todo = {I2}, [I2]
    while todo:
        a = todo.pop()
        for b in (S, V):
            c = mm2(a, b)
            if c not in group:
                group.add(c)
                todo.append(c)
    need(len(group) == 96, '96 exact lifts')
    reps = sorted({min(tuple(mul(z, power((0, 1), j)) for z in a)
                       for j in range(4)) for a in group})
    need(len(reps) == 24, '24 projective classes')
    actions = set()
    for a in group:
        need(mm2(adj2(a), a) == I2, 'unitarity')
        action = []
        for p in PAULIS:
            image = mm2(mm2(a, p), adj2(a))
            choices = [sign*(k+1) for k, q in enumerate(PAULIS)
                       for sign in (1, -1)
                       if image == tuple(gscale(z, sign) for z in q)]
            need(len(choices) == 1, 'signed Pauli normalizer')
            action.append(choices[0])
        actions.add(tuple(action))
    need(len(actions) == 24, '24 signed Pauli actions')
    return reps


def trace_inner(a, b):
    t = Z
    for x, y in zip(a, b):
        t = add(t, mul(conj(x), y))
    need(all(v % 4 == 0 for v in t), 'integral trace')
    return tuple(v//4 for v in t)


N = 24
ID = [[ONE if i == j else Z for j in range(N)] for i in range(N)]


def scale(a, s):
    return [[gscale(z, s) for z in row] for row in a]


def plus(*matrices):
    return [[(sum(a[i][j][0] for a in matrices),
              sum(a[i][j][1] for a in matrices))
             for j in range(N)] for i in range(N)]


def dot(a, b):
    c = [[Z for _ in range(N)] for _ in range(N)]
    for i in range(N):
        for k in range(N):
            if a[i][k] == Z:
                continue
            for j in range(N):
                if b[k][j] != Z:
                    c[i][j] = add(c[i][j], mul(a[i][k], b[k][j]))
    return c


def hermitian(a):
    return all(a[i][j] == conj(a[j][i]) for i in range(N) for j in range(N))


def trace(a):
    return sum(a[i][i][0] for i in range(N)), sum(a[i][i][1] for i in range(N))


def action(a, v):
    return [tuple(sum(mul(a[i][j], v[j])[k] for j in range(N)) for k in (0, 1))
            for i in range(N)]


def energy(a, v):
    w = action(a, v)
    z = tuple(sum(mul(conj(v[i]), w[i])[k] for i in range(N)) for k in (0, 1))
    need(z[1] == 0, 'real quadratic energy')
    return z[0]


def norm2(v):
    return sum(x*x+y*y for x, y in v)


def projectors(t, r):
    a = [[power(z, r) if i != j and sum(v*v for v in z) == 2 else Z
          for j, z in enumerate(row)] for i, row in enumerate(t)]
    b = [[power(z, r) if i != j and sum(v*v for v in z) == 1 else Z
          for j, z in enumerate(row)] for i, row in enumerate(t)]
    need(hermitian(a) and hermitian(b), 'Hermitian overlap components')
    need(dot(a, b) == dot(b, a), 'overlap components commute')
    if r % 2:
        p = scale(plus(b, scale(ID, 2)), F(1, 6))
        q = plus(ID, scale(p, -1))
        k = 6*2**((r-1)//2)
        rows = [(k, 4, 4, scale(plus(p, scale(a, F(1, k))), F(1, 2))),
                (-k, 4, 4, scale(plus(p, scale(a, F(-1, k))), F(1, 2))),
                (0, -2, 16, q)]
    else:
        p8 = scale(dot(b, plus(b, scale(ID, 4))), F(1, 96))
        pm4 = scale(dot(b, plus(b, scale(ID, -8))), F(1, 48))
        p0 = plus(ID, scale(p8, -1), scale(pm4, -1))
        small, big = 2**(r//2+1), 3*2**(r//2+1)
        rows = [(0, -4, 4, pm4)]
        for p, k, beta, rank in ((p8, big, 8, 1), (p0, small, 0, 9)):
            ap = dot(a, p)
            for sign in (1, -1):
                e = scale(plus(p, scale(ap, F(sign, k))), F(1, 2))
                rows.append((sign*k, beta, rank, e))
    need(plus(*(e for _, _, _, e in rows)) == ID, 'projectors resolve identity')
    for alpha, beta, rank, e in rows:
        need(hermitian(e) and dot(e, e) == e, 'orthogonal projector')
        need(trace(e) == (rank, 0), 'projector dimension')
        need(dot(a, e) == scale(e, alpha), 'A joint eigenvalue')
        need(dot(b, e) == scale(e, beta), 'B joint eigenvalue')
    # Distinct joint eigenpairs of commuting Hermitian matrices are orthogonal.
    need(len({(alpha, beta) for alpha, beta, _, _ in rows}) == len(rows), 'distinct pairs')
    return rows


def gram(t, f):
    return scale([[power(z, f) for z in row] for row in t], F(1, 2**f))


def predicted(f):
    s = F(1, 2**((f-1)//2))
    if f % 2:
        return sorted([(1-s*s, 16), (1+2*s*s-3*s, 4), (1+2*s*s+3*s, 4)])
    return sorted([(1-s*s, 4), (1-s, 9), (1+s, 9),
                   (1+2*s*s-3*s, 1), (1+2*s*s+3*s, 1)])


def at_width(bases, f):
    r = (f-1) % 4+1
    k = (f-r)//4
    return [(F(1)+F((-4)**k*a+b, 2**f), rank, e)
            for a, b, rank, e in bases[r]]


def first_column(e):
    return next([e[i][j] for i in range(N)] for j in range(N)
                if any(e[i][j] != Z for i in range(N)))


def encode(v):
    return [[str(x), str(y)] for x, y in v]


def characteristic(a):
    """Newton trace identities, independent of the projector computation."""
    p = a
    traces = [0]
    for k in range(1, N+1):
        z = trace(p)
        need(z[1] == 0, 'real power trace')
        traces.append(z[0])
        if k < N:
            p = dot(p, a)
    coefficients = [1]
    for k in range(1, N+1):
        numerator = -sum(coefficients[k-j]*traces[j] for j in range(1, k+1))
        need(numerator % k == 0, 'integral characteristic coefficient')
        coefficients.append(numerator//k)
    return coefficients


def factored_characteristic(f):
    out = [1]
    for lam, rank in predicted(f):
        eigenvalue = lam*2**f
        need(eigenvalue.denominator == 1, 'integer unnormalized eigenvalue')
        eigenvalue = eigenvalue.numerator
        for _ in range(rank):
            nxt = out+[0]
            for j, value in enumerate(out):
                nxt[j+1] -= eigenvalue*value
            out = nxt
    return out


def main(check_saved=False):
    reps = census()
    t = [[trace_inner(a, b) for b in reps] for a in reps]
    for i, row in enumerate(t):
        need(row[i] == (2, 0), 'diagonal trace')
        counts = {v: sum(sum(x*x for x in z) == v for j, z in enumerate(row) if j != i)
                  for v in (0, 1, 2)}
        need(counts == {0: 9, 1: 8, 2: 6}, 'complete overlap distribution')
        for j, z in enumerate(row):
            if i != j and sum(x*x for x in z) == 2:
                need(power(z, 4) == (-4, 0), 'A four-step recurrence')
            if sum(x*x for x in z) == 1:
                need(power(z, 4) == ONE, 'B four-step recurrence')
    bases = {r: projectors(t, r) for r in range(1, 5)}
    characteristic_widths = list(range(1, 11))
    for f in characteristic_widths:
        raw = [[power(z, f) for z in row] for row in t]
        need(characteristic(raw) == factored_characteristic(f), 'independent characteristic polynomial')
    widths = []
    for f in range(1, 33):
        rows = at_width(bases, f)
        need(sorted((lam, rank) for lam, rank, _ in rows) == predicted(f), 'all-width spectrum formula')
        h = gram(t, f)
        need(plus(*(scale(e, lam) for lam, _, e in rows)) == h, 'direct Gram spectral reconstruction')
        if f >= 5:
            need(min(lam for lam, _, _ in rows) >= F(3, 8), 'uniform lower bound')
            need(max(lam for lam, _, _ in rows) <= F(15, 8), 'uniform upper bound')
        widths.append({'f': f, 'spectrum': [[str(lam), rank] for lam, rank in predicted(f)]})
    # Literal vec((2U)^tensor f) gives an independent entry oracle.
    literals = {}
    literal_entries = 0
    for f in (4, 5, 6):
        vectors = []
        for a in reps:
            v = [ONE]
            for _ in range(f):
                v = [mul(x, y) for x in v for y in a]
            vectors.append(v)
        literals[f] = vectors
        for i, v in enumerate(vectors):
            for j, w in enumerate(vectors):
                actual = tuple(sum(mul(conj(x), y)[k] for x, y in zip(v, w)) for k in (0, 1))
                need(actual == gscale(power(t[i][j], f), 4**f), 'literal tensor entry')
                literal_entries += 1
    witnesses, inverse_diagonals, omitted = {}, {}, {}
    for f in (5, 6, 7, 8):
        h = gram(t, f)
        rows = at_width(bases, f)
        inverse = plus(*(scale(e, 1/lam) for lam, _, e in rows))
        need(dot(h, inverse) == ID, 'direct exact inverse')
        s = F(1, 2**((f-1)//2))
        delta = ((1-s*s)*(1-4*s*s)/(1-2*s*s) if f % 2 else
                 2*(1-s*s)*(1-4*s*s)/(2-7*s*s))
        need(all(inverse[g][g] == (1/delta, 0) for g in range(N)), 'constant inverse diagonal and exact formula')
        inverse_diagonals[str(f)] = str(1/delta)
        for g in range(N):
            c = [gscale(inverse[i][g], delta) for i in range(N)]
            need(c[g] == ONE and energy(h, c) == delta, 'attained missing-class minimum')
            hc = action(h, c)
            need(all(hc[i] == (delta, 0) if i == g else hc[i] == Z for i in range(N)), 'least-squares orthogonality')
            if g == 0:
                omitted[str(f)] = {'energy': str(delta), 'residual_coefficients': encode(c)}
                if f in literals:
                    v = [tuple(sum(mul(c[g], literals[f][g][j])[k] for g in range(N))
                               for k in (0, 1)) for j in range(4**f)]
                    need(norm2(v)/8**f == delta, 'literal omitted-class extremizer')
        if f in (5, 6):
            for label, lam in (('min', F(3, 8)), ('max', F(15, 8))):
                e = next(e for value, _, e in rows if value == lam)
                v = first_column(e)
                need(action(h, v) == [gscale(z, lam) for z in v], 'attained extremal eigenvalue')
                witnesses[str(f)+label] = encode(v)
    controls = []
    h5 = gram(t, 5)
    low = first_column(next(e for lam, _, e in at_width(bases, 5) if lam == F(3, 8)))
    high = first_column(next(e for lam, _, e in at_width(bases, 5) if lam == F(15, 8)))
    need(energy(h5, low) < (F(3, 8)+F(1, 1024))*norm2(low), 'reject stronger lower bound')
    controls.append('stronger uniform lower bound rejected by exact eigenvector')
    need(energy(h5, high) > (F(15, 8)-F(1, 1024))*norm2(high), 'reject smaller upper bound')
    controls.append('smaller uniform upper bound rejected by exact eigenvector')
    zero = first_column(next(e for lam, _, e in at_width(bases, 4) if lam == 0))
    need(norm2(zero) > 0 and energy(gram(t, 4), zero) == 0, 'reject extension to width4')
    controls.append('width4 positive lower bound rejected by null vector')
    for f in (5, 6, 7, 8):
        # Two actual phase-related tensor vectors have a nontrivial null
        # combination; dropping their relative phase fails at5,6,7.
        v = literals[5][0] if f == 5 else [ONE]
        phase = power((0, 1), f)
        phase_v = [mul(phase, z) for z in v]
        residual = [add(mul(phase, z), neg(w)) for z, w in zip(v, phase_v)]
        need(norm2(residual) == 0, 'phase relation')
        if f != 8:
            need(norm2([add(z, neg(w)) for z, w in zip(v, phase_v)]) > 0,
                 'phase not discarded')
    controls.append('central phase quotient cannot be replaced by96 independent lifts')
    i, j = next((i, j) for i in range(N) for j in range(N) if h5[i][j][1])
    mutated = [row[:] for row in h5]
    mutated[i][j] = conj(mutated[i][j])
    need(not hermitian(mutated), 'reject lost conjugation/phase')
    controls.append('altered imaginary entry rejected by Hermitian identity')
    wrong = plus(*(scale(e, F(1)+F(4*a+b, 32)) for a, b, _, e in bases[1]))
    need(wrong != h5, 'reject wrong A recurrence sign')
    controls.append('positive-four recurrence rejected by direct width5 Gram')
    c = [[F(x), F(y)] for x, y in omitted['5']['residual_coefficients']]
    need(energy(h5, c) < F(45, 56)+F(1, 1024), 'reject stronger missing-class floor')
    controls.append('stronger missing-class floor rejected by literal-checked optimum')
    out = {'status': 'PASS_EXACT_ONE_QUBIT_SPECTRUM', 'group_order': 96,
           'projective_classes': 24, 'representatives_2U': reps,
           'joint_spectra': {str(r): [[a, b, rank] for a, b, rank, _ in bases[r]] for r in bases},
           'independent_characteristic_polynomial_widths': characteristic_widths,
           'widths': widths, 'literal_tensor_gram_entries': literal_entries,
           'sharp_uniform_Riesz_bounds_from_f5': ['3/8', '15/8'],
           'sharp_uniform_Gram_condition_number': '5',
           'extremal_eigenvectors': witnesses, 'inverse_diagonals': inverse_diagonals,
           'omitted_class_extremizers': omitted,
           'sharp_uniform_missing_class_squared_HS_error_from_f5': '45/56',
           'controls_rejected': controls,
           'scope': 'Exact one-qubit algebra and normalized Hilbert-Schmidt norms; no physical/native, supplier, kappa or full multiplication theorem claim.'}
    if check_saved:
        need(json.loads(Path(__file__).with_name('RESULT.json').read_text(encoding='utf-8')) == json.loads(json.dumps(out)),
             'committed result differs from exact recomputation')
    print(json.dumps(out, sort_keys=True, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-saved', action='store_true')
    main(parser.parse_args().check_saved)
