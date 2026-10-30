"""Exact prime-field arithmetic for bounded corroboration, not all fields.

apoursh with substantial OpenAI Codex assistance. Apache-2.0.
Sector-factor construction credits Nick Petalas PR6031 and Krzysztof Wojt
PR5128, generalized here from the binary verifier.
"""
from functools import lru_cache
from itertools import product


def require(condition, message):
    if not condition:
        raise ValueError(message)


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def zeros(r, c):
    return [[0] * c for _ in range(r)]


def transpose(a):
    return [list(x) for x in zip(*a)]


def add(a, b, p, sign=1):
    return [[(x + sign * y) % p for x, y in zip(r, s)]
            for r, s in zip(a, b)]


def scale(a, c, p):
    return [[c * x % p for x in r] for r in a]


def mul(a, b, p, columns=0):
    cols = transpose(b) if b else [[] for _ in range(columns)]
    return [[sum(x * y for x, y in zip(r, c)) % p for c in cols]
            for r in a]


def apply(a, v, p):
    return tuple(sum(x * y for x, y in zip(r, v)) % p for r in a)


def rref(a, p):
    rows = [list(r) for r in a]
    if not rows:
        return (), ()
    pivots = []
    for j in range(len(rows[0])):
        k = next((i for i in range(len(pivots), len(rows)) if rows[i][j]), None)
        if k is None:
            continue
        q = len(pivots)
        rows[q], rows[k] = rows[k], rows[q]
        c = pow(rows[q][j], -1, p)
        rows[q] = [c * x % p for x in rows[q]]
        for i in range(len(rows)):
            if i != q and rows[i][j]:
                c = rows[i][j]
                rows[i] = [(x - c * y) % p for x, y in zip(rows[i], rows[q])]
        pivots.append(j)
    return tuple(tuple(r) for r in rows[:len(pivots)]), tuple(pivots)


def rank(a, p):
    return len(rref(a, p)[0])


def inverse(a, p):
    n = len(a)
    rows, pivots = rref([list(r) + e for r, e in zip(a, eye(n))], p)
    require(pivots[:n] == tuple(range(n)), "singular inverse")
    return [list(r[n:]) for r in rows]


def kernel(a, p):
    rows, pivots = rref(a, p)
    n = len(a[0])
    out = []
    for j in range(n):
        if j not in pivots:
            v = [int(i == j) for i in range(n)]
            for i, k in enumerate(pivots):
                v[k] = -rows[i][j] % p
            out.append(tuple(v))
    return tuple(out)


def image(a, p):
    return rref(transpose(a), p)[0]


def extend(start, candidates, p):
    chosen = [tuple(v) for v in start]
    extra = []
    for v in candidates:
        if rank(chosen + [tuple(v)], p) > len(chosen):
            chosen.append(tuple(v))
            extra.append(tuple(v))
    return extra


def block(parts):
    return [sum((a[i] for a in row), [])
            for row in parts for i in range(len(row[0]))]


def sub(a, r0, r1, c0, c1):
    return [r[c0:c1] for r in a[r0:r1]]


@lru_cache(None)
def subspaces(d, p):
    vectors = tuple(product(range(p), repeat=d))
    spaces = {()}
    frontier = {()}
    for _ in range(d):
        new = {rref(space + (v,), p)[0] for space in frontier for v in vectors}
        frontier = new - spaces
        spaces.update(new)
    return tuple(sorted(spaces, key=lambda s: (len(s), s)))


@lru_cache(None)
def choices(t, p):
    im, ker = image(t, p), kernel(t, p)
    spaces = subspaces(len(t), p)
    ich = tuple(s for s in spaces if rank(s + im, p) == len(s))
    nch = tuple(s for s in spaces if rank(s + ker, p) == len(ker))
    return ich, nch


def compressed(a, b, h, p):
    return [add(add(add(eye(len(a)), a, p, -1), b, p, -1), h, p),
            add(a, h, p, -1), add(b, h, p, -1), h]


def factor_maps(a, b, h, p):
    d = len(a)
    ai, bi = inverse(a, p), inverse(b, p)
    bih, hbi = mul(bi, h, p), mul(h, bi, p)
    z, i = zeros(d, d), eye(d)
    g = block([[z, ai], [scale(bih, -1, p), scale(bi, -1, p)],
               [add(i, bih, p, -1), add(ai, bi, p, -1)]])
    gp = block([[ai, scale(bi, -1, p), add(ai, bi, p, -1)],
                [z, hbi, add(hbi, i, p, -1)]])
    return g, gp


def sector_factors(t, ij, nj, p):
    """Minimal XY=t with image(X)=ij and kernel(Y)=nj; cited construction."""
    d = len(t)
    sigma = image(t, p)
    full = list(sigma) + extend(sigma, eye(d), p)
    coordinates = mul(inverse(transpose(full), p), t, p)
    phi = coordinates[:len(sigma)]
    kb = extend(nj, kernel(t, p), p)
    full = list(nj) + kb
    full += extend(full, eye(d), p)
    coords = inverse(transpose(full), p)
    psi = coords[len(nj):len(nj) + len(kb)]
    tau = extend(sigma, ij, p)
    y = phi + psi + zeros(len(tau), d)
    columns = list(sigma) + zeros(len(psi), d) + tau
    x = transpose(columns) if columns else [[] for _ in range(d)]
    require(mul(x, y, p, d) == t, "sector product")
    require(rank(x, p) == len(ij) and d - rank(y, p) == len(nj), "sector ranks")
    return x, y


def build_pair(a, b, h, ichoice, nchoice, p):
    t = compressed(a, b, h, p)
    select = [(image(t[0], p), kernel(t[0], p))] + list(zip(ichoice, nchoice))
    xs, ys, pd, qd = [], [], [], []
    for j, (tj, (ij, nj)) in enumerate(zip(t, select)):
        x, y = sector_factors(tj, ij, nj, p)
        xs.append(x)
        ys.extend(y)
        pd.extend([int(j in (1, 3))] * len(y))
        qd.extend([int(j in (2, 3))] * len(y))
    projection = [sum((x[i] for x in xs), []) for i in range(len(a))]
    require(mul(projection, ys, p) == eye(len(a)), "split identity")
    m = transpose(transpose(ys) + list(kernel(projection, p)))
    mi = inverse(m, p)
    pp = mul(mi, [[s * x % p for x in row] for s, row in zip(pd, m)], p)
    qq = mul(mi, [[s * x % p for x in row] for s, row in zip(qd, m)], p)
    return pp, qq


def literal_rank(a, b, h, pp, qq, p):
    d, n = len(a), len(pp)
    pq, qp = mul(pp, qq, p), mul(qq, pp, p)
    require(mul(pp, pp, p) == pp and mul(qq, qq, p) == qq and pq == qp,
            "not commuting idempotents")
    require(sub(pp, 0, d, 0, d) == a and sub(qq, 0, d, 0, d) == b
            and sub(pq, 0, d, 0, d) == h, "wrong prescribed blocks")
    complements = []
    for matrix, pivot in ((pp, a), (qq, b)):
        correction = mul(mul(sub(matrix, d, n, 0, d), inverse(pivot, p), p),
                         sub(matrix, 0, d, d, n), p)
        complements.append(add(sub(matrix, d, n, d, n), correction, p, -1))
    s, z = complements
    return rank(add(mul(s, z, p), mul(z, s, p), p, -1), p)
