#!/usr/bin/env python3
"""Exact corroboration of the positive-degree Newton residual prefix theorem."""

import hashlib
import json
import math
import platform
import sys
from pathlib import Path

Pair = tuple[int, int]
PHASES: tuple[Pair, ...] = ((1, 0), (0, 1), (-1, 0), (0, -1))
PACKAGE_FILES = (
    "PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def choose(t: int, k: int) -> int:
    """Integer falling-factorial definition, including negative upper indices."""
    require(0 <= k <= 64 and abs(t) <= 256, "binomial domain exceeded")
    value = 1
    for h in range(1, k + 1):
        numerator = value * (t - h + 1)
        require(numerator % h == 0, "nonintegral generalized binomial")
        value = numerator // h
    return value


def multiply(z: Pair, w: Pair) -> Pair:
    return (z[0] * w[0] - z[1] * w[1], z[0] * w[1] + z[1] * w[0])


def divide_pi(z: Pair) -> Pair:
    require((z[0] + z[1]) % 2 == 0, "Gaussian quotient is not integral")
    return ((z[0] + z[1]) // 2, (z[1] - z[0]) // 2)


def residual(n: int, a: int, degree: int, j: int) -> Pair:
    require(2 <= n <= 24 and 1 <= degree < n, "positive-degree domain exceeded")
    require(0 <= a <= n - degree and 0 <= j <= n, "invalid weight or offset")
    total, power = (0, 0), (1, 0)
    for h in range(degree + 1):
        coefficient = choose(j - a, h)
        total = (total[0] + coefficient * power[0],
                 total[1] + coefficient * power[1])
        power = multiply(power, (-1, 1))
    total = multiply(PHASES[a % 4], total)
    phase = PHASES[j % 4]
    value = (phase[0] - total[0], phase[1] - total[1])
    for _ in range(degree + 1):
        value = divide_pi(value)
    return value


def valuation(z: Pair) -> int | None:
    if z == (0, 0):
        return None
    norm = z[0] * z[0] + z[1] * z[1]
    limit = norm.bit_length()
    require(limit <= 1024, "coefficient height bound exceeded")
    for exponent in range(limit):
        if (z[0] + z[1]) % 2:
            return exponent
        z = divide_pi(z)
    raise RuntimeError("valuation iteration bound exhausted")


def demand_tree(coefficients: list[Pair], n: int, q: int) -> list[int]:
    require(2 <= n <= 10 and 0 < q <= 32, "tree resource bound exceeded")
    require(len(coefficients) == n + 1, "coefficient count mismatch")
    size = 1 << n
    tree = [0] * (2 * size)
    betas = [valuation(z) for z in coefficients]
    for label in range(size):
        beta = betas[label.bit_count()]
        tree[size + label] = 0 if beta is None else max(0, q - beta)
    for node in range(size - 1, 0, -1):
        tree[node] = max(tree[2 * node], tree[2 * node + 1])
    return tree


def check_prefixes(tree: list[int], n: int, a: int, degree: int, q: int) -> dict:
    """Compare every literal prefix with a separate binomial-parity oracle."""
    size = 1 << n
    require(len(tree) == 2 * size, "tree size mismatch")
    visited, mass, full = 0, 0, 0
    k = degree + 1
    period = 1 << k.bit_length()
    for depth in range(1, n + 1):
        remaining = n - depth
        level_full = 0
        for bits in range(1 << depth):
            weight = bits.bit_count()
            expected = any((((weight + u - a) % period) & k) == k
                           for u in range(remaining + 1))
            actual = tree[(1 << depth) + bits]
            require((actual == q) == expected, "full-precision prefix mismatch")
            if depth <= n - degree - 1:
                require(actual == q, "forced prefix lost full precision")
            visited += 1
            level_full += actual == q
            mass += (1 << remaining) * actual
        weighted = sum(math.comb(depth, w) for w in range(depth + 1)
                       if any((((w + u - a) % period) & k) == k
                              for u in range(remaining + 1)))
        require(level_full == weighted, "weighted full-prefix count mismatch")
        full += level_full
    sharp_node = (1 << (n - degree)) + (1 << a) - 1
    require(tree[sharp_node] == 0, "sharp zero-band prefix is live")
    lower = size * (n - degree - 1) * q
    require(mass >= lower, "gather lower bound failed")
    return {"prefixes": visited, "full_prefixes": full,
            "mass": mass, "lower_bound": lower}


def check_binomial_lemmas() -> dict:
    parity_cases, difference_cases = 0, 0
    for k in range(1, 65):
        period = 1 << k.bit_length()
        for t in range(-128, 129):
            expected = int(((t % period) & k) == k)
            require(choose(t, k) % 2 == expected, "binary parity lemma failed")
            parity_cases += 1
    for k in range(1, 33):
        for t in range(-64, 65):
            difference = sum((-1) ** (k - r) * math.comb(k, r) * choose(t + r, k)
                             for r in range(k + 1))
            require(difference == 1, "finite-difference no-gap lemma failed")
            difference_cases += 1
    return {"binary_parity_cases": parity_cases,
            "finite_difference_windows": difference_cases}


def check_coefficients() -> dict:
    cases, negative, sharp, windows = 0, 0, 0, 0
    for n in range(2, 25):
        for degree in range(1, n):
            for a in range(n - degree + 1):
                coefficients = [residual(n, a, degree, j) for j in range(n + 1)]
                for j, z in enumerate(coefficients):
                    unit = (z[0] + z[1]) % 2
                    require(unit == choose(j - a, degree + 1) % 2,
                            "first surviving Gaussian digit mismatch")
                    cases += 1
                    negative += j < a
                require(all(z == (0, 0) for z in coefficients[a:a + degree + 1]),
                        "sharp interpolation band is not zero")
                sharp += 1
                for start in range(n - degree):
                    interval = coefficients[start:start + degree + 2]
                    require(any((z[0] + z[1]) % 2 for z in interval),
                            "R+2 consecutive weights contain no unit")
                    windows += 1
    return {"gaussian_coefficients": cases, "negative_offsets": negative,
            "sharp_zero_bands": sharp, "unit_windows": windows}


def check_trees() -> dict:
    profiles, prefixes, sharp, low_degree = 0, 0, 0, 0
    fixture = None
    for n in range(2, 11):
        for degree in range(1, n):
            for a in range(n - degree + 1):
                coefficients = [residual(n, a, degree, j) for j in range(n + 1)]
                for p in (0, 1, 3):
                    q = p + 2 * n - degree - 1
                    tree = demand_tree(coefficients, n, q)
                    result = check_prefixes(tree, n, a, degree, q)
                    profiles += 1
                    prefixes += result["prefixes"]
                    sharp += 1
                    if n >= 4 and degree <= n // 2 - 1:
                        require(2 * result["mass"] >= n * (1 << n) * (p + n),
                                "free-bulk low-degree corollary failed")
                        low_degree += 1
                    if (n, degree, a, p) == (8, 3, 2, 3):
                        fixture = {"n": n, "R": degree, "a": a, "p": p,
                                   "Q": q, **result}
    require(fixture is not None, "missing positive-degree fixture")
    return {"tree_profiles": profiles, "literal_prefixes": prefixes,
            "sharp_cutoff_witnesses": sharp, "free_bulk_cases": low_degree,
            "fixture": fixture}


def check_rejections() -> int:
    n, degree, a, q = 6, 2, 1, 9
    tree = demand_tree([residual(n, a, degree, j) for j in range(n + 1)], n, q)
    # The first eight depth-three nodes are all forced to Q by the theorem.
    rejected = 0
    for node in range(8, 16):
        mutant = tree.copy()
        mutant[node] -= 1
        try:
            check_prefixes(mutant, n, a, degree, q)
        except RuntimeError as error:
            require(str(error) == "full-precision prefix mismatch",
                    "mutant rejected for an unexpected reason")
            rejected += 1
        else:
            raise RuntimeError("underprecision mutant accepted")
    return rejected


def main() -> None:
    require(sys.version_info >= (3, 12), "Python 3.12 or later is required")
    result = {"status": "PASS_NEWTON_RESIDUAL_PREFIX_FLOOR",
              "claim_type": "scoped written proof with finite corroboration",
              "lemmas": check_binomial_lemmas(),
              "coefficients": check_coefficients(),
              "trees": check_trees(), "rejected_underprecision_profiles": check_rejections()}
    package = Path(__file__).resolve().parent
    hashes = {}
    for name in PACKAGE_FILES:
        data = (package / name).read_bytes()
        require(len(data) <= 16 * 1024 * 1024, "package file size limit exceeded")
        hashes[name] = hashlib.sha256(data).hexdigest()
    result["receipt"] = {"package_sha256": hashes, "python": platform.python_version(),
                         "implementation": platform.python_implementation(),
                         "optimized": bool(sys.flags.optimize)}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
