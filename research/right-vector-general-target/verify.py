"""Exhaustive check of the right-vector general-target formula on small algebras.

Alphabet (research/f2-right-vector-diagonal-minimum, #4243): paid factors
I + u y^T with u in R^n, y in K^n; free maps GL_n(K) anywhere in a word.
For every n x n matrix M over each listed K-algebra R this script computes

  cost(M)   exact minimum number of paid factors, by breadth-first search
            over words Q S (normal form of #4243),
  delta(M)  min over T in GL_n(K) of dim_K (M T - I) K^n,

and records every target where cost != delta (cost >= delta is the
#4243 lower bound and is asserted).  It also computes the minimum with no
free map (products of factors only) and compares it with dim_K (M - I) K^n,
recording every matrix where the two differ.  Writes nothing.
"""
import hashlib
import itertools
import sys

import numpy as np


def algebra(name):
    """Return (p, r, basis_mul, one_coords) for a K-algebra with K = F_p."""
    if name == "F2":
        return 2, 1, lambda i, j: {0: 1}, [1]
    if name == "F3":
        return 3, 1, lambda i, j: {0: 1}, [1]
    if name == "F4":  # F2[w]/(w^2+w+1)
        return 2, 2, lambda i, j: {i + j: 1} if i + j < 2 else {0: 1, 1: 1}, [1, 0]
    if name == "F2[C2]":
        return 2, 2, lambda i, j: {(i + j) % 2: 1}, [1, 0]
    if name == "F2xF2":
        return 2, 2, lambda i, j: {i: 1} if i == j else {}, [1, 1]
    if name == "F3xF3":
        return 3, 2, lambda i, j: {i: 1} if i == j else {}, [1, 1]
    if name == "F2[C3]":
        return 2, 3, lambda i, j: {(i + j) % 3: 1}, [1, 0, 0]
    if name == "F2[x]/(x^3)":
        return 2, 3, lambda i, j: {i + j: 1} if i + j < 3 else {}, [1, 0, 0]
    if name == "M2(F2)":  # basis E_ab at index 2a+b, noncommutative
        def mul(i, j):
            a, b = divmod(i, 2)
            c, d = divmod(j, 2)
            return {2 * a + d: 1} if b == c else {}
        return 2, 4, mul, [1, 0, 0, 1]
    raise SystemExit("unknown algebra " + name)


class Ring:
    def __init__(self, name):
        p, r, basis_mul, one = algebra(name)
        self.name, self.p, self.r, self.q = name, p, r, p ** r
        q = self.q
        self.mul = np.zeros((q, q), dtype=np.int64)
        self.add = np.zeros((q, q), dtype=np.int64)
        for a in range(q):
            va = self.dec(a)
            for b in range(q):
                vb = self.dec(b)
                out = [0] * r
                for i in range(r):
                    for j in range(r):
                        for k, c in basis_mul(i, j).items():
                            out[k] += va[i] * vb[j] * c
                self.mul[a, b] = self.enc(out)
                self.add[a, b] = self.enc([x + y for x, y in zip(va, vb)])
        self.neg = np.array([self.enc([-x for x in self.dec(a)]) for a in range(q)])
        self.one = self.enc(one)
        self.scal = [self.enc([s * x for x in one]) for s in range(p)]
        e = self.one
        assert all(self.mul[e, a] == a == self.mul[a, e] for a in range(q))
        # associativity and K-centrality are checked, not assumed
        m = self.mul
        trip = m[m[:, :, None], np.arange(q)[None, None, :]]
        trip2 = m[np.arange(q)[:, None, None], m[None, :, :]]
        assert (trip == trip2).all(), "not associative"
        for s in self.scal:
            assert (m[s, :] == m[:, s]).all(), "K not central"

    def dec(self, x):
        return [(x // self.p ** k) % self.p for k in range(self.r)]

    def enc(self, v):
        return sum((v[k] % self.p) * self.p ** k for k in range(self.r))


def rank_mod_p(V, p):
    """Row rank over F_p of each matrix V[s] (shape S x rows x cols)."""
    V = V.copy() % p
    S, rows, cols = V.shape
    rk = np.zeros(S, dtype=np.int64)
    inv = np.array([pow(x, -1, p) if x else 0 for x in range(p)])
    ar = np.arange(rows)
    for c in range(cols):
        cand = (V[:, :, c] != 0) & (ar[None, :] >= rk[:, None])
        idx = np.nonzero(cand.any(1))[0]
        if len(idx) == 0:
            continue
        piv = np.argmax(cand, 1)[idx]
        top = rk[idx]
        a = V[idx, piv].copy()
        b = V[idx, top].copy()
        V[idx, top] = a
        V[idx, piv] = b
        prow = V[idx, top] * inv[V[idx, top, c]][:, None] % p
        V[idx, top] = prow
        for rr in range(rows):
            keep = rr != top
            sel = idx[keep]
            V[sel, rr] = (V[sel, rr] - V[sel, rr, c][:, None] * prow[keep]) % p
        rk[idx] += 1
    return rk


def gl_n(p, n):
    out = []
    for t in itertools.product(range(p), repeat=n * n):
        M = np.array(t).reshape(n, n)
        if rank_mod_p(M[None], p)[0] == n:
            out.append(t)
    return out


def run(name, n):
    R = Ring(name)
    p, r, q = R.p, R.r, R.q
    N = n * n
    size = q ** N
    pw = q ** np.arange(N)

    def matmul(A, B):
        C = np.zeros_like(A)
        for i in range(n):
            for j in range(n):
                acc = np.zeros(A.shape[0], dtype=np.int64)
                for k in range(n):
                    acc = R.add[acc, R.mul[A[:, i * n + k], B[:, k * n + j]]]
                C[:, i * n + j] = acc
        return C

    ident = np.array([[R.one if i == j else 0 for i in range(n) for j in range(n)]], dtype=np.int64)
    GL = np.array([[R.scal[x] for x in t] for t in gl_n(p, n)], dtype=np.int64)
    ys = [y for y in itertools.product(range(p), repeat=n)
          if any(y) and y[next(i for i in range(n) if y[i])] == 1]
    facs = []
    for u in itertools.product(range(q), repeat=n):
        for y in ys:
            facs.append([R.add[ident[0, i * n + j], R.mul[u[i], R.scal[y[j]]]]
                         for i in range(n) for j in range(n)])
    facs = np.unique(np.array(facs, dtype=np.int64), axis=0)

    def bfs(start):
        level = np.full(size, -1, dtype=np.int64)
        front = start
        level[front @ pw] = 0
        L = 0
        while len(front):
            L += 1
            new = []
            for F in facs:
                P = matmul(np.broadcast_to(F, front.shape).copy(), front)
                c = P @ pw
                fresh = level[c] == -1
                if fresh.any():
                    level[c[fresh]] = L
                    new.append(P[fresh])
            if not new:
                break
            front = np.unique(np.concatenate(new), axis=0)
        return level

    allM = np.stack([(np.arange(size) // q ** k) % q for k in range(N)], axis=1)

    def image_dim(T):
        D = R.add[matmul(allM, np.broadcast_to(T, allM.shape).copy()), R.neg[ident[0]][None, :]]
        V = np.zeros((size, n, n * r), dtype=np.int64)
        for j in range(n):
            for i in range(n):
                for k in range(r):
                    V[:, j, i * r + k] = (D[:, i * n + j] // p ** k) % p
        return rank_mod_p(V, p)

    cost = bfs(GL)
    delta = np.min(np.stack([image_dim(T) for T in GL]), axis=0)
    assert (cost >= 0).all(), "unreachable target"
    assert (cost >= delta).all(), "lower bound of #4243 violated"
    fails = np.nonzero(cost != delta)[0]
    bare = bfs(ident)
    raw = image_dim(ident[0])
    assert (bare >= 0).all()
    assert (bare >= raw).all(), "column bound violated"
    gaps = np.nonzero(bare != raw)[0]
    witnesses = [[R.dec(int(x)) for x in allM[g]] for g in gaps]
    return {
        "ring": name, "n": n, "targets": size, "factors": len(facs), "free_maps": len(GL),
        "max_cost": int(cost.max()),
        "cost_hist": np.bincount(cost).tolist(),
        "formula_failures": len(fails),
        "failure_pairs": sorted(set((int(cost[g]), int(delta[g])) for g in fails)),
        "failure_examples": [[R.dec(int(x)) for x in allM[g]] for g in fails[:2]],
        "no_free_map_gaps": len(gaps),
        "gap_examples": witnesses[:2],
        "gap_bare_cost": sorted(set(int(bare[g]) for g in gaps)),
        "gap_raw_dim": sorted(set(int(raw[g]) for g in gaps)),
    }


CASES = [("F2", 2), ("F3", 2), ("F2", 3), ("F4", 2), ("F2[C2]", 2), ("F2xF2", 2),
         ("F3xF3", 2), ("F2[C3]", 2), ("F2[x]/(x^3)", 2), ("M2(F2)", 2), ("F2[C2]", 3)]
EXPECTED_GAPS = {("F2xF2", 2): 2, ("F2[C3]", 2): 6, ("M2(F2)", 2): 684}
LARGE = ("F2[C2]", 3)
EXPECTED_FAILURES = {("M2(F2)", 2): 72}


def m2_permutation_witness():
    """Independent check in M_4(F_2) = M_2(M_2(F_2)).

    The target [[E11, E01], [E10, E00]] is the 4x4 transposition of
    coordinates 0 and 3.  A factor is I + U (y^T kron I_2) with U a 4x2
    binary matrix and y in F_2^2; a free map is S kron I_2.  Check that no
    word with two factors reaches it, that one with three does, and that
    T = I already gives image dimension 2.
    """
    P = np.eye(4, dtype=np.int64)[[3, 1, 2, 0]]
    I2 = np.eye(2, dtype=np.int64)
    ys = [np.array(y) for y in ((1, 0), (0, 1), (1, 1))]
    Us = [np.array(b, dtype=np.int64).reshape(4, 2) for b in itertools.product((0, 1), repeat=8)]
    F = np.unique(np.array([(np.eye(4, dtype=np.int64) + U @ np.kron(y[None, :], I2)) % 2
                            for U in Us for y in ys]), axis=0)
    Ss = [np.kron(np.array(t).reshape(2, 2), I2) for t in gl_n(2, 2)]
    pw = 2 ** np.arange(16)
    two = (np.einsum("aij,bjk->abik", F, F) % 2).reshape(-1, 16)
    two_codes = set(np.unique(two @ pw).tolist())
    hits2 = [S for S in Ss if int(((P @ S) % 2).reshape(16) @ pw) in two_codes]
    assert not hits2, "two factors suffice"
    three = set()
    for A in F:
        three.update(np.unique(((np.einsum("ij,bjk->bik", A, two.reshape(-1, 4, 4))) % 2).reshape(-1, 16) @ pw).tolist())
    assert any(int(((P @ S) % 2).reshape(16) @ pw) in three for S in Ss), "three factors fail"
    # image of x -> (P - I)(x kron I_2): span of the two 4x2 blocks, rank 2
    cols = np.stack([((P - np.eye(4, dtype=np.int64)) @ np.kron(e[:, None], I2) % 2).reshape(8)
                     for e in (np.array([1, 0]), np.array([0, 1]))])
    assert rank_mod_p(cols[None], 2)[0] == 2
    return len(F)


def main():
    stage = sys.argv[sys.argv.index("--stage") + 1] if "--stage" in sys.argv else "main"
    assert stage in ("main", "large"), stage
    cases = [c for c in CASES if (c == LARGE) == (stage == "large")]
    with open(__file__, "rb") as fh:
        digest = hashlib.sha256(fh.read())
    digest.update(stage.encode())
    parts = []
    for name, n in cases:
        res = run(name, n)
        print(res, flush=True)
        assert res["formula_failures"] == EXPECTED_FAILURES.get((name, n), 0), (name, n)
        if res["formula_failures"]:
            assert res["failure_pairs"] == [(3, 2)]
        want = EXPECTED_GAPS.get((name, n), 0)
        assert res["no_free_map_gaps"] == want, (name, n, res["no_free_map_gaps"])
        if want and name != "M2(F2)":
            assert res["gap_bare_cost"] == [3] and res["gap_raw_dim"] == [2]
        digest.update(repr(res).encode())
        parts.append(f"{name}:n{n}:{res['targets']}")
    if stage == "large":
        print("receipt", digest.hexdigest())
        print("PASS_RIGHT_VECTOR_GENERAL_TARGET_LARGE", " ".join(parts),
              "formula_failures=0 no_free_map_gaps=0 no_new_kappa")
        return 0
    nf = m2_permutation_witness()
    print("independent M_4(F_2) check: transposition (0 3) needs 3 factors, formula 2;", nf, "factors")
    digest.update(str(nf).encode())
    print("receipt", digest.hexdigest())
    print("PASS_RIGHT_VECTOR_GENERAL_TARGET", " ".join(parts),
          "formula_failures=M2(F2):72 no_free_map_gaps=F2xF2:2,F2[C3]:6,M2(F2):684 no_new_kappa")
    return 0


if __name__ == "__main__":
    sys.exit(main())
