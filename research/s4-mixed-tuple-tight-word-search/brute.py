"""Independent unpruned meet-in-the-middle word counter in exact F2[S4] (group-algebra elements are
frozensets of permutations; no cut potentials). Counts all words of paid gates I+([s]+1)uv^T with the
given label counts whose product equals diag(t_1..t_r)."""
import sys, itertools
from collections import Counter
def perm(s): return tuple(int(ch) for ch in s)
def compose(a, b): return tuple(a[b[x]-1] for x in range(4))
E = perm('1234'); GENS = {1: perm('2134'), 2: perm('1324'), 3: perm('1243')}
def amul(x, y):  # group algebra product over F2
    out = set()
    for a in x:
        for b in y:
            out ^= {compose(a, b)}
    return frozenset(out)
def aadd(x, y): return frozenset(set(x) ^ set(y))
def mmul(A, B):
    r = len(A); return tuple(tuple(_sum(amul(A[i][k], B[k][j]) for k in range(r)) for j in range(r)) for i in range(r))
def _sum(it):
    acc = frozenset()
    for t in it: acc = aadd(acc, t)
    return acc
def gate(s, u, v, r):
    x = frozenset({GENS[s], E})  # [s]+1
    return tuple(tuple(aadd(frozenset({E}) if i == j else frozenset(), x if (u >> i & 1) and (v >> j & 1) else frozenset()) for j in range(r)) for i in range(r))
def count(targets, counts, ka):
    r = len(targets); n = sum(counts); kb = n - ka
    gates = [(s, u, v) for u in range(1, 1 << r) for v in range(1, 1 << r) if bin(u & v).count('1') % 2 for s in (1, 2, 3)]
    G = {g: gate(*g, r) for g in gates}
    I = tuple(tuple(frozenset({E}) if i == j else frozenset() for j in range(r)) for i in range(r))
    T = tuple(tuple(frozenset({perm(targets[i])}) if i == j else frozenset() for j in range(r)) for i in range(r))
    table = Counter()
    for w in itertools.product(gates, repeat=ka):
        c = [0, 0, 0]
        for g in w: c[g[0]-1] += 1
        if any(c[k] > counts[k] for k in range(3)): continue
        M = I
        for g in w: M = mmul(M, G[g])
        table[(M, tuple(c))] += 1
    total = 0
    for w in itertools.product(gates, repeat=kb):  # w = (L_n, L_{n-1}, ..., L_{ka+1}); T*L_n*...*L_{ka+1} = prefix
        c = [0, 0, 0]
        for g in w: c[g[0]-1] += 1
        rest = tuple(counts[k] - c[k] for k in range(3))
        if min(rest) < 0: continue
        M = T
        for g in w: M = mmul(M, G[g])
        total += table.get((M, rest), 0)
    return total, len(gates)
if __name__ == '__main__':
    counts = tuple(int(x) for x in sys.argv[1].split(',')); ka = int(sys.argv[2]); targets = sys.argv[3:]
    total, ng = count(targets, counts, ka)
    print('targets', targets, 'counts', counts, 'gates', ng, 'split', ka, 'total_words', total)
