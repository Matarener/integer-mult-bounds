"""Exact rational projectors of the frames (second method for frame dimension and nesting).

P_F is the orthogonal projector (form <x,y> = dot/2, so dot-orthogonal) onto the Q-span of
frame F's E8 lines: P = L^T (L L^T)^-1 L for a row basis L.  For a climb A -> B the native
transport identities P_A P_B = P_B P_A = P_A are checked exactly; with D_U the address-half
exchange [[I-U, U], [U, I-U]], they imply D_(P_B-P_A) D_(P_A) = D_(P_B) (written argument in
README), which is also checked literally on the changed receiver and SOURCE77 paths.
"""
from fractions import Fraction as Q


def matmul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]


def basis(rows):
    out = []
    for r in rows:
        v = [Q(x) for x in r]
        for b, p in out:
            if v[p]:
                f = v[p] / b[p]
                v = [x - f * y for x, y in zip(v, b)]
        p = next((i for i, x in enumerate(v) if x), None)
        if p is not None:
            out.append((v, p))
    return [v for v, _ in out]


def inverse(m):
    n = len(m)
    a = [list(r) + [Q(int(i == j)) for j in range(n)] for i, r in enumerate(m)]
    for c in range(n):
        p = next(i for i in range(c, n) if a[i][c])
        a[c], a[p] = a[p], a[c]
        inv = 1 / a[c][c]
        a[c] = [x * inv for x in a[c]]
        for i in range(n):
            if i != c and a[i][c]:
                f = a[i][c]
                a[i] = [x - f * y for x, y in zip(a[i], a[c])]
    return [r[n:] for r in a]


def projector(lines, frame, dim=8):
    L = basis([lines[i] for i in frame])
    if not L:
        return [[Q(0)] * dim for _ in range(dim)], 0
    G = matmul(L, [list(c) for c in zip(*L)])
    P = matmul(matmul([list(c) for c in zip(*L)], inverse(G)), L)
    return P, len(L)


def D(U):
    n = len(U)
    I = [[Q(int(i == j)) for j in range(n)] for i in range(n)]
    IU = [[I[i][j] - U[i][j] for j in range(n)] for i in range(n)]
    return [IU[i] + U[i] for i in range(n)] + [U[i] + IU[i] for i in range(n)]


def check(word, climbs, geo, focus):
    lines = [list(map(int, x)) for x in word['lines']]
    cache = {}

    def P(f):
        if f not in cache:
            cache[f] = projector(lines, word['frames'][f])
        return cache[f]
    rank_ok = all(P(f)[1] == geo.dim[f] and sum(P(f)[0][i][i] for i in range(8)) == geo.dim[f]
                  for f in {x for _, a, b, _ in climbs for x in (a, b)})
    pairs = sorted({(a, b) for _, a, b, _ in climbs})
    nest_ok = all(matmul(P(a)[0], P(b)[0]) == P(a)[0] and matmul(P(b)[0], P(a)[0]) == P(a)[0] for a, b in pairs)
    d_ok = True
    for a, b in focus:
        pa, pb = P(a)[0], P(b)[0]
        diff = [[pb[i][j] - pa[i][j] for j in range(8)] for i in range(8)]
        d_ok &= matmul(D(diff), D(pa)) == D(pb)
    return dict(frames_projected=len(cache), climb_pairs=len(pairs), projector_rank_equals_dim=rank_ok,
                nested_projector_identity=nest_ok, focus_transitions=[list(x) for x in focus],
                address_exchange_identity_on_focus=d_ok)
