#!/usr/bin/env python3
"""Exact finite identity witness; no query-optimality enumeration or dependencies."""
from dataclasses import dataclass
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json


@dataclass(frozen=True)
class Q:
    a: F = F(0)
    b: F = F(0)

    def __post_init__(self):
        object.__setattr__(self, 'a', F(self.a))
        object.__setattr__(self, 'b', F(self.b))

    @staticmethod
    def coerce(x):
        return x if isinstance(x, Q) else Q(x)

    def __add__(self, other):
        o = Q.coerce(other)
        return Q(self.a + o.a, self.b + o.b)

    __radd__ = __add__

    def __neg__(self):
        return Q(-self.a, -self.b)

    def __sub__(self, other):
        return self + -Q.coerce(other)

    def __rsub__(self, other):
        return Q.coerce(other) + -self

    def __mul__(self, other):
        o = Q.coerce(other)
        return Q(self.a*o.a-self.b*o.b, self.a*o.b+self.b*o.a)

    __rmul__ = __mul__

    def __truediv__(self, other):
        o = Q.coerce(other)
        d = o.a*o.a+o.b*o.b
        if not d:
            raise ZeroDivisionError
        return self * Q(o.a/d, -o.b/d)

    def __bool__(self):
        return bool(self.a or self.b)


Z, O, II = Q(0), Q(1), Q(0, 1)


def need(condition, label):
    if not condition:
        raise RuntimeError(label)


def zero(n, m):
    return [[Z for _ in range(m)] for _ in range(n)]


def ident(n):
    x = zero(n, n)
    for j in range(n):
        x[j][j] = O
    return x


def add(a, b):
    return [[x+y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def scale(a, c):
    return [[x*c for x in row] for row in a]


def sub(a, b):
    return add(a, scale(b, -1))


def mul(a, b):
    out = zero(len(a), len(b[0]))
    need(len(a[0]) == len(b), 'matrix product dimensions')
    for row, ar in zip(out, a):
        for j, x in enumerate(ar):
            if x:
                for c, y in enumerate(b[j]):
                    if y:
                        row[c] = row[c] + x*y
    return out


def power(a, n):
    out = ident(len(a))
    for _ in range(n):
        out = mul(out, a)
    return out


def inverse(a):
    n = len(a)
    out = [row[:] + ir for row, ir in zip(a, ident(n))]
    for j in range(n):
        pivot = next(p for p in range(j, n) if out[p][j])
        out[j], out[pivot] = out[pivot], out[j]
        c = out[j][j]
        out[j] = [x/c for x in out[j]]
        for p in range(n):
            if p != j and out[p][j]:
                c = out[p][j]
                out[p] = [x-c*y for x, y in zip(out[p], out[j])]
    return [row[n:] for row in out]


def rank(a):
    out = [row[:] for row in a]
    r = 0
    for j in range(len(a[0])):
        candidates = [p for p in range(r, len(a)) if out[p][j]]
        if not candidates:
            continue
        p = candidates[0]
        out[p], out[r] = out[r], out[p]
        c = out[r][j]
        out[r] = [x/c for x in out[r]]
        for p in range(r+1, len(a)):
            c = out[p][j]
            if c:
                out[p] = [x-c*y for x, y in zip(out[p], out[r])]
        r += 1
        if r == len(a):
            break
    return r


def blockdiag(blocks):
    total = sum(len(b) for b in blocks)
    out = zero(total, total)
    j = 0
    for b in blocks:
        for r in range(len(b)):
            for c in range(len(b)):
                out[j+r][j+c] = b[r][c]
        j += len(b)
    return out


def vec(n, entries):
    out = zero(n, 1)
    for j, x in entries.items():
        out[j][0] = Q.coerce(x)
    return out


def native_check():
    d = 4
    s = zero(d*d, d*d)
    n = zero(d*d, d*d)
    for a in range(d):
        for b in range(d):
            s[b*d+a][a*d+b] = O
            n[a*d+b][a*d+b] = II if a < 2 else -II
    a = mul(n, s)
    b = scale(a, II)
    eye = ident(16)
    need(mul(s, s) == eye and power(b, 4) == eye, 'native S^2=B^4=I')
    need(mul(mul(s, b), s) == inverse(b), 'native SBS=B^-1')
    need(mul(mul(s, a), s) != inverse(a), 'dropped global i must be detected')
    need(power(a, 2) == mul(n, mul(mul(s, n), s)), 'native A^2=NT')
    need(power(b, 2) == scale(power(a, 2), -1), 'native B^2=-A^2')
    chars = [(-1, 1, {0: 1}), (1, -1, {1: 1, 4: -1}),
             (1, 1, {10: 1}), (-1, -1, {11: 1, 14: -1})]
    for bv, sv, entries in chars:
        v = vec(16, entries)
        need(rank(v) == 1, f'nonzero native character B={bv},S={sv}')
        need(mul(b, v) == scale(v, bv), f'native character B={bv}')
        need(mul(s, v) == scale(v, sv), f'native character S={sv}')
    wp = vec(16, {2: 1, 8: -II})
    wm = vec(16, {8: 1, 2: -II})
    e = [[wp[j][0], wm[j][0]] for j in range(16)]
    br = [[II, Z], [Z, -II]]
    sr = [[Z, O], [O, Z]]
    need(rank(e) == 2 and mul(b, e) == mul(e, br), 'native two-dimensional B intertwiner')
    need(mul(s, e) == mul(e, sr), 'native two-dimensional S intertwiner')
    multiplicities = {}
    for bv, sv, _ in chars:
        pb = zero(16, 16)
        for j in range(4):
            pb = add(pb, scale(power(b, j), F(bv**j, 4)))
        ps = scale(add(eye, scale(s, sv)), F(1, 2))
        pr = mul(pb, ps)
        need(mul(pr, pr) == pr, f'character projector B={bv},S={sv}')
        multiplicities[f'B={bv},S={sv}'] = rank(pr)
    need(sorted(multiplicities.values()) == [1, 1, 3, 3], 'native character multiplicities')
    return multiplicities


def shear(m, dst, src, c):
    out = ident(m)
    out[dst][src] = Q.coerce(c)
    return out


def eval_r(hp, hm, s):
    t = len(s)
    out = zero(len(hp)*t, len(hp[0])*t)
    eye = ident(t)
    for a in range(len(hp)):
        for b in range(len(hp[0])):
            ablock = add(scale(eye, (hp[a][b]+hm[a][b])/2),
                         scale(s, (hp[a][b]-hm[a][b])/2))
            for r in range(t):
                for c in range(t):
                    out[a*t+r][b*t+c] = ablock[r][c]
    return out


def resolvent_check(b, s):
    m, k, t = 3, 5, len(b)
    signs, banks = [1, -1, -1, 1, 1], [0, 1, 2, 0, 2]
    us, vs, ds = [], [], []
    w = ident(m*t)
    for j, (eps, bank) in enumerate(zip(signs, banks)):
        hp = mul(shear(m, 0, 1, j+1), shear(m, 1, 2, -1))
        hm = mul(shear(m, 2, 0, j+2), shear(m, 0, 1, 1))
        hpi, hmi = inverse(hp), inverse(hm)
        h = eval_r(hp, hm, s)
        hi = eval_r(hpi, hmi, s)
        need(mul(h, hi) == ident(m*t), f'invertible bridge {j}')
        u = eval_r([[hpi[a][bank]] for a in range(m)],
                   [[hmi[a][bank]] for a in range(m)], s)
        v = eval_r([hp[bank]], [hm[bank]], s)
        need(mul(v, u) == ident(t), f'query idempotent coupling {j}')
        bp = b if eps == 1 else inverse(b)
        d = sub(bp, ident(t))
        query = ident(m*t)
        for a in range(t):
            for c in range(t):
                query[bank*t+a][bank*t+c] = bp[a][c]
        direct = mul(mul(hi, query), h)
        factor = add(ident(m*t), mul(mul(u, d), v))
        need(direct == factor, f'conjugated direct query equals rank-one factor {j}')
        w = mul(direct, w)
        us.append(u); vs.append(v); ds.append(d)
    u = [sum((block[r] for block in us), []) for r in range(m*t)]
    v = sum(vs, [])
    d = blockdiag(ds)
    ell = zero(k*t, k*t)
    for a in range(k):
        for c in range(a):
            block = mul(vs[a], us[c])
            for r in range(t):
                for q in range(t):
                    ell[a*t+r][c*t+q] = block[r][q]
    ld = mul(ell, d)
    finite = zero(k*t, k*t)
    term = ident(k*t)
    for _ in range(k):
        finite = add(finite, term)
        term = mul(term, ld)
    need(term == zero(k*t, k*t), 'strict triangular nilpotence')
    g = mul(d, finite)
    invertible_d = rank(d) == k*t
    if invertible_d:
        need(g == inverse(sub(inverse(d), ell)), 'inverse resolvent formula')
    need(sub(w, ident(m*t)) == mul(mul(u, g), v), 'direct product equals chronological resolvent')
    # This incorrect ordering is not algebraically interchangeable in this model.
    bad = mul(finite, d)
    ordering_control = sub(w, ident(m*t)) != mul(mul(u, bad), v)
    return {'dimension': t, 'direct_product_rank': rank(sub(w, ident(m*t))),
            'inverse_resolvent_defined': invertible_d,
            'wrong_resolvent_order_rejected': ordering_control}


def attaining_check(b):
    t = len(b)
    q0 = blockdiag([b, ident(t), ident(t)])
    q1 = blockdiag([ident(t), b, ident(t)])
    got = mul(mul(q1, q1), mul(q0, q0))
    want = blockdiag([power(b, 2), power(b, 2), ident(t)])
    need(got == want, 'four-query attainment on two output banks and restored helper')


def main():
    chars = native_check()
    rho = ([[II, Z], [Z, -II]], [[Z, O], [O, Z]])
    records = {'rho_2d': resolvent_check(*rho)}
    for bv in [1, -1]:
        for sv in [1, -1]:
            key = f'B={bv},S={sv}'
            records[key] = resolvent_check([[Q(bv)]], [[Q(sv)]])
            attaining_check([[Q(bv)]])
    attaining_check(rho[0])
    need(records['rho_2d']['wrong_resolvent_order_rejected'], 'reversed resolvent order must fail')
    root = Path(__file__).resolve().parent
    out = {
        'status': 'PASS_EXACT_NATIVE_CONSTITUENTS_AND_NONCOMMUTATIVE_RESOLVENT',
        'arithmetic': 'Gaussian rationals; Python Fraction; no floating point',
        'native_dimension_X': 4,
        'native_dimension_X_tensor_X': 16,
        'native_char_multiplicities': chars,
        'wrong_global_phase_rejected': True,
        'formula_witness': {'banks': 3, 'queries': 5, 'records': records},
        'attainment': '2 output banks + 1 restored bank; 4 calls; all 5 simple constituents',
        'coverage': 'Finite exact identity witness, not exhaustive optimization; all-parameter bound in PROOF.md',
        'formal_kernel_proof': False,
        'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'proof_sha256': hashlib.sha256((root/'PROOF.md').read_bytes()).hexdigest(),
    }
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
