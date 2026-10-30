"""Bounded exact evaluations of the composite cyclic-chirp factorization.

Produced by Nick Petalas. Apache-2.0.
The arithmetic here evaluates the formula in a supplied modular ring. Complex
rank and optimality are the written theorem, not consequences of this model.
"""

from math import gcd


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parameters(n, a, b):
    require(type(n) is int and 1 <= n <= 255 and n % 2 == 1,
            "n must be odd and between 1 and 255")
    require(type(a) is int and type(b) is int,
            "coefficients must be integers")
    require(a.bit_length() <= 256 and b.bit_length() <= 256,
            "coefficients exceed the 256-bit reference limit")
    a, b = a % n, b % n
    g = gcd(a, n)
    return a, b, g, n // g


def phase_table(n, modulus, root):
    require(type(modulus) is int and 2 <= modulus <= 1_000_000,
            "invalid modular-ring size")
    require(type(root) is int and 0 < root < modulus,
            "invalid root representative")
    require(pow(root, n, modulus) == 1, "root must have order dividing n")
    return tuple(pow(root, j, modulus) for j in range(n))


def factorized(n, a, b, values, modulus, root):
    """Return E_b C E_b^* x without modifying x; no scratch ABI is claimed."""
    a, b, g, m = parameters(n, a, b)
    phases = phase_table(n, modulus, root)
    require(type(values) in (tuple, list) and len(values) == n,
            "input must have exactly n coordinates")
    require(all(type(x) is int and 0 <= x < modulus for x in values),
            "input coordinates must be modular-ring representatives")
    folded = [0] * m
    for r in range(m):
        folded[r] = sum(phases[(-b * (r + h * m)) % n] * values[r + h * m]
                        for h in range(g)) % modulus
    middle = [0] * m
    for s in range(m):
        middle[s] = sum(phases[(a * (s - r) ** 2) % n] * folded[r]
                        for r in range(m)) % modulus
    return [phases[(b * j) % n] * middle[j % m] % modulus for j in range(n)]


def repair(n, a, values, modulus, root):
    """Sum one chirp for every phase residue modulo gcd(a,n)."""
    _, _, g, _ = parameters(n, a, 0)
    result = [0] * n
    for b in range(g):
        contribution = factorized(n, a, b, values, modulus, root)
        result = [(x + y) % modulus for x, y in zip(result, contribution)]
    return result
