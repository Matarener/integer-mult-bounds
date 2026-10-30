#!/usr/bin/env python3
"""Exact near-unit rational Stein generators and bounded corroboration.

Produced by Nick Petalas. Apache-2.0.
Gram-Schmidt and the factorization convention are credited to PR4198.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction as F
from math import isqrt
from pathlib import Path

Z = tuple[F, F]
Vector = tuple[Z, ...]
Matrix = tuple[Vector, ...]
ZERO: Z = (F(0), F(0))
MAX_DIM = 8
MAX_BITS = 512
MAX_PRECISION = 128


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def add(x: Z, y: Z) -> Z:
    return x[0] + y[0], x[1] + y[1]


def mul(x: Z, y: Z) -> Z:
    return x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0]


def scale(x: Z, q: F) -> Z:
    return x[0] * q, x[1] * q


def conjugate(x: Z) -> Z:
    return x[0], -x[1]


def inner(x: Vector, y: Vector) -> Z:
    need(len(x) == len(y), "inner dimension")
    answer = ZERO
    for a, b in zip(x, y, strict=True):
        answer = add(answer, mul(conjugate(a), b))
    return answer


def norm2(x: Vector) -> F:
    value = inner(x, x)
    need(value[1] == 0 and value[0] >= 0, "squared norm")
    return value[0]


def power2(exponent: int) -> F:
    return F(1 << exponent) if exponent >= 0 else F(1, 1 << -exponent)


def normalize(n: F, precision: int) -> tuple[F, F, int]:
    """Return c, grid, exponent with n <= c*c < (1+2^-p)^2*n."""
    need(type(n) is F and n > 0, "positive rational squared norm")
    need(type(precision) is int and 1 <= precision <= MAX_PRECISION,
         "precision capacity")
    need(max(n.numerator.bit_length(), n.denominator.bit_length()) <= 65536,
         "normalizer bit capacity")
    exponent = (n.numerator.bit_length() - n.denominator.bit_length()) // 2 + 1
    if power2(2 * (exponent - 1)) >= n:
        exponent -= 1
    grid = power2(exponent - precision - 1)
    quotient = n / (grid * grid)
    floor = isqrt(quotient.numerator // quotient.denominator)
    mantissa = floor + (floor * floor * quotient.denominator < quotient.numerator)
    c = mantissa * grid
    need(power2(2 * (exponent - 1)) < n <= power2(2 * exponent), "binade")
    need((1 << precision) < mantissa <= (1 << (precision + 1)), "mantissa")
    need((c - grid) ** 2 < n <= c * c, "least grid upper bound")
    need(c * c < (1 + power2(-precision)) ** 2 * n, "near-unit bound")
    return c, grid, exponent


def matrix(values: tuple[tuple[object, ...], ...]) -> Matrix:
    need(type(values) is tuple and 1 <= len(values) <= MAX_DIM, "matrix capacity")
    rows = []
    for row in values:
        need(type(row) is tuple and len(row) == len(values), "square matrix")
        entries = []
        for value in row:
            parts = value if type(value) is tuple else (value, 0)
            need(len(parts) == 2 and all(type(x) in (int, F) for x in parts),
                 "exact rational complex entries")
            z = (F(parts[0]), F(parts[1]))
            need(all(max(x.numerator.bit_length(), x.denominator.bit_length())
                     <= MAX_BITS for x in z), "component bit capacity")
            entries.append(z)
        rows.append(tuple(entries))
    return tuple(rows)


def columns(a: Matrix) -> tuple[Vector, ...]:
    return tuple(tuple(a[i][j] for i in range(len(a))) for j in range(len(a)))


def produce(a: Matrix, precision: int) -> tuple[tuple[Vector, Vector, Vector, F], ...]:
    """Return (g, coefficient row, orthogonal residual, c) for each term."""
    a = matrix(a)
    need(type(precision) is int and 1 <= precision <= MAX_PRECISION,
         "precision capacity")
    accepted: list[Vector] = []
    terms = []
    for original in columns(a):
        residual = original
        for previous in accepted:
            weight = scale(inner(previous, residual), 1 / norm2(previous))
            residual = tuple(add(x, scale(mul(v, weight), F(-1)))
                             for x, v in zip(residual, previous, strict=True))
        n = norm2(residual)
        if n == 0:
            continue
        c, _, _ = normalize(n, precision)
        g = tuple(scale(x, 1 / c) for x in residual)
        row = tuple(scale(inner(residual, col), c / n) for col in columns(a))
        need(norm2(g) <= 1, "generator column norm")
        terms.append((g, row, residual, c))
        accepted.append(residual)
    return tuple(terms)


def gram(a: Matrix) -> Matrix:
    cols = columns(a)
    return tuple(tuple(inner(x, y) for y in cols) for x in cols)


def outer(x: Vector, row: Vector) -> Matrix:
    return tuple(tuple(mul(a, b) for b in row) for a in x)


def positive_semidefinite(a: Matrix) -> bool:
    """Independent exact Hermitian Schur test, including zero pivots."""
    n = len(a)
    if any(a[i][j] != conjugate(a[j][i]) for i in range(n) for j in range(n)):
        return False
    work = [list(row) for row in a]
    for k in range(n):
        pivot = work[k][k]
        if pivot[1] or pivot[0] < 0:
            return False
        if pivot[0] == 0:
            if any(work[k][j] != ZERO for j in range(k + 1, n)):
                return False
            continue
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                correction = scale(mul(work[i][k], work[k][j]), -1 / pivot[0])
                work[i][j] = add(work[i][j], correction)
    return True


def independent_rank(a: Matrix) -> int:
    """Gaussian elimination, separate from the producer's orthogonalization."""
    work = [list(row) for row in a]
    count = 0
    for j in range(len(a)):
        pivot = next((i for i in range(count, len(a)) if work[i][j] != ZERO), None)
        if pivot is None:
            continue
        work[count], work[pivot] = work[pivot], work[count]
        z = work[count][j]
        inverse = scale(conjugate(z), 1 / norm2((z,)))
        work[count] = [mul(x, inverse) for x in work[count]]
        for i in range(count + 1, len(a)):
            weight = work[i][j]
            work[i] = [add(x, scale(mul(weight, y), F(-1)))
                       for x, y in zip(work[i], work[count], strict=True)]
        count += 1
    return count


def check_production(a: Matrix, precision: int) -> int:
    terms = produce(a, precision)
    need(len(terms) == independent_rank(a), "exact generator count")
    n = len(a)
    total = [[ZERO for _ in range(n)] for _ in range(n)]
    residuals = tuple(term[2] for term in terms)
    for i, x in enumerate(residuals):
        need(all(inner(x, y) == ZERO for y in residuals[:i]), "orthogonal residuals")
    ga = gram(a)
    for g, row, v, c in terms:
        term = outer(g, row)
        for i in range(n):
            for j in range(n):
                total[i][j] = add(total[i][j], term[i][j])
        coefficient = c * c / norm2(v)
        need(coefficient < (1 + power2(-precision)) ** 2, "strict factor")
        difference = tuple(tuple(add(scale(ga[i][j], coefficient),
                                    scale(mul(conjugate(row[i]), row[j]), F(-1)))
                                 for j in range(n)) for i in range(n))
        need(positive_semidefinite(difference), "row operator-norm domination")
    need(tuple(tuple(row) for row in total) == a, "complete reconstruction")
    return len(terms)


def small_normalizer_oracle(n: F, precision: int) -> F:
    # Bounded exhaustive exponent and mantissa oracle, without isqrt or bit-log.
    for exponent in range(-12, 13):
        if power2(2 * (exponent - 1)) < n <= power2(2 * exponent):
            grid = power2(exponent - precision - 1)
            for q in range((1 << precision) + 1, (1 << (precision + 1)) + 1):
                if (q * grid) ** 2 >= n:
                    return q * grid
    raise ValueError("oracle fixture outside bounded domain")


def check_normalizers() -> dict[str, int]:
    values = sorted({F(a, b) for a in range(1, 49) for b in range(1, 33)})
    cases = 0
    for n in values:
        for p in range(1, 6):
            c, grid, exponent = normalize(n, p)
            need(c == small_normalizer_oracle(n, p), "independent grid oracle")
            need(max(c.numerator.bit_length(), c.denominator.bit_length())
                 <= abs(exponent) + p + 2, "normalizer height")
            need(grid > 0, "positive grid")
            cases += 1
    stress = 0
    for exponent in (-2048, -200, -1, 0, 1, 200, 2048):
        for delta in (F(0), F(1, 1 << 200), F(-1, 1 << 200)):
            for p in (1, 3, 32, 128):
                normalize(power2(2 * exponent) * (1 + delta), p)
                stress += 1
    return {"distinct_small_norms": len(values), "oracle_comparisons": cases,
            "wide_normalizers": stress}


def fixtures() -> tuple[Matrix, ...]:
    alphabet = (0, 1, -1, (0, 1), (0, -1))
    result = [matrix(((a, b), (c, d)))
              for a, b, c, d in itertools.product(alphabet, repeat=4)]
    result.extend(matrix((((a, b),),)) for a in range(-4, 5) for b in range(-4, 5))
    for size in (3, 4, 8):
        result.append(matrix(tuple(tuple(int(i == j) for j in range(size))
                                   for i in range(size))))
        result.append(matrix(tuple(tuple((F(i + 1, j + 1), F(j - i, 7))
                                         for j in range(size)) for i in range(size))))
        result.append(matrix(tuple(tuple(F(1, 1 << (200 * i)) if i == j and i < 2
                                         else 0 for j in range(size))
                                   for i in range(size))))
    result.append(matrix(((1, 0, 0), (1, 0, 0), (1, 0, 0))))
    result.append(matrix(((1, 1, 0), (1, 1 + F(1, 1 << 200), 0), (0, (0, 1), 1))))
    return tuple(result)


def rejected(action, message: str) -> None:
    try:
        action()
    except ValueError:
        return
    raise ValueError("control accepted: " + message)


def check_controls() -> list[str]:
    controls = [
        (lambda: normalize(F(0), 3), "zero norm"),
        (lambda: normalize(F(-1), 3), "negative norm"),
        (lambda: normalize(1.0, 3), "floating norm"),
        (lambda: normalize(F(1), 0), "zero precision"),
        (lambda: normalize(F(1), True), "boolean precision"),
        (lambda: normalize(F(1), MAX_PRECISION + 1), "precision capacity"),
        (lambda: normalize(F(1 << 65536), 3), "normalizer bit capacity"),
        (lambda: matrix(((0.5,),)), "floating entry"),
        (lambda: matrix(((True,),)), "boolean entry"),
        (lambda: matrix(((1, 0),)), "nonsquare input"),
        (lambda: matrix(tuple((0,) * 9 for _ in range(9))), "dimension capacity"),
        (lambda: matrix(((1 << MAX_BITS,),)), "component capacity"),
    ]
    for action, message in controls:
        rejected(action, message)
    need(not positive_semidefinite(matrix(((0, 1), (1, 0)))), "zero pivot control")
    need(not positive_semidefinite(matrix(((1, (0, 1)), ((0, 1), 1)))),
         "Hermitian control")
    need(not positive_semidefinite(matrix(((-1,),))), "negative pivot control")
    need(normalize(F(3), 3)[0] == F(7, 4), "round-up positive fixture")
    need(F(13, 8) ** 2 < 3, "round-down fails column norm")
    need(F(2) ** 2 >= (1 + F(1, 8)) ** 2 * 3, "old binade fails new bound")
    residues = [(u, v) for u in range(3) for v in range(3) if (u*u + v*v) % 3 == 0]
    need(residues == [(0, 0)], "Gaussian-rational exact-unit obstruction")
    return [message for _, message in controls] + [
        "zero PSD pivot", "non-Hermitian matrix", "negative PSD pivot",
        "round-down failure", "old factor-two failure", "mod-three norm obstruction"]


def authenticate_and_hash() -> dict[str, str]:
    package = Path(__file__).resolve().parent
    root = package.parents[1]
    sources = json.loads((package / "SOURCES.json").read_text())
    hashes = {}
    for row in sources["files"]:
        if row["usage"] == "input":
            path = root / row["path"]
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            need(digest == row["sha256"], "source hash: " + row["path"])
            hashes[row["path"]] = digest
    for name in ("README.md", "PROOF.md", "verify.py", "TASK.json", "SOURCES.json", "VERIFY.json"):
        hashes[name] = hashlib.sha256((package / name).read_bytes()).hexdigest()
    return hashes


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    hashes = authenticate_and_hash()
    counts = check_normalizers()
    matrices = fixtures()
    terms = sum(check_production(a, p) for a in matrices for p in (1, 3, 9))
    witness = produce(matrix(((1, 0, 0), (1, 0, 0), (1, 0, 0))), 3)[0]
    need(witness[3] == F(7, 4) and norm2(witness[0]) == F(48, 49), "witness column")
    need(norm2(witness[1]) == F(49, 16), "witness coefficient row")
    report = {"status": "PASS_NEAR_UNIT_STEIN_NORMALIZATION", "claim": "scoped proof",
              **counts, "matrices": len(matrices), "factorizations": 3 * len(matrices),
              "generator_terms": terms, "controls": check_controls(),
              "witness": {"precision": 3, "c": "7/4", "g_norm_squared": "48/49",
                          "a_norm_squared": "49/16", "old_a_norm_squared": "4"},
              "sha256": hashes}
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.receipt is not None:
        with args.receipt.open("x") as output:
            need(output.write(encoded) == len(encoded), "receipt write")
    print(encoded, end="")


if __name__ == "__main__":
    main()
