"""Self-contained verification of the finite facts used in the E8 hand proof of uniqueness of the length-8
P104 decoding code (see E8-PROOF.md).  Standard library only; exact arithmetic.  Apache-2.0.
V1  the 104 ports contain exactly one D8 subsystem; there are 759 frames (8 pairwise orthogonal ports).
V2  for every port t, the frame equations sum_{x in F, x non-orth t} g(x) = c (F a frame not containing t) have
    rank 41 on the 48 unknowns, and the 7-dim family g(x) = (r_x.r_t)(r_x.v), v in r_t^perp (mod 3), solves the
    homogeneous system: so the homogeneous solutions are exactly that family.
V3  for every port t, r_t and the roots r_x of the ports x for which the third line of the A2 through t, x is a port
    span F_3^8.
V4  (independent cross-check of steps 3-4) the symmetric system has only the solution N = 1 on non-orth pairs.
V5  sign-step availability in the D8 matching frame T."""
import itertools, sys, time
from fractions import Fraction as Q
T0 = time.time()
def log(*a): print('[%6.1fs]' % (time.time() - T0), *a, flush=True)
log('START verify_e8hand')
P = [11, 19, 35, 131, 259, 13, 21, 37, 69, 133, 261, 41, 73, 265, 49, 81, 145, 273, 161, 193, 321, 385, 14, 22, 38, 70, 134, 262, 26, 74, 138, 50, 146, 274, 98, 290, 194, 322, 386, 28, 44, 140, 268, 84, 148, 276, 100, 164, 292, 196, 324, 388, 56, 88, 152, 280, 168, 296, 200, 328, 392, 112, 176, 304, 208, 336, 400, 224, 352, 416, 508, 506, 502, 494, 478, 446, 382, 254, 505, 501, 493, 477, 445, 381, 253, 499, 475, 443, 379, 251, 487, 471, 439, 375, 247, 463, 431, 367, 239, 415, 351, 223, 319, 191]
LINES = [q for q in range(512) if bin(q).count('1') in (3, 7)]
def root(q):
    c = [(q >> k) & 1 for k in range(9)]
    if sum(c) == 7:
        i, j = [k for k in range(9) if not c[k]]; r = [Q(0)] * 9; r[i] = Q(1); r[j] = Q(-1); return tuple(r)
    return tuple(Q(2, 3) if c[k] else Q(-1, 3) for k in range(9))
R = {q: root(q) for q in LINES}
def ip(a, b): return sum(x * y for x, y in zip(R[a], R[b]))
PS = set(P)
assert len(P) == 104 and PS <= set(LINES)
assert all((ip(a, b) == 0) == (bin(a & b).count('1') % 2 == 1) for a in P for b in P if a != b), 'conflict = orthogonality'
def frames(pool):
    out = []
    def rec(cur, cand):
        if len(cur) == 8: out.append(tuple(cur)); return
        for i, q in enumerate(cand): rec(cur + [q], [x for x in cand[i + 1:] if ip(q, x) == 0])
    rec([], list(pool)); return out
FR = frames(P); log('V1 frames', len(FR)); assert len(FR) == 759
# ---- D8: find it via a frame and a partition of its 8 lines into 4 pairs whose unions are blocks
def frame_view(T):
    v = {}
    for q in LINES:
        if q in T: continue
        c = [ip(q, t) for t in T]; B = tuple(i for i in range(8) if c[i] != 0); assert len(B) == 4
        v[q] = B
    return v
def parts(rest):
    if not rest: yield []; return
    a = rest[0]
    for b in rest[1:]:
        for p in parts([x for x in rest if x not in (a, b)]): yield [(a, b)] + p
D8s = set(); D8T = None
for T in FR:
    v = frame_view(T); blocks = {}
    for q, B in v.items(): blocks.setdefault(B, []).append(q)
    for pt in parts(list(range(8))):
        if all(tuple(sorted(p + q)) in blocks for p, q in itertools.combinations(pt, 2)):
            L = set(T)
            for p, q in itertools.combinations(pt, 2): L |= set(blocks[tuple(sorted(p + q))])
            if L <= PS: D8s.add(frozenset(L)); D8T = D8T or (T, pt)
log('V1 D8 subsystems inside the ports', len(D8s)); assert len(D8s) == 1
D8 = next(iter(D8s))
# orthonormal D8 axes u_1..u_8: vectors (r_x +- r_y)/2 of orthogonal D8 pairs occurring 7 times
cnt = {}
for x, y in itertools.combinations(sorted(D8), 2):
    if ip(x, y) == 0:
        for sg in (1, -1):
            w = tuple((a + sg * b) / 2 for a, b in zip(R[x], R[y]))
            if w[next(i for i in range(9) if w[i] != 0)] < 0: w = tuple(-c for c in w)
            cnt[w] = cnt.get(w, 0) + 1
U = [w for w, c in cnt.items() if c == 7]; assert len(U) == 8
def dotv(a, b): return sum(x * y for x, y in zip(a, b))
assert all(dotv(U[i], U[j]) == (1 if i == j else 0) for i in range(8) for j in range(8))
def coords(q): return [dotv(R[q], u) for u in U]
def red(q):  # E8 (x) Z_(3) = Z_(3)^8 in D8 coordinates; 1/2 = 2 mod 3
    return tuple(int(c * 2) * 2 % 3 if c.denominator == 2 else int(c) % 3 for c in coords(q))
RD = {q: red(q) for q in LINES}
def d3(a, b): return sum(x * y for x, y in zip(a, b)) % 3
assert all((d3(RD[a], RD[b]) == 0) == (ip(a, b) == 0) for a in LINES for b in LINES if a != b)
assert all(d3(RD[q], RD[q]) == 2 for q in LINES)
miss = sorted(q for q in LINES if q not in PS)
def sv(q):
    s = ['+' if c > 0 else '-' for c in coords(q)]
    return ''.join(s) if s[0] == '+' else ''.join('-' if c == '+' else '+' for c in s)
log('V1 missing lines (all half-spin, sign vectors in D8 axes):', sorted(sv(q) for q in miss))
assert not (set(miss) & D8)
def rref(rows, n):
    rows = [list(r) for r in rows]; k = 0; piv = []
    for c in range(n):
        p = next((i for i in range(k, len(rows)) if rows[i][c] % 3), None)
        if p is None: continue
        rows[k], rows[p] = rows[p], rows[k]; inv = rows[k][c] % 3
        rows[k] = [(x * inv) % 3 for x in rows[k]]
        for i in range(len(rows)):
            if i != k and rows[i][c] % 3:
                f = rows[i][c]; rows[i] = [(x - f * y) % 3 for x, y in zip(rows[i], rows[k])]
        piv.append(c); k += 1
    return rows[:k], piv
def third(t, x):
    s = 1 if ip(t, x) > 0 else -1
    v = tuple(a - s * b for a, b in zip(R[t], R[x]))
    return next(q for q in LINES if R[q] == v or R[q] == tuple(-c for c in v))
KER = {}; NB = {}; ok2 = ok3 = True
for t in P:
    N = [x for x in P if x != t and ip(t, x) != 0]; idx = {x: i for i, x in enumerate(N)}; NB[t] = idx
    rows = []
    for F in FR:
        if t in F: continue
        r = [0] * 48
        for x in F:
            if x in idx: r[idx[x]] = 1
        assert sum(r) == 4; rows.append(r)
    red_, piv = rref(rows, 48)
    # family: basis of r_t^perp mod 3, g_v(x) = (r_x.r_t)(r_x.v)
    perp = [v for v in itertools.product(range(3), repeat=8) if d3(v, RD[t]) == 0]
    fam = []
    for v in perp:
        g = [d3(RD[x], RD[t]) * d3(RD[x], v) % 3 for x in N]
        if rref(fam + [g], 48)[1].__len__() > len(fam): fam.append(g)
        if len(fam) == 7: break
    sol = all(sum(a * b for a, b in zip(r, g)) % 3 == 0 for r in rows for g in fam)
    good = len(piv) == 41 and len(fam) == 7 and sol
    ok2 &= good
    A2 = [x for x in N if third(t, x) in PS]
    rk3 = len(rref([RD[t]] + [RD[x] for x in A2], 8)[1]); ok3 &= rk3 == 8
    # store kernel basis for V4
    free = [c for c in range(48) if c not in piv]; K = []
    for f in free:
        v = [0] * 48; v[f] = 1
        for r, c in zip(red_, piv): v[c] = (-r[f]) % 3
        K.append(v)
    KER[t] = K
    log('t=%d frames-not-containing-t %d rank %d family-dim %d family-solves %s | A2-completable %d span %d'
        % (t, len(rows), len(piv), len(fam), sol, len(A2), rk3))
log('V2 per-port linear lemma holds for all 104 ports:', ok2); log('V3 A2 span holds for all 104 ports:', ok3)
var = {}
for t in P:
    for k in range(7): var[t, k] = len(var)
eqs = []
for t in P:
    for x in NB[t]:
        if x < t: continue
        r = [0] * len(var)
        for k, v in enumerate(KER[t]): r[var[t, k]] = (r[var[t, k]] + v[NB[t][x]]) % 3
        for k, v in enumerate(KER[x]): r[var[x, k]] = (r[var[x, k]] - v[NB[x][t]]) % 3
        eqs.append(r)
rk4 = len(rref(eqs, len(var))[1]); log('V4 symmetric system unknowns', len(var), 'rank', rk4, 'only N=1:', rk4 == len(var))
# V5: in the D8 matching frame T every block has >= 1 ports, and for every pair {a,b} of T, every block through it
# and every sign sigma there is a port with sigma_ab = sigma
T, pt = D8T; v = frame_view(T); ok5 = True
for B in set(v.values()):
    ok5 &= sum(1 for q, b in v.items() if b == B and q in PS) >= 1
for a, b in itertools.combinations(range(8), 2):
    for B in set(v.values()):
        if a in B and b in B:
            sig = set()
            for q, bb in v.items():
                if bb == B and q in PS:
                    sig.add((ip(q, T[a]) * ip(q, T[b])) > 0)
            ok5 &= sig == {True, False}
log('V5 sign-step availability in the D8 frame:', ok5)
ALL = ok2 and ok3 and rk4 == len(var) and ok5
log('RESULT', 'PASS' if ALL else 'FAIL')
sys.exit(0 if ALL else 1)
