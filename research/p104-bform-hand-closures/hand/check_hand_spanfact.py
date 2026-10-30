#!/usr/bin/env python3
"""Exact checks of the finite facts used in HAND-SPANFACT.md (a few seconds).

Labels: ../data/p104_port_labels.json "P" (9-bit labels of the 104 ports, the repo's lab), coordinates ../data/p104_r8_d8.json.
"""
import itertools, json
from collections import Counter
from fractions import Fraction as Fr
from pathlib import Path

H = Path(__file__).parent
P = json.loads((H.parent / "data" / "p104_port_labels.json").read_text())["P"]
R = json.loads((H.parent / "data" / "p104_r8_d8.json").read_text())["R8"]
pc = lambda v: bin(v).count("1")
dot = lambda a, b: sum(x * y for x, y in zip(a, b))
roots = []
for i, j in itertools.combinations(range(8), 2):
    for a in (2, -2):
        for b in (2, -2):
            v = [0] * 8; v[i] = a; v[j] = b; roots.append(tuple(v))
for s in itertools.product((1, -1), repeat=8):
    if s.count(-1) % 2 == 0: roots.append(s)
canon = lambda v: v if next(c for c in v if c) > 0 else tuple(-c for c in v)
lines = sorted({canon(r) for r in roots})
ports = [canon(tuple(r)) for r in R]
pidx = {p: i for i, p in enumerate(ports)}
removed = [l for l in lines if l not in pidx]
ONE = (1 << 9) - 1

# (G) labels: ports have odd weight 3 or 7; the 16 missing odd labels of weight 3/7 attach to the removed lines so
#     that, with u = complement of the label (an even-weight vector), distinct lines are orthogonal iff u.u' = 0 mod 2
assert all(pc(q) in (3, 7) for q in P) and len(set(P)) == 104
miss = [q for q in range(512) if pc(q) in (3, 7) and q not in P]
assert len(miss) == 16
lab = {ports[t]: P[t] for t in range(104)}
for l in removed:
    orth = {t for t in range(104) if dot(R[t], l) == 0}
    c = [q for q in miss if {t for t in range(104) if pc(P[t] & q) % 2} == orth]
    assert len(c) == 1; lab[l] = c[0]
assert sorted(lab.values()) == sorted(q for q in range(512) if pc(q) in (3, 7))
U = {l: lab[l] ^ ONE for l in lines}
for a, b in itertools.combinations(lines, 2):
    assert (dot(a, b) == 0) == (pc(U[a] & U[b]) % 2 == 0)
print("G: labels <-> the 120 vectors of weight 2/6 in E; orthogonal <=> B(u,u') = 0: PASS")

# Gauss sum on E (even-weight vectors), Q(u) = wt(u)/2 mod 2
E = [u for u in range(512) if pc(u) % 2 == 0]
Q = lambda u: (pc(u) // 2) % 2
assert sum((-1) ** Q(u) for u in E) == 16
print("Gauss: sum_E (-1)^Q = 16: PASS")

# (F) |O(z)| >= 44 for every z != 0, where O(z) = ports t with lab(t).z odd
O = {z: {t for t in range(104) if pc(P[t] & z) % 2} for z in range(1, 512)}
assert min(len(o) for o in O.values()) == 44
# and O(z) = {t : B(u_t, a) != eps} with eps = wt(z) mod 2, a = z + eps*1
for z in range(1, 512):
    eps = pc(z) % 2; a = z ^ (ONE if eps else 0)
    assert O[z] == {t for t in range(104) if pc(U[ports[t]] & a) % 2 != eps}
print("F: min |O(z)| = 44, and O(z) = {B(u,a) != eps}: PASS")

# (D') all proper subsets J of the Bourbaki simple roots: |Phi_J^+| > 37 only for J = Delta - {1} (D7, 42)
#      and J = Delta - {8} (E7, 63); the D7 complement is spanned by a norm-4 lattice vector
S = [(1, -1, -1, -1, -1, -1, -1, 1), (2, 2, 0, 0, 0, 0, 0, 0)] + \
    [tuple(-2 if k == i else 2 if k == i + 1 else 0 for k in range(8)) for i in range(6)]
G = [[Fr(dot(a, b)) for b in S] for a in S]
def solve(Mx, rhs):
    n = len(Mx); A = [row[:] + [rhs[i]] for i, row in enumerate(Mx)]
    for c in range(n):
        p = next(r for r in range(c, n) if A[r][c] != 0); A[c], A[p] = A[p], A[c]
        A[c] = [x / A[c][c] for x in A[c]]
        for r in range(n):
            if r != c and A[r][c] != 0: A[r] = [x - A[r][c] * y for x, y in zip(A[r], A[c])]
    return [A[i][n] for i in range(n)]
coef = {r: solve(G, [Fr(dot(s, r)) for s in S]) for r in roots}
pos = [r for r in roots if all(x >= 0 for x in coef[r])]
big = []
for k in range(8):
    for J in itertools.combinations(range(8), k):
        n = sum(1 for r in pos if all(coef[r][i] == 0 for i in range(8) if i not in J))
        if n > 37: big.append((J, n))
assert sorted(big, key=lambda x: x[1]) == [((1, 2, 3, 4, 5, 6, 7), 42), ((0, 1, 2, 3, 4, 5, 6), 63)], big
w1 = [v for v in itertools.product(range(-4, 5), repeat=8)
      if all(dot(v, s) == 0 for s in S[1:]) and dot(v, v) == 16]
assert len(w1) == 2 and any(dot(w1[0], s) != 0 for s in S[:1])
assert any(dot(a, b) == 0 and tuple(x + y for x, y in zip(a, b)) == w1[0] for a in roots for b in roots)
print("D': only E7 (63) and D7 (42) exceed 37; D7 normal = norm-4 vector = sum of two orthogonal roots: PASS")

# (H) a norm-4 vector meets every frame in <= 2 lines with inner product +-2 (doubled scale: +-8)
n4 = sorted({canon(tuple(x + y for x, y in zip(a, b))) for a in roots for b in roots if dot(a, b) == 0})
assert len(n4) == 1080
rem = set(removed)
for v in n4:
    assert sum(1 for l in lines if abs(dot(l, v)) == 8) == 14
    assert sum(1 for l in removed if abs(dot(l, v)) == 8) <= 4
print("H: 14 lines with ip +-2 per norm-4 vector, <= 4 of them removed: PASS")

# brute-force corroboration of SpanFact on all root and norm-4 directions (the two special hyperplane types)
viol = 0
for y in list(lines) + n4:
    N = {t for t in range(104) if dot(R[t], y) != 0}
    for z in range(1, 512):
        s = O[z] & N
        if 1 <= len(s) <= 4 and not any(P[w] == z for w in s): viol += 1
assert viol == 0
print("corroboration: SpanFact holds on all 120 root and 1080 norm-4 hyperplane normals: PASS")
print("ALL PASS")
