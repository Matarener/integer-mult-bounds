#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bounded exact certificates for the ordered-shear admissible-prime criterion."""
from fractions import Fraction as Q
from itertools import combinations, permutations, product
from math import gcd
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
PRIMES = (2, 3, 5, 7, 11)
MAX_BYTES = 1 << 20


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read_bounded(path):
    with path.open("rb") as stream:
        payload = stream.read(MAX_BYTES + 1)
    need(len(payload) <= MAX_BYTES, "file capacity")
    return payload


def identity(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def multiply(a, b):
    n = len(a)
    return [[sum((a[i][k] * b[k][j] for k in range(n)), Q(0))
             for j in range(n)] for i in range(n)]


def eliminate(matrix):
    """Return X, P, Y with X A Y=P, preserving the source's physical order."""
    n = len(matrix)
    need(1 <= n <= 3 and all(len(row) == n for row in matrix), "matrix dimensions")
    need(all(type(x) is int and abs(x) <= 512 for row in matrix for x in row),
         "integer matrix domain")
    a = [[Q(x) for x in row] for row in matrix]
    left, right = identity(n), identity(n)
    rows, cols = list(range(n)), list(range(n))
    for _ in range(n):
        candidates = [(i, j) for i in rows for j in reversed(cols) if a[i][j]]
        if not candidates:
            break
        r, c = candidates[0]
        pivot = a[r][c]
        for j in cols:
            if j < c:
                coefficient = -a[r][j] / pivot
                for i in range(n):
                    a[i][j] += coefficient * a[i][c]
                    right[i][j] += coefficient * right[i][c]
        for i in rows:
            if i > r:
                coefficient = -a[i][c] / pivot
                for j in range(n):
                    a[i][j] += coefficient * a[r][j]
                    left[i][j] += coefficient * left[r][j]
        for j in range(n):
            a[r][j] /= pivot
            left[r][j] /= pivot
        rows.remove(r)
        cols.remove(c)
    need(multiply(multiply(left, matrix), right) == a, "factor identity")
    need(all(x in (0, 1) for row in a for x in row), "zero/one pattern")
    need(all(sum(row) <= 1 for row in a), "pattern row capacity")
    need(all(sum(a[i][j] for i in range(n)) <= 1 for j in range(n)),
         "pattern column capacity")
    return left, a, right


def determinant(matrix):
    n = len(matrix)
    total = 0
    for order in permutations(range(n)):
        inversions = sum(order[i] > order[j] for i in range(n) for j in range(i + 1, n))
        term = (-1) ** inversions
        for i in range(n):
            term *= matrix[i][order[i]]
        total += term
    return total


def minor_data(matrix):
    """Independent Leibniz-minor oracle, including the top determinantal divisor."""
    rows, cols = len(matrix), len(matrix[0])
    rank, divisor, checked = 0, 1, 0
    for size in range(1, min(rows, cols) + 1):
        current = 0
        for rs in combinations(range(rows), size):
            for cs in combinations(range(cols), size):
                value = determinant([[matrix[i][j] for j in cs] for i in rs])
                current = gcd(current, value)
                checked += 1
        if current:
            rank, divisor = size, abs(current)
    return rank, divisor, checked


def modular_rank(matrix, prime):
    a = [[x % prime for x in row] for row in matrix]
    height, width, rank = len(a), len(a[0]), 0
    for col in range(width):
        candidates = [i for i in range(rank, height) if a[i][col]]
        if not candidates:
            continue
        pivot = candidates[0]
        a[rank], a[pivot] = a[pivot], a[rank]
        inverse = pow(a[rank][col], -1, prime)
        a[rank] = [x * inverse % prime for x in a[rank]]
        for i in range(rank + 1, height):
            scale = a[i][col]
            a[i] = [(x - scale * y) % prime for x, y in zip(a[i], a[rank])]
        rank += 1
        if rank == height:
            break
    return rank


def local_lower_unit(matrix, prime):
    n = len(matrix)
    triangular = all(matrix[i][j] == 0 for i in range(n) for j in range(i + 1, n))
    integral = all(x.denominator % prime != 0 for row in matrix for x in row)
    units = all(matrix[i][i].numerator % prime != 0 for i in range(n))
    return triangular and integral and units


def check_matrix(matrix):
    left, pattern, right = eliminate(matrix)
    n, records, minors = len(matrix), [], 0
    for end in range(1, n + 1):
        for start in range(n):
            block = [row[start:] for row in matrix[:end]]
            rank, divisor, count = minor_data(block)
            need(rank == sum(pattern[i][j] for i in range(end) for j in range(start, n)),
                 "ordered rational rank profile")
            records.append((block, rank, divisor))
            minors += count
    for prime in PRIMES:
        same_profile = all(modular_rank(block, prime) == rank for block, rank, _ in records)
        unit_divisors = all(divisor % prime != 0 for _, _, divisor in records)
        admitted = local_lower_unit(left, prime) and local_lower_unit(right, prime)
        need(same_profile == unit_divisors == admitted, "intrinsic prime criterion")
    return minors, sum(not all(divisor % p for _, _, divisor in records) for p in PRIMES)


def mul2(a, b, modulus):
    return ((a[0] * b[0] + a[1] * b[2]) % modulus,
            (a[0] * b[1] + a[1] * b[3]) % modulus,
            (a[2] * b[0] + a[3] * b[2]) % modulus,
            (a[2] * b[1] + a[3] * b[3]) % modulus)


def finite_ring_oracle(modulus):
    """Enumerate every invertible lower pair and every 2x2 partial permutation."""
    need(modulus in (2, 3, 4, 5, 8, 9), "finite oracle modulus")
    units = [x for x in range(modulus) if gcd(x, modulus) == 1]
    lower = [(a, 0, b, d) for a, d in product(units, repeat=2) for b in range(modulus)]
    patterns = ((0, 0, 0, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0),
                (0, 0, 0, 1), (1, 0, 0, 1), (0, 1, 1, 0))
    reached, products_checked = set(), 0
    for left in lower:
        for pattern in patterns:
            first = mul2(left, pattern, modulus)
            for right in lower:
                reached.add(mul2(first, right, modulus))
                products_checked += 1
    cases = 0
    for value in range(modulus):
        admissible = value == 0 or gcd(value, modulus) == 1
        for diagonal in (0, 1):
            need(((1, value, 0, diagonal) in reached) == admissible,
                 "sharp first failing width")
            cases += 1
    return products_checked, cases, len(reached)


def reject(condition, message):
    """The condition describes an explicitly false proposed criterion."""
    need(not condition, "false claim accepted: " + message)


def controls():
    a = [[1, 2], [0, 0]]
    b = [[1, 2], [0, 1]]
    need(modular_rank(a, 2) == 1 and modular_rank(b, 2) == 2, "total rank controls")
    need(determinant(b) == 1, "unimodular control")
    left, pattern, right = eliminate(b)
    reject(local_lower_unit(left, 2) and local_lower_unit(right, 2), "full rank suffices")
    reject(minor_data([b[0][1:]])[1] % 2 != 0, "determinant alone suffices")
    reject(pattern == [[1, 0], [0, 1]], "rational and special-fiber patterns agree")
    changed = [row[:] for row in left]
    changed[0][0] += 1
    reject(multiply(multiply(changed, b), right) == pattern, "changed factor")
    reject(local_lower_unit([[Q(1), Q(1)], [Q(0), Q(1)]], 3), "upper factor")
    reject(local_lower_unit([[Q(1, 3), Q(0)], [Q(0), Q(1)]], 3), "nonintegral factor")
    reject(local_lower_unit([[Q(3), Q(0)], [Q(0), Q(1)]], 3), "nonunit diagonal")
    for malformed in ([], [[1, 2]], [[True]], [[513]]):
        try:
            eliminate(malformed)
        except ValueError:
            continue
        raise ValueError("invalid matrix accepted")
    return 7, 4


def source_hashes():
    pins = json.loads(read_bounded(HERE / "SOURCES.json"))
    need(len(pins["files"]) <= 8, "source inventory capacity")
    for row in pins["files"]:
        if row["usage"] == "input":
            need(row["path"] == "upstream/build/sections/04-swap.tex", "source input domain")
            need(hashlib.sha256(read_bounded(ROOT / row["path"])).hexdigest() == row["sha256"],
                 "source bytes")
    return {name: hashlib.sha256(read_bounded(HERE / name)).hexdigest() for name in FILES}


def main():
    hashes = source_hashes()
    matrices, minors, exclusions = 0, 0, 0
    for dimension, alphabet in ((2, (-2, -1, 0, 1, 2)), (3, (0, 1))):
        for values in product(alphabet, repeat=dimension * dimension):
            matrix = [list(values[i * dimension:(i + 1) * dimension]) for i in range(dimension)]
            count, failed_primes = check_matrix(matrix)
            matrices += 1
            minors += count
            exclusions += failed_primes
    products_checked, family_cases, reachable = 0, 0, {}
    for modulus in (2, 3, 4, 5, 8, 9):
        count, cases, size = finite_ring_oracle(modulus)
        products_checked += count
        family_cases += cases
        reachable[str(modulus)] = size
    false_claims, invalid_inputs = controls()
    print(json.dumps(dict(status="PASS_ORDERED_SHEAR_ADMISSIBLE_PRIMES", matrices=matrices,
                          prime_tests=matrices * len(PRIMES), minors=minors,
                          excluded_matrix_prime_pairs=exclusions,
                          finite_ring_factor_products=products_checked,
                          finite_ring_family_cases=family_cases, reachable_matrices=reachable,
                          false_claim_controls=false_claims, invalid_input_controls=invalid_inputs,
                          package_sha256=hashes,
                          scope="scoped written prime-admissibility proof; finite corroboration; no new kappa"),
                     sort_keys=True))


if __name__ == "__main__":
    main()
