#!/usr/bin/env python3
"""Exact depth-three repetition/orbit formulas. SHIN09-git + OpenAI Codex.
Apache-2.0. All checks remain active under Python -O.
"""
from math import comb, gcd


def require(condition, message):
    if not condition:
        raise ValueError(message)


def divisors(m):
    require(isinstance(m, int) and 1 <= m <= 128, "modulus outside 1..128")
    return [d for d in range(1, m + 1) if m % d == 0]


def mobius(n):
    result, p = 1, 2
    while p * p <= n:
        if n % p == 0:
            n //= p
            result = -result
            if n % p == 0:
                return 0
        p += 1
    return -result if n > 1 else result


def phi(n):
    return sum(gcd(k, n) == 1 for k in range(1, n + 1))


def repeated_counts(n, d, a, b, t):
    """Unreduced integer pair/triple counts of v**d."""
    pair_shift = comb(d, 2) * n * n
    return (d * a + pair_shift, d * b + pair_shift,
            d * t + comb(d, 2) * n * (a + b) + comb(d, 3) * n**3)


def fixed_count(m, c, d, rows):
    """Fixed points of a rotation of order d, for d dividing m."""
    require(d in divisors(m) and 0 <= c < m, "invalid fixed-point argument")
    n = m // d
    if d % 2 == 0 and n % 2 == 1:
        return 0
    delta = c - comb(d, 3) * n**3
    if delta % d:
        return 0
    return rows[n][(delta // d) % n]


def period_row(m, c, rows):
    ds = divisors(m)
    fixed = {d: fixed_count(m, c, d, rows) for d in ds}
    exact = {d: sum(mobius(e // d) * fixed[e] for e in ds if e % d == 0)
             for d in ds}
    for d in ds:
        require(exact[d] >= 0, "negative exact-period population")
        require(exact[d] % (3 * m // d) == 0, "nonintegral exact-period orbit count")
    require(sum(exact.values()) == rows[m][c], "period partition does not sum to W")
    weighted = sum(phi(d) * fixed[d] for d in ds)
    require(weighted % (3 * m) == 0, "nonintegral Burnside count")
    orbits = weighted // (3 * m)
    require(orbits == sum(exact[d] // (3 * m // d) for d in ds),
            "Burnside and exact-period counts disagree")
    return dict(fixed={str(k): v for k, v in fixed.items()},
                exact_repetitions={str(k): v for k, v in exact.items()},
                primitive_words=exact[1], cyclic_orbits=orbits)


def unit_repeated_count(m, c, rows):
    require(m >= 2 and 0 < c < m and gcd(c, m) == 1, "target must be a unit")
    if m % 3 or m % 9 == 0:
        return 0
    n = m // 3
    if (c - n**3) % 3:
        return 0
    return rows[n][((c - n**3) // 3) % n]


def check_unit_row(m, c, rows, row):
    repeated = unit_repeated_count(m, c, rows)
    allowed = (m % 3 == 0 and m % 9 != 0 and
               (c - (m // 3)**3) % 3 == 0)
    exists = allowed and (m, c) not in ((6, 5), (12, 1))
    require((repeated > 0) == exists, "unit repetition existence classification")
    require(row["primitive_words"] == rows[m][c] - repeated, "unit primitive formula")
    require(row["cyclic_orbits"] * (3 * m) == rows[m][c] + 2 * repeated,
            "unit orbit formula")
    for d, count in row["exact_repetitions"].items():
        require(int(d) in (1, 3) or count == 0, "forbidden unit repetition")
    return repeated
