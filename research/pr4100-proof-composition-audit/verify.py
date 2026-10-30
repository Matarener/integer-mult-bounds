#!/usr/bin/env python3
"""Independent finite checks of #4100 PROOF.md's transform and recovery chain.

Standard library only. Exact integer, rational and cyclotomic arithmetic where
the claim is algebraic; 60-digit Decimal arithmetic where Gaussian kernels
enter. Finite corroboration of the written re-derivation in README.md, not an
all-size proof. Ryanson Jonathan with Claude Code (Claude Opus 5.5)
assistance. Apache-2.0.
"""
from decimal import Decimal, getcontext
from fractions import Fraction
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/unconditional-batched-crt"
getcontext().prec = 60
TOL = Decimal(10) ** -40


def need(condition, message):
    if not condition:
        raise AssertionError(message)


# --- 0. Source binding --------------------------------------------------------

PHRASES = {
    "PROOF.md": [
        "y_i = k P_i^-1 mod s_i.",
        "M F_plus((F_minus f)(F_minus g)/r)=(f*g)/(rM)",
        "its r-th power is -1",
        "Each t_i is even, so a is periodic on the target rectangle.",
        "T_gauss P_s F_s=P_t F_t S_gauss",
        "P_s F_s = D N^-1 C P_t F_t S_gauss.",
        "(R F_s^+)(U*pointwise V1)=(u*cyclic v)/S^2.",
        "S>T/2>=2n/b>2Ndigits-2",
        "0<=kj<Ndigits*2^b<2^(2b)",
        "Since S<T<2^b eventually, the factor is<2^(4b+4).",
    ],
    "CRT.md": ["Phi_G(a)_i = k_G / P_(G,i) mod s_i,"],
}


def check_sources():
    pins = json.loads((Path(__file__).parent / "SOURCES.json").read_text())
    pinned = {row["path"]: row["sha256"] for row in pins["files"]}
    for name in ("PROOF.md", "CRT.md", "check_batched_crt.py"):
        path = SOURCE / name
        rel = path.relative_to(ROOT).as_posix()
        need(hashlib.sha256(path.read_bytes()).hexdigest() == pinned[rel], f"pin {rel}")
    for name, phrases in PHRASES.items():
        text = (SOURCE / name).read_text()
        for phrase in phrases:
            need(phrase in text, f"source phrase missing from {name}: {phrase}")
    spec = importlib.util.spec_from_file_location("pr4100_crt", SOURCE / "check_batched_crt.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, sum(len(v) for v in PHRASES.values())


# --- 1. Address isomorphism -----------------------------------------------------

def address_map(k, moduli):
    out, prefix = [], 1
    for s in moduli:
        out.append(k * pow(prefix, -1, s) % s)
        prefix *= s
    return tuple(out)


def address_inverse(y, moduli):
    """The unique k mod S with k = P_i y_i mod s_i (PROOF.md's stated inverse)."""
    S = math.prod(moduli)
    k, prefix = 0, 1
    for yi, s in zip(y, moduli):
        target = prefix * yi % s
        comp = S // s
        k += target * comp * pow(comp, -1, s)
        prefix *= s
    return k % S


def check_address(crt):
    count = 0
    rng = random.Random(4100)
    for moduli in ((3, 5), (3, 5, 7), (3, 5, 7, 11), (5, 7, 11, 13)):
        S = math.prod(moduli)
        images = {}
        for k in range(S):
            y = address_map(k, moduli)
            need(y not in images, "address map injective")
            images[y] = k
            need(address_inverse(y, moduli) == k, "stated inverse")
            digits, rest = [], k
            for s in moduli:
                digits.append(rest % s)
                rest //= s
            need(y == crt.direct(digits, moduli), "agrees with CRT.md's root map (source direct())")
            count += 1
        for _ in range(64):
            a, b = rng.randrange(S), rng.randrange(S)
            ya, yb, yab = address_map(a, moduli), address_map(b, moduli), address_map((a + b) % S, moduli)
            need(yab == tuple((p + q) % s for p, q, s in zip(ya, yb, moduli)), "additive mod S")
        if S <= 105:  # cyclic convolution of length S equals tensor cyclic convolution
            f = [rng.randrange(-9, 10) for _ in range(S)]
            g = [rng.randrange(-9, 10) for _ in range(S)]
            conv = [sum(f[i] * g[(k - i) % S] for i in range(S)) for k in range(S)]
            tf = {address_map(k, moduli): f[k] for k in range(S)}
            tg = {address_map(k, moduli): g[k] for k in range(S)}
            for k in range(S):
                y = address_map(k, moduli)
                total = 0
                for z in itertools.product(*(range(s) for s in moduli)):
                    w = tuple((a - b) % s for a, b, s in zip(y, z, moduli))
                    total += tf[z] * tg[w]
                need(total == conv[k], "convolution transported by the address map")
    # Controls: a shared factor destroys bijectivity; unscaled residues miss CRT.md's root map.
    need(len({(k % 3, k % 9) for k in range(27)}) < 27, "control: non-coprime moduli are not a bijection")
    need(any(tuple(k % s for s in (3, 5, 7)) != address_map(k, (3, 5, 7)) for k in range(105)),
         "control: plain residues differ from the scaled map")
    return count


# --- 2. Synthetic convolution over K[y]/(y^r+1), K = Q(zeta_2r) -------------------

class Neg:
    """Elements of A[w]/(w^n+1) as tuples; A is Fraction or another Neg ring."""

    @staticmethod
    def zero(n, base):
        return tuple(base for _ in range(n))

    @staticmethod
    def add(a, b, add):
        return tuple(add(x, y) for x, y in zip(a, b))

    @staticmethod
    def mul(a, b, add, mul, neg, zero):
        n = len(a)
        out = [zero] * n
        for i, x in enumerate(a):
            for j, y in enumerate(b):
                term = mul(x, y)
                if i + j < n:
                    out[i + j] = add(out[i + j], term)
                else:
                    out[i + j - n] = add(out[i + j - n], neg(term))
        return tuple(out)

    @staticmethod
    def shift(a, e, neg):
        """Multiply by w^e, e taken mod 2n."""
        n = len(a)
        e %= 2 * n
        out = [None] * n
        for i, x in enumerate(a):
            j = i + e
            sign = (j // n) % 2
            out[j % n] = neg(x) if sign else x
        return tuple(out)


def make_rings(r):
    kz = Fraction(0)
    K_zero = Neg.zero(r, kz)
    k_add = lambda a, b: Neg.add(a, b, lambda x, y: x + y)
    k_neg = lambda a: tuple(-x for x in a)
    k_mul = lambda a, b: Neg.mul(a, b, lambda x, y: x + y, lambda x, y: x * y, lambda x: -x, kz)
    k_scale = lambda a, c: tuple(x * c for x in a)
    R_zero = Neg.zero(r, K_zero)
    r_add = lambda a, b: Neg.add(a, b, k_add)
    r_mul = lambda a, b: Neg.mul(a, b, k_add, k_mul, k_neg, K_zero)
    r_scale = lambda a, c: tuple(k_scale(x, c) for x in a)
    r_shift = lambda a, e: Neg.shift(a, e, k_neg)
    k_zpow = lambda a, e: Neg.shift(a, e, lambda x: -x)  # multiply K element by z^e
    return dict(K_zero=K_zero, k_add=k_add, k_mul=k_mul, k_scale=k_scale, k_zpow=k_zpow,
                R_zero=R_zero, r_add=r_add, r_mul=r_mul, r_scale=r_scale, r_shift=r_shift)


def synthetic_transform(records, axes, r, sign, ops):
    """Normalized multidimensional DFT over prod Z_t (t | 2r) with twiddles y^(+-E)."""
    M = math.prod(axes)
    out = {}
    for k in itertools.product(*(range(t) for t in axes)):
        acc = ops["R_zero"]
        for x in itertools.product(*(range(t) for t in axes)):
            E = sum((2 * r // t) * xi * ki for t, xi, ki in zip(axes, x, k))
            acc = ops["r_add"](acc, ops["r_shift"](records[x], sign * E))
        out[k] = ops["r_scale"](acc, Fraction(1, M))
    return out


def butterfly_dif(seq, r, ops):
    """Normalized radix-2 DIF with H0=[[1,1],[1,-1]]/2 and y twiddles; bit-reversed output."""
    t = len(seq)
    x = list(seq)
    h = t // 2
    while h >= 1:
        for start in range(0, t, 2 * h):
            for i in range(h):
                a, b = x[start + i], x[start + i + h]
                x[start + i] = ops["r_scale"](ops["r_add"](a, b), Fraction(1, 2))
                diff = ops["r_scale"](ops["r_add"](a, tuple(tuple(-c for c in kk) for kk in b)), Fraction(1, 2))
                x[start + i + h] = ops["r_shift"](diff, -(2 * r // (2 * h)) * i)
        h //= 2
    bits = t.bit_length() - 1
    return [x[int(format(k, f"0{bits}b")[::-1], 2) if bits else 0] for k in range(t)]


def check_synthetic():
    rng = random.Random(116)
    cases = 0
    for r, others in ((2, (2,)), (4, (4,)), (4, (4, 2)), (4, (2, 2))):
        ops = make_rings(r)
        rand_k = lambda: tuple(Fraction(rng.randrange(-3, 4)) for _ in range(r))
        shape = (r,) + others
        T, M = math.prod(shape), math.prod(others)
        f = {x: rand_k() for x in itertools.product(*(range(t) for t in shape))}
        g = {x: rand_k() for x in itertools.product(*(range(t) for t in shape))}
        # Reference: normalized cyclic convolution (f*g)/T over prod Z_t, exact in K.
        ref = {}
        for x in f:
            acc = ops["K_zero"]
            for z in f:
                w = tuple((a - b) % t for a, b, t in zip(x, z, shape))
                acc = ops["k_add"](acc, ops["k_mul"](f[z], g[w]))
            ref[x] = ops["k_scale"](acc, Fraction(1, T))

        def pipeline(twist=True, divide_r=True, untwist=True):
            def pack(h):
                recs = {}
                for xo in itertools.product(*(range(t) for t in others)):
                    recs[xo] = tuple(ops["k_zpow"](h[(x0,) + xo], x0 if twist else 0) for x0 in range(r))
                return recs
            Ff = synthetic_transform(pack(f), others, r, -1, ops)
            Fg = synthetic_transform(pack(g), others, r, -1, ops)
            prod = {k: ops["r_scale"](ops["r_mul"](Ff[k], Fg[k]), Fraction(1, r) if divide_r else 1) for k in Ff}
            back = synthetic_transform(prod, others, r, +1, ops)
            out = {}
            for xo, rec in back.items():
                rec = ops["r_scale"](rec, M)
                for x0 in range(r):
                    out[(x0,) + xo] = ops["k_zpow"](rec[x0], -x0 if untwist else 0)
            return out

        recs = {xo: tuple(f[(x0,) + xo] for x0 in range(r)) for xo in itertools.product(*(range(t) for t in others))}
        round_trip = synthetic_transform(synthetic_transform(recs, others, r, -1, ops), others, r, +1, ops)
        need(all(round_trip[k] == ops["r_scale"](recs[k], Fraction(1, M)) for k in recs), "F+ F- = I/M")
        need(pipeline() == ref, "M F+((F- f)(F- g)/r) with twist equals (f*g)/T exactly")
        need(pipeline(twist=False, untwist=False) != ref, "control: no twist gives negacyclic, not cyclic")
        need(pipeline(divide_r=False) != ref, "control: omitting /r changes the scale")
        # The twist's r-th power is -1.
        one = tuple(Fraction(int(i == 0)) for i in range(r))
        need(ops["k_zpow"](one, r) == tuple(-c for c in one), "twist^r = -1")
        # Normalized H0/2 butterfly network equals F- up to bit reversal (one axis).
        t = others[0]
        seq = [tuple(rand_k() for _ in range(r)) for _ in range(t)]
        direct = synthetic_transform({(i,): seq[i] for i in range(t)}, (t,), r, -1, ops)
        need(butterfly_dif(seq, r, ops) == [direct[(k,)] for k in range(t)], "H0/2 butterflies give F-")
        cases += 1
    return cases


# --- 3. Chirp identity -------------------------------------------------------------

def chirp_exponent_ok(s, t):
    """conj(a(x)) a(x-z mod t) conj(a(z)) == exp(2 pi i s x z/t) for all x,z, in units pi i/t."""
    return all((s * (x * x - ((x - z) % t) ** 2 + z * z) - 2 * s * x * z) % (2 * t) == 0
               for x in range(t) for z in range(t))


def check_chirp():
    pairs = 0
    for t in (2, 4, 6, 8, 16, 32, 64):
        for s in range(1, 3 * t, 2):
            if math.gcd(s, t) != 1:
                continue
            need(chirp_exponent_ok(s, t), f"chirp identity t={t} s={s}")
            need(all((s * ((x + t) ** 2 - x * x)) % (2 * t) == 0 for x in range(t)), "a periodic mod t")
            need(len({(-s * x) % t for x in range(t)}) == t, "Q is a permutation")
            pairs += 1
    odd_failures = sum(not chirp_exponent_ok(s, t) for t in (3, 5, 7, 9) for s in range(1, 2 * t, 2)
                       if math.gcd(s, t) == 1)
    need(odd_failures > 0 and all(not chirp_exponent_ok(s, t) for t in (3, 5, 7, 9)
                                  for s in range(1, 2 * t, 2) if math.gcd(s, t) == 1),
         "control: every coprime odd-t case fails")
    return pairs, odd_failures


# --- 4. Gaussian Poisson identity and factorization (60 digits) -----------------------

def dec_pi():
    getcontext().prec += 4
    three = Decimal(3)
    lasts, t, s, n, na, d, da = 0, three, 3, 1, 0, 0, 24
    while s != lasts:
        lasts = s
        n, na = n + na, na + 8
        d, da = d + da, da + 32
        t = (t * n) / d
        s += t
    getcontext().prec -= 4
    return +s


PI = dec_pi()


def cos_sin(x):
    x = x % (2 * PI)
    if x > PI:
        x -= 2 * PI
    c = s = Decimal(0)
    term, k = Decimal(1), 0
    while True:
        if k % 4 == 0:
            c += term
        elif k % 4 == 1:
            s += term
        elif k % 4 == 2:
            c -= term
        else:
            s -= term
        k += 1
        term = term * x / k
        if abs(term) < Decimal(10) ** -70:
            return c, s


ROOT_CACHE = {}


def root(n, k):
    """exp(2 pi i k/n) as (re, im)."""
    key = (n, k % n)
    if key not in ROOT_CACHE:
        ROOT_CACHE[key] = cos_sin(2 * PI * Decimal(k % n) / n)
    return ROOT_CACHE[key]


def cmul(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def cadd(a, b):
    return (a[0] + b[0], a[1] + b[1])


def cscale(a, c):
    return (a[0] * c, a[1] * c)


ZERO = (Decimal(0), Decimal(0))


class Axis:
    """One axis of PROOF.md's 'Exact Gaussian and source-transform identity'."""

    def __init__(self, s, t, alpha):
        self.s, self.t, self.alpha = s, t, Decimal(alpha)
        self.a = PI * self.alpha ** 2
        self.q = [math.floor(Fraction(t * j, s) + Fraction(1, 2)) for j in range(s)]
        self.beta = [Decimal(t * j) / s - self.q[j] for j in range(s)]
        X = 9 / float(alpha)
        self.N = [[self.n_entry(j, jp, X) for jp in range(s)] for j in range(s)]

    def g(self, x):
        return (-self.a * x * x).exp()

    def n_entry(self, j, jp, X):
        """N[j,j'] = sum_n g(t(j'+sn)/s - q_j) exp(a beta_j'^2); alias n=0 is principal."""
        s, t = self.s, self.t
        lo = math.floor((s * (self.q[j] - X)) / t) - 2
        hi = math.ceil((s * (self.q[j] + X)) / t) + 2
        total = Decimal(0)
        for jj in range(lo, hi + 1):
            if jj % s == jp:
                total += self.g(Decimal(t * jj) / s - self.q[j])
        return total * (self.a * self.beta[jp] ** 2).exp()

    def principal_diagonal(self, j):
        return self.g(Decimal(self.t * j) / self.s - self.q[j]) * (self.a * self.beta[j] ** 2).exp()

    def F_s(self, u, sign=-1):
        s = self.s
        return [cscale(sum_c(cmul(root(s, sign * m * l), u[l]) for l in range(s)), Decimal(1) / s)
                for m in range(s)]

    def T_gauss(self, w):
        """(T w)_k = sum_{j in Z} g(tj/s - k) w_{j mod s}."""
        s, t = self.s, self.t
        X = 9 / float(self.alpha)
        out = []
        for k in range(t):
            acc = ZERO
            for j in range(math.floor(s * (k - X) / t) - 2, math.ceil(s * (k + X) / t) + 3):
                acc = cadd(acc, cscale(w[j % s], self.g(Decimal(t * j) / s - k)))
            out.append(acc)
        return out

    def S_gauss(self, u, drop_alpha=False):
        """(S u)_m = alpha^-1 sum_{j in Z} exp(-pi alpha^-2 (j - sm/t)^2) u_{j mod s}."""
        s, t, al = self.s, self.t, self.alpha
        Y = 9 * float(al)
        out = []
        for m in range(t):
            c = Fraction(s * m, t)
            acc = ZERO
            for j in range(math.floor(c - Y) - 1, math.ceil(c + Y) + 2):
                x = Decimal(j) - Decimal(s * m) / t
                acc = cadd(acc, cscale(u[j % s], (-PI * x * x / (al * al)).exp()))
            out.append(acc if drop_alpha else cscale(acc, 1 / al))
        return out

    def PtFt(self, v, norm=None, sign=-1):
        """(P_t F_t v)_k = (F_t v)_{-sk}, F_t normalized by 1/t (or by 1/norm for a control)."""
        s, t = self.s, self.t
        scale = Decimal(1) / (norm or t)
        return [cscale(sum_c(cmul(root(t, -sign * s * k * m), v[m]) for m in range(t)), scale)
                for k in range(t)]

    def PsFs(self, u):
        Fu = self.F_s(u)
        return [Fu[(self.t * j) % self.s] for j in range(self.s)]

    def DNinvC(self, v):
        rhs = [v[self.q[j]] for j in range(self.s)]
        x = solve(self.N, rhs)
        return [cscale(x[j], (self.a * self.beta[j] ** 2).exp()) for j in range(self.s)]

    def RFs(self, u):
        return self.DNinvC(self.PtFt(self.S_gauss(u)))


def sum_c(items):
    acc = ZERO
    for z in items:
        acc = cadd(acc, z)
    return acc


def solve(A, b):
    n = len(A)
    M = [list(row) + [b[i]] for i, row in enumerate(A)]
    for col in range(n):
        piv = max(range(col, n), key=lambda i: abs(M[i][col]))
        M[col], M[piv] = M[piv], M[col]
        need(abs(M[col][col]) > Decimal(10) ** -30, "N invertible")
        for i in range(col + 1, n):
            f = M[i][col] / M[col][col]
            if f:
                for j in range(col, n):
                    M[i][j] -= f * M[col][j]
                M[i][n] = cadd(M[i][n], cscale(M[col][n], -f))
    x = [ZERO] * n
    for i in reversed(range(n)):
        acc = M[i][n]
        for j in range(i + 1, n):
            acc = cadd(acc, cscale(x[j], -M[i][j]))
        x[i] = cscale(acc, 1 / M[i][i])
    return x


def maxdiff(a, b):
    return max(max(abs(x[0] - y[0]), abs(x[1] - y[1])) for x, y in zip(a, b))


def basis(n, l):
    return [(Decimal(int(i == l)), Decimal(0)) for i in range(n)]


def check_gaussian():
    rows = nonzero_rows = 0
    worst = Decimal(0)
    controls = {"F_t normalized by 1/s": 0, "S_gauss without alpha^-1": 0, "P_t with +sk": 0}
    for s, t, alpha in ((3, 4, "1.7"), (5, 6, "1.3"), (5, 8, "2"), (7, 8, "2.5"), (31, 32, "3")):
        ax = Axis(s, t, alpha)
        nonzero_rows += s - 1
        for j in range(s):
            need(abs(ax.principal_diagonal(j) - 1) < TOL, "principal diagonal term of N is one")
        for l in range(s):
            u = basis(s, l)
            Fu = ax.F_s(u)
            lhs = ax.T_gauss([Fu[(t * j) % s] for j in range(s)])
            Su = ax.S_gauss(u)
            rhs = ax.PtFt(Su)
            d = maxdiff(lhs, rhs)
            worst = max(worst, d)
            need(d < TOL, f"Poisson identity s={s} t={t} l={l}: {d}")
            if maxdiff(lhs, ax.PtFt(Su, norm=s)) > Decimal("1e-3"):
                controls["F_t normalized by 1/s"] += 1
            if maxdiff(lhs, ax.PtFt(ax.S_gauss(u, drop_alpha=True))) > Decimal("1e-3"):
                controls["S_gauss without alpha^-1"] += 1
            # e_0 gives a real symmetric S_gauss u, so the sign control is blind there; count l != 0 only.
            if l and maxdiff(lhs, ax.PtFt(Su, sign=+1)) > Decimal("1e-3"):
                controls["P_t with +sk"] += 1
            d2 = maxdiff(ax.PsFs(u), ax.RFs(u))
            worst = max(worst, d2)
            need(d2 < TOL, f"P_s F_s = D N^-1 C P_t F_t S_gauss, s={s} t={t} l={l}: {d2}")
            rows += 1
    need(controls["F_t normalized by 1/s"] == rows and controls["S_gauss without alpha^-1"] == rows
         and controls["P_t with +sk"] == nonzero_rows, f"every control detected on every eligible row: {controls}")
    return rows, worst, controls


# --- 5. Recovery: dilation commutation, end-to-end toy product, exact inequalities ----------

def check_dilation():
    count = 0
    for s in (3, 5, 7, 11, 13, 31):
        for t in (4, 8, 16, 32):
            c, ci = t % s, pow(t, -1, s)
            for sign in (-1, 1):
                # (F D_c w)_k kernel at source m: zeta^{sign*k*c^-1*m}; (D_{c^-1} F w)_k: zeta^{sign*(c^-1 k)*m}
                need(all((sign * k * ci * m - sign * ((ci * k) % s) * m) % s == 0
                         for k in range(s) for m in range(s)), "F D_c = D_{c^-1} F")
            # (R F+)(RFu . RFv): coefficient of u_a v_b at j is S^-3 sum_k zeta^{t k (j-a-b)} = S^-2 [j=a+b]
            for a, b, j in itertools.product(range(s), repeat=3):
                nonzero = (t * (j - a - b)) % s == 0
                need(nonzero == ((j - a - b) % s == 0), "orthogonality after dilation")
            count += 1
    return count


def check_end_to_end():
    """Multiply integers through PROOF.md's composed chain on a toy grid."""
    moduli, targets, alphas, b = (3, 5), (4, 8), ("1.7", "2"), 3
    axes = [Axis(s, t, a) for s, t, a in zip(moduli, targets, alphas)]
    S = math.prod(moduli)
    shape = moduli

    def tensor_apply(tensor, axis_index, fn, out_len):
        new = {}
        sizes = list(tensor_shape(tensor))
        ranges = [range(n) for i, n in enumerate(sizes) if i != axis_index]
        for rest in itertools.product(*ranges):
            idx = lambda v: tuple(list(rest[:axis_index]) + [v] + list(rest[axis_index:]))
            line = [tensor[idx(v)] for v in range(sizes[axis_index])]
            res = fn(line)
            need(len(res) == out_len, "line length")
            for v in range(out_len):
                new[idx(v)] = res[v]
        return new

    def tensor_shape(tensor):
        dims = len(next(iter(tensor)))
        return [max(k[i] for k in tensor) + 1 for i in range(dims)]

    def RF(tensor, conj=False):
        if conj:
            tensor = {k: (v[0], -v[1]) for k, v in tensor.items()}
        for i, ax in enumerate(axes):
            tensor = tensor_apply(tensor, i, ax.S_gauss, ax.t)
        for i, ax in enumerate(axes):
            tensor = tensor_apply(tensor, i, ax.PtFt, ax.t)
        for i, ax in enumerate(axes):
            tensor = tensor_apply(tensor, i, ax.DNinvC, ax.s)
        if conj:
            tensor = {k: (v[0], -v[1]) for k, v in tensor.items()}
        return tensor

    def RF_direct(tensor):
        for i, ax in enumerate(axes):
            tensor = tensor_apply(tensor, i, ax.PsFs, ax.s)
        return tensor

    rng = random.Random(1166)
    ndig = (S + 1) // 2
    scale = Fraction(1, 2 ** (b + 2))
    samples = [(2 ** (b * ndig) - 1, 2 ** (b * ndig) - 1), (1, 1), (0, 12345)]
    samples += [(rng.randrange(2 ** (b * ndig)), rng.randrange(2 ** (b * ndig))) for _ in range(5)]
    checked, flushed = 0, [0]
    for x, y in samples:
        def tensorize(n):
            digits = [(n >> (b * i)) & (2 ** b - 1) for i in range(ndig)] + [0] * (S - ndig)
            return {address_map(k, moduli): (Decimal(digits[k] * scale.numerator) / scale.denominator,
                                             Decimal(0)) for k in range(S)}
        u, v = tensorize(x), tensorize(y)
        U, V1 = RF(u), RF(v)
        direct_u = RF_direct(u)
        need(max(maxdiff([U[k]], [direct_u[k]]) for k in U) < TOL, "composed R F_s equals definition")
        prod = {k: cmul(U[k], V1[k]) for k in U}
        back = RF(prod, conj=True)
        factor = S * S * 2 ** (2 * b + 4)
        coeffs = [0] * S
        for yidx, val in back.items():
            real = val[0] * factor
            nearest = int(real.to_integral_value())
            need(abs(real - nearest) < Decimal("1e-30") and abs(val[1] * factor) < Decimal("1e-30"),
                 "values are near integers")
            coeffs[address_inverse(yidx, moduli)] = nearest
        carry, digits = 0, []
        for c in coeffs:
            total = c + carry
            digits.append(total % 2 ** b)
            carry = total // 2 ** b
        # S = 2*Ndigits-1 here (PROOF.md's minimum), so the top digit can arrive as the final carry.
        extra = 0
        while carry:
            digits.append(carry % 2 ** b)
            carry //= 2 ** b
            extra += 1
        need(extra <= 1, "final carry is at most one b-bit digit")
        flushed[0] += extra
        need(sum(d << (b * i) for i, d in enumerate(digits)) == x * y, "exact product recovered")
        checked += 1
        # Control: the wrong final scale S instead of S^2 does not recover the product.
        if x * y > 1:
            wrong = sum(int((val[0] * S * 2 ** (2 * b + 4)).to_integral_value()) for val in back.values())
            need(wrong != sum(coeffs), "control: scale S instead of S^2 fails")
    need(flushed[0] > 0, "the S = 2*Ndigits-1 fixture exercises a nonzero final carry")
    return checked, flushed[0]


def check_recovery_inequalities():
    first_good_b = None
    for b in range(2, 65):
        n_values = [2 ** (b - 1) + 1, 2 ** b] if b > 1 else [2]
        ok = True
        for n in n_values:
            T = 1 << (math.ceil(Fraction(4 * n, b)) - 1).bit_length()
            need(Fraction(4 * n, b) <= T < Fraction(8 * n, b), "T in [4n/b, 8n/b)")
            ok = ok and T < 2 ** b
        if ok and first_good_b is None:
            first_good_b = b
        if first_good_b is not None:
            need(ok, "T < 2^b persists")
    count = 0
    for n in range(4, 1 << 14):
        b = (n - 1).bit_length()  # ceil(log2 n)
        T = 1 << (math.ceil(Fraction(4 * n, b)) - 1).bit_length()
        need(Fraction(4 * n, b) <= T < Fraction(8 * n, b), "unique power of two")
        nd = -(-n // b)
        need(Fraction(T, 2) >= Fraction(2 * n, b) > 2 * nd - 2, "T/2 >= 2n/b > 2Ndigits-2")
        need(nd * (2 ** b - 1) ** 2 < 2 ** (3 * b), "c_j < 2^(3b)")
        need(nd < 2 ** b, "Ndigits < 2^b")
        count += 1
    # Carry bound: k_j <= Ndigits(2^b-1) (sharper than the stated < Ndigits 2^b), worst-case digits.
    carries = 0
    for b in range(1, 7):
        for nd in range(1, 40):
            full = [min(j + 1, 2 * nd - 1 - j, nd) * (2 ** b - 1) ** 2 for j in range(2 * nd - 1)]
            k = 0
            for c in full + [0] * 4:
                need(0 <= k <= nd * (2 ** b - 1), "carry bound")
                k = (c + k) // 2 ** b
            need(k == 0, "carries terminate")
            carries += 1
    return first_good_b, count, carries


def main():
    crt, phrases = check_sources()
    addresses = check_address(crt)
    synthetic = check_synthetic()
    chirp_pairs, odd_failures = check_chirp()
    gaussian_rows, worst, controls = check_gaussian()
    dilation = check_dilation()
    products, flushed_carries = check_end_to_end()
    first_b, recovery_n, carry_cases = check_recovery_inequalities()
    print(json.dumps({
        "status": "PASS_PR4100_PROOF_COMPOSITION_FINITE",
        "source_phrases": phrases,
        "address_points": addresses,
        "synthetic_convolution_cases_exact": synthetic,
        "chirp_even_t_pairs_exact": chirp_pairs,
        "chirp_odd_t_controls_failing": odd_failures,
        "gaussian_basis_rows": gaussian_rows,
        "gaussian_worst_residual": f"{worst:.3e}",
        "gaussian_controls_detected": controls,
        "dilation_cases": dilation,
        "end_to_end_products": products,
        "end_to_end_final_carry_digits": flushed_carries,
        "T_lt_2_pow_b_from_b": first_b,
        "recovery_n_checked": recovery_n,
        "carry_cases": carry_cases,
        "all_size_theorem_claimed": False,
        "new_kappa_claimed": False,
    }, indent=2))


if __name__ == "__main__":
    sys.exit(main())
