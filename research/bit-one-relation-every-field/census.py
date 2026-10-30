"""Odd-characteristic one-relation register census (stdlib only).

Apache-2.0. Prepared for Josie Elliston with Claude (Anthropic) assistance.

Model of research/bit-one-relation-seed04 with register coefficients in F_p:
paid factors I + ([A_j]-1) N_j, N_j = x y^T, y^T x = 1 over F_p, and the
frames A_j generate H = Z^k / Z r for one primitive relation r in {-1,0,1}^k.
A word is *diagonal* when the product equals diag([C_1],...,[C_W]) exactly
(every formal coefficient).  The disjoint-assignment property asks for
pairwise disjoint I_w with C_w = sum_{j in I_w} A_j in H.
"""
import itertools


def idempotents(p, W):
    out = set()
    for x in itertools.product(range(p), repeat=W):
        if not any(x):
            continue
        for y in itertools.product(range(p), repeat=W):
            if sum(a * b for a, b in zip(x, y)) % p == 1:
                out.add(tuple(x[i] * y[j] % p for i in range(W) for j in range(W)))
    return sorted(out)


def matmul(A, B, p, W):
    return tuple(sum(A[i * W + l] * B[l * W + j] for l in range(W)) % p
                 for i in range(W) for j in range(W))


def offdiag(N, W):
    return tuple(0 if i == j else N[i * W + j] for i in range(W) for j in range(W))


def neg(M, p):
    return tuple((-a) % p for a in M)


def identity(W):
    return tuple(1 if i == j else 0 for i in range(W) for j in range(W))


def relations(k):
    """Primitive r in {-1,0,1}^k with support >= 2, one of each pair +-r
    (first nonzero entry +1)."""
    for r in itertools.product((-1, 0, 1), repeat=k):
        nz = [x for x in r if x]
        if len(nz) >= 2 and nz[0] == 1:
            yield r


def coeffs_extend(cs, N, IN, p, W):
    """cs[T] = ordered product over prefix of (N_j if j in T else I-N_j)."""
    bit = len(cs)
    new = [None] * (2 * bit)
    for T, c in enumerate(cs):
        new[T] = matmul(c, IN, p, W)
        new[T | bit] = matmul(c, N, p, W)
    return new


def evaluate(cs, r, k, p, W):
    """Return None if not diagonal, else the list of diagonal classes, one per
    register, each as its canonical integer exponent vector (pivot entry 0)."""
    piv = next(j for j in range(k) if r[j])
    rp = r[piv]
    acc = {}
    reps = {}
    for T, c in enumerate(cs):
        if not any(c):
            continue
        v = [(T >> j) & 1 for j in range(k)]
        m = v[piv] * rp
        key = tuple(v[j] - m * r[j] for j in range(k))
        if key in acc:
            acc[key] = tuple((a + b) % p for a, b in zip(acc[key], c))
        else:
            acc[key] = c
    # classes of subset monomials: representatives
    diag = [None] * W
    for key, c in acc.items():
        if not any(c):
            continue
        for i in range(W):
            for j in range(W):
                if i != j and c[i * W + j]:
                    return None
        for i in range(W):
            if c[i * W + i]:
                if diag[i] is not None or c[i * W + i] != 1:
                    return None
                diag[i] = key
    if any(d is None for d in diag):
        return None
    return diag


def subset_reps(key, r, k):
    """All 0/1 vectors in the class key + Z r (bitmasks)."""
    out = []
    for n in range(-2, 3):
        v = [key[j] + n * r[j] for j in range(k)]
        if all(x in (0, 1) for x in v):
            out.append(sum(1 << j for j in range(k) if v[j]))
    return out


def disjoint_ok(diag, r, k):
    choices = [subset_reps(key, r, k) for key in diag]
    for pick in itertools.product(*choices):
        used = 0
        ok = True
        for T in pick:
            if used & T:
                ok = False
                break
            used |= T
        if ok:
            return True
    return False
