"""Exact binary matrices and full formal Q8 coefficients. Apache-2.0."""

from itertools import product

MAX_CALLS = 9


def require(ok, message):
    if not ok:
        raise ValueError(message)


def validate(a):
    n = len(a)
    require(1 <= n <= MAX_CALLS, "call dimension must be in 1..9")
    require(all(type(row) is int and 0 <= row < 1 << n for row in a),
            "invalid binary row")
    require(all(row >> i & 1 for i, row in enumerate(a)), "Gram diagonal is not one")


def combinations(rows):
    """All binary sums, indexed by the chosen rows; at most 512 entries."""
    out = [0] * (1 << len(rows))
    for mask in range(1, len(out)):
        bit = mask & -mask
        out[mask] = out[mask ^ bit] ^ rows[bit.bit_length() - 1]
    return out


def multiply(a, b):
    table = combinations(b)
    return tuple(table[row] for row in a)


def rank(rows):
    pivots = [0] * MAX_CALLS
    result = 0
    for row in rows:
        for bit in range(MAX_CALLS - 1, -1, -1):
            if row >> bit & 1:
                if pivots[bit]:
                    row ^= pivots[bit]
                else:
                    pivots[bit] = row
                    result += 1
                    break
    return result


def grams(n):
    """Every diagonal-one n-by-n matrix exactly once, without symmetry pruning."""
    require(type(n) is int and 1 <= n <= 5, "census dimension must be in 1..5")
    choices = []
    for i in range(n):
        low = (1 << i) - 1
        choices.append(tuple((x & low) | ((x & ~low) << 1) | (1 << i)
                             for x in range(1 << (n - 1))))
    return product(*choices)


def labels(n, si, sj):
    return tuple(mask for mask in range(1 << n)
                 if mask.bit_count() >= si and n - mask.bit_count() >= sj
                 and (mask.bit_count() - si) % 2 == 0
                 and (n - mask.bit_count() - sj) % 2 == 0)


def first_order(a, mask, si, sj, table=None):
    """PR3517's orthogonal target projectors, tested on im A."""
    sums = combinations(a) if table is None else table
    full = (1 << len(a)) - 1
    zi = tuple(sums[row & mask] for row in a)
    zj = tuple(sums[row & (full ^ mask)] for row in a)
    if rank(zi) != si or rank(zj) != sj:
        return None
    li = tuple(row & mask for row in a)
    lj = tuple(row & (full ^ mask) for row in a)
    zero = (0,) * len(a)
    if (multiply(li, zi) != zi or multiply(lj, zj) != zj
            or multiply(li, zj) != zero or multiply(lj, zi) != zero):
        return None
    return zi, zj


def qmul(g, h):
    """z^s i^a j^b, encoded as 4s+2b+a; j i = z i j."""
    s, a, b = g >> 2, g & 1, g >> 1 & 1
    t, c, d = h >> 2, h & 1, h >> 1 & 1
    return ((s ^ t ^ (b & c) ^ (a & c) ^ (b & d)) << 2) | ((b ^ d) << 1) | (a ^ c)


def endpoint(a, mask):
    """Return T A, preserving all eight group coefficients; gate zero first."""
    n = len(a)
    coeff = [[0] * n for _ in range(8)]
    coeff[0] = list(a)
    for call in range(n):
        g = 1 if mask >> call & 1 else 2
        old = tuple(part[call] for part in coeff)
        for row in range(n):
            if a[row] >> call & 1:
                for h in range(8):
                    coeff[h][row] ^= old[h]
                    coeff[qmul(g, h)][row] ^= old[h]
    return tuple(tuple(part) for part in coeff)


def target(a, zi, zj):
    out = [(0,) * len(a) for _ in range(8)]
    out[0] = tuple(x ^ y ^ z for x, y, z in zip(a, zi, zj, strict=True))
    out[5], out[6] = zi, zj
    return tuple(out)


def accepts(a, mask, si, sj):
    validate(a)
    require(type(mask) is int and 0 <= mask < 1 << len(a), "invalid label mask")
    require(type(si) is int and type(sj) is int and 0 <= si + sj <= len(a)
            and min(si, sj) >= 0, "invalid target ranks")
    projections = first_order(a, mask, si, sj)
    return projections is not None and endpoint(a, mask) == target(a, *projections)
