#!/usr/bin/env python3
"""Exact finite corroboration of the rational-shear carry-count theorem."""

from fractions import Fraction
from hashlib import sha1, sha256
from itertools import product
import json
from math import gcd, prod
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
MAX_RADIX = (1 << 127) - 1
MAX_COMPONENT = 1 << 16


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def validate(a, h, q):
    if any(type(value) is not int for value in (a, h, q)):
        raise ValueError("coefficient components and radix must be integers")
    if not 0 < abs(a) <= MAX_COMPONENT or not 1 <= h <= MAX_COMPONENT:
        raise ValueError("nonzero reduced coefficient exceeds checker bounds")
    if not 2 <= q <= MAX_RADIX:
        raise ValueError("radix exceeds checker bounds")
    if gcd(abs(a), h) != 1 or gcd(h, q) != 1:
        raise ValueError("coefficient must be reduced and denominator a radix unit")


def zero_count(a, h, q):
    """Return the exact count; the written theorem has no checker-size cap."""
    validate(a, h, q)
    magnitude = abs(a)
    last = (q - 1) // max(magnitude, h)
    result = (last + 1) * q - magnitude * last * (last + 1) // 2
    require(q <= result <= q * q, "zero count is outside its feasible range")
    return result


def carry_numerator(a, h, q, x, y):
    """Return h*C from the literal canonical low modular product."""
    low = (x + a * y * pow(h, -1, q)) % q
    numerator = h * (x - low) + a * y
    require(numerator % q == 0, "carry numerator must be divisible by the radix")
    return numerator // q


def limit_density(a, h):
    height = max(abs(a), h)
    return 1 - Fraction(1, height) + Fraction(abs(a), 2 * height * height)


def coefficients(bound):
    return tuple((a, h) for h in range(1, bound + 1)
                 for a in range(-bound, bound + 1)
                 if a and gcd(abs(a), h) == 1)


def check_scalar_counts():
    fixtures = pairs = 0
    for q in range(2, 32):
        for a, h in coefficients(12):
            if gcd(h, q) != 1:
                continue
            observed = 0
            for x, y in product(range(q), repeat=2):
                observed += carry_numerator(a, h, q, x, y) == 0
                pairs += 1
            require(observed == zero_count(a, h, q), "literal scalar count differs")
            require(observed == zero_count(-a, h, q), "sign symmetry differs")
            fixtures += 1
    return {"scalar_fixtures": fixtures, "scalar_low_pairs": pairs}


def check_high_translations():
    fixtures = pairs = 0
    for q in range(2, 20):
        for a, h in coefficients(6):
            if gcd(h, q) != 1:
                continue
            for width in (2, 3):
                full_modulus = q ** width
                high_modulus = q ** (width - 1)
                inverse = pow(h, -1, full_modulus)
                observed = 0
                for x, y in product(range(q), repeat=2):
                    full = ((h * x + a * y) * inverse) % full_modulus
                    numerator = carry_numerator(a, h, q, x, y)
                    high = numerator * pow(h, -1, high_modulus) % high_modulus
                    require(full % q == (x + a * y * pow(h, -1, q)) % q,
                            "full product has the wrong low digit")
                    require(full // q == high, "carry fails the full-width oracle")
                    if q >= abs(a) + h:
                        require((full < q) == (numerator == 0),
                                "large-radix exact/residue equivalence differs")
                    observed += full < q
                    pairs += 1
                if q >= abs(a) + h:
                    require(observed == zero_count(a, h, q), "translation count differs")
                fixtures += 1
    # The sufficient large-radix premise cannot simply be omitted.
    numerator = carry_numerator(4, 1, 3, 1, 2)
    require(numerator == 3 and (1 + 4 * 2) % 9 == 0,
            "small-radix cancellation control disappeared")
    return {"high_fixtures": fixtures, "full_width_low_pairs": pairs,
            "small_radix_cancellation_controls": 1}


def determinant(entries, n, q):
    if n == 2:
        return (entries[0] * entries[3] - entries[1] * entries[2]) % q
    require(n == 3 and len(entries) == 9, "only finite 2/3-dimensional oracles exist")
    a, b, c, d, e, f, g, h, i = entries
    return (a * (e * i - f * h) - b * (d * i - f * g)
            + c * (d * h - e * g)) % q


def check_matrix_counts():
    candidates = invertible = fixtures = 0
    for n, q in ((2, 2), (2, 3), (2, 5), (2, 7), (3, 2), (3, 3)):
        menu = tuple((a, h) for a, h in coefficients(4) if gcd(h, q) == 1)
        row_counts = [0] * (q * q)
        actual_group = 0
        for entries in product(range(q), repeat=n * n):
            candidates += 1
            if determinant(entries, n, q) != 0:
                row_counts[q * entries[0] + entries[1]] += 1
                actual_group += 1
                invertible += 1
        completions = prod(q ** n - q ** j for j in range(1, n))
        require(actual_group == (q ** n - 1) * completions, "GL size differs")
        for a, h in menu:
            observed = sum(row_counts[q * x + y]
                           for x, y in product(range(q), repeat=2)
                           if carry_numerator(a, h, q, x, y) != 0)
            expected = (q * q - zero_count(a, h, q)) * q ** (n - 2) * completions
            require(observed == expected, "complete GL carry count differs")
            fixtures += 1
    return {"matrix_candidates": candidates, "invertible_matrices": invertible,
            "matrix_coefficient_fixtures": fixtures}


def check_payload_identity():
    cases = 0
    for q in (3, 5, 7):
        for a, h in coefficients(4):
            if gcd(h, q) != 1:
                continue
            for width in (2, 3):
                full_modulus, high_modulus = q ** width, q ** (width - 1)
                for x, y, hx, hy in product(range(q), range(q), (0, 1), (0, 1)):
                    low = (x + a * y * pow(h, -1, q)) % q
                    k = carry_numerator(a, h, q, x, y)
                    high = (hx + (a * hy + k) * pow(h, -1, high_modulus)) % high_modulus
                    full = (x + q * hx + a * (y + q * hy)
                            * pow(h, -1, full_modulus)) % full_modulus
                    require(low + q * high == full, "arbitrary-high affine identity differs")
                    cases += 1
    return {"arbitrary_high_cases": cases}


def check_limits_and_controls():
    expected = ((1, 1, Fraction(1, 2)), (1, 2, Fraction(5, 8)),
                (1, 4, Fraction(25, 32)), (3, 2, Fraction(5, 6)),
                (4, 1, Fraction(7, 8)))
    for a, h, density in expected:
        require(limit_density(a, h) == density, "displayed limiting density differs")
    for exponent in range(1, 17):
        h = 1 << exponent
        require(limit_density(1, h) > limit_density(1, h // 2),
                "reciprocal dyadic carries must become more frequent")
    invalid = ((0, 1, 5), (2, 4, 5), (1, 0, 5), (1, -2, 5),
               (1, 2, 4), (1, 1, 1), (True, 1, 5), (1, True, 5),
               (1, 1, False), (1.0, 1, 5), (MAX_COMPONENT + 1, 1, 5),
               (1, MAX_COMPONENT + 1, 5), (1, 1, MAX_RADIX + 1))
    for args in invalid:
        try:
            zero_count(*args)
        except ValueError:
            continue
        raise RuntimeError("invalid coefficient or radix was accepted")
    # Named semantic mutations have explicit separating fixtures.
    require(zero_count(1, 4, 5) != zero_count(1, 1, 5), "lost denominator control")
    require(zero_count(3, 2, 7) != 7 * 7 - zero_count(3, 2, 7),
            "zero/nonzero complement control")
    gl_probability = Fraction((25 - zero_count(1, 4, 5)), 24)
    scalar_probability = Fraction((25 - zero_count(1, 4, 5)), 25)
    require(gl_probability != scalar_probability, "GL conditioning control")
    return {"limit_fixtures": len(expected), "dyadic_monotonicity_cases": 16,
            "invalid_inputs_rejected": len(invalid), "semantic_controls": 3}


def source_and_package_hashes():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    for source in sources["retained_predecessors"]:
        payload = (PACKAGE / source["retained_path"]).read_bytes()
        require(sha256(payload).hexdigest() == source["sha256"], "retained source SHA256 differs")
        header = b"blob " + str(len(payload)).encode("ascii") + b"\0"
        require(sha1(header + payload).hexdigest() == source["git_blob"],
                "retained source Git blob differs")
    paths = sorted(path for path in PACKAGE.rglob("*") if path.is_file())
    require(len(paths) <= 16, "unexpected package files or generated leftovers")
    return {str(path.relative_to(PACKAGE)): sha256(path.read_bytes()).hexdigest()
            for path in paths}


def main():
    counts = {}
    counts.update(check_scalar_counts())
    counts.update(check_high_translations())
    counts.update(check_matrix_counts())
    counts.update(check_payload_identity())
    counts.update(check_limits_and_controls())
    receipt = {"status": "PASS_RATIONAL_SHEAR_CARRY_DENSITY",
               "claim_type": "scoped written proof with finite corroboration",
               "counts": counts, "package_sha256": source_and_package_hashes(),
               "no_new_kappa": True}
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
