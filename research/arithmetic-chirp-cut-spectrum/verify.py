#!/usr/bin/env python3
"""Exact finite corroboration of the arithmetic-chirp cut theorem.

Produced by Nick Petalas. Apache-2.0.
No floating point arithmetic, predecessor executable, or generated input is used.
"""

from fractions import Fraction
from hashlib import sha256
import json
from math import gcd
from pathlib import Path
import platform
import sys


MAX_ORDER = 36
MAX_BINARY_WIDTH = 128
PACKAGE = Path(__file__).resolve().parent


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def trim(poly: list[int]) -> tuple[int, ...]:
    end = len(poly)
    for _ in range(len(poly)):
        if end == 0 or poly[end - 1] != 0:
            break
        end -= 1
    return tuple(poly[:end])


def divide_monic(dividend: tuple[int, ...], divisor: tuple[int, ...]
                 ) -> tuple[tuple[int, ...], tuple[int, ...]]:
    require(len(dividend) <= MAX_ORDER + 1 and len(divisor) <= MAX_ORDER + 1,
            "polynomial size limit")
    require(bool(divisor) and divisor[-1] == 1, "nonmonic divisor")
    remainder = list(dividend)
    quotient = [0] * max(0, len(dividend) - len(divisor) + 1)
    for offset in reversed(range(len(quotient))):
        coefficient = remainder[offset + len(divisor) - 1]
        quotient[offset] = coefficient
        for j, value in enumerate(divisor):
            remainder[offset + j] -= coefficient * value
    return trim(quotient), trim(remainder)


def cyclotomics(limit: int) -> tuple[tuple[int, ...], ...]:
    require(1 <= limit <= MAX_ORDER, "cyclotomic order limit")
    result: list[tuple[int, ...]] = [()]
    for n in range(1, limit + 1):
        poly = tuple([-1] + [0] * (n - 1) + [1])
        for divisor in range(1, n):
            if n % divisor == 0:
                poly, remainder = divide_monic(poly, result[divisor])
                require(not remainder, "inexact cyclotomic division")
        require(poly[-1] == 1, "cyclotomic leading coefficient")
        result.append(poly)
    return tuple(result)


def gram_entry(n: int, low: int, a: int, b: int, u: int, w: int,
               phi: tuple[int, ...]) -> tuple[int, ...]:
    """Sum the literal quadratic phase differences, then remove row phases."""
    require(1 <= n <= MAX_ORDER and 1 <= low <= n and n % low == 0,
            "invalid split")
    require(0 <= u < low and 0 <= w < low, "invalid row")
    high = n // low
    coefficients = [0] * n
    row_phase = a * (u * u - w * w) + b * (u - w)
    for v in range(high):
        x, y = u + low * v, w + low * v
        exponent = (a * (x * x - y * y) + b * (x - y) - row_phase) % n
        coefficients[exponent] += 1
    _, remainder = divide_monic(tuple(coefficients), phi)
    return remainder


def direct_gram(n: int, low: int, a: int, b: int,
                phi: tuple[int, ...]) -> list[list[int]]:
    matrix = [[0] * low for _ in range(low)]
    high = n // low
    for u in range(low):
        for w in range(u, low):
            value = gram_entry(n, low, a, b, u, w, phi)
            require(value in ((), (high,)), "unexpected dephased Gram entry")
            matrix[u][w] = high if value else 0
            matrix[w][u] = matrix[u][w]
    return matrix


def spectrum_from_gram(matrix: list[list[int]]) -> tuple[int, ...]:
    """Read all-ones Gram blocks from literal entries, without a gcd input."""
    size = len(matrix)
    require(1 <= size <= MAX_ORDER, "Gram size limit")
    unseen = set(range(size))
    eigenvalues = []
    for row in range(size):
        if row not in unseen:
            continue
        block = {j for j in range(size) if matrix[row][j] != 0}
        require(row in block and block <= unseen, "overlapping Gram blocks")
        weight = matrix[row][row]
        for i in block:
            for j in range(size):
                require(matrix[i][j] == (weight if j in block else 0),
                        "Gram component is not a constant block")
        eigenvalues.append(weight * len(block))
        unseen.difference_update(block)
    require(not unseen, "unprocessed Gram rows")
    return tuple(sorted(eigenvalues, reverse=True))


def predicted_spectrum(n: int, low: int, a: int) -> tuple[int, ...]:
    require(1 <= n <= MAX_ORDER and low >= 1 and n % low == 0,
            "invalid factorization")
    high = n // low
    period = high // gcd(2 * a, high)
    quotient, extra = divmod(low, period)
    counts = [quotient + 1] * extra
    counts.extend([quotient] * (period - extra) if quotient else [])
    return tuple(high * count for count in counts)


def exact_census() -> dict[str, int]:
    phis = cyclotomics(MAX_ORDER)
    cases = entries = truncations = nonflat = 0
    for n in range(1, MAX_ORDER + 1):
        for low in range(1, n + 1):
            if n % low:
                continue
            for a in range(n):
                for b in (0, -3):
                    gram = direct_gram(n, low, a, b, phis[n])
                    actual = spectrum_from_gram(gram)
                    expected = predicted_spectrum(n, low, a)
                    require(actual == expected, "cut spectrum mismatch")
                    require(sum(actual) == n, "incorrect Frobenius mass")
                    nonflat += int(len(set(actual)) > 1)
                    for kept in range(len(actual) + 1):
                        tail = sum(Fraction(x, n) for x in actual[kept:])
                        retained = sum(Fraction(x, n) for x in expected[:kept])
                        require(tail == 1 - retained, "truncation mass mismatch")
                        truncations += 1
                    cases += 1
                    entries += low * (low + 1) // 2
    return {"phase_cases": cases, "exact_gram_entries": entries,
            "truncation_values": truncations, "nonflat_cases": nonflat}


def binary_profiles() -> dict[str, int]:
    profiles = cuts = 0
    for width in range(1, MAX_BINARY_WIDTH + 1):
        for valuation in range(1, width + 1):
            a = 0 if valuation == width else 1 << (valuation - 1)
            maximum = 1
            for cut in range(width + 1):
                low, high = 1 << cut, 1 << (width - cut)
                period = high // gcd(2 * a, high)
                rank = min(low, period)
                predicted = 1 << min(cut, max(width - cut - valuation, 0))
                require(rank == predicted, "binary cut formula mismatch")
                require(low % rank == 0, "binary spectrum not flat")
                maximum = max(maximum, rank)
                cuts += 1
            require(maximum == 1 << ((width - valuation) // 2),
                    "binary peak formula mismatch")
            profiles += 1
    return {"binary_profiles": profiles, "binary_cuts": cuts}


def projector_controls() -> int:
    """Construct attaining projectors and check their actual residual traces."""
    phis = cyclotomics(MAX_ORDER)
    checked = 0
    for n, low, a in ((12, 4, 1), (16, 4, 1), (18, 6, 1), (12, 4, 0)):
        gram = direct_gram(n, low, a, -7, phis[n])
        blocks = []
        seen: set[int] = set()
        for i in range(low):
            if i not in seen:
                block = {j for j in range(low) if gram[i][j]}
                blocks.append(block)
                seen.update(block)
        blocks.sort(key=len, reverse=True)
        eigenvalues = spectrum_from_gram(gram)
        for kept in range(len(blocks) + 1):
            projector = [[Fraction(0) for _ in range(low)] for _ in range(low)]
            for block in blocks[:kept]:
                for i in block:
                    for j in block:
                        projector[i][j] = Fraction(1, len(block))
            for i in range(low):
                for j in range(low):
                    square = sum(projector[i][k] * projector[k][j]
                                 for k in range(low))
                    require(square == projector[i][j], "nonidempotent projector")
            trace = sum(projector[i][i] for i in range(low))
            captured = sum(projector[i][j] * gram[j][i]
                           for i in range(low) for j in range(low))
            require(trace == kept, "wrong projector rank")
            require(Fraction(n - captured, n) ==
                    sum(Fraction(x, n) for x in eigenvalues[kept:]),
                    "attaining approximation residual mismatch")
            checked += 1
    return checked


def controls() -> dict[str, int]:
    phis = cyclotomics(MAX_ORDER)
    # The factor two matters; this nontrivial 4-by-4 split has rank two.
    observed = spectrum_from_gram(direct_gram(16, 4, 1, 0, phis[16]))
    require(len(observed) == 2 and len(observed) != 4, "missing-factor-two control")
    # General radix splits need not have a flat spectrum: 4 rows, period 3.
    observed = spectrum_from_gram(direct_gram(12, 4, 1, 5, phis[12]))
    require(observed == (6, 3, 3), "nonflat-spectrum control")
    # A denominator dividing 2a gives a product phase, despite large order.
    require(predicted_spectrum(32, 4, 16) == (32,), "degenerate-phase control")
    # Signs, linear shifts and representatives modulo N cannot affect the spectrum.
    for a in (-37, -12, -1, 0, 1, 12, 37):
        for b in (-29, 0, 31):
            observed = spectrum_from_gram(direct_gram(24, 4, a, b, phis[24]))
            require(observed == predicted_spectrum(24, 4, a), "signed-phase control")
    rejected = 0
    for n, low in ((0, 1), (4, 0), (5, 2), (-1, 1)):
        try:
            predicted_spectrum(n, low, 1)
        except ValueError:
            rejected += 1
    require(rejected == 4, "factorization boundary controls")
    return {"structural_controls": 3, "signed_shift_controls": 21,
            "invalid_input_controls": rejected}


def main() -> None:
    encoded_peak = max(min(1 << k, (1 << (65 - k)) // gcd(2, 1 << (65 - k)))
                       for k in range(66))
    require(encoded_peak == 1 << 32, "encoded width-65 example")
    result = {"status": "PASS_ARITHMETIC_CHIRP_CUT_SPECTRUM",
              "claim_type": "scoped written proof with exact finite corroboration",
              "census": exact_census(), "binary": binary_profiles(),
              "controls": controls(), "attaining_projectors": projector_controls(),
              "environment": {"python": sys.version,
                              "platform": platform.platform(),
                              "machine": platform.machine()},
              "encoded_example": {"width": 65, "a": 1,
                                  "minimum_peak_exact_bond": encoded_peak}}
    hashes = {}
    for name in ("verify.py", "PROOF.md", "README.md", "TASK.json",
                 "SOURCES.json", "VERIFY.json"):
        hashes[name] = sha256((PACKAGE / name).read_bytes()).hexdigest()
    result["package_sha256"] = hashes
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
