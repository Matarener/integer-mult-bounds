#!/usr/bin/env python3
"""Independent exact review: full Q(i)[D8] and rational realified matrices.

No producer modules are imported. This is finite identity verification, not
an exhaustive oracle optimum search or a formal-kernel proof.
Substantial OpenAI Codex assistance; local review artifact.
"""
from fractions import Fraction as F
from itertools import product
import json
import sys


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


# Generic rectangular matrices; every algebra supplies explicit scalar ops.
def zero(n, m, z):
    return [[z for _ in range(m)] for _ in range(n)]


def eye(n, z=F(0), o=F(1)):
    return [[o if a == b else z for b in range(n)] for a in range(n)]


def madd(a, b, plus=lambda x, y: x+y):
    need(len(a) == len(b) and len(a[0]) == len(b[0]), 'sum shape')
    return [[plus(x, y) for x, y in zip(r, s)] for r, s in zip(a, b)]


def neg(a):
    return [[-x for x in row] for row in a]


def mm(a, b, z=F(0), plus=lambda x, y: x+y, times=lambda x, y: x*y):
    need(len(a[0]) == len(b), 'product shape')
    out = zero(len(a), len(b[0]), z)
    for i, row in enumerate(a):
        for k, x in enumerate(row):
            if x == z:
                continue
            for j, y in enumerate(b[k]):
                if y != z:
                    out[i][j] = plus(out[i][j], times(x, y))
    return out


def scale(a, c):
    return [[c*x for x in row] for row in a]


def power(a, k):
    out = eye(len(a))
    for _ in range(k):
        out = mm(a, out)
    return out


def rank(a):
    a = [row[:] for row in a]
    r = 0
    for c in range(len(a[0])):
        p = next((j for j in range(r, len(a)) if a[j][c]), None)
        if p is None:
            continue
        a[r], a[p] = a[p], a[r]
        a[r] = [x/a[r][c] for x in a[r]]
        for j in range(r+1, len(a)):
            q = a[j][c]
            if q:
                a[j] = [x-q*y for x, y in zip(a[j], a[r])]
        r += 1
        if r == len(a):
            break
    return r


def inv(a):
    n = len(a)
    b = [row[:] + er for row, er in zip(a, eye(n))]
    for c in range(n):
        p = next((j for j in range(c, n) if b[j][c]), None)
        need(p is not None, 'invertible matrix')
        b[c], b[p] = b[p], b[c]
        b[c] = [x/b[c][c] for x in b[c]]
        for j in range(n):
            if j != c:
                q = b[j][c]
                b[j] = [x-q*y for x, y in zip(b[j], b[c])]
    return [row[n:] for row in b]


def kron(a, b):
    return [[x*y for x in ar for y in br] for ar in a for br in b]


def blockdiag(blocks):
    out = zero(sum(map(len, blocks)), sum(map(len, blocks)), F(0))
    at = 0
    for b in blocks:
        for i, row in enumerate(b):
            out[at+i][at:at+len(b)] = row[:]
        at += len(b)
    return out


# Full group algebra: basis i^c B^a S^b, a mod4,b mod2,c in{0,1}.
G0 = (F(0),)*16


def basis(a=0, b=0, c=0):
    out = list(G0)
    out[4*(a % 4)+2*(b % 2)+(c % 2)] = F((-1)**(c//2))
    return tuple(out)


G1, GB, GS = basis(), basis(1), basis(b=1)


def ga(x, y):
    return tuple(a+b for a, b in zip(x, y))


def gn(x):
    return tuple(-a for a in x)


def gm(x, y):
    out = list(G0)
    for j, a in enumerate(x):
        if not a:
            continue
        ja, jb, jc = j//4, (j//2) % 2, j % 2
        for k, b in enumerate(y):
            if not b:
                continue
            ka, kb, kc = k//4, (k//2) % 2, k % 2
            ix = 4*((ja+(-1)**jb*ka) % 4)+2*((jb+kb) % 2)+(jc+kc) % 2
            out[ix] += a*b*(-1 if jc+kc == 2 else 1)
    return tuple(out)


def gs(x, c):
    return tuple(c*a for a in x)


def gmm(a, b):
    return mm(a, b, G0, ga, gm)


def gadd(a, b):
    return madd(a, b, ga)


def ge(n):
    return eye(n, G0, G1)


def shear(n, a, b, c):
    out = ge(n)
    out[a][b] = c
    return out


def chronological(signs, m):
    k = len(signs)
    us, vs, ds = [], [], []
    w = ge(m)
    for j, eps in enumerate(signs):
        bank = j % m
        a, c = (bank+1) % m, (bank+2) % m
        x = ga(gs(G1, j+1), gs(GS, j+2))
        y = ga(gs(G1, (-1)**j), basis(b=1, c=1))
        h = gmm(shear(m, a, bank, x), shear(m, bank, c, y))
        hi = gmm(shear(m, bank, c, gn(y)), shear(m, a, bank, gn(x)))
        need(gmm(h, hi) == ge(m), 'explicit R bridge inverse')
        u = [[row[bank]] for row in hi]
        v = [h[bank]]
        need(gmm(v, u) == [[G1]], 'split rank-one coupling')
        d = ga(basis(eps), gn(G1))
        q = ge(m)
        q[bank][bank] = basis(eps)
        direct = gmm(gmm(hi, q), h)
        factor = gadd(ge(m), gmm(gmm(u, [[d]]), v))
        need(direct == factor, 'one query conjugation order')
        w = gmm(direct, w)
        us.append(u); vs.append(v); ds.append(d)
    u = [[us[j][i][0] for j in range(k)] for i in range(m)]
    v = [vs[j][0] for j in range(k)]
    d, ell = zero(k, k, G0), zero(k, k, G0)
    for j in range(k):
        d[j][j] = ds[j]
        for h in range(j):
            ell[j][h] = gmm(vs[j], us[h])[0][0]
    ld = gmm(ell, d)
    term, series = ge(k), zero(k, k, G0)
    for _ in range(k):
        series = gadd(series, term)
        term = gmm(ld, term)
    need(term == zero(k, k, G0), 'strict triangular series terminates')
    delta = gadd(w, [[gn(z) for z in row] for row in ge(m)])
    need(delta == gmm(gmm(u, gmm(d, series)), v), 'full D8 chronological identity')
    wrong = gmm(gmm(u, gmm(series, d)), v)
    return delta != wrong


# Native matrices use ordinary rational realification, independent of D8.
def ckron(x, y):
    a, b = x; c, d = y
    return madd(kron(a, c), neg(kron(b, d))), madd(kron(a, d), kron(b, c))


def ci(x):
    return neg(x[1]), x[0]


def realify(x):
    a, b = x
    return [ar+[-v for v in br] for ar, br in zip(a, b)] + [br+ar for ar, br in zip(a, b)]


def native_checks():
    half = F(1, 2)
    cr = [[half, half], [half, half]]
    cim = [[half, -half], [-half, half]]
    z = [[F(1), F(0)], [F(0), F(-1)]]
    hp = mm(z, cr), neg(mm(z, cim))
    hq = mm(z, cr), mm(z, cim)
    n1 = ci(ckron(hp, hq))
    rn1 = realify(n1)
    need(mm(rn1, rn1) == scale(eye(8), -1), 'literal N1 square')
    need(sum(rn1[j][j] for j in range(8)) == 0, 'literal N1 trace')
    ii4 = realify((zero(4, 4, F(0)), eye(4)))
    need(rank(madd(rn1, neg(ii4))) == rank(madd(rn1, ii4)) == 4,
         'literal N1 balanced +/-i dimensions')
    n2 = ci(ci(ci(ckron(n1, n1))))  # i^(1-2)=-i normalization
    rn2 = realify(n2)
    need(mm(rn2, rn2) == scale(eye(32), -1), 'literal f2 normalized square')
    ii16 = realify((zero(16, 16, F(0)), eye(16)))
    need(rank(madd(rn2, neg(ii16))) == rank(madd(rn2, ii16)) == 16,
         'literal f2 balanced +/-i dimensions')
    s = zero(16, 16, F(0))
    for a in range(4):
        for b in range(4):
            s[4*b+a][4*a+b] = F(1)
    ac = mm(kron(n1[0], eye(4)), s), mm(kron(n1[1], eye(4)), s)
    ra, rb = realify(ac), realify(ci(ac))
    rs = realify((s, zero(16, 16, F(0))))
    ident = eye(32)
    need(power(rb, 4) == ident and mm(rs, rs) == ident, 'literal D8 orders')
    need(mm(mm(rs, rb), rs) == power(rb, 3), 'literal D8 conjugation')
    need(mm(mm(rs, ra), rs) != power(ra, 3), 'omitted i phase defect')
    mult = {}
    for b, sv in product((1, -1), repeat=2):
        pb = zero(32, 32, F(0))
        for j in range(4):
            pb = madd(pb, scale(power(rb, j), F(b**j, 4)))
        ps = scale(madd(ident, scale(rs, sv)), half)
        p = mm(pb, ps)
        need(mm(p, p) == p, 'actual constituent projector')
        mult[f'B={b},S={sv}'] = rank(p)//2
    need(mult == {'B=1,S=1': 3, 'B=1,S=-1': 1,
                  'B=-1,S=1': 3, 'B=-1,S=-1': 1}, 'actual D8 character multiplicities')
    need(rank(madd(ident, neg(power(rb, 2))))//2 == 8, 'four two-dimensional copies')
    return {'f1_N_eigenspace_dimensions': [2, 2], 'f2_N_eigenspace_dimensions': [8, 8],
            'f1_D8_character_multiplicities': mult, 'f1_two_dimensional_copies': 4,
            'wrong_global_phase_rejected': True}


def adjacent_checks():
    # Full rational regular representation of Q[z]/(z^4+1).
    z = zero(4, 4, F(0))
    z[0][3] = F(-1)
    for j in range(3):
        z[j+1][j] = F(1)
    need(power(z, 4) == scale(eye(4), -1), 'quartic representation')
    for eps in (1, -1):
        zp = z if eps == 1 else inv(z)
        dz = madd(zp, neg(eye(4)))
        dminus = madd(neg(zp), neg(eye(4)))
        delta = madd(inv(dminus), neg(inv(dz)))
        formula = scale(mm(z, inv(madd(power(z, 2), neg(eye(4))))), -2*eps)
        need(delta == formula and rank(delta) == 4, 'quartic opposite coefficient inverse')
    # Exact per-bit primitive word on two arbitrary arrays, realified.
    h = F(1, 2)
    c = realify(([[h, h], [h, h]], [[h, -h], [-h, h]]))
    ci_ = inv(c)
    ident = eye(4)
    def block_shear(dst, src, op):
        out = eye(8)
        for a in range(4):
            for b in range(4):
                out[4*dst+a][4*src+b] = op[a][b]
        return out
    ops = [block_shear(0, 1, c), block_shear(1, 0, scale(ci_, -1)), block_shear(0, 1, c)]
    swap = zero(8, 8, F(0))
    for j in range(8):
        swap[j][(j+4) % 8] = F(1)
    ops += [swap, blockdiag([scale(ident, -1), ident])]
    w = eye(8)
    for op in ops:
        w = mm(op, w)
    need(w == blockdiag([ci_, c]), 'zero-helper per-bit arbitrary-input identity')
    need(mm(blockdiag([mm(c, c), ident]), w) == blockdiag([c, c]), 'same forward orientation')
    for op in reversed(ops):
        w = mm(inv(op), w)
    need(w == eye(8), 'literal inverse on both arbitrary inputs')
    defect = eye(8)
    for op in ops[1:]:
        defect = mm(op, defect)
    need(defect != blockdiag([ci_, c]), 'omitted whole shear defect')
    return {'quartic_opposite_identity_both_signs': True,
            'zero_helper_per_bit_identity_and_literal_inverse': True,
            'zero_helper_same_forward_orientation': True}


def main():
    if '--force-failure' in sys.argv:
        need(False, 'forced explicit failure control')
    need(gm(gm(GS, GB), GS) == basis(-1), 'full group algebra D8 law')
    cases = list(product((-1, 1), repeat=5))
    rejected = sum(chronological(s, 3) for s in cases)
    need(rejected > 0, 'bad noncommutative factor ordering detected')
    out = {'status': 'PASS_INDEPENDENT_UNARY_REVIEW', 'arithmetic': 'exact Python Fraction',
           'group_algebra': 'full Q(i)[D8], not a two-dimensional quotient',
           'chronology_domain': {'banks': 3, 'calls': 5, 'sign_patterns': len(cases),
                                 'fixed_R_bridges': True, 'wrong_order_rejections': rejected},
           'native': native_checks(), 'adjacent': adjacent_checks(),
           'evidence_class': 'finite exact identity checks; not exhaustive optimization; no formal kernel'}
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
