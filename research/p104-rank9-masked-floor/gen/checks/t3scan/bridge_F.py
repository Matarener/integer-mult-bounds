"""Bridge between RankNine roots rho (A8 coordinates, 9 entries, norm 18) and BForm ports r8 (doubled D8, norm 8).
Checks 4*dot(rho_a,rho_b) == 9*dot(r8_a,r8_b) for all pairs and computes the 8x9 matrix F (entries in Z/9) with
F rho_x = r8_x for all 104 lines; prints 9F as integer rows."""
import re, sys
from fractions import Fraction as Fr
L = sys.argv[1]
defs = open(L + '/RankNine/Data.lean').read()
lab = [int(x) for x in re.search(r'def labelData[^:]*:[^=]*:=\s*\[([^\]]*)\]', defs).group(1).replace('\n', '').split(',')]
def rootOf(q):
    zs = [k for k in range(9) if not (q >> k) & 1]
    if len(zs) == 6: return [2 if (q >> k) & 1 else -1 for k in range(9)]
    return [3 if k == zs[0] else -3 if k == zs[1] else 0 for k in range(9)]
rho = [rootOf(q) for q in lab[:104]]
d8 = open(L + '/BForm/E8/Data.lean').read()
blk = re.search(r'def r8Data : List \(List Int\) := \[(.*?)\]\]', d8, re.S).group(1) + ']'
r8 = [[int(v) for v in row.replace('(', '').replace(')', '').split(',')] for row in re.findall(r'\[([^\[\]]*)\]', blk)]
assert len(rho) == 104 and len(r8) == 104, (len(rho), len(r8))
dot = lambda a, b: sum(x * y for x, y in zip(a, b))
bad = [(a, b) for a in range(104) for b in range(104) if 4 * dot(rho[a], rho[b]) != 9 * dot(r8[a], r8[b])]
print('pairs with 4 rho.rho != 9 r8.r8:', len(bad))
# solve F rho_x = r8_x: pick 9 independent rho (rank of rho is 8: sum of entries is 0), least squares exact
# rho span = {sum = 0}; extend F by F(1,...,1) = 0.
import itertools
rows = [list(map(Fr, v)) for v in rho]
# Gaussian elimination to pick basis of 8 roots
basis = []; ech = []
for i, v in enumerate(rows):
    w = v[:]
    for (p, e) in ech:
        if w[p] != 0:
            f = w[p] / e[p]; w = [a - f * b for a, b in zip(w, e)]
    piv = next((k for k in range(9) if w[k] != 0), None)
    if piv is not None:
        ech.append((piv, w)); basis.append(i)
    if len(basis) == 8: break
A = [rows[i] for i in basis] + [[Fr(1)] * 9]   # 9x9, invertible
R = [list(map(Fr, r8[i])) for i in basis] + [[Fr(0)] * 8]
# F = R^T A^{-T}: F A^T = R^T  -> solve A X = R with X = F^T
n = 9; M = [A[i][:] + R[i][:] for i in range(n)]
for c in range(n):
    p = next(r for r in range(c, n) if M[r][c] != 0); M[c], M[p] = M[p], M[c]
    M[c] = [x / M[c][c] for x in M[c]]
    for r in range(n):
        if r != c and M[r][c] != 0:
            f = M[r][c]; M[r] = [a - f * b for a, b in zip(M[r], M[c])]
X = [row[n:] for row in M]          # 9x8, X = F^T
F = [[X[j][k] for j in range(9)] for k in range(8)]
ok = all(sum(F[k][j] * rho[x][j] for j in range(9)) == r8[x][k] for x in range(104) for k in range(8))
print('F rho_x = r8_x for all x:', ok)
F9 = [[int(9 * F[k][j]) for j in range(9)] for k in range(8)]
assert all(9 * F[k][j] == F9[k][j] for k in range(8) for j in range(9))
print('9F =', F9)
