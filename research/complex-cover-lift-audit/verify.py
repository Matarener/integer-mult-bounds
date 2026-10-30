#!/usr/bin/env python3
"""Audit #4100 COMPLEX.md: common cover, defect correction and arbitrary-f lift.

Propositions checked (COMPLEX.md at #4100 head 337d049):
1. Gamma = |O(73,2)| = 2^1296 prod_{i=1}^{36}(2^(2i)-1);
2. P_g C_all P_g^-1 = C_all X_delta, delta_i = (wt(row_i g)-1)/2 mod 2,
   for orthogonal g (with or without a translation);
3. H0 = ((1-i)/2) D C D, D = diag(1,i), and its tensor form;
4. the depth recursion D(e), two-level halving and the row-stock padding;
5. the arbitrary-f lift on the four literal PR4088 words: every warp generator
   G -> M^(tensor f) and every scalar kept as a scalar preserves the forward
   and dual endpoint contracts.

The word format and endpoint contract are read from PR4088's
vendor/audit_core.py; nothing is imported from it.  Standard library only.
Run with --full to add the n = 7 brute-force count of O(7,2) (about 8 min).
"""
import gzip
import json
import random
import sys
from fractions import Fraction as Q
from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
CRT = ROOT / "research" / "unconditional-batched-crt"
MIXED = ROOT / "research" / "staged544-mixed-fourth-entry"
WORDS = ["THREE-base", "THREE-extra", "FOUR-base", "FOUR-extra"]
V, N = 112, 704


def popcount(x):
    return bin(x).count("1")


# --------------------------------------------------------------- sources
def check_sources():
    cx = (CRT / "COMPLEX.md").read_text(encoding="utf-8")
    for needle in ["Set W=322560 and Gamma=2^1296 product_{i=1}^{36}(2^(2i)-1).",
                   "This is |O(73,2)|: the all-one vector has norm1",
                   "Define D(e)=0 for e<73 and D(e)=1+D(48floor(e/73)) otherwise.",
                   "Reserve q=ceil(log2((W Gamma)^D(h))) row bits. Pad their complete range",
                   "delta_i=(wt(row_i(g))-1)/2 mod2. The identity",
                   "P_g C_all P_g^-1=C_all X_delta follows by expanding Hamming weight modulo4.",
                   "H0=((1-i)/2) D C D. Tensor diagonals are phases from address weight modulo4.",
                   "Evaluate each unary generator G at G tensor f, and every scalar coefficient",
                   "becomes i^(fa). A role SCALE or bridge sign stays scalar.",
                   "{1:8060060,2:2310120,3:751813,4:327210,5:66425,8:25920,48:138492}"]:
        assert needle in cx, needle
    core = (MIXED / "vendor" / "audit_core.py").read_text(encoding="utf-8")
    for needle in ["# Exact free-operator semantics.  A value is a dict {(input, word): Fraction};",
                   "# word is a reduced tuple of signed operator ids (leftmost = applied last).",
                   "return word[1:] if word and word[0] == -op else (op,) + word",
                   "V, N, H = 112, 704, 9"]:
        assert needle in core, needle


# --------------------------------------------------------- 1. cover size
def sp_order(m):
    out = 2 ** (m * m)
    for i in range(1, m + 1):
        out *= 2 ** (2 * i) - 1
    return out


def orthogonal_matrices(n):
    """All g in GL(n,2) with g g^T = I, as tuples of row bitmasks."""
    odd = [v for v in range(1, 2 ** n) if popcount(v) % 2]

    def rec(rows):
        if len(rows) == n:
            yield tuple(rows)
            return
        for v in odd:
            if all(popcount(v & r) % 2 == 0 for r in rows):
                yield from rec(rows + [v])

    yield from rec([])


def check_cover(full=False):
    out = {}
    for n in (1, 3, 5) + ((7,) if full else ()):
        count = 0
        for g in orthogonal_matrices(n):
            count += 1
            assert all(popcount(r) % 2 for r in g)  # g fixes the all-one vector
        assert count == sp_order((n - 1) // 2), n
        out[n] = count
    gamma = sp_order(36)
    return out, gamma


# ---------------------------------------------------- 2. defect identity
def mat_vec(rows, x):
    y = 0
    for i, r in enumerate(rows):
        y |= (popcount(r & x) & 1) << i
    return y


def transpose(rows, n):
    return [sum(((rows[i] >> j) & 1) << i for i in range(n)) for j in range(n)]


def delta_of(rows):
    return sum((((popcount(r) - 1) // 2) % 2) << i for i, r in enumerate(rows))


def defect_holds(rows, n):
    """Entrywise: C_all[x,y] = ((1+i)/2)^n (-i)^wt(x^y), P_g sends x to g x.

    (P_g C_all P_g^-1)[x,y] = C_all[g^-1 x, g^-1 y] and (C_all X_delta)[x,y] =
    C_all[x, y^delta], so the identity is wt(g^-1 z) = wt(z ^ delta) mod 4 for
    every z.  A translation x -> x+v cancels in x^y.
    """
    ginv = transpose(rows, n)
    d = delta_of(rows)
    return all(popcount(mat_vec(ginv, z)) % 4 == popcount(z ^ d) % 4 for z in range(2 ** n))


def random_orthogonal(n, rng, steps=60):
    """Products of coordinate permutations and transvections x + (x.u)u, wt(u) even."""
    rows = [1 << i for i in range(n)]
    for _ in range(steps):
        if rng.random() < 0.3:
            perm = list(range(n))
            rng.shuffle(perm)
            rows = [rows[perm[i]] for i in range(n)]
        else:
            u = rng.getrandbits(n)
            if popcount(u) % 2:
                u ^= 1
            ug = 0
            for i in range(n):
                if (u >> i) & 1:
                    ug ^= rows[i]
            rows = [r ^ ug if (u >> i) & 1 else r for i, r in enumerate(rows)]
    return rows


def is_orthogonal(rows, n):
    return all(popcount(rows[i] & rows[j]) % 2 == (i == j) for i in range(n) for j in range(n))


def check_defect():
    for n in (1, 3, 5):
        for g in orthogonal_matrices(n):
            assert defect_holds(list(g), n), (n, g)
    rng = random.Random(4100)
    nonzero = 0
    for _ in range(400):
        g = random_orthogonal(73, rng)
        assert is_orthogonal(g, 73)
        ginv, d = transpose(g, 73), delta_of(g)
        nonzero += d != 0
        assert popcount(d) % 4 == 0
        for _ in range(200):
            z = rng.getrandbits(73)
            assert popcount(mat_vec(ginv, z)) % 4 == popcount(z ^ d) % 4
    assert nonzero > 300
    return nonzero


# --------------------------------------------------------- 3. H0 identity
class G:
    """Exact Gaussian rationals."""

    def __init__(self, re, im=0):
        self.re, self.im = Q(re), Q(im)

    def __mul__(self, o):
        return G(self.re * o.re - self.im * o.im, self.re * o.im + self.im * o.re)

    def __eq__(self, o):
        return self.re == o.re and self.im == o.im


def check_h0():
    I = G(0, 1)
    c_same, c_diff = G(Q(1, 2), Q(1, 2)), G(Q(1, 2), Q(-1, 2))
    scal = G(Q(1, 2), Q(-1, 2))
    for h in range(1, 7):
        s = G(1)
        for _ in range(h):
            s = s * scal
        for x in range(2 ** h):
            for y in range(2 ** h):
                c = G(1)
                for k in range(h):
                    c = c * (c_same if ((x ^ y) >> k) & 1 == 0 else c_diff)
                ph = G(1)
                for _ in range(popcount(x) + popcount(y)):
                    ph = ph * I
                rhs = s * ph * c
                lhs = G(Q((-1) ** popcount(x & y), 2 ** h))
                assert lhs == rhs, (h, x, y)
    z = G(1)
    for h in range(1, 200):
        z = z * G(1, -1)
        w = G(1)
        for _ in range(h // 2):
            w = w * G(0, -2)
        if h % 2:
            w = w * G(1, -1)
        assert z == w


# ------------------------------------------------- 4. depth and stock
def depth(e):
    d = 0
    while e >= 73:
        e, d = 48 * (e // 73), d + 1
    return d


def check_depth_and_stock(limit=200_000):
    prev = 0
    for e in range(1, limit + 1):
        d = depth(e)
        assert d >= prev
        prev = d
        if e >= 73:
            f = e // 73
            assert all(depth(r * f) <= d - 1 for r in (1, 2, 3, 4, 5, 8, 48))
            assert 2 * 48 * ((48 * f) // 73) <= e
    M1 = 322560 * sp_order(36)
    rows = {}
    for h in (73, 10 ** 3, 10 ** 6, 10 ** 12, 10 ** 30):
        M = M1 ** depth(h)
        q = (M - 1).bit_length()
        R = -(-2 ** q // M) * M
        assert 2 ** q <= R < 2 ** (q + 1) and R % M == 0
        rows[h] = {"D": depth(h), "q": q, "R_over_2q": float(Q(R, 2 ** q)),
                   "fits_in_q_bits": R <= 2 ** q}
    return rows


# ------------------------------------------------------ 5. arbitrary-f lift
def program(w):
    """Literal executed sequence: corrections, wrapper, A, cut, B+warps, restore, cleanup."""
    items = [("corr", c["target"], c["source"], tuple(c["operator_word"]),
              Q(c["coefficient"])) for c in w["initial_corrections"]]
    items += w["precondition"] + w["compensation"] + w["A"] + w["cut"]
    at = {}
    for k, rec in enumerate(w["warps"], 1):
        at.setdefault(rec[0], []).append(["warp", rec[1], k])
    for p in range(len(w["B"]) + 1):
        items += at.get(p, [])
        if p < len(w["B"]):
            items.append(w["B"][p])
    return items + w["restore"] + w["cleanup"]


PHASE = [1, 1j, -1, -1j]


class Mono:
    """Monomial matrix: column x goes to row perm[x] with phase i^ph[x]."""

    def __init__(self, perm, ph):
        self.perm, self.ph = perm, ph

    def apply(self, v):
        out = [0j] * len(v)
        for x, a in enumerate(v):
            out[self.perm[x]] = PHASE[self.ph[x]] * a
        return out

    def inverse(self):
        perm, ph = [0] * len(self.perm), [0] * len(self.perm)
        for x, y in enumerate(self.perm):
            perm[y], ph[y] = x, (-self.ph[x]) % 4
        return Mono(perm, ph)

    def transpose(self):
        inv = self.inverse()
        return Mono(inv.perm, [(-p) % 4 for p in inv.ph])

    def tensor_power(self, f):
        d, perm, ph = len(self.perm), [0], [0]
        for _ in range(f):
            perm = [p * d + self.perm[x] for p in perm for x in range(d)]
            ph = [(a + self.ph[x]) % 4 for a in ph for x in range(d)]
        return Mono(perm, ph)


def random_mono(d, rng):
    perm = list(range(d))
    rng.shuffle(perm)
    return Mono(perm, [rng.randrange(4) for _ in range(d)])


def run_word(w, rep, dual, rng, dim, scalar_hook=None, inv=None):
    """Execute w with warp k -> rep[k]; return the relative contract error."""
    removed = set(w["removed"])
    live = [r for r in range(N) if r not in removed]
    restored = sorted(map(int, w["helper_final"]))
    rnd = lambda: [complex(rng.gauss(0, 1), rng.gauss(0, 1)) for _ in range(dim)]
    x = {r: rnd() for r in live}
    for c in restored:
        x[c + N] = rnd()
    reg = {r: list(v) for r, v in x.items()}
    inv = inv or {k: m.inverse() for k, m in rep.items()}
    tr = {k: m.transpose() for k, m in rep.items()}
    trinv = {k: m.transpose() for k, m in inv.items()}

    def op(k):  # dual symbol D_k = K_k^(-T)
        if dual:
            return trinv[k] if k > 0 else tr[-k]
        return rep[k] if k > 0 else inv[-k]

    def axpy(t, s, q):
        reg[t] = [a + q * b for a, b in zip(reg[t], s)]

    for g in program(w):
        kind = g[0]
        if kind == "add":
            t, s, q = g[1], g[2], Q(g[3], g[4])
            q = scalar_hook(q) if scalar_hook else q
            if dual:
                t, s, q = s, t, -q
            axpy(t, reg[s], complex(q))
        elif kind == "scale":
            q = Q(g[2], g[3])
            q = scalar_hook(q) if scalar_hook else q
            if dual:
                q = 1 / q
            reg[g[1]] = [complex(q) * a for a in reg[g[1]]]
        elif kind == "warp":
            reg[g[1]] = op(g[2]).apply(reg[g[1]])
        elif kind == "corr":
            _, t, s, word, c = g
            if dual:
                v = reg[t]
                for o in word:  # (G_w1 ... G_wn)^T x = G_wn^T ... G_w1^T x
                    v = (tr[o] if o > 0 else trinv[-o]).apply(v)
                axpy(s, v, -complex(c))
            else:
                v = reg[s]
                for o in reversed(word):
                    v = (rep[o] if o > 0 else inv[-o]).apply(v)
                axpy(t, v, complex(c))
        else:
            raise AssertionError(f"unknown primitive {g!r}")

    scale = max(abs(a) for v in x.values() for a in v)
    err = 0.0
    for r in live:
        expect = list(x[r])
        if dual and r < V:
            expect = [a - b for a, b in zip(expect, x[r + V])]
        if not dual and V <= r < 2 * V:
            expect = [a + b for a, b in zip(expect, x[r - V])]
        err = max(err, max(abs(a - b) for a, b in zip(reg[r], expect)))
    for c in restored:
        err = max(err, max(abs(a - b) for a, b in zip(reg[c + N], x[c + N])))
    return err / scale


def load_word(name):
    with gzip.open(MIXED / "inputs" / f"{name}.json.gz") as fh:
        return json.load(fh)


def word_scalars(w):
    parts = ("precondition", "compensation", "A", "cut", "B", "restore", "cleanup")
    qs = [Q(g[3], g[4]) for p in parts for g in w[p] if g[0] == "add"]
    qs += [Q(g[2], g[3]) for p in parts for g in w[p] if g[0] == "scale"]
    qs += [Q(c["coefficient"]) for c in w["initial_corrections"]]
    kinds = {g[0] for p in parts for g in w[p]}
    return qs, kinds


def check_lift(fs=(1, 2, 3), d=4):
    rng = random.Random(4088)
    out = {}
    for name in WORDS:
        w = load_word(name)
        qs, kinds = word_scalars(w)
        assert kinds <= {"add", "scale", "warp"}, kinds
        assert all(q.denominator & (q.denominator - 1) == 0 for q in qs)
        gens = range(1, len(w["warps"]) + 1)
        assert all(0 < abs(o) <= len(w["warps"]) for c in w["initial_corrections"]
                   for o in c["operator_word"])
        errs = {}
        for f in fs:
            for dual in (False, True):
                rep = {k: random_mono(d, rng).tensor_power(f) for k in gens}
                e = run_word(w, rep, dual, rng, d ** f)
                assert e < 1e-9, (name, f, dual, e)
                errs[f"f{f}_{'dual' if dual else 'forward'}"] = e
        out[name] = {"events": len(program(w)), "scalars": len(qs),
                     "negative_scalars": sum(q < 0 for q in qs),
                     "warp_generators": len(w["warps"]), "max_error": max(errs.values())}
    return out


def main():
    full = "--full" in sys.argv
    check_sources()
    print("PASS source binding: COMPLEX.md statements and PR4088 free-word semantics")
    counts, gamma = check_cover(full)
    print(f"PASS cover size: |O(n,2)| = |Sp(n-1,2)| for n in {sorted(counts)} "
          f"({counts}); Gamma has {gamma.bit_length()} bits")
    nz = check_defect()
    print(f"PASS defect identity: all of O(3,2), O(5,2); n = 73 on 400 random g "
          f"x 200 z ({nz} with delta != 0, wt(delta) = 0 mod 4 throughout)")
    check_h0()
    print("PASS H0 = ((1-i)/2) D C D exactly, tensor powers h <= 6, scalar parity split h < 200")
    stock = check_depth_and_stock()
    print("PASS depth: D monotone, every child rank drops D, two levels halve (e <= 2e5)")
    for h, row in stock.items():
        print(f"     h={h}: D={row['D']}, q={row['q']}, R/2^q={row['R_over_2q']:.4f}, "
              f"fits in q bits: {row['fits_in_q_bits']}")
    lift = check_lift()
    for name, row in lift.items():
        print(f"PASS lift {name}: {row['events']} events, {row['warp_generators']} warp "
              f"generators, {row['scalars']} real dyadic scalars; f = 1,2,3 forward and "
              f"dual, max relative error {row['max_error']:.1e}")
    print("PASS_COMPLEX_COVER_LIFT_AUDIT")


if __name__ == "__main__":
    main()
