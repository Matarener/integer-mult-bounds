"""Finite facts for the B-form floor (BFORM2.md), exact integer arithmetic, characteristic 0.  Apache-2.0.
S0  label caps: max ports in a d-dim subspace of F_2^9 is f(7) = 36, f(8) = 60.
S1  hyperplanes holding >= 38 E8 lines are exactly the E7 hyperplanes (normal = root, 63 lines) and the D7
    hyperplanes (normal = norm-4 vector, 42 lines); every other hyperplane holds <= 37 lines (E6+A1), by the
    classification of E8 hyperplane flats (maximal parabolics).  Checked here: the E7/D7 hyperplanes hold
    <= 55 ports, so |N(y)| >= 49 for every real y != 0.
S2' Span input: for every label z != 0 (O(z) = ports with label.z = 1, |O(z)| >= 44) and every E7/D7
    hyperplane H, the number of ports of O(z) outside H is 0 or >= 5, except exactly z = l_p, H = r_p^perp, O(z)\H = {p}.
S3  biclique: if A x B is pairwise non-orthogonal and |A| >= 13 then |B| <= 4 (bicliques.py)."""
import itertools, time
T0 = time.time()
def log(*a): print('[%7.1fs]' % (time.time() - T0), *a, flush=True)
log('START spanlemma')
P = [11, 19, 35, 131, 259, 13, 21, 37, 69, 133, 261, 41, 73, 265, 49, 81, 145, 273, 161, 193, 321, 385, 14, 22, 38, 70, 134, 262, 26, 74, 138, 50, 146, 274, 98, 290, 194, 322, 386, 28, 44, 140, 268, 84, 148, 276, 100, 164, 292, 196, 324, 388, 56, 88, 152, 280, 168, 296, 200, 328, 392, 112, 176, 304, 208, 336, 400, 224, 352, 416, 508, 506, 502, 494, 478, 446, 382, 254, 505, 501, 493, 477, 445, 381, 253, 499, 475, 443, 379, 251, 487, 471, 439, 375, 247, 463, 431, 367, 239, 415, 351, 223, 319, 191]
LINES = [q for q in range(512) if bin(q).count('1') in (3, 7)]
def root(q):  # 3 x root, A8 coordinates
    c = [(q >> k) & 1 for k in range(9)]
    if sum(c) == 7:
        i, j = [k for k in range(9) if not c[k]]; r = [0] * 9; r[i] = 3; r[j] = -3; return tuple(r)
    return tuple(2 if c[k] else -1 for k in range(9))
RT = {q: root(q) for q in LINES}
def dot(a, b): return sum(x * y for x, y in zip(a, b))
assert all(dot(RT[q], RT[q]) == 18 for q in LINES)
# S0
def span(vs):
    s = {0}
    for v in vs:
        if v not in s: s |= {x ^ v for x in s}
    return s
def ldot(a, b): return bin(a & b).count('1') & 1
f = {}
for d in (7, 8):
    best = 0
    # subspaces of dim d = z-perp intersections: dim 8 = z^perp, dim 7 = <z1,z2>^perp
    if d == 8:
        for z in range(1, 512): best = max(best, sum(1 for q in P if ldot(q, z) == 0))
    else:
        for z1 in range(1, 512):
            for z2 in range(z1 + 1, 512):
                best = max(best, sum(1 for q in P if ldot(q, z1) == 0 and ldot(q, z2) == 0))
    f[d] = best
log('S0 label caps f(7), f(8) =', f[7], f[8]); assert f[7] == 36 and f[8] == 60
# S1 normals
E7n = [RT[q] for q in LINES]
D7 = set()
for a, b in itertools.combinations(LINES, 2):
    if dot(RT[a], RT[b]) == 0:
        for s in (1, -1):
            v = tuple(x + s * y for x, y in zip(RT[a], RT[b]))
            if v < tuple(-x for x in v): v = tuple(-x for x in v)
            D7.add(v)
D7n = sorted(D7)
log('E7 normals', len(E7n), 'D7 normals', len(D7n)); assert len(E7n) == 120 and len(D7n) == 1080
assert all(dot(v, v) == 36 for v in D7n)
inH = lambda n, q: dot(n, RT[q]) == 0
lines7 = Counter = None
c7 = {sum(1 for q in LINES if inH(n, q)) for n in E7n}; cd7 = {sum(1 for q in LINES if inH(n, q)) for n in D7n}
log('E8 lines per E7 hyperplane', c7, 'per D7 hyperplane', cd7); assert c7 == {63} and cd7 == {42}
mp = max(sum(1 for q in P if inH(n, q)) for n in E7n + D7n)
log('S1 max ports in an E7/D7 hyperplane', mp, '-> min |N(y)| =', 104 - mp); assert mp == 55
# S2' (corrected span input): |O(z) \ H| is 0 or >= 5, except exactly the 104 pairs (z = label of a port p,
# H = r_p^perp, an E7 hyperplane) where O(z) \ H = {p}.  (The uncorrected S2 FAILS on precisely these pairs.)
NORM = E7n + D7n
HP = [frozenset(q for q in P if inH(n, q)) for n in NORM]
bad = []; hist = {}
for z in range(1, 512):
    O = [q for q in P if ldot(q, z) == 1]
    assert len(O) >= 44
    for hi, H in enumerate(HP):
        out = [q for q in O if q not in H]
        k = len(out)
        if k <= 8: hist[k] = hist.get(k, 0) + 1
        if 1 <= k <= 4: bad.append((z, hi, tuple(out)))
log("S2 histogram of |O(z) \\ H| for small values (0..8):", {k: v for k, v in sorted(hist.items()) if k <= 8})
log("S2 exceptional pairs (1 <= |O(z) \\ H| <= 4):", len(bad))
ok = len(bad) == len(P)
for z, hi, out in bad:
    ok &= z in P and out == (z,) and hi < 120 and NORM[hi] == RT[z]
log("S2' exceptions are exactly (z = port label p, H = r_p^perp, O(z) \\ H = {p}) for all 104 ports:", ok)
assert ok
log('PASS')
log('DONE')
