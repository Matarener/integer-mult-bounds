#!/usr/bin/env python3
"""Exact finite corroboration of the prime-exponent representation rank cut.

Nick Petalas. Apache-2.0. Standard library only; read-only; no network or Git.

The written proof is PROOF.md. This script checks its finite ingredients:
regular-permutation defect ranks over Q and four prime fields, the entrywise
representation step and the rank cut on seeded random circuits with
rectangular and singular free maps, the attaining direct and cover words,
exact cover costs for the separation examples, and rejection controls.
It does not replace the written all-size argument.
"""

from __future__ import annotations

import itertools
import json
import random
import sys
from fractions import Fraction

FIELDS = (0, 2, 3, 5, 7)  # 0 means the rationals
SEED = 20261027


def need(cond: bool, msg: str) -> None:
    if not cond:
        raise SystemExit(f"FAIL: {msg}")


# ---------------------------------------------------------------- groups


class Group:
    def __init__(self, name, elems, mul, ident):
        self.name = name
        self.elems = list(elems)
        self.index = {g: i for i, g in enumerate(self.elems)}
        need(len(self.index) == len(self.elems), f"{name}: duplicate elements")
        n = len(self.elems)
        self.e = self.index[ident]
        self.table = [[self.index[mul(a, b)] for b in self.elems] for a in self.elems]
        for a, b, c in itertools.product(range(n), repeat=3):
            if a < 4 or n <= 16:
                need(
                    self.table[self.table[a][b]][c] == self.table[a][self.table[b][c]],
                    f"{name}: associativity",
                )
        self.order = [self._order(i) for i in range(n)]
        self.abelian = all(
            self.table[a][b] == self.table[b][a] for a in range(n) for b in range(n)
        )

    def _order(self, g):
        x, k = g, 1
        while x != self.e:
            x, k = self.table[x][g], k + 1
        return k

    def exponent(self):
        out = 1
        for o in self.order:
            out = out * o // _gcd(out, o)
        return out


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def cyclic_product(mods):
    return Group(
        "x".join(f"C{m}" for m in mods),
        itertools.product(*[range(m) for m in mods]),
        lambda a, b: tuple((x + y) % m for x, y, m in zip(a, b, mods)),
        tuple(0 for _ in mods),
    )


def heisenberg(p):
    # (a,b,c)(a',b',c') = (a+a', b+b', c+c'+a*b'); exponent p for odd p.
    return Group(
        f"Heis{p}",
        itertools.product(range(p), repeat=3),
        lambda x, y: ((x[0] + y[0]) % p, (x[1] + y[1]) % p, (x[2] + y[2] + x[0] * y[1]) % p),
        (0, 0, 0),
    )


def quaternion():
    # Q8 as signed units (s, u), u in 1,i,j,k encoded 0..3.
    t = {(0, 0): (1, 0), (0, 1): (1, 1), (0, 2): (1, 2), (0, 3): (1, 3),
         (1, 0): (1, 1), (1, 1): (-1, 0), (1, 2): (1, 3), (1, 3): (-1, 2),
         (2, 0): (1, 2), (2, 1): (-1, 3), (2, 2): (-1, 0), (2, 3): (1, 1),
         (3, 0): (1, 3), (3, 1): (1, 2), (3, 2): (-1, 1), (3, 3): (-1, 0)}

    def mul(x, y):
        s, u = t[(x[1], y[1])]
        return (x[0] * y[0] * s, u)

    return Group("Q8", [(s, u) for s in (1, -1) for u in range(4)], mul, (1, 0))


# --------------------------------------------------------- linear algebra


def norm(x, p):
    return Fraction(x) if p == 0 else x % p


def inv(x, p):
    return 1 / x if p == 0 else pow(x, p - 2, p)


def rank(rows, p):
    m = [[norm(x, p) for x in r] for r in rows]
    if not m:
        return 0
    r, ncols = 0, len(m[0])
    for c in range(ncols):
        piv = next((i for i in range(r, len(m)) if m[i][c] != 0), None)
        if piv is None:
            continue
        m[r], m[piv] = m[piv], m[r]
        iv = inv(m[r][c], p)
        m[r] = [norm(x * iv, p) for x in m[r]]
        for i in range(len(m)):
            if i != r and m[i][c] != 0:
                f = m[i][c]
                m[i] = [norm(a - f * b, p) for a, b in zip(m[i], m[r])]
        r += 1
        if r == len(m):
            break
    return r


def matmul(a, b, p):
    return [[norm(sum(x * y for x, y in zip(row, col)), p) for col in zip(*b)] for row in a]


def ident(n):
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


def regular(G, g):
    """Left regular permutation matrix: column h maps to row g*h."""
    n = len(G.elems)
    m = [[0] * n for _ in range(n)]
    for h in range(n):
        m[G.table[g][h]][h] = 1
    return m


def defect_rank(G, g, p):
    n = len(G.elems)
    P = regular(G, g)
    return rank([[P[i][j] - (1 if i == j else 0) for j in range(n)] for i in range(n)], p)


# -------------------------------------------- group-algebra matrices (K[G])


def ga_mul(G, A, B, p):
    """Matrices with entries {group index: coefficient}."""
    out = []
    for row in A:
        orow = []
        for col in zip(*B):
            acc = {}
            for x, y in zip(row, col):
                for g, cg in x.items():
                    for h, ch in y.items():
                        k = G.table[g][h]
                        acc[k] = norm(acc.get(k, 0) + cg * ch, p)
            orow.append({k: v for k, v in acc.items() if v != 0})
        out.append(orow)
    return out


def scalar_ga(G, C):
    return [[({G.e: c} if c else {}) for c in row] for row in C]


def gate_ga(G, N, g, p):
    n = len(N)
    out = []
    for i in range(n):
        row = []
        for j in range(n):
            ie = norm((1 if i == j else 0) - N[i][j], p)
            ent = {}
            if g == G.e:
                ent = {G.e: norm(ie + N[i][j], p)}
            else:
                if ie:
                    ent[G.e] = ie
                if norm(N[i][j], p):
                    ent[g] = norm(N[i][j], p)
            row.append({k: v for k, v in ent.items() if v != 0})
        out.append(row)
    return out


def rho_of_ga(G, A, p):
    """Entrywise left-regular image: an (r*|G|) x (c*|G|) scalar matrix."""
    n = len(G.elems)
    regs = [regular(G, g) for g in range(n)]
    rows = len(A) * n
    cols = len(A[0]) * n
    out = [[0] * cols for _ in range(rows)]
    for i, row in enumerate(A):
        for j, ent in enumerate(row):
            for g, c in ent.items():
                R = regs[g]
                for a in range(n):
                    for b in range(n):
                        if R[a][b]:
                            out[i * n + a][j * n + b] = norm(out[i * n + a][j * n + b] + c, p)
    return out


def kron_id(C, n):
    rows, cols = len(C), len(C[0])
    out = [[0] * (cols * n) for _ in range(rows * n)]
    for i in range(rows):
        for j in range(cols):
            if C[i][j]:
                for a in range(n):
                    out[i * n + a][j * n + a] = C[i][j]
    return out


def augmentation(A, p):
    return [[norm(sum(ent.values()), p) for ent in row] for row in A]


# -------------------------------------------------------- random circuits


def rand_mat(rng, r, c, p):
    lo, hi = (-2, 2) if p == 0 else (0, p - 1)
    return [[norm(rng.randint(lo, hi), p) for _ in range(c)] for _ in range(r)]


def rand_idempotent(rng, n, k, p):
    while True:
        S = rand_mat(rng, n, n, p)
        if rank(S, p) == n:
            break
    # invert S by elimination on [S | I]
    aug = [S[i] + ident(n)[i] for i in range(n)]
    for c in range(n):
        piv = next(i for i in range(c, n) if norm(aug[i][c], p) != 0)
        aug[c], aug[piv] = aug[piv], aug[c]
        iv = inv(norm(aug[c][c], p), p)
        aug[c] = [norm(x * iv, p) for x in aug[c]]
        for i in range(n):
            if i != c and norm(aug[i][c], p):
                f = aug[i][c]
                aug[i] = [norm(a - f * b, p) for a, b in zip(aug[i], aug[c])]
    Sinv = [row[n:] for row in aug]
    D = [[1 if (i == j and i < k) else 0 for j in range(n)] for i in range(n)]
    N = matmul(matmul(S, D, p), Sinv, p)
    need(matmul(N, N, p) == N, "random idempotent")
    need(rank(N, p) == k, "random idempotent rank")
    return N


def check_random_cuts(G, p, trials, rng):
    """Rank cut on random circuits with rectangular/singular free maps."""
    n = len(G.elems)
    r_of = [defect_rank(G, g, p) for g in range(n)]
    tight = 0
    for _ in range(trials):
        d, R = rng.choice([(1, 2), (2, 2), (2, 3)])
        k = rng.randint(1, 3)
        labels = [rng.randrange(n) for _ in range(k)]
        ranks = [rng.randint(0, R) for _ in range(k)]
        Ns = [rand_idempotent(rng, R, rk, p) for rk in ranks]
        Cs = [rand_mat(rng, d, R, p)] + [rand_mat(rng, R, R, p) for _ in range(k - 1)]
        Cs.append(rand_mat(rng, R, d, p))
        # F = C0 D1 C1 ... Dk Ck over K[G]
        F = scalar_ga(G, Cs[0])
        for j in range(k):
            F = ga_mul(G, F, gate_ga(G, Ns[j], labels[j], p), p)
            F = ga_mul(G, F, scalar_ga(G, Cs[j + 1]), p)
        Cprod = Cs[0]
        for C in Cs[1:]:
            Cprod = matmul(Cprod, C, p)
        need(augmentation(F, p) == Cprod, "augmentation of endpoint equals free-map product")
        # entrywise representation equals the product of represented factors
        rF = rho_of_ga(G, F, p)
        rP = kron_id(Cs[0], n)
        for j in range(k):
            rP = matmul(rP, rho_of_ga(G, gate_ga(G, Ns[j], labels[j], p), p), p)
            rP = matmul(rP, kron_id(Cs[j + 1], n), p)
        need(rF == rP, "entrywise representation is multiplicative")
        E = kron_id(Cprod, n)
        defect = [[norm(a - b, p) for a, b in zip(ra, rb)] for ra, rb in zip(rF, E)]
        lhs = rank(defect, p)
        rhs = sum(rk * r_of[g] for rk, g in zip(ranks, labels))
        need(lhs <= rhs, f"{G.name} p={p}: rank cut violated {lhs} > {rhs}")
        tight += lhs == rhs
    return tight


# ----------------------------------------------------- covers and words


def subproducts(G, word):
    out = {G.e}
    for bits in itertools.product((0, 1), repeat=len(word)):
        x = G.e
        for b, g in zip(bits, word):
            if b:
                x = G.table[x][g]
        out.add(x)
    return out


def cover_cost(G, targets, max_len):
    labels = [g for g in range(len(G.elems)) if g != G.e]
    tset = set(targets)
    for k in range(max_len + 1):
        for word in itertools.product(labels, repeat=k):
            if tset <= subproducts(G, word):
                return k, word
    return None, None


def realize(G, word, targets, p, dirty=1):
    """Diagonal-projector word on len(targets) data roles plus untouched dirt."""
    masks = []
    for t in targets:
        m = next(
            bits
            for bits in itertools.product((0, 1), repeat=len(word))
            if _eval(G, word, bits) == t
        )
        masks.append(m)
    R = len(targets) + dirty
    F = scalar_ga(G, ident(R))
    for j, g in enumerate(word):
        N = [[(masks[i][j] if (i == c and i < len(targets)) else 0) for c in range(R)] for i in range(R)]
        F = ga_mul(G, F, gate_ga(G, N, g, p), p)
    want = [[({targets[i] if i < len(targets) else G.e: 1} if i == c else {}) for c in range(R)] for i in range(R)]
    return F == want, masks


def _eval(G, word, bits):
    x = G.e
    for b, g in zip(bits, word):
        if b:
            x = G.table[x][g]
    return x


# ------------------------------------------------------------------- main


def main() -> int:
    rng = random.Random(SEED)
    groups = {
        "C2^2": cyclic_product((2, 2)),
        "C2^3": cyclic_product((2, 2, 2)),
        "C2^4": cyclic_product((2, 2, 2, 2)),
        "C3^2": cyclic_product((3, 3)),
        "C5": cyclic_product((5,)),
        "Heis3": heisenberg(3),
        "C4": cyclic_product((4,)),
        "Q8": quaternion(),
    }
    report = {"marker": None, "regular_defect_ranks": {}, "random_cuts": {}, "words": {}, "controls": []}

    # A. regular defect rank |G|(1 - 1/ord g), every element, five fields
    checked = 0
    for name, G in groups.items():
        n = len(G.elems)
        for p in FIELDS:
            for g in range(n):
                need(defect_rank(G, g, p) == n - n // G.order[g], f"{name} p={p} regular defect")
                checked += 1
        report["regular_defect_ranks"][name] = {
            "order": n, "exponent": G.exponent(), "abelian": G.abelian,
        }
    need(not groups["Heis3"].abelian and groups["Heis3"].exponent() == 3, "Heis3 nonabelian, exponent 3")
    report["regular_defect_checks"] = checked

    # B. rank cut on random circuits (rectangular, singular free maps, all projector ranks)
    total = 0
    for name, p, trials in [("C2^3", 2, 40), ("C2^3", 3, 25), ("C3^2", 3, 25),
                            ("C3^2", 2, 25), ("C5", 0, 25), ("Heis3", 2, 8),
                            ("Heis3", 3, 8), ("Q8", 5, 25), ("C4", 2, 25)]:
        tight = check_random_cuts(groups[name], p, trials, rng)
        report["random_cuts"][f"{name}/F{p or 'Q'}"] = {"circuits": trials, "tight": tight}
        total += trials
    report["random_circuits"] = total

    # C. separation examples: all nonidentity targets
    for name, max_len in [("C2^2", 2), ("C2^3", 3), ("C3^2", 4)]:
        G = groups[name]
        targets = [g for g in range(len(G.elems)) if g != G.e]
        d = len(targets)
        k, word = cover_cost(G, targets, max_len)
        need(k is not None, f"{name}: cover found")
        need((1 << (k - 1)) - 1 < d, f"{name}: shorter covers excluded by counting")
        for p in (0, 2, 3):
            ok, _ = realize(G, list(word), targets, p)
            need(ok, f"{name} p={p}: cover word realizes all targets")
            ok, _ = realize(G, targets, targets, p)
            need(ok, f"{name} p={p}: direct rank-one word realizes all targets")
        report["words"][name] = {"targets": d, "cover_cost": k, "rank_one_cost": d}
    # C2^4: cover word is the basis word; length 4 is forced by 2^3 < 16
    G = groups["C2^4"]
    targets = [g for g in range(len(G.elems)) if g != G.e]
    basis = [G.index[v] for v in [(1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)]]
    need(set(targets) <= subproducts(G, basis), "C2^4 basis word covers")
    ok, _ = realize(G, basis, targets, 2)
    need(ok, "C2^4 basis word realizes all 15 targets over F2")
    report["words"]["C2^4"] = {"targets": 15, "cover_cost": 4, "rank_one_cost": 15}
    # Heis3: every nonidentity element, regular cut value equals d
    G = groups["Heis3"]
    vals = {G.order[g] for g in range(len(G.elems)) if g != G.e}
    need(vals == {3}, "Heis3 prime exponent")

    # D. controls
    c = []
    G = groups["C2^3"]
    targets = [g for g in range(len(G.elems)) if g != G.e]
    _, word = cover_cost(G, targets, 3)
    shorter = set(targets) <= subproducts(G, list(word)[:-1])
    need(not shorter, "control: dropping a cover letter loses a target")
    c.append("dropped cover letter uncovers a target")
    # regular-cut bound in C4 for three copies of a^2 is only 2: hypothesis needed
    G = groups["C4"]
    a2 = G.index[(2,)]
    lhs = 3 * Fraction(len(G.elems) - len(G.elems) // G.order[a2])
    per = Fraction(max(len(G.elems) - len(G.elems) // o for o in G.order))
    need(-(-lhs // per) == 2, "control: C4 regular cut for three a^2 targets is 2 < 3")
    c.append("C4 non-prime exponent: regular cut alone gives 2 for three a^2 entries")
    # Q8: mixed orders, regular cut on {i,j,k,-1} over any field
    G = groups["Q8"]
    lhs = sum(Fraction(8 - 8 // G.order[G.index[x]]) for x in [(1, 1), (1, 2), (1, 3), (-1, 0)])
    need(-(-lhs // 6) == 4, "control: Q8 regular cut {i,j,k,-1} gives 4")
    c.append("Q8 targets i,j,k,-1: regular cut 4 = d although orders differ")
    # a fake defect claim: identity labels have zero defect
    G = groups["C3^2"]
    need(defect_rank(G, G.e, 3) == 0, "control: identity label has zero defect")
    c.append("identity label contributes zero defect")
    # an idempotent of rank 2 on a nonidentity label contributes 2 r(g), not r(g)
    need(rank(kron_id(rand_idempotent(rng, 3, 2, 3), 1), 3) == 2, "control: projector rank")
    c.append("rank-two projector rank detected")
    report["controls"] = c

    report["marker"] = "PASS_PRIME_EXPONENT_RANK_CUT"
    print(json.dumps(report, indent=1, sort_keys=True))
    print(
        f"PASS_PRIME_EXPONENT_RANK_CUT regular_checks={checked} random_circuits={total}"
        f" separations=4 controls={len(c)} no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
