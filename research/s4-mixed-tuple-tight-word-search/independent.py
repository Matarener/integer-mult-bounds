"""Second, separately written method: pruned depth-first search from the target end, computed
directly in the natural (4-point) and ordered-pair (12-point) permutation representations as
explicit F2 matrices (no group-algebra bit masks). Reports node counts per depth."""
import itertools, sys
def perm(s): return tuple(int(ch) for ch in s)                       # one-line, 1-based
def compose(a, b): return tuple(a[b[x]-1] for x in range(4))          # (ab)(x) = a(b(x))
GENS = {1: perm('2134'), 2: perm('1324'), 3: perm('1243')}
POINTS = {'nat': [(x,) for x in range(1, 5)],
          'pair': [(x, y) for x in range(1, 5) for y in range(1, 5) if x != y]}
def act(g, pt): return tuple(g[x-1] for x in pt)
def rep(g, mod):  # rho(g) as list of column images: matrix[row][col]=1 iff row = g.col
    pts = POINTS[mod]; d = len(pts)
    return [[1 if pts[a] == act(g, pts[b]) else 0 for b in range(d)] for a in range(d)]
CUTH = {'c1': ('nat', lambda p: p[0] <= 1), 'c3': ('nat', lambda p: p[0] <= 3), 'inv': ('pair', lambda p: p[0] < p[1])}
def big(mats_by_role_pair, r, d):  # build (r*d)x(r*d) row-bitset matrix from function (i,j)->dxd matrix
    rows = []
    for i in range(r):
        for a in range(d):
            x = 0
            for j in range(r):
                blk = mats_by_role_pair(i, j)
                if blk is None: continue
                for b in range(d):
                    if blk[a][b]: x |= 1 << (j*d + b)
            rows.append(x)
    return rows
def matmul(A, B):  # row bitsets: (AB)_row = xor of B rows selected by A_row
    out = []
    for x in A:
        y = 0; k = 0
        while x:
            if x & 1: y ^= B[k]
            x >>= 1; k += 1
        out.append(y)
    return out
def rank(rows):
    rows = [x for x in rows if x]; rk = 0
    while rows:
        p = rows.pop(); 
        if not p: continue
        rk += 1; lb = p & -p
        rows = [x ^ p if x & lb else x for x in rows]
        rows = [x for x in rows if x]
    return rk
def block_rank(M, r, mod, inH, fwd):
    pts = POINTS[mod]; d = len(pts)
    Hrows = [i*d+a for i in range(r) for a in range(d) if inH(pts[a])]
    Crows = [i*d+a for i in range(r) for a in range(d) if not inH(pts[a])]
    rs, cs = (Crows, Hrows) if fwd else (Hrows, Crows)
    sub = []
    for q in rs:
        x = 0
        for t, c in enumerate(cs):
            if M[q] >> c & 1: x |= 1 << t
        sub.append(x)
    return rank(sub)
def charge(g, mod, inH):
    return sum(1 for p in POINTS[mod] if inH(p) and not inH(act(g, p)))
def search(targets, counts, maxdepth=None):
    r = len(targets); ident = perm('1234')
    gates = [(s, u, v) for u in range(1, 1 << r) for v in range(1, 1 << r) if bin(u & v).count('1') % 2 for s in (1, 2, 3)]
    mods = {'nat': 4, 'pair': 12}
    Trep = {m: big(lambda i, j, m=m: rep(perm(targets[i]), m) if i == j else None, r, d) for m, d in mods.items()}
    G = {}
    for (s, u, v) in gates:
        for m, d in mods.items():
            rho = rep(GENS[s], m); A = [[rho[a][b] ^ (a == b) for b in range(d)] for a in range(d)]
            G[(s, u, v, m)] = big(lambda i, j: [[(1 if (i == j and a == b) else 0) ^ (A[a][b] & (u >> i & 1) & (v >> j & 1)) for b in range(d)] for a in range(d)], r, d)
    ch = {c: tuple(charge(GENS[s], CUTH[c][0], CUTH[c][1]) for s in (1, 2, 3)) for c in CUTH}
    phiT = {}
    for c, (m, f) in CUTH.items():
        a, b = block_rank(Trep[m], r, m, f, True), block_rank(Trep[m], r, m, f, False)
        assert a == b; phiT[c] = a
        assert sum(x*y for x, y in zip(ch[c], counts)) >= a, ('cut infeasible', c)
    # full: full-depth window survivors; the endpoint P_0 = I is NOT checked here, so this is an
    # upper bound on words (verify.py.exact_words rechecks it in exact F2[S4] arithmetic).
    nodes = [0]*(sum(counts)+1); full = []
    def ok(M, m):
        for c, (mod, f) in CUTH.items():
            hi = sum(x*y for x, y in zip(ch[c], m)); lo = phiT[c] - (sum(x*y for x, y in zip(ch[c], counts)) - hi)
            for fwd in (True, False):
                ph = block_rank(M[mod], r, mod, f, fwd)
                if ph < lo or ph > hi: return False
        return True
    def dfs(M, m, depth, word):
        if depth == sum(counts):
            full.append(list(word)); return
        if maxdepth is not None and depth == maxdepth: return
        for (s, u, v) in gates:
            if m[s-1] == 0: continue
            M2 = {mod: matmul(M[mod], G[(s, u, v, mod)]) for mod in mods}
            m2 = list(m); m2[s-1] -= 1
            if ok(M2, m2):
                nodes[depth+1] += 1; word.append((s, u, v)); dfs(M2, m2, depth+1, word); word.pop()
    dfs(Trep, list(counts), 0, [])
    return nodes[1:], full, len(gates)
if __name__ == '__main__':
    counts = tuple(int(x) for x in sys.argv[1].split(',')); md = None
    if sys.argv[2].startswith('maxdepth='): md = int(sys.argv[2].split('=')[1]); targets = sys.argv[3:]
    else: targets = sys.argv[2:]
    nodes, full, ng = search(targets, counts, md)
    print('targets', targets, 'counts', counts, 'gates', ng, 'nodes_per_depth', nodes, 'full_depth_survivors', len(full))
