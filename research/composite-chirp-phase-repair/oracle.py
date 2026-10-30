"""Literal matrices and integer-polynomial checks, independent of chirp.py.

Produced by Nick Petalas. Apache-2.0.
"""

from math import isqrt


def require(condition, message):
    if not condition:
        raise ValueError(message)


def prime(p):
    return p >= 2 and all(p % d for d in range(2, 1 + isqrt(p)))


def field(n):
    require(type(n) is int and 1 <= n <= 63, "oracle axis limit")
    if n == 1:
        return 3, 1
    for k in range(2, 1025):
        p = k * n + 1
        if not prime(p):
            continue
        for root in range(2, p):
            if pow(root, n, p) == 1 and all(
                    pow(root, d, p) != 1 for d in range(1, n) if n % d == 0):
                return p, root
    raise ValueError("bounded field search exhausted")


def matrix(n, a, b, p, root):
    return [[pow(root, (a * (j - k) ** 2 + b * (j - k)) % n, p)
             for k in range(n)] for j in range(n)]


def apply(rows, values, p):
    return [sum(x * y for x, y in zip(row, values)) % p for row in rows]


def rank(rows, p):
    a = [list(row) for row in rows]
    height, width = len(a), len(a[0])
    pivot = 0
    for column in range(width):
        found = next((r for r in range(pivot, height) if a[r][column] % p), None)
        if found is None:
            continue
        a[pivot], a[found] = a[found], a[pivot]
        inverse = pow(a[pivot][column], -1, p)
        a[pivot] = [x * inverse % p for x in a[pivot]]
        for r in range(pivot + 1, height):
            multiplier = a[r][column] % p
            a[r] = [(x - multiplier * y) % p for x, y in zip(a[r], a[pivot])]
        pivot += 1
        if pivot == height:
            break
    return pivot


def polynomial_division(numerator, denominator):
    work = list(numerator)
    degree = len(denominator) - 1
    quotient = [0] * max(1, len(work) - degree)
    for k in range(len(work) - 1, degree - 1, -1):
        coefficient = work[k]
        quotient[k - degree] = coefficient
        for j in range(degree + 1):
            work[k - degree + j] -= coefficient * denominator[j]
    return quotient, work[:degree]


def cyclotomic(n):
    """Construct Phi_n by exact division, with no symbolic-algebra dependency."""
    polynomials = {}
    for k in range(1, n + 1):
        if n % k:
            continue
        value = [-1] + [0] * (k - 1) + [1]
        for d in range(1, k):
            if k % d == 0:
                value, remainder = polynomial_division(value, polynomials[d])
                require(not any(remainder), "nonexact cyclotomic division")
        polynomials[k] = value
    return polynomials[n]


def reduced(polynomial, phi):
    _, remainder = polynomial_division(polynomial, phi)
    return tuple(remainder)


def gram_entry(n, a, b, j, ell, phi):
    polynomial = [0] * n
    for k in range(n):
        exponent = (a * ((j - k) ** 2 - (ell - k) ** 2) + b * (j - ell)) % n
        polynomial[exponent] += 1
    return reduced(polynomial, phi)
