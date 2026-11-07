"""(copy of t2review/common.py from the review branch claude/project-thread-ul6l6g @ 191714b, BASE path adjusted)
Independent re-implementation for the review of the T2 hand proof (NOTE 13.21).  Only the definition of P104
(list P of 9-bit labels) and the 9 frameless type representatives (orbitsW.json) are taken from the repo; everything
else (roots, frames, relations, grids, rules, peeling) is rebuilt here from scratch."""
import json, os, itertools
from fractions import Fraction as Fr
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(os.path.dirname(HERE))
src = open(os.path.join(BASE, 'p104lib.py')).read()
P = eval(src[src.index('P = [') + 4: src.index(']', src.index('P = [')) + 1])
assert len(P) == 104 and len(set(P)) == 104
def root(q):
    c = [(q >> k) & 1 for k in range(9)]
    if sum(c) == 7:
        i, j = [k for k in range(9) if not c[k]]; r = [0] * 9; r[i] = 3; r[j] = -3; return tuple(r)
    assert sum(c) == 3
    return tuple(2 if c[k] else -1 for k in range(9))
ALL = [q for q in range(512) if bin(q).count('1') in (3, 7)]
assert len(ALL) == 120
R = [root(q) for q in P]
def dot(a, b): return sum(x * y for x, y in zip(a, b))
for r in R: assert dot(r, r) == 18 and sum(r) == 0
N = 104
G = [[dot(R[i], R[j]) for j in range(N)] for i in range(N)]   # 9 x (E8 Gram), norm 18
OR = [[G[i][j] == 0 for j in range(N)] for i in range(N)]
for i in range(N):
    for j in range(N):
        assert G[i][j] in (0, 9, -9) or i == j
def frames_of(idx):
    out = []
    def rec(cur, cand):
        if len(cur) == 8: out.append(tuple(cur)); return
        for k, q in enumerate(cand): rec(cur + [q], [r for r in cand[k + 1:] if OR[q][r]])
    rec([], list(idx)); return out
FR = frames_of(range(N))
def types():
    rw = [r for r in json.load(open(os.path.join(BASE, 'orbitsW.json'))) if not r['frame']]
    assert len(rw) == 9
    return [sorted(i for i in range(N) if int(r['mask']) >> i & 1) for r in rw]
def mu_gram(x, y): return Fr(G[x][y], G[y][y])     # mu_xy = M_xy / M_yy in the Gram world: +-1/2 or 0
def relations(C, minF=4):
    """all frame relations on C x C: (t, s, K, |F|, O) with t, s in C \\ F, t != s, t perp O, K = {f in F: f !perp t, s}.
    Meaning (non-degenerate partial frame): mu_ts = sum_{f in K} mu_tf mu_fs."""
    Cs = set(C); out = []
    for E in FR:
        F = [e for e in E if e in Cs]; O = tuple(e for e in E if e not in Cs)
        if len(F) < minF: continue
        Fs = set(F)
        for t in C:
            if t in Fs or not all(OR[t][o] for o in O): continue
            Tt = [f for f in F if not OR[t][f]]
            for s in C:
                if s in Fs or s == t: continue
                out.append((t, s, frozenset(f for f in Tt if not OR[f][s]), len(F), O))
    return out

# ---- abstract tritangent grid (D.11 table); a grid line is (letter X, group i)
GL = [(X, i) for i in range(3) for X in range(3)]
def grid_relations():
    out = []
    for (a, i), (b, j) in itertools.permutations(GL, 2):
        if a == b:                      # twins: k = third group, any 2 of {Ak, Bk, Ck}
            k = 3 - i - j
            for K in itertools.combinations([(X, k) for X in range(3)], 2): out.append(((a, i), (b, j), frozenset(K)))
        elif i == j:                    # orthogonal (same group): k != i, c = third letter
            c = 3 - a - b
            for k in range(3):
                if k == i: continue
                out.append(((a, i), (b, j), frozenset([(c, k), (a, k)])))
                out.append(((a, i), (b, j), frozenset([(c, k), (b, k)])))
        else:                           # cross: k third group, terms {a,b}k
            k = 3 - i - j
            out.append(((a, i), (b, j), frozenset([(a, k), (b, k)])))
    return out
GRELS = grid_relations(); assert len(GRELS) == 162
def g_orth(x, y): return x != y and x[1] == y[1]
def find_grids(C, relset):
    """complete grids in C carrying all 162 D.11 relations (relset = set of (t,s,K)); returns list of maps GL -> line"""
    Cs = set(C)
    tris = [t for t in itertools.combinations(C, 3) if OR[t[0]][t[1]] and OR[t[0]][t[2]] and OR[t[1]][t[2]]]
    def full(a, b): return all(not OR[x][y] for x in a for y in b)
    adj = defaultdict(set)
    for i, a in enumerate(tris):
        for j in range(i + 1, len(tris)):
            if full(a, tris[j]): adj[i].add(j); adj[j].add(i)
    shaped = []; good = []
    for i in adj:
        for j in adj[i]:
            if j <= i: continue
            for k in adj[i] & adj[j]:
                if k <= j: continue
                shaped.append((i, j, k))
    for g in shaped:
        T = [tris[x] for x in g]
        found = None
        for p1 in itertools.permutations(range(3)):
            for p2 in itertools.permutations(range(3)):
                mp = {}
                for X in range(3): mp[(X, 0)] = T[0][X]; mp[(X, 1)] = T[1][p1[X]]; mp[(X, 2)] = T[2][p2[X]]
                if all((mp[t], mp[s], frozenset(mp[f] for f in K)) in relset for t, s, K in GRELS):
                    found = mp; break
            if found: break
        if found: good.append(found)
    return shaped, good
