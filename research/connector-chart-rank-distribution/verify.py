#!/usr/bin/env python3
"""Exact chart-rank enumerator and bounded independent matrix oracles."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import product
from math import prod
from pathlib import Path
import json
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def prime_power(q):
    require(type(q) is int and 2 <= q <= 256, "field order capacity")
    for p in range(2, q + 1):
        if q % p == 0:
            remaining = q
            for _ in range(8):
                if remaining % p == 0:
                    remaining //= p
            return remaining == 1
    return False


def gaussian(q, n, k):
    if k < 0 or k > n:
        return 0
    numerator = prod(q ** (n - i) - 1 for i in range(k))
    denominator = prod(q ** (k - i) - 1 for i in range(k))
    require(numerator % denominator == 0, "nonintegral Gaussian coefficient")
    return numerator // denominator


def injections(q, n, k):
    return prod(q ** n - q ** i for i in range(k)) if 0 <= k <= n else 0


def validate(q, n, a, b, c):
    require(prime_power(q), "order is not a prime power")
    require(all(type(x) is int for x in (n, a, b, c)), "dimensions must be integers")
    require(0 <= n <= 12, "codomain dimension capacity")
    require(0 <= a <= n and 0 <= b <= n, "map rank range")
    require(0 <= c <= min(a, b), "intersection dimension range")


def containment_moments(q, n, a, b, c):
    moments = []
    for t in range(n + 1):
        total = 0
        for h in range(c + 1):
            j = t - b + c - h
            if 0 <= j <= n - b:
                spaces = gaussian(q, c, h) * gaussian(q, n - b, j)
                spaces *= q ** ((c - h) * j)
                lifts = q ** (t * (c - h)) * injections(q, t, a - c + h)
                total += spaces * lifts
        moments.append(total)
    return tuple(moments)


def rank_distribution(q, n, a, b, c):
    """Return counts of GL_n charts at each residual rank, including zero."""
    validate(q, n, a, b, c)
    moments = containment_moments(q, n, a, b, c)
    counts = []
    for t in range(n + 1):
        lower = sum(counts[r] * gaussian(q, n - r, t - r) for r in range(t))
        counts.append(moments[t] - lower)
    multiplicity = injections(q, n, n) // injections(q, n, a)
    result = tuple(multiplicity * value for value in counts)
    require(all(value >= 0 for value in result), "negative chart count")
    require(sum(result) == injections(q, n, n), "chart total")
    return result


def minimum_density(q, n, a, b, c):
    validate(q, n, a, b, c)
    s, r = min(a, b), max(a, b)
    numerator = q ** (c * (r - c)) * injections(q, r - c, s - c)
    return Fraction(numerator, injections(q, n, s))


def add(a, b, q):
    return a ^ b if q == 4 else (a + b) % q


def multiply(a, b, q):
    if q != 4:
        return a * b % q
    a0, a1, b0, b1 = a & 1, a >> 1, b & 1, b >> 1
    return (a0 * b0 ^ a1 * b1) | ((a0 * b1 ^ a1 * b0 ^ a1 * b1) << 1)


def negative(a, q):
    return a if q == 4 else -a % q


def matrix_rank(matrix, q):
    require(q in (2, 3, 4, 5), "oracle field capacity")
    require(len(matrix) <= 6, "oracle row capacity")
    width = len(matrix[0]) if matrix else 0
    require(width <= 6 and all(len(row) == width for row in matrix), "oracle shape")
    require(all(type(x) is int and 0 <= x < q for row in matrix for x in row), "field entry")
    rows = [list(row) for row in matrix]
    rank = 0
    for column in range(width):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        value = rows[rank][column]
        inverse = multiply(value, value, q) if q == 4 else pow(value, q - 2, q)
        rows[rank] = [multiply(x, inverse, q) for x in rows[rank]]
        for i in range(rank + 1, len(rows)):
            coefficient = negative(rows[i][column], q)
            rows[i] = [add(x, multiply(coefficient, y, q), q)
                       for x, y in zip(rows[i], rows[rank])]
        rank += 1
    return rank


def matrices(q, rows, columns):
    require(rows <= 3 and columns <= 3 and q ** (rows * columns) <= 6561,
            "matrix enumeration capacity")
    for entries in product(range(q), repeat=rows * columns):
        yield tuple(tuple(entries[i * columns:(i + 1) * columns]) for i in range(rows))


def general_linear(q, n):
    return tuple(matrix for matrix in matrices(q, n, n) if matrix_rank(matrix, q) == n)


def matmul(left, right, q):
    width = len(right[0]) if right else 0
    output = []
    for row in left:
        target = []
        for j in range(width):
            value = 0
            for k in range(len(right)):
                value = add(value, multiply(row[k], right[k][j], q), q)
            target.append(value)
        output.append(tuple(target))
    return tuple(output)


def subtract(left, right, q):
    return tuple(tuple(add(x, negative(y, q), q) for x, y in zip(a, b))
                 for a, b in zip(left, right))


def canonical_pair(n, a, b, c):
    width = a + b - c
    first = tuple(tuple(int(j == i) for j in range(width)) if i < a
                  else (0,) * width for i in range(n))
    second = tuple(tuple(int((i < c and j == i) or
                             (c <= i < b and j == a + i - c))
                         for j in range(width)) for i in range(n))
    return first, second


def check_oracle(q, n, first, second, charts):
    a, b = matrix_rank(first, q), matrix_rank(second, q)
    c = a + b - matrix_rank(first + second, q)
    actual = Counter(matrix_rank(subtract(second, matmul(r, first, q), q), q)
                     for r in charts)
    expected = rank_distribution(q, n, a, b, c)
    require(tuple(actual[t] for t in range(n + 1)) == expected, "matrix oracle mismatch")
    density = minimum_density(q, n, a, b, c)
    require(Fraction(actual[max(a, b) - c], len(charts)) == density, "minimum density")
    require(expected == rank_distribution(q, n, b, a, c), "chart inversion symmetry")
    return len(charts)


def canonical_oracles():
    cases = comparisons = 0
    for q, maximum in ((2, 3), (3, 2), (4, 2), (5, 2)):
        for n in range(maximum + 1):
            charts = general_linear(q, n)
            require(len(charts) == injections(q, n, n), "GL enumeration")
            for a in range(n + 1):
                for b in range(n + 1):
                    for c in range(min(a, b) + 1):
                        first, second = canonical_pair(n, a, b, c)
                        comparisons += check_oracle(q, n, first, second, charts)
                        cases += 1
    return cases, comparisons


def arbitrary_pair_oracles():
    pairs = comparisons = 0
    for q, n, width in ((2, 2, 3), (3, 2, 2)):
        charts = general_linear(q, n)
        maps = tuple(matrices(q, n, width))
        for first in maps:
            transformed = tuple(matmul(r, first, q) for r in charts)
            for second in maps:
                a, b = matrix_rank(first, q), matrix_rank(second, q)
                c = a + b - matrix_rank(first + second, q)
                actual = Counter(matrix_rank(subtract(second, x, q), q) for x in transformed)
                expected = rank_distribution(q, n, a, b, c)
                require(tuple(actual[t] for t in range(n + 1)) == expected,
                        "arbitrary-pair distribution")
                pairs += 1
                comparisons += len(charts)
    return pairs, comparisons


def controls():
    rejected = 0
    bad = ((6, 3, 2, 2, 1), (2, 13, 2, 2, 1), (2, 3, 4, 2, 1),
           (2, 3, 2, 2, 3), (2, 3, 2.0, 2, 1), (1, 3, 2, 2, 1))
    for arguments in bad:
        try:
            rank_distribution(*arguments)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid input accepted")
    require(rank_distribution(2, 3, 2, 2, 1) == (0, 8, 96, 64), "worked example")
    moments = containment_moments(2, 3, 2, 2, 1)
    require(moments == (0, 2, 30, 42), "containment fixture")
    require(tuple(4 * x for x in moments) != (0, 8, 96, 64), "inversion omission control")
    require(sum((0, 2, 24, 16)) != 168, "stabilizer omission control")
    require(multiply(2, 2, 4) == 3 and add(2, 2, 4) == 0, "F4 is not Z/4")
    require(minimum_density(2, 3, 2, 2, 1) == Fraction(1, 21), "density example")
    return rejected, 4


def main():
    canonical, canonical_charts = canonical_oracles()
    arbitrary, arbitrary_charts = arbitrary_pair_oracles()
    rejected, mathematical_controls = controls()
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {name: sha256((package / name).read_bytes()).hexdigest() for name in names}
    receipt = {"canonical_cases": canonical, "canonical_chart_comparisons": canonical_charts,
               "arbitrary_map_pairs": arbitrary, "arbitrary_chart_comparisons": arbitrary_charts,
               "invalid_inputs_rejected": rejected, "mathematical_controls": mathematical_controls,
               "example": [0, 8, 96, 64], "minimum_fraction": "1/21",
               "python": sys.version.split()[0], "sha256": hashes}
    print(json.dumps(receipt, sort_keys=True))
    print("PASS_CONNECTOR_CHART_RANK_DISTRIBUTION")


if __name__ == "__main__":
    main()
