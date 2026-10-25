#!/usr/bin/env python3
"""#4334's sharp right-vector threshold, checked over extension fields F_4, F_8, F_9, F_16, F_25, F_27.

Model (#4334): paid factors I + u y^T with u in R^2, R = K^k, and y in K^2 common to all components;
GL_2(K) free and common. For each q this builds #4334's quadratic-extension target (multiplication by
one representative of each K-line of L = K[X]/(h), h irreducible) and checks: no common pivot phi, t;
#4334's explicit three-factor word reproduces every component; delta = 2 over all free T. Over F_4 it
also shows by exhaustive search that no word with two paid factors exists, without the criterion.
Standard library only; no code from #4334.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from itertools import product
import json
import random
import sys

FIELDS = [(2, 2), (2, 3), (3, 2), (2, 4), (5, 2), (3, 3)]


def need(condition, message):
    if not condition:
        raise AssertionError(message)


class GF:
    """F_(p^k) as F_p[x]/(f), elements encoded as integers in base p"""

    def __init__(self, p, k):
        self.p, self.k, self.q = p, k, p ** k
        for tail in product(range(p), repeat=k):
            f = list(tail) + [1]
            self.f = f
            table = [[self._mul(a, b) for b in range(self.q)] for a in range(self.q)]
            if all(any(table[a][b] == 1 for b in range(1, self.q)) for a in range(1, self.q)):
                self.M = table
                break
        self.A = [[self._enc([(x + y) % p for x, y in zip(self._dec(a), self._dec(b))]) for b in range(self.q)] for a in range(self.q)]
        self.neg = [next(b for b in range(self.q) if self.A[a][b] == 0) for a in range(self.q)]
        self.inv = [None] + [next(b for b in range(1, self.q) if self.M[a][b] == 1) for a in range(1, self.q)]

    def _dec(self, a):
        return [(a // self.p ** i) % self.p for i in range(self.k)]

    def _enc(self, v):
        return sum(c * self.p ** i for i, c in enumerate(v))

    def _mul(self, a, b):
        x, y, k, p = self._dec(a), self._dec(b), self.k, self.p
        r = [0] * (2 * k - 1)
        for i in range(k):
            for j in range(k):
                r[i + j] = (r[i + j] + x[i] * y[j]) % p
        for d in range(2 * k - 2, k - 1, -1):
            c = r[d]
            if c:
                for i in range(k + 1):
                    r[d - k + i] = (r[d - k + i] - c * self.f[i]) % p
        return self._enc(r[:k])

    def add(self, a, b):
        return self.A[a][b]

    def mul(self, a, b):
        return self.M[a][b]

    def sub(self, a, b):
        return self.A[a][self.neg[b]]


def mm(K, x, y):
    return tuple(tuple(K.add(K.mul(x[i][0], y[0][j]), K.mul(x[i][1], y[1][j])) for j in range(2)) for i in range(2))


def mv(K, x, v):
    return tuple(K.add(K.mul(x[i][0], v[0]), K.mul(x[i][1], v[1])) for i in range(2))


def det(K, x):
    return K.sub(K.mul(x[0][0], x[1][1]), K.mul(x[0][1], x[1][0]))


def singer_target(K):
    """components A_l: multiplication by (1, x) and (0, 1) in L = K[X]/(X^2 + bX + c), basis (1, X)"""
    q = K.q
    b, c = next((b, c) for b in range(q) for c in range(q)
                if all(K.add(K.add(K.mul(x, x), K.mul(b, x)), c) for x in range(q)))
    # X * X = -bX - c; multiplication by u0 + u1 X sends 1 -> (u0, u1), X -> (-c u1, u0 - b u1)
    comps = []
    for u0, u1 in [(1, x) for x in range(q)] + [(0, 1)]:
        comps.append(((u0, K.neg[K.mul(c, u1)]), (u1, K.sub(u0, K.mul(b, u1)))))
    return comps


def points(K):
    return [(1, x) for x in range(K.q)] + [(0, 1)]


def line(K, v):
    """normalized representative of the K-line through a nonzero vector"""
    s = K.inv[v[0]] if v[0] else K.inv[v[1]]
    return (K.mul(s, v[0]), K.mul(s, v[1]))


def three_factor_word(K, M):
    """#4334 Section 3, componentwise: M = [[1,0],[r,1]] [[1,b],[0,D]] [[e,0],[f,1]]"""
    (a, b), (c, d) = M
    r = 0 if d else 1
    D = K.sub(d, K.mul(r, b))
    f = K.mul(K.inv[D], K.sub(c, K.mul(r, a)))
    e = K.sub(a, K.mul(b, f))
    return mm(K, mm(K, ((1, 0), (r, 1)), ((1, b), (0, D))), ((e, 0), (f, 1)))


def rank_stack(K, rows):
    rows, rank = [list(r) for r in rows], 0
    for col in range(2):
        piv = next((i for i in range(rank, len(rows)) if rows[i][col]), None)
        if piv is None:
            continue
        rows[rank], rows[piv] = rows[piv], rows[rank]
        iv = K.inv[rows[rank][col]]
        for i in range(len(rows)):
            if i != rank and rows[i][col]:
                fct = K.mul(rows[i][col], iv)
                rows[i] = [K.sub(x, K.mul(fct, y)) for x, y in zip(rows[i], rows[rank])]
        rank += 1
    return rank


def gl2(K):
    rng = range(K.q)
    return [((a, b), (c, d)) for a, b, c, d in product(rng, rng, rng, rng) if det(K, ((a, b), (c, d)))]


def two_factor_exists(K, comps):
    """exhaustive: M_i S^-1 = (I + u1_i y1^T)(I + u2_i y2^T) for one S, y1, y2 and some u1_i, u2_i"""
    I = ((1, 0), (0, 1))
    vecs = list(product(range(K.q), repeat=2))
    ys = points(K)
    for S in gl2(K):
        dS = K.inv[det(K, S)]
        Sinv = ((K.mul(S[1][1], dS), K.neg[K.mul(S[0][1], dS)]), (K.neg[K.mul(S[1][0], dS)], K.mul(S[0][0], dS)))
        targets = [mm(K, Mi, Sinv) for Mi in comps]
        for y1 in ys:
            for y2 in ys:
                def ok(X):
                    for u2 in vecs:
                        F2 = ((K.add(1, K.mul(u2[0], y2[0])), K.mul(u2[0], y2[1])), (K.mul(u2[1], y2[0]), K.add(1, K.mul(u2[1], y2[1]))))
                        # need X F2^-1 - I = u1 y1^T, a rank <= 1 matrix with row space in span(y1)
                        dF = det(K, F2)
                        if not dF:
                            continue
                        iv = K.inv[dF]
                        F2i = ((K.mul(F2[1][1], iv), K.neg[K.mul(F2[0][1], iv)]), (K.neg[K.mul(F2[1][0], iv)], K.mul(F2[0][0], iv)))
                        Z = mm(K, X, F2i)
                        Z = ((K.sub(Z[0][0], 1), Z[0][1]), (Z[1][0], K.sub(Z[1][1], 1)))
                        if all(K.sub(K.mul(Z[i][0], y1[1]), K.mul(Z[i][1], y1[0])) == 0 for i in range(2)):
                            return True
                    return False
                if all(ok(X) for X in targets):
                    return True
    return False


def main():
    out = {}
    rng = random.Random(4334)
    for p, k in FIELDS:
        K = GF(p, k)
        q = K.q
        comps = singer_target(K)
        need(len(comps) == q + 1 and all(det(K, A) for A in comps), f"q={q}: q+1 invertible components")
        P = points(K)
        # each input line is sent onto every line exactly once
        for t in P:
            need(sorted(line(K, mv(K, A, t)) for A in comps) == sorted(P), f"q={q}: images of t={t} cover P^1")
        # hence no common pivot: every (phi, t) is killed by some component
        for phi in P:
            for t in P:
                need(any(K.add(K.mul(phi[0], v[0]), K.mul(phi[1], v[1])) == 0 for v in (mv(K, A, t) for A in comps)),
                     f"q={q}: common pivot at phi={phi}, t={t}")
        # #4334's three-factor word, every component
        need(all(three_factor_word(K, A) == A for A in comps), f"q={q}: three-factor word")
        # delta = 2: min over free T of dim((M T - I) K^2) on the stacked components
        G = gl2(K)
        need(min(rank_stack(K, [row for A in comps for row in ((lambda X: ((K.sub(X[0][0], 1), X[0][1]), (X[1][0], K.sub(X[1][1], 1))))(mm(K, A, T)))])
                 for T in G) == 2, f"q={q}: delta = 2")
        # the other side of the threshold: k = q random invertible components always share a pivot
        for _ in range(300):
            sample = [rng.choice(G) for _ in range(q)]
            need(any(all(K.add(K.mul(phi[0], v[0]), K.mul(phi[1], v[1])) for v in (mv(K, A, t) for A in sample))
                     for phi in P for t in P), f"q={q}: k = q sample has a common pivot")
        out[str(q)] = {"components": q + 1, "gl2": len(G)}
    # direct exhaustive confirmation over F_4, without the pivot criterion: cost > 2
    K4 = GF(2, 2)
    need(not two_factor_exists(K4, singer_target(K4)), "F_4: no two-paid-factor word exists")
    need(two_factor_exists(K4, singer_target(K4)[:4]), "control: dropping one component makes two factors suffice")
    print(json.dumps({
        "status": "PASS_RIGHT_VECTOR_EXTENSION_FIELDS",
        "fields": out,
        "f4_two_factor_exhaustive": "no word",
        "new_kappa_claimed": False,
    }, indent=1))


if __name__ == "__main__":
    sys.exit(main())
