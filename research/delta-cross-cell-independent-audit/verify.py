#!/usr/bin/env python3
"""Independent exact checks of PR4462's conditional matrix implications.

mihir-s-05 with substantial OpenAI Codex assistance. Apache-2.0.
The reviewed author's verifier is authenticated as evidence, never executed.
Universal arguments, including spectral and exponential steps, are in README.md.
"""
from fractions import Fraction as F
from hashlib import sha256, sha1
from pathlib import Path
import itertools
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    rows = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))['files']
    count = 0
    for row in rows:
        if row['usage'] == 'input':
            data = (ROOT / row['path']).read_bytes()
            require(sha256(data).hexdigest() == row['sha256'], 'source drift: ' + row['path'])
            count += 1
    review = json.loads((HERE / 'REVIEWED.json').read_text(encoding='utf-8'))
    for row in review['files']:
        data = (HERE / row['path']).read_bytes()
        require(sha256(data).hexdigest() == row['sha256'], 'review snapshot drift')
        require(sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == row['git_blob'],
                'review Git blob mismatch')
        count += 1
    return count


def eye(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def transpose(a):
    return [list(row) for row in zip(*a)]


def add(a, b, sign=1):
    return [[x + sign*y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def scale(a, c):
    return [[c*x for x in row] for row in a]


def mul(a, b):
    return [[sum((x*y for x, y in zip(row, col)), F(0)) for col in transpose(b)] for row in a]


def inverse(a):
    n = len(a)
    aug = [row[:] + unit for row, unit in zip(a, eye(n))]
    for j in range(n):
        pivot = next((i for i in range(j, n) if aug[i][j]), None)
        require(pivot is not None, 'singular matrix')
        aug[j], aug[pivot] = aug[pivot], aug[j]
        d = aug[j][j]
        aug[j] = [x/d for x in aug[j]]
        for i in range(n):
            if i != j:
                d = aug[i][j]
                aug[i] = [x-d*y for x, y in zip(aug[i], aug[j])]
    return [row[n:] for row in aug]


def norm_inf(a):
    return max(sum(map(abs, row)) for row in a)


def off_bounds(a):
    b = [[abs(x) if i != j else F(0) for j, x in enumerate(row)] for i, row in enumerate(a)]
    return norm_inf(b), norm_inf(transpose(b))


def polynomial(a, c, length):
    unit = eye(len(a))
    q = add(unit, scale(mul(transpose(a), a), c), -1)
    power, total = unit, scale(unit, F(0))
    for _ in range(length):
        total = add(total, power)
        power = mul(power, q)
    return scale(mul(total, transpose(a)), c), power


def scalar_checks():
    # README proves this small rational delta envelope for every p >= 2;
    # do not reproduce the predecessor's million-bit D arithmetic in a loop.
    for p in range(2, 513):
        gap, budget, e = F(1, 8*p*p), F(1, 32*p**3), F(1, 64*p**4)
        envelope = F(1, 128*p**4)
        require(32760*p-2 > 4*p+3, 'delta exponent envelope')
        require(32768*p-1 > 4*p+2, 'raw oracle exponent envelope')
        require(2*envelope + 2*(p-1)*e < budget, 'combined within/across budget')
        q = gap-budget
        require(q == F(4*p-1, 32*p**3) and q >= F(7, 64*p*p), 'robust gap')
        require(q > F(1, 10*p*p) and q*q*p**11 > 1 and 1/q < p**6, 'inverse endpoints')
        require(100 < p**7 and 10 < p**4, 'monotone endpoint inequalities')
        length = p**24
        require((2*length-1)*(p-1) < p**26, 'polynomial bandwidth')
        require((2*length+1)*(p-1) < p**26, 'conservative agreement radius')
        margin = p**24*((p-1)**2+1) - p + 1
        require(p**26-(2*p**24+1)*(p-1) == margin and margin > 0, 'radius margin')
        for share in (F(0), F(1, 5), F(1, 2), F(1)):
            inside, outside = (1-gap)*share, (1-gap)*(1-share)
            off = inside/(1-envelope) + outside
            ceiling = (1-envelope)/(gap-envelope)
            require(1/(1-off) <= ceiling < 1/q, 'split inverse envelope')
            require((1-envelope)*off-(inside+outside) == -envelope*outside, 'split algebra')
    p = 2
    d = 1 << (32760*p)
    delta, gap = F(4, d), F(1, 8*p*p)
    require((1-delta)/(gap-delta) == F(8*p*p*(d-4), d-32*p*p), 'U identity')
    for rho, expected in [(F(91, 10000), True), (F(92, 10000), False)]:
        q = F(1, 32)-rho
        require(q > 0 and (q*q*2**11 > 1) == expected, 'p2 sharp endpoint')
    return 511


def mixed_matrices():
    count = 0
    p, n = 3, 4
    gap, budget = F(1, 8*p*p), F(1, 32*p**3)
    e, delta_envelope = F(1, 64*p**4), F(1, 128*p**4)
    edges = [(0, 1), (0, 2), (1, 3), (2, 3)]
    ideal = eye(n)
    for i, j in edges:
        ideal[i][j] = ideal[j][i] = (1-gap)/2
    for cuts in itertools.product((0, 1), repeat=n-1):
        cells = [0]
        for cut in cuts:
            cells.append(cells[-1]+cut)
        for mode in (-1, 0, 1):
            h = eye(n)
            for i, j in edges:
                if cells[i] == cells[j]:
                    h[i][j] = ideal[i][j]/(1-delta_envelope)
                    h[j][i] = ideal[j][i]/(1-delta_envelope)
                else:
                    h[i][j] = ideal[i][j] + mode*e
                    h[j][i] = ideal[j][i] - mode*e
            require(max(off_bounds(h)) <= 1-gap+budget, 'mixed matrix budget')
            inv = inverse(h)
            require(mul(h, inv) == eye(n) == mul(inv, h), 'inverse identity')
            bound = 1/(gap-budget)
            require(norm_inf(inv) <= bound and norm_inf(transpose(inv)) <= bound, 'two inverse norms')
            for signs in itertools.product((-1, 1), repeat=n):
                out = mul(inv, [[F(x)] for x in signs])
                require(sum(row[0]**2 for row in out) <= bound**2*n, 'inverse response bound')
            count += 1
    return count


def polynomial_checks():
    h = [[F(1), F(1, 3), F(0)], [F(-1, 5), F(1), F(1, 7)], [F(0), F(1, 11), F(1)]]
    inv, c = inverse(h), F(1, 2**11)
    wrong_side_rejected = False
    for length in range(1, 5):
        approx, power = polynomial(h, c, length)
        residual = add(inv, approx, -1)
        require(residual == mul(power, inv), 'left normal-equation residual')
        wrong_side_rejected |= residual != mul(inv, power)
    require(wrong_side_rejected, 'nonnormal wrong-side control did not reject')
    full = eye(9)
    for i in range(8):
        full[i][i+1], full[i+1][i] = F(1, 16), F(-1, 32)
    section = [row[1:8] for row in full[1:8]]
    pf, _ = polynomial(full, c, 2)
    ps, _ = polynomial(section, c, 2)
    require(pf[4][1:8] == ps[3], 'interior polynomial row')
    require(pf[1][1:8] != ps[0], 'near-face locality control did not reject')
    for i, row in enumerate(pf):
        require(all(x == 0 for j, x in enumerate(row) if abs(i-j) > 3), 'length-two bandwidth')
    return {'residual_lengths': [1, 2, 3, 4], 'locality_fixture_order': 9}


def boundary_controls():
    p, r = 2, F(249, 256)
    h = eye(6)
    h[0][1] = -r
    for i in range(1, 6):
        h[i][i-1] = -r
    rows, cols = off_bounds(h)
    require(rows == r and cols == 2*r, 'one-sided fixture')
    inv = inverse(h)
    expected = [r**i/(1-r*r) for i in range(6)]
    require([row[0] for row in inv] == expected, 'one-sided inverse column')
    energy = sum(x*x for x in expected)
    require(energy > (10*p*p)**2, 'row-only fails claimed 2-norm ceiling')
    inv_t = inverse(transpose(h))
    require(inv_t == transpose(inv) and sum(x*x for x in inv_t[0]) == energy,
            'column-only transpose control')
    for rho, succeeds in [(F(91, 10000), True), (F(92, 10000), False)]:
        t = F(31, 32)+rho
        a = [[F(1), -t], [-t, F(1)]]
        require(mul(a, [[F(1)], [F(1)]]) == [[1-t], [1-t]], 'exact threshold eigenvector')
        require(((1-t)**2 > F(1, 2**11)) == succeeds, 'excess threshold control')
    singular = [[F(0), F(0)], [F(0), F(0)]]
    require(off_bounds(singular) == (0, 0), 'zero off-sums')
    try:
        inverse(singular)
    except ValueError:
        pass
    else:
        raise ValueError('diagonal-one omission control did not reject')
    return {'row_only_inverse_column_squared_norm': str(energy),
            'claimed_ceiling_squared': 1600,
            'controls': ['row-only', 'column-only', 'excess-0.0092', 'missing-unit-diagonal',
                         'nonnormal-wrong-residual-side', 'near-face-agreement']}


def main():
    report = {'status': 'PASS_DELTA_CROSS_CELL_INDEPENDENT_AUDIT',
              'authenticated_files': authenticate(), 'scalar_p_cases': scalar_checks(),
              'mixed_matrix_cases': mixed_matrices(), 'polynomial_checks': polynomial_checks(),
              'boundary_controls': boundary_controls(), 'new_kappa_claimed': False,
              'scope': 'Exact finite checks support the separate all-p conditional proof; no Gaussian gap, generator, Schur or full theorem verification.'}
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
