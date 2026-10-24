# Split ALL plane groups of size g into equivalence classes: two groups are the same local-decoder problem iff their
# tariff tables t(A, R) (A, R subsets of the group) and orthogonality patterns agree up to a permutation of the planes.
# Usage: python v4_classify.py <g> <chunk> <nchunks>   -> classes_g<g>_<chunk>.json  {key: [count, representative]}
import itertools, json, sys, hashlib
from v4lib import *
g, chunk, nch = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
labels, pairs = load_geometry(); planes = [(labels[a], labels[b]) for a, b in pairs]; NP = len(planes)
ORTH = [[i != j and all(dot(x, y) == 0 for x in planes[i] for y in planes[j]) for j in range(NP)] for i in range(NP)]
_sc = {}
def sp(D):
    D = tuple(sorted(D))
    if D not in _sc: _sc[D] = span([v for i in D for v in planes[i]])
    return _sc[D]
perms = list(itertools.permutations(range(g)))
def remap(mask, perm):   # plane i of the permuted group = plane perm[i] of the original
    return sum(1 << i for i in range(g) if mask >> perm[i] & 1)
pm_tables = [[remap(m, p) for m in range(2 ** g)] for p in perms]
inv = [[0] * (2 ** g) for _ in perms]
for k, p in enumerate(perms):
    for m in range(2 ** g): inv[k][pm_tables[k][m]] = m
out = {}
for G in itertools.combinations(range(NP), g):
    if G[0] % nch != chunk: continue
    t = {}
    for A in range(1, 2 ** g):
        sA = sp([G[i] for i in range(g) if A >> i & 1])
        for R in range(1, 2 ** g): t[A, R] = pair_rank(sA, sp([G[i] for i in range(g) if R >> i & 1]))
    best = None
    for k, p in enumerate(perms):
        iv = inv[k]
        tab = tuple(t[iv[A], iv[R]] for A in range(1, 2 ** g) for R in range(1, 2 ** g))
        o = tuple(ORTH[G[p[i]]][G[p[j]]] for i in range(g) for j in range(g))
        key = (tab, o)
        if best is None or key < best: best = key
    h = hashlib.sha1(repr(best).encode()).hexdigest()
    if h in out: out[h][0] += 1
    else: out[h] = [1, list(G)]
json.dump(out, open(f'classes_g{g}_{chunk}.json', 'w'))
print('g', g, 'chunk', chunk, 'classes', len(out), 'groups', sum(v[0] for v in out.values()), flush=True)
