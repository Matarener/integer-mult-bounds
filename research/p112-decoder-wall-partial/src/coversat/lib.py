# Minimal stdlib library for the COVERSAT scripts (orbit matrices from ../ct8/orbits.json; ranks as in CT8-INT/lib.py).
import os, json, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
import sys; sys.path.insert(0, os.path.join(HERE, '..', 'ct8'))
from exact import f2rank_rows
P31 = 2147483647
_ORB = json.load(open(os.path.join(HERE, '..', 'ct8', 'orbits.json')))
def orbit(o):
    d = _ORB[str(o)]; return d['lines_P112_order'], d['B']
def qrank01(rows8, X=255, Y=255):
    """exact Q-rank of a 0/1 matrix given as row bitmasks (row t, bit s), restricted to X x Y.  0/1 8x8 minors <= 8^4 < P31."""
    A = [[(rows8[t] >> s) & 1 for s in range(8) if Y >> s & 1] for t in range(8) if X >> t & 1]
    A = [r for r in A if any(r)]
    if not A: return 0
    rk = 0; nc = len(A[0])
    for col in range(nc):
        pr = next((i for i in range(rk, len(A)) if A[i][col] % P31), None)
        if pr is None: continue
        A[rk], A[pr] = A[pr], A[rk]; iv = pow(A[rk][col], P31 - 2, P31)
        for i in range(len(A)):
            if i != rk and A[i][col] % P31:
                f = A[i][col] * iv % P31; A[i] = [(x - f * y) % P31 for x, y in zip(A[i], A[rk])]
        rk += 1
    return rk

def f2rank01(rows8, X=255, Y=255):
    return f2rank_rows([rows8[t] & Y for t in range(8) if X >> t & 1])

def brows(B): return [sum(1 << s for s in range(8) if B[t][s]) for t in range(8)]

def aut(B):
    return [p for p in itertools.permutations(range(8)) if all(B[p[i]][p[j]] == B[i][j] for i in range(8) for j in range(8))]

def atom_S(c, r):
    D = [0] * 9
    for i in range(1, 9): D[i] = D[i - 1] | sum(1 << s for s in range(8) if c[s] == i)
    return [D[r[t]] if r[t] else 0 for t in range(8)]

def masked(Bp_rows, S): return [Bp_rows[t] & S[t] for t in range(8)]
