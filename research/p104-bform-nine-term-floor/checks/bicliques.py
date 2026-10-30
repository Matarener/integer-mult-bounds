"""B-form support structure on P104: A x B must be pairwise non-orthogonal (c_u beta_s = 0 on orthogonal pairs).
Enumerate the closed bicliques (A = C(B), B = C(A), C(S) = lines non-orthogonal to every line of S, a line counts as
non-orthogonal to itself) with |A| >= 13, and the facts used in BFORM2.md.  Exact, char 0.
Apache-2.0."""
import itertools, time, json
from fractions import Fraction as Q
T0 = time.time()
def log(*a): print('[%7.1fs]' % (time.time() - T0), *a, flush=True)
log('START bicliques')
P = [11, 19, 35, 131, 259, 13, 21, 37, 69, 133, 261, 41, 73, 265, 49, 81, 145, 273, 161, 193, 321, 385, 14, 22, 38, 70, 134, 262, 26, 74, 138, 50, 146, 274, 98, 290, 194, 322, 386, 28, 44, 140, 268, 84, 148, 276, 100, 164, 292, 196, 324, 388, 56, 88, 152, 280, 168, 296, 200, 328, 392, 112, 176, 304, 208, 336, 400, 224, 352, 416, 508, 506, 502, 494, 478, 446, 382, 254, 505, 501, 493, 477, 445, 381, 253, 499, 475, 443, 379, 251, 487, 471, 439, 375, 247, 463, 431, 367, 239, 415, 351, 223, 319, 191]
N = len(P)
def root(q):
    c = [(q >> k) & 1 for k in range(9)]
    if sum(c) == 7:
        i, j = [k for k in range(9) if not c[k]]; r = [0] * 9; r[i] = 3; r[j] = -3; return r
    return [2 if c[k] else -1 for k in range(9)]
R = [root(q) for q in P]
def ip(i, j): return sum(a * b for a, b in zip(R[i], R[j]))
NB = [sum(1 << j for j in range(N) if ip(i, j) != 0) for i in range(N)]   # closed non-orth neighbourhood (incl. i)
ALL = (1 << N) - 1
def C(mask):
    m = ALL
    for i in range(N):
        if mask >> i & 1: m &= NB[i]
    return m
pc = lambda m: bin(m).count('1')
log('neighbourhood sizes', sorted({pc(x) for x in NB}))
# closed sets with |A| >= 13: intersections of neighbourhoods, DFS over generators in increasing order
TH = 13
closed = {}
def dfs(start, S):
    for b in range(start, N):
        S2 = S & NB[b]
        if pc(S2) < TH or S2 == S: continue
        if S2 in closed: continue
        Bc = C(S2); closed[S2] = Bc
        dfs(b + 1, S2)
dfs(0, ALL)
log('closed A-sets with |A| >= %d:' % TH, len(closed))
from collections import Counter
hist = Counter((pc(A), pc(B)) for A, B in closed.items())
for k in sorted(hist): log('  |A|, |B| =', k, 'count', hist[k])
log('max |B| over closed A with |A| >= 13:', max(pc(B) for B in closed.values()))
json.dump([[A, B] for A, B in closed.items()], open('bicliques.json', 'w'))
log('DONE')
