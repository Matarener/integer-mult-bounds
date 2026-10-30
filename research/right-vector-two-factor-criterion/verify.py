"""Exact two-factor criterion for right-vector targets at n = 2.

Alphabet (research/f2-right-vector-diagonal-minimum, #4243, #4265): paid
factors I + u y^T with u in R^2, y in K^2; free maps GL_2(K) anywhere.
PROOF.md shows, for every K-algebra R,

  cost(M) <= 2  iff  some G, H in GL_2(K) give N = G M H with N12 in N11 R,
  cost(M) <= 1  iff  delta(M) <= 1, and then cost(M) = delta(M).

For local R, every target with a unit entry then costs delta(M).
Stage "main" compares this criterion with the exact minimum found by
breadth-first search on every target over five algebras (cost 99 means
unreachable), checks the local statement, checks the rank form of the
criterion over M2(F2), and lifts a 3-factor M2(F2) target to F2[S3].
Stage "s3" counts criterion failures on all 2^24 targets over F2[S3].
Writes nothing.
"""
import hashlib
import itertools
import sys

import numpy as np


def algebra(name):
    """Return (p, r, basis_mul, one_coords) for a K-algebra with K = F_p."""
    if name == "F2xF2":
        return 2, 2, lambda i, j: {i: 1} if i == j else {}, [1, 1]
    if name == "F2[C3]":
        return 2, 3, lambda i, j: {(i + j) % 3: 1}, [1, 0, 0]
    if name == "F2[x,y]/(x,y)^2":  # basis 1, x, y; commutative and local
        return 2, 3, lambda i, j: {i + j: 1} if i == 0 or j == 0 else {}, [1, 0, 0]
    if name == "UT2(F2)":  # basis E00, E01, E11 at indices 0, 1, 2
        pos = [(0, 0), (0, 1), (1, 1)]

        def mul(i, j):
            (a, b), (c, d) = pos[i], pos[j]
            return {pos.index((a, d)): 1} if b == c else {}
        return 2, 3, mul, [1, 0, 1]
    if name == "M2(F2)":  # basis E_ab at index 2a+b
        def mul(i, j):
            a, b = divmod(i, 2)
            c, d = divmod(j, 2)
            return {2 * a + d: 1} if b == c else {}
        return 2, 4, mul, [1, 0, 0, 1]
    if name == "F2[S3]":  # basis = S3 as permutation tuples, identity first
        g = sorted(itertools.permutations(range(3)))

        def mul(i, j):
            return {g.index(tuple(g[i][g[j][k]] for k in range(3))): 1}
        return 2, 6, mul, [1, 0, 0, 0, 0, 0]
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
        m = self.mul
        assert all(m[self.one, a] == a == m[a, self.one] for a in range(q))
        trip = m[m[:, :, None], np.arange(q)[None, None, :]]
        trip2 = m[np.arange(q)[:, None, None], m[None, :, :]]
        assert (trip == trip2).all(), "not associative"
        for s in self.scal:
            assert (m[s, :] == m[:, s]).all(), "K not central"
        # in_ideal[a, z]: z lies in the right ideal a R = span_K {a b_k}
        basis = [self.enc([int(i == k) for i in range(r)]) for k in range(r)]
        span = np.array([[self.dec(int(m[a, b])) for b in basis] for a in range(q)])
        base = rank_mod_p(span, p)
        ext = np.concatenate([np.repeat(span[:, None], q, 1),
                              np.array([self.dec(z) for z in range(q)])[None, :, None, :]
                              .repeat(q, 0)], axis=2).reshape(q * q, r + 1, r)
        self.in_ideal = (rank_mod_p(ext, p).reshape(q, q) == base[:, None])

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


def gl2(p):
    return [t for t in itertools.product(range(p), repeat=4)
            if (t[0] * t[3] - t[1] * t[2]) % p]


def matmul(R, A, B):
    """Row-wise product of 2x2 matrices over R stored as (S, 4) code arrays."""
    C = np.zeros(np.broadcast_shapes(A.shape, B.shape), dtype=np.int64)
    for i in range(2):
        for j in range(2):
            C[:, 2 * i + j] = R.add[R.mul[A[:, 2 * i], B[:, j]], R.mul[A[:, 2 * i + 1], B[:, 2 + j]]]
    return C


def lift(R, t):
    return np.array([[R.scal[x] for x in t]], dtype=np.int64)


def criterion(R, M):
    """True where some G, H in GL_2(K) give N = G M H with N12 in N11 R."""
    ok = np.zeros(len(M), dtype=bool)
    gls = [lift(R, t) for t in gl2(R.p)]
    for G in gls:
        GM = matmul(R, G, M)
        for H in gls:
            N = matmul(R, GM, H)
            ok |= R.in_ideal[N[:, 0], N[:, 1]]
    return ok


def all_targets(q):
    size = q ** 4
    return np.stack([(np.arange(size) // q ** k) % q for k in range(4)], axis=1)


UNREACHABLE = 99
LOCAL = ("F2[x,y]/(x,y)^2",)


def exact_costs(R, allM):
    """Exact minimum number of paid factors by BFS over words Q S (#4243)."""
    q, p = R.q, R.p
    pw = q ** np.arange(4)
    ident = np.array([R.one, 0, 0, R.one])
    ys = [(1, 0)] + [(x, 1) for x in range(p)]
    facs = np.unique(np.array([[R.add[ident[2 * i + j], R.mul[u[i], R.scal[y[j]]]]
                                for i in range(2) for j in range(2)]
                               for u in itertools.product(range(q), repeat=2) for y in ys]), axis=0)
    level = np.full(len(allM), -1, dtype=np.int64)
    front = np.concatenate([lift(R, t) for t in gl2(p)])
    level[front @ pw] = 0
    L = 0
    while len(front):
        L += 1
        new = []
        for F in facs:
            P = matmul(R, F[None], front)
            c = P @ pw
            fresh = level[c] == -1
            if fresh.any():
                level[c[fresh]] = L
                new.append(P[fresh])
        if not new:
            break
        front = np.unique(np.concatenate(new), axis=0)
    level[level < 0] = UNREACHABLE
    return level


def delta(R, allM):
    """min over T in GL_2(K) of dim_K (M T - I) K^2."""
    p, r = R.p, R.r
    best = np.full(len(allM), 9, dtype=np.int64)
    ident = np.array([R.one, 0, 0, R.one])
    for t in gl2(p):
        D = R.add[matmul(R, allM, lift(R, t)), R.neg[ident][None, :]]
        V = np.zeros((len(allM), 2, 2 * r), dtype=np.int64)
        for j in range(2):
            for i in range(2):
                for k in range(r):
                    V[:, j, i * r + k] = (D[:, 2 * i + j] // p ** k) % p
        best = np.minimum(best, rank_mod_p(V, p))
    return best


def compare(name):
    R = Ring(name)
    allM = all_targets(R.q)
    cost = exact_costs(R, allM)
    dlt = delta(R, allM)
    crit = criterion(R, allM)
    assert (cost >= dlt).all(), "lower bound of #4243 violated"
    assert ((cost <= 2) == crit).all(), "two-factor criterion disagrees with search"
    assert ((cost <= 1) == (dlt <= 1)).all() and (cost[dlt <= 1] == dlt[dlt <= 1]).all()
    unit = R.in_ideal[:, R.one]
    if name in LOCAL:  # the non-units form an ideal J
        nonunit = np.nonzero(~unit)[0]
        assert np.isin(R.add[nonunit[:, None], nonunit[None, :]], nonunit).all()
        assert np.isin(R.mul[nonunit[:, None], np.arange(R.q)[None, :]], nonunit).all()
        has_unit = unit[allM].any(1)
        assert (cost[has_unit] == dlt[has_unit]).all(), "local theorem violated"
        assert not (~crit & has_unit).any()
    return R, allM, cost, crit, {"ring": name, "targets": len(allM),
                                 "cost_hist": np.bincount(cost[cost < UNREACHABLE]).tolist(),
                                 "unreachable": int((cost == UNREACHABLE).sum()),
                                 "criterion_failures": int((~crit).sum()),
                                 "delta_gaps": int((cost != dlt).sum())}


def m2_rank_form(R, allM, crit):
    """Over M2(F2): criterion iff some phi, t != 0 give rank (phi x I) M = rank (phi x I) M (t x I)."""
    bits = ((allM[:, :, None] >> np.arange(4)[None, None, :]) & 1).reshape(-1, 2, 2, 2, 2)
    big = bits.transpose(0, 1, 3, 2, 4).reshape(-1, 4, 4)  # [2i+a, 2j+b] = bit 2a+b of entry (i,j)
    vecs = [np.array(v) for v in ((1, 0), (0, 1), (1, 1))]
    I2 = np.eye(2, dtype=np.int64)
    ok = np.zeros(len(allM), dtype=bool)
    for phi in vecs:
        top = np.einsum("ij,sjk->sik", np.kron(phi[None, :], I2), big) % 2
        rk = rank_mod_p(top, 2)
        for t in vecs:
            ok |= rank_mod_p(top @ np.kron(t[:, None], I2) % 2, 2) == rk
    assert (ok == crit).all(), "rank form disagrees"


def s3_rep():
    """Unital K-algebra map rho: F2[S3] -> M2(F2) from S3 = GL_2(F_2) on nonzero vectors."""
    S, M = Ring("F2[S3]"), Ring("M2(F2)")
    g = sorted(itertools.permutations(range(3)))
    v = [(1, 0), (0, 1), (1, 1)]
    mats = [M.enc([v[s[0]][0], v[s[1]][0], v[s[0]][1], v[s[1]][1]]) for s in g]
    rho = np.array([0] * S.q, dtype=np.int64)
    for x in range(S.q):
        acc = 0
        for k, c in enumerate(S.dec(x)):
            if c:
                acc = M.add[acc, mats[k]]
        rho[x] = acc
    assert rho[S.one] == M.one
    assert (rho[S.mul] == M.mul[rho[:, None], rho[None, :]]).all(), "rho not multiplicative"
    assert (rho[S.add] == M.add[rho[:, None], rho[None, :]]).all()
    assert len(set(rho.tolist())) == M.q, "rho not surjective"
    return S, M, rho


def s3_witness(M, cost_m2):
    """Lift a 3-factor M2(F2) word to F2[S3]; its image costs 3, so it costs 3."""
    S, Mr, rho = s3_rep()
    section = {int(rho[x]): x for x in range(S.q - 1, -1, -1)}
    pw = Mr.q ** np.arange(4)
    target = np.array([Mr.enc([0, 0, 0, 1]), Mr.enc([0, 1, 0, 0]),
                       Mr.enc([0, 0, 1, 0]), Mr.enc([1, 0, 0, 0])])  # [[E11, E01], [E10, E00]]
    assert cost_m2[target @ pw] == 3
    # find a 3-factor word over M2(F2) ending in a free map that hits the target
    ys = [(1, 0), (0, 1), (1, 1)]
    ident_m = np.array([Mr.one, 0, 0, Mr.one])
    words = [(u, y) for u in itertools.product(range(Mr.q), repeat=2) for y in ys]

    def fac(R, u, y):
        return np.array([[R.add[[R.one, 0, 0, R.one][2 * i + j], R.mul[u[i], R.scal[y[j]]]]
                          for i in range(2) for j in range(2)]])
    gls = gl2(2)
    want = {}
    for t in gls:  # target T^{-1}
        X = target[None]
        for s in gls:
            if (matmul(Mr, lift(Mr, t), lift(Mr, s)) == ident_m).all():
                want[int(matmul(Mr, X, lift(Mr, s))[0] @ pw)] = t
    found = None
    for w1 in words:
        A = fac(Mr, *w1)
        for w2 in words:
            AB = matmul(Mr, A, fac(Mr, *w2))
            for w3 in words:
                code = int(matmul(Mr, AB, fac(Mr, *w3))[0] @ pw)
                if code in want:
                    found = (w1, w2, w3, want[code])
                    break
            if found:
                break
        if found:
            break
    assert found, "no three-factor word"
    *ws, t = found
    W = lift(S, (1, 0, 0, 1))
    for u, y in ws:
        W = matmul(S, W, fac(S, (section[u[0]], section[u[1]]), y))
    W = matmul(S, W, lift(S, t))
    assert (rho[W[0]] == target).all()
    assert not criterion(S, W)[0], "lifted witness passes the criterion"
    return [S.dec(int(x)) for x in W[0]], [ws, t]


def s3_count():
    S, _, rho = s3_rep()
    q = S.q
    fails = 0
    proj_fails = 0
    m2 = Ring("M2(F2)")
    m2_crit = criterion(m2, all_targets(m2.q))
    chunk = q ** 3
    M = np.zeros((chunk, 4), dtype=np.int64)
    for k in range(3):
        M[:, k] = (np.arange(chunk) // q ** k) % q
    for hi in range(q):
        M[:, 3] = hi
        c = criterion(S, M)
        fails += int((~c).sum())
        img = rho[M] @ (m2.q ** np.arange(4))
        proj_fails += int((~m2_crit[img]).sum())
        assert not (c & ~m2_crit[img]).any(), "projection failure without lift failure"
    return {"targets": q ** 4, "criterion_failures": fails,
            "projected_m2_failures": proj_fails}


EXPECTED = {"F2[x,y]/(x,y)^2": (4096, 12), "F2xF2": (256, 0), "F2[C3]": (4096, 0), "UT2(F2)": (4096, 12), "M2(F2)": (65536, 72)}


def main():
    stage = sys.argv[sys.argv.index("--stage") + 1] if "--stage" in sys.argv else "main"
    assert stage in ("main", "s3"), stage
    with open(__file__, "rb") as fh:
        digest = hashlib.sha256(fh.read())
    digest.update(stage.encode())
    if stage == "s3":
        res = s3_count()
        print(res, flush=True)
        assert res["criterion_failures"] == 120060
        assert res["projected_m2_failures"] == 72 * 4 ** 4  # kernel of rho has 4 elements
        digest.update(repr(res).encode())
        print("receipt", digest.hexdigest())
        print("PASS_RIGHT_VECTOR_TWO_FACTOR_S3", f"targets={res['targets']}",
              f"three_or_more={res['criterion_failures']}", "no_new_kappa")
        return 0
    parts = []
    for name in EXPECTED:
        R, allM, cost, crit, res = compare(name)
        print(res, flush=True)
        assert (res["targets"], res["criterion_failures"]) == EXPECTED[name], name
        fail_costs = sorted(set(cost[~crit].tolist()))
        assert fail_costs == ([UNREACHABLE] if name in LOCAL else [3] if res["criterion_failures"] else [])
        assert res["unreachable"] == (12 if name in LOCAL else 0)
        digest.update(repr(res).encode())
        parts.append(f"{name}:{res['targets']}:{res['criterion_failures']}")
        if name == "M2(F2)":
            m2_rank_form(R, allM, crit)
            wit, word = s3_witness(R, cost)
            print("F2[S3] witness (entries in group basis):", wit, "word:", word, flush=True)
            digest.update(repr((wit, word)).encode())
    print("receipt", digest.hexdigest())
    print("PASS_RIGHT_VECTOR_TWO_FACTOR_CRITERION", " ".join(parts),
          "m2_rank_form=ok f2s3_lift=cost3 no_new_kappa")
    return 0


if __name__ == "__main__":
    sys.exit(main())
