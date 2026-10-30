# Singular-D rank bound for the B-form census (BFORM4.md).  lbz(X) = min over S subset X, |S| <= 4, S pairwise
# non-orthogonal, of rank_Fp of the E8 roots of X \ S (p = 2^31 - 1, so <= the rational rank: a sound lower bound).
# It replaces the propagation bound lb(X) of the repo census in the J-conditions: in the singular case the rows
# t in Zr (alpha_t = 0) have p0(t) = 0, Zr is a pairwise non-orthogonal set inside A cap B, |Zr| <= |B| <= 4, and
# for t outside Zr p0(t) = alpha_t r_t, so rank p0(X) >= lbz(X).
# Big X (|X| >= 28): every flat V with |X \ V| <= 4 holds >= 24 ports, so V is (inside) one of the listed flats:
# rank-7 flats of type E7, D7, E6A1, A7 (normals = E8 vectors of norm 2, 4, 6, 8 with a rank-7 root complement)
# and rank-6 flats E6, D6 (complements of A2 and of A1A1); all other parabolic flats hold <= 23 lines.
# Small X: exhaustive over the non-orthogonal sets S.   Apache-2.0.
import itertools, sys
PR = (1 << 31) - 1
try:
    from setup9 import *   # full repo setup (needs networkx), as run on Kaggle by cnt104z.py / cnt9z.py
    L, v, G, frames, nbar, h, basis, cls = load('P104')
except ImportError:        # light path for the bounded verifier (no networkx): the same L and G as setup9.load
    from common2 import E8, Gmat
    from frames_data import load_frames
    F0, F1 = load_frames()
    L = [E8[i] for i in range(120) if i not in set(F0) | set(F1)]; v = len(L); G = Gmat(L)
def ivec(r): return tuple(int(2 * x) for x in r)
PV = [ivec(r) for r in L]                      # ports, doubled coordinates
E8L = [ivec(r) for r in E8]                    # 120 lines
def idot(a, b): return sum(x * y for x, y in zip(a, b))
NO = [sum(1 << s for s in range(v) if G[t][s] != 0) for t in range(v)]   # non-orth incl. self
def rank_p(vecs):
    basis = {}
    for vv in vecs:
        w = [x % PR for x in vv]
        for piv, b in basis.items():
            if w[piv]:
                f = w[piv]; w = [(x - f * y) % PR for x, y in zip(w, b)]
        for i, x in enumerate(w):
            if x:
                inv = pow(x, PR - 2, PR); w = [(y * inv) % PR for y in w]; basis[i] = w; break
        if len(basis) == 8: break
    return len(basis)
def bits(m): return [t for t in range(v) if m >> t & 1]
def mrank(m): return rank_p([PV[t] for t in bits(m)])
def build_flats():
    import itertools as it
    normals = set()
    for x in it.product(range(-2, 3), repeat=8):         # integer part (doubled coords even)
        n2 = sum(a * a for a in x)
        if 0 < n2 <= 8 and sum(x) % 2 == 0: normals.add(tuple(2 * a for a in x))
    odd = (-5, -3, -1, 1, 3, 5)
    def rec(pre, s2):
        if len(pre) == 8:
            if sum(pre) % 4 == 0: normals.add(tuple(pre))
            return
        for a in odd:
            if s2 + a * a + (7 - len(pre)) <= 32: rec(pre + [a], s2 + a * a)
    rec([], 0)
    seen = set(); out = {}
    for n in normals:
        m = tuple(-a for a in n)
        if m in seen: continue
        seen.add(n)
        rts = [r for r in E8L if idot(r, n) == 0]
        if rank_p(rts) != 7: continue
        pm = sum(1 << t for t in range(v) if idot(PV[t], n) == 0)
        out[pm] = None
    hyper = len(out)
    for a, b in it.combinations(range(120), 2):
        pm = sum(1 << t for t in range(v) if idot(PV[t], E8L[a]) == 0 and idot(PV[t], E8L[b]) == 0)
        out.setdefault(pm, None)
    fl = [(pm, mrank(pm)) for pm in out]
    return hyper, fl
HYPER, FLATS = build_flats()
BIG = [(m, r) for m, r in FLATS if bin(m).count('1') >= 24]
import numpy as np
M64 = (1 << 64) - 1
BLO = np.array([m & M64 for m, r in BIG], dtype=np.uint64); BHI = np.array([m >> 64 for m, r in BIG], dtype=np.uint64)
BRK = np.array([r for m, r in BIG])
def popc(a):
    if hasattr(np, 'bitwise_count'): return np.bitwise_count(a).astype(np.int64)
    a = a.copy(); c = np.zeros(a.shape, dtype=np.int64)
    while a.any(): c += (a & np.uint64(1)).astype(np.int64); a >>= np.uint64(1)
    return c
def outside_counts(X):
    return popc(np.uint64(X & M64) & ~BLO) + popc(np.uint64(X >> 64) & ~BHI)
lbz_cache = {}
def lbz(X):
    if X in lbz_cache: return lbz_cache[X]
    n = bin(X).count('1')
    best = mrank(X)
    if n >= 28:
        oc = outside_counts(X)
        for i in np.nonzero((oc <= 4) & (BRK < best))[0]:
            m, r = BIG[i]
            if r >= best: continue
            S = X & ~m
            if all(NO[a] >> b & 1 for a, b in itertools.combinations(bits(S), 2)): best = r
    else:
        xs = bits(X)
        for k in range(1, 5):
            for S in itertools.combinations(xs, k):
                if any(not (NO[a] >> b & 1) for a, b in itertools.combinations(S, 2)): continue
                Sm = sum(1 << t for t in S)
                r = mrank(X & ~Sm)
                if r < best: best = r
    lbz_cache[X] = best
    return best
if __name__ == '__main__':
    import random, time
    t0 = time.time()
    print('flats: hyperplane masks', HYPER, 'all', len(FLATS), 'with >= 24 ports', len(BIG), flush=True)
    from collections import Counter
    print('BIG (ports, rank) histogram', sorted(Counter((bin(m).count('1'), r) for m, r in BIG).items()), flush=True)
    from fractions import Fraction as Fq
    def kernel1(rows):
        A = [[Fq(x) for x in r] for r in rows]; piv = []; ri = 0
        for c in range(8):
            p = next((i for i in range(ri, len(A)) if A[i][c] != 0), None)
            if p is None: continue
            A[ri], A[p] = A[p], A[ri]; pv = A[ri][c]; A[ri] = [x / pv for x in A[ri]]
            for i in range(len(A)):
                if i != ri and A[i][c] != 0:
                    f = A[i][c]; A[i] = [x - f * y for x, y in zip(A[i], A[ri])]
            piv.append(c); ri += 1
        free = [c for c in range(8) if c not in piv]
        if len(free) != 1: return None
        n = [Fq(0)] * 8; n[free[0]] = Fq(1)
        for i, c in enumerate(piv): n[c] = -A[i][free[0]]
        return n
    HM = {m for m, r in FLATS[:HYPER]}
    allm = {m for m, r in FLATS}
    lc = Counter()
    for m, r in FLATS[:HYPER]:
        pass
    random.seed(11); miss = 0; tested = 0; types = Counter()
    for it_ in range(6000):
        S = random.sample(range(v), 7)
        n = kernel1([PV[t] for t in S])
        if n is None: continue
        lines = sum(1 for r in E8L if sum(a * b for a, b in zip(r, n)) == 0)
        pm = sum(1 << t for t in range(v) if sum(a * b for a, b in zip(PV[t], n)) == 0)
        types[lines] += 1
        if bin(pm).count('1') >= 24:
            tested += 1
            if pm not in allm: miss += 1; print('MISSING hyperplane', lines, bin(pm).count('1'), flush=True)
    print('random port hyperplanes: E8-line counts', sorted(types.items()), 'with >= 24 ports', tested, 'missing', miss, flush=True)
    assert miss == 0
    # self-test: big X vs exhaustive on random X of size 28..34 built near flats
    random.seed(7); bad = 0
    for i in range(40):
        m, r = random.choice(BIG)
        inside = random.sample(bits(m), min(bin(m).count('1'), random.randint(24, 30)))
        out = [t for t in range(v) if not m >> t & 1]
        k = random.randint(0, 4); extra = []
        for t in random.sample(out, len(out)):
            if len(extra) < k and all(NO[t] >> s & 1 for s in extra): extra.append(t)
        X = sum(1 << t for t in inside + extra)
        fast = lbz(X); lbz_cache.pop(X)
        xs = bits(X); best = mrank(X)
        for kk in range(1, 5):
            for S in itertools.combinations(xs, kk):
                if any(not (NO[a] >> b & 1) for a, b in itertools.combinations(S, 2)): continue
                best = min(best, mrank(X & ~sum(1 << t for t in S)))
        bad += fast != best
        print('selftest', i, '|X|', len(xs), 'fast', fast, 'exhaustive', best, flush=True)
    print('SELFTEST mismatches', bad, round(time.time() - t0), 's', flush=True)
    assert bad == 0
