#!/usr/bin/env python3
"""Exact finite corroboration of the written Gaussian-origin theorem."""

import hashlib
import json
from fractions import Fraction as F
from pathlib import Path
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def model(n, width, theta):
    require(type(n) is int and 2 <= n <= 10, "fixture length outside 2..10")
    require(type(width) is int and 1 <= width < n, "invalid bandwidth")
    require(type(theta) is F and theta > 0, "theta must be a positive Fraction")


def origin(n, beta, theta):
    return F(n - 1, 2) + beta / theta


def exponent(i, j, beta, theta, centre):
    h = j - i
    return (1 + theta) * h * h + 2 * beta * h - theta * (
        (i - centre) ** 2 - (j - centre) ** 2
    )


def simplified(i, j, beta, theta, centre):
    h = j - i
    return (1 + 2 * theta) * h * h + 2 * (beta + theta * (i - centre)) * h


def power_two(exponent_value):
    require(exponent_value.denominator == 1, "nonintegral dyadic exponent")
    k = exponent_value.numerator
    require(abs(k) <= 4096, "fixture exponent exceeds memory bound")
    return F(1, 1 << k) if k >= 0 else F(1 << -k)


def rows(n, width, beta, theta, centre):
    """Use a=96 log(2), so every admitted fixture has rational entries."""
    model(n, width, theta)
    return tuple(
        sum(
            (power_two(96 * exponent(i, j, beta, theta, centre))
             for j in range(n) if 0 < abs(i - j) <= width),
            F(0),
        )
        for i in range(n)
    )


def fixtures():
    cases = edges = reflection_checks = strict_checks = 0
    for n in range(2, 11):
        for width in range(1, min(n - 1, 3) + 1):
            for theta in (F(1, 4), F(1, 8), F(1, 16)):
                for beta in (F(-1, 2), F(0), F(1, 3)):
                    centre = origin(n, beta, theta)
                    best = rows(n, width, beta, theta, centre)
                    for offset in (F(1, 2), F(1)):
                        left = rows(n, width, beta, theta, centre - offset)
                        right = rows(n, width, beta, theta, centre + offset)
                        require(left == right[::-1], "reflection failed")
                        require(max(best) < max(left), "strict optimality failed")
                        require(all(2 * b < l + r for b, l, r in zip(best, left, right)),
                                "strict row convexity failed")
                        reflection_checks += n
                        strict_checks += n + 1
                    for i in range(n):
                        for j in range(n):
                            if 0 < abs(i - j) <= width:
                                q = exponent(i, j, beta, theta, centre)
                                require(q == simplified(i, j, beta, theta, centre),
                                        "chirp expansion failed")
                                expected = ((1 + 2 * theta) * (j - i) ** 2
                                            + 2 * theta * (i - F(n - 1, 2)) * (j - i))
                                require(q == expected, "optimal exponent failed")
                                edges += 1
                    cases += 1
    return dict(parameter_cases=cases, exponent_identities=edges,
                reflected_rows=reflection_checks, strict_inequalities=strict_checks)


def analytic_example():
    n, width, theta, beta = 10, 2, F(1, 1444), F(-1, 2)
    centre = origin(n, beta, theta)
    delta = 1 - (n - 3) * theta
    require(centre == F(-1435, 2) and delta == F(1437, 1444), "example parameters")
    # Machin: atan(1/5) > 1/5-(1/5)^3/3 and atan(1/239) < 1/239.
    pi_lower = 16 * (F(1, 5) - F(1, 375)) - F(4, 239)
    require(pi_lower > F(157, 50), "pi lower certificate")
    require(9 * pi_lower * delta > 28, "exponent lower certificate")
    term = total = F(1)
    for k in range(1, 13):
        term *= F(7, k)
        total += term
    require(total > 1024, "positive Taylor certificate for exp(7)")
    edges = 0
    for i in range(n):
        for j in range(n):
            if 0 < abs(i - j) <= width:
                q = exponent(i, j, beta, theta, centre)
                require(q >= delta * (i - j) ** 2 >= delta, "entry majorant")
                edges += 1
    require(edges == 34 and 2 * width == 4, "banded entry count")
    # 4 exp(-28) < 4 / 2^40 = 2^-38.
    require(F(4, 1 << 40) == F(1, 1 << 38), "row-norm certificate")
    chirp_range = 9 * theta * ((9 - centre) ** 2 - centre ** 2)
    require(chirp_range == 81, "chirp range coefficient of pi")
    return dict(example_entries=edges, optimal_origin=str(centre),
                norm_upper="2^-38", chirp_range="exp(81*pi)")


def reject(call):
    try:
        call()
    except ValueError:
        return
    raise ValueError("invalid input was accepted")


def controls():
    for args in ((1, 1, F(1, 4)), (11, 1, F(1, 4)), (4, 0, F(1, 4)),
                 (4, 4, F(1, 4)), (4, 1, F(0)), (4, 1, F(-1, 4)),
                 (4, 1, 0.25), (True, 1, F(1, 4))):
        reject(lambda args=args: model(*args))
    reject(lambda: power_two(F(1, 2)))
    reject(lambda: power_two(F(4097)))
    n, w, beta, theta = 6, 2, F(-1, 2), F(1, 8)
    centre = origin(n, beta, theta)
    optimum = max(rows(n, w, beta, theta, centre))
    require(max(rows(n, w, beta, theta, F(n - 1, 2) - beta / theta)) > optimum,
            "wrong-sign origin control")
    require(max(rows(n, w, beta, theta, F(n, 2) + beta / theta)) > optimum,
            "wrong-midpoint origin control")
    require(exponent(0, 1, beta, theta, centre) !=
            (1 + theta) + 2 * (beta + theta * (0 - centre)),
            "omitted quadratic theta control")
    require(max(rows(8, 2, F(0), F(1, 4), origin(8, F(0), F(1, 4)))) > 1,
            "optimality must not imply contraction in every parameter regime")
    require(exponent(0, 1, F(0), F(0), F(0)) ==
            exponent(0, 1, F(0), F(0), F(5)), "theta-zero boundary")
    return 15


def receipt():
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        with (package / name).open("rb") as source:
            data = source.read(128 * 1024 + 1)
        require(len(data) <= 128 * 1024, "package file exceeds receipt limit")
        hashes[name] = hashlib.sha256(data).hexdigest()
    return hashes


def main():
    require(sys.argv[1:] in ([], ["--emit"]), "usage: verify.py [--emit]")
    result = dict(schema="gaussian-origin-optimum/v1", **fixtures(),
                  **analytic_example(), controls=controls(), files=receipt())
    if sys.argv[1:] != ["--emit"]:
        print("PASS_GAUSSIAN_ORIGIN_OPTIMUM")
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
