#!/usr/bin/env python3
"""Exact checks for the plane-port clique odd-cycle lemma (see PROOF.md).

The lemma is proved in PROOF.md. This script authenticates the E3 source
sentence it sharpens, corroborates the lemma on exact rational
decompositions of the identity, and checks that the conditions it imposes are
not vacuous: a triangle can satisfy E3's spectral inequality.
"""
from fractions import Fraction
from pathlib import Path
import hashlib
import random

PLANES = 3
DIM = 2 * PLANES
THEORY = Path(__file__).resolve().parents[1] / "plane-port-global-rank-dual" / "THEORY.md"
THEORY_SHA256 = "dab2db4431bc6e75b48fcce4dc4a0d7a0bf1fc65a26b4e3dce2cdf7689d963b8"
E3_SENTENCE = "If the cross terms are bipartite"
TRIALS = 400


def require(ok, message="check failed"):
    if not ok:
        raise SystemExit("FAIL: " + message)


def rank(rows):
    m = [list(r) for r in rows]
    r = 0
    for c in range(len(m[0]) if m else 0):
        piv = next((i for i in range(r, len(m)) if m[i][c] != 0), None)
        if piv is None:
            continue
        m[r], m[piv] = m[piv], m[r]
        for i in range(len(m)):
            if i != r and m[i][c] != 0:
                f = m[i][c] / m[r][c]
                m[i] = [a - f * b for a, b in zip(m[i], m[r])]
        r += 1
    return r


def rank_one_factors(mat):
    """Exact rank factorization: mat = sum of outer(u, v)."""
    m = [list(r) for r in mat]
    terms = []
    while any(x != 0 for row in m for x in row):
        i, j = next((i, j) for i in range(DIM) for j in range(DIM) if m[i][j] != 0)
        u = [m[k][j] for k in range(DIM)]
        v = [m[i][k] / m[i][j] for k in range(DIM)]
        terms.append((u, v))
        m = [[m[a][b] - u[a] * v[b] for b in range(DIM)] for a in range(DIM)]
    return terms


def planes_of(vec):
    return frozenset(p for p in range(PLANES) if vec[2 * p] != 0 or vec[2 * p + 1] != 0)


def outer_sum(terms):
    return [[sum((u[a] * v[b] for u, v in terms), Fraction(0)) for b in range(DIM)] for a in range(DIM)]


def block_support(mat):
    return {(p, q) for p in range(PLANES) for q in range(PLANES) if p != q
            and any(mat[2 * p + a][2 * q + b] != 0 for a in (0, 1) for b in (0, 1))}


def bipartite(edges):
    side = {}
    for start in range(PLANES):
        if start in side:
            continue
        side[start], stack = 0, [start]
        while stack:
            p = stack.pop()
            for a, b in edges:
                for x, y in ((a, b), (b, a)):
                    if x == p:
                        if y not in side:
                            side[y] = 1 - side[p]
                            stack.append(y)
                        elif side[y] == side[p]:
                            return False
    return True


def random_term(rng):
    s = rng.sample(range(PLANES), rng.randint(1, PLANES))
    t = rng.sample(range(PLANES), rng.randint(1, PLANES))
    u = [Fraction(rng.randint(-3, 3)) if k // 2 in s else Fraction(0) for k in range(DIM)]
    v = [Fraction(rng.randint(-3, 3), rng.choice((1, 2))) if k // 2 in t else Fraction(0) for k in range(DIM)]
    return u, v


def check_decompositions():
    rng = random.Random(20261027)
    identity = [[Fraction(int(a == b)) for b in range(DIM)] for a in range(DIM)]
    bip = saving_shaped = 0
    for _ in range(TRIALS):
        terms = [t for t in (random_term(rng) for _ in range(rng.randint(1, 6)))
                 if planes_of(t[0]) and planes_of(t[1])]
        rest = [[identity[a][b] - x for b, x in enumerate(row)] for a, row in enumerate(outer_sum(terms))]
        terms += rank_one_factors(rest)
        require(outer_sum(terms) == identity)
        diag = [t for t in terms if planes_of(t[0]) & planes_of(t[1])]
        cross = [t for t in terms if not planes_of(t[0]) & planes_of(t[1])]
        n = outer_sum(cross)
        g = {(p, q) for u, v in cross for p in planes_of(u) for q in planes_of(v)}
        h = {(p, q) for u, v in diag for p in planes_of(u) for q in planes_of(v) if p != q}
        supp = block_support(n)
        require(supp <= g & h, "support of N must lie in both term graphs")
        m = DIM - rank([[identity[a][b] - n[a][b] for b in range(DIM)] for a in range(DIM)])
        require(len(diag) >= DIM - m)
        if bipartite(supp):
            bip += 1
            plus = DIM - rank([[identity[a][b] + n[a][b] for b in range(DIM)] for a in range(DIM)])
            require(plus == m and 2 * m <= rank(n))
        if 2 * m > len(cross):
            saving_shaped += 1
            require(not bipartite(g & h))
    return bip, saving_shaped


def check_triangle_control():
    """Three single-source cross terms whose sum has 2m = 4 > rank 3."""
    m_mat = [[Fraction(int(i == j)) - 1 for j in range(3)] for i in range(3)]  # I - J
    cross = []
    for j in range(3):
        u = [Fraction(int(k == 2 * j)) for k in range(DIM)]
        v = [m_mat[j][k // 2] if k % 2 == 0 else Fraction(0) for k in range(DIM)]
        cross.append((u, v))
    require(all(not planes_of(u) & planes_of(v) for u, v in cross))
    n = outer_sum(cross)
    one = [[Fraction(int(a == b)) - n[a][b] for b in range(DIM)] for a in range(DIM)]
    m = DIM - rank(one)
    require((rank(n), m) == (3, 2) and 2 * m > len(cross))
    require(not bipartite(block_support(n)) and len(block_support(n)) == 6)
    # Any completion must put diagonal terms on all six directed pairs.
    return block_support(n)


def main():
    data = THEORY.read_bytes()
    require(hashlib.sha256(data).hexdigest() == THEORY_SHA256)
    require(E3_SENTENCE in data.decode())
    bip, saving_shaped = check_decompositions()
    pairs = check_triangle_control()
    require(bip > 0)
    print(f"decompositions={TRIALS} bipartite_supports={bip} spectral_saving_shapes={saving_shaped}")
    print(f"triangle_control rank=3 m=2 directed_pairs={len(pairs)}")
    print("PASS_PLANE_PORT_CLIQUE_ODD_CYCLE")


if __name__ == "__main__":
    main()
