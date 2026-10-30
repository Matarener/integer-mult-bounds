#!/usr/bin/env python3
"""Exact checks of the finite facts used in HAND-ROOTFACT.md (runs in < 1 s).

Coordinates: doubled D8 (E8 roots have norm 8), the same as ../data/p104_r8_d8.json.
"""
import itertools, json, sys
from fractions import Fraction as Fr
from pathlib import Path

def dot(a, b): return sum(x * y for x, y in zip(a, b))

roots = []
for i, j in itertools.combinations(range(8), 2):
    for a in (2, -2):
        for b in (2, -2):
            v = [0] * 8; v[i] = a; v[j] = b; roots.append(tuple(v))
for s in itertools.product((1, -1), repeat=8):
    if s.count(-1) % 2 == 0: roots.append(s)
assert len(roots) == 240
canon = lambda v: v if next(c for c in v if c) > 0 else tuple(-c for c in v)
lines = sorted({canon(r) for r in roots}); assert len(lines) == 120

ports = [canon(tuple(p)) for p in json.loads((Path(__file__).parent.parent / "data" / "p104_r8_d8.json").read_text())["R8"]]
assert len(ports) == 104 and len(set(ports)) == 104 and set(ports) <= set(lines)
removed = [l for l in lines if l not in set(ports)]
assert len(removed) == 16

# (A) the 16 removed lines are two frames (8 pairwise orthogonal lines each)
nb = [l for l in removed[1:] if dot(l, removed[0]) == 0]
splits = []
for c in itertools.combinations(nb, 7):
    F1 = [removed[0], *c]; F2 = [l for l in removed if l not in F1]
    if all(dot(a, b) == 0 for F in (F1, F2) for a, b in itertools.combinations(F, 2)): splits.append((F1, F2))
assert len(splits) == 1
F1, F2 = splits[0]
for F in (F1, F2):
    assert len(F) == 8 and all(dot(a, b) == 0 for a, b in itertools.combinations(F, 2))
print("A: removed lines = two frames: PASS")

# (B) a root is non-orthogonal to itself and to exactly 56 other lines
for r in lines:
    assert sum(1 for l in lines if dot(l, r) != 0) == 57
print("B: every root line is non-orthogonal to exactly 57 lines (itself included): PASS")

# (C) a root outside a frame is non-orthogonal to exactly 4 of its 8 lines
for r in lines:
    for F in (F1, F2):
        k = sum(1 for f in F if dot(f, r) != 0)
        assert k == (1 if r in F else 4)
print("C: frame counts 1 (own frame) / 4 (other frame): PASS")

# (D) Bourbaki simple roots of E8, doubled; every root is a non-negative or non-positive integer
#     combination; |Phi_J^+| for the eight maximal J (delete one node)
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
coef = {}
for r in roots:
    c = solve(G, [Fr(dot(s, r)) for s in S])
    assert all(x.denominator == 1 for x in c) and (all(x >= 0 for x in c) or all(x <= 0 for x in c))
    coef[r] = c
pos = [r for r in roots if all(x >= 0 for x in coef[r])]; assert len(pos) == 120
sizes = {}
for drop in range(8):
    sizes[drop + 1] = sum(1 for r in pos if coef[r][drop] == 0)
print("D: |Phi_J^+| after deleting node i:", sizes)
assert sorted(sizes.values()) == [14, 16, 22, 23, 28, 37, 42, 63]
assert sizes[8] == 63 and max(v for k, v in sizes.items() if k != 8) == 42
# the E7 = Phi_{J}, J = nodes 1..7, is the orthogonal complement of the highest root
hi = max(pos, key=lambda r: sum(coef[r]))
assert all(dot(hi, s) == 0 for s in S[:7]) and dot(hi, S[7]) != 0
print("D: E7 parabolic = highest-root-perp: PASS")

# (E) the bound is attained: N(r) = 49 for r in P104, 52 for a removed line
vals = {sum(1 for p in ports if dot(p, r) != 0) for r in ports}
vals2 = {sum(1 for p in ports if dot(p, r) != 0) for r in removed}
assert vals == {49} and vals2 == {52}
print("E: N(root) = 49 on ports, 52 on removed lines: PASS")
print("ALL PASS")
