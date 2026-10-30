#!/usr/bin/env python3
"""Exact checks for the new hidden-window equality classification.

Produced by Nick Petalas. Apache-2.0. Standard library only.
The written proof, rather than this finite census, establishes the theorem.
"""

from fractions import Fraction
from hashlib import sha256
from math import isqrt
from pathlib import Path
import json
import platform


MAX_BITS = 256
MAX_H = 16


def require(condition, message):
    if not condition:
        raise ValueError(message)


def bounded_integer(value, low, high, name):
    require(type(value) is int and low <= value <= high, name)


def normalized_attainers(ell):
    """Return every (a,z,c) attaining the bound at normalized budget ell."""
    bounded_integer(ell, 0, 2**MAX_BITS, "normalized budget out of range")
    result = []
    if ell % 4 in (0, 3):
        n = isqrt((ell + 1) // 4)
        if n >= 3 and ell in (4*n*n - 1, 4*n*n):
            result.append((n*(n-1), 2*n*n-1, n*(n+1)))
    if ell % 2 == 0:
        u = isqrt(2*ell + 1)
        n = (u-1) // 2
        if n >= 4 and 2*n*(n+1) == ell:
            result.append((n*(n-1)//2, n*n+n-1, (n+1)*(n+2)//2))
    require(len(result) <= 2, "classification capacity")
    return tuple(sorted(result))


def attainers(h, budget):
    bounded_integer(h, 1, MAX_H, "endpoint multiplicity out of range")
    bounded_integer(budget, 1, 2**MAX_BITS, "call budget out of range")
    return normalized_attainers(budget // (6**h // 2))


def endpoint_data(h, budget, residual):
    """Check literal quadratic hypotheses; return exact comparison data."""
    bounded_integer(h, 1, MAX_H, "endpoint multiplicity out of range")
    bounded_integer(budget, 1, 2**MAX_BITS, "call budget out of range")
    require(type(residual) is tuple and len(residual) == 3, "residual shape")
    a, z, c = residual
    for value in residual:
        bounded_integer(value, 1, 2**MAX_BITS, "coefficient out of range")
    delta = z*z - 4*a*c
    require(delta > 0 and 2*a < z < 4*a, "distinct roots and interior vertex")
    require(a-z+c > 0 and 4*a-2*z+c > 0, "strict interior roots")
    scale = 6**h // 2
    require(scale*(a+z+c) <= budget, "per-profile budget exceeded")
    ell = budget // scale
    cap = (ell-1) // 2
    require(cap >= z > 0, "trace cap")
    gap = cap*cap*delta - z*z
    require(gap >= 0, "discrete bound violated")
    return delta, cap, gap


def multiply(left, right):
    require(len(left) <= 2*MAX_H+3 and len(right) <= 3, "polynomial capacity")
    result = [0] * (len(left)+len(right)-1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i+j] += a*b
    return result


def polynomial(h, residual):
    bounded_integer(h, 1, MAX_H, "endpoint multiplicity out of range")
    a, z, c = residual
    result = [c, -z, a]
    for _ in range(h):
        result = multiply(result, [2, -3, 1])
    return [(-1)**(h+1)*value for value in result]


def evaluate(coefficients, x):
    require(1 <= len(coefficients) <= 2*MAX_H+3, "evaluation capacity")
    value = Fraction(0)
    for coefficient in reversed(coefficients):
        value = value*x + coefficient
    return value


def divide_linear(coefficients, root):
    """Independent monic synthetic division in ascending coefficient order."""
    require(2 <= len(coefficients) <= 2*MAX_H+3, "division capacity")
    quotient = [0] * (len(coefficients)-1)
    quotient[-1] = coefficients[-1]
    for j in range(len(quotient)-2, -1, -1):
        quotient[j] = coefficients[j+1] + root*quotient[j+1]
    require(coefficients[0] + root*quotient[0] == 0, "nonzero remainder")
    return quotient


def divisor_oracle(limit):
    """Enumerate Delta=1 by divisors, without either family formula."""
    bounded_integer(limit, 1, 4096, "divisor oracle limit")
    found = {ell: set() for ell in range(limit+1)}
    trials = 0
    for z in range(1, (limit-1)//2+1, 2):
        product = (z*z-1)//4
        for a in range((z+1)//4+1, (z-1)//2):
            trials += 1
            if product % a:
                continue
            c = product // a
            for ell in (2*z+1, 2*z+2):
                if ell <= limit and a+z+c <= ell:
                    found[ell].add((a, z, c))
    return found, trials


def full_coefficient_oracle(limit):
    """Enumerate all positive coefficient triples and every allowed budget."""
    bounded_integer(limit, 1, 96, "coefficient oracle limit")
    found = {ell: set() for ell in range(limit+1)}
    triples = 0
    eligible = 0
    comparisons = 0
    for a in range(1, limit+1):
        for z in range(1, limit-a+1):
            for c in range(1, limit-a-z+1):
                triples += 1
                delta = z*z-4*a*c
                if not (delta > 0 and 2*a < z < 4*a):
                    continue
                if min(a-z+c, 4*a-2*z+c) <= 0:
                    continue
                eligible += 1
                for ell in range(a+z+c, limit+1):
                    comparisons += 1
                    cap = (ell-1)//2
                    require(cap*cap*delta >= z*z, "oracle inequality")
                    if cap*cap*delta == z*z:
                        found[ell].add((a, z, c))
    return found, (triples, eligible, comparisons)


def check_profiles(oracle):
    profiles = 0
    for ell, residuals in oracle.items():
        for h in range(1, 7):
            scale = 6**h // 2
            for remainder in (0, scale//2, scale-1):
                if ell == 0 and remainder == 0:
                    continue
                budget = scale*ell + remainder
                require(set(attainers(h, budget)) == residuals, "floor budget")
            for residual in residuals:
                delta, cap, gap = endpoint_data(h, scale*ell, residual)
                require(delta == 1 and gap == 0, "attainer comparison")
                a, z, c = residual
                r, s = Fraction(z-1, 2*a), Fraction(z+1, 2*a)
                word = polynomial(h, residual)
                paid_a = [max(-value, 0) for value in word]
                paid_b = [max(value, 0) for value in word]
                count = scale*(a+z+c)
                require(sum(paid_a) == sum(paid_b) == count, "exact counts")
                require(sum(v*2**j for j, v in enumerate(paid_a)) ==
                        sum(v*2**j for j, v in enumerate(paid_b)), "rank mass")
                for root in (1, 2):
                    reduced = word
                    for _ in range(h):
                        reduced = divide_linear(reduced, root)
                    require(evaluate(reduced, root) != 0, "exact multiplicity")
                for x, positive in (((1+r)/2, False), ((r+s)/2, True),
                                    ((s+2)/2, False)):
                    require((evaluate(word, x) > 0) == positive, "window sign")
                require(cap == z and 1 < r < s < 2, "attainer roots")
                profiles += 1
    return profiles


def expect_rejection(function, *arguments):
    try:
        function(*arguments)
    except ValueError:
        return
    raise ValueError("invalid input accepted")


def controls():
    rejected = 0
    bad = ((2, 7, 6), (3, 11, 10), (1, 2, 1), (1, 1, 1),
           (0, 17, 12), (6, -17, 12), (6, 17), [6, 17, 12])
    for residual in bad:
        expect_rejection(endpoint_data, 1, 1000, residual)
        rejected += 1
    expect_rejection(endpoint_data, 1, 104, (6, 17, 12))
    rejected += 1
    for h in (0, MAX_H+1, True):
        expect_rejection(attainers, h, 105)
        rejected += 1
    for budget in (0, -1, 2**MAX_BITS+1, True):
        expect_rejection(attainers, 1, budget)
        rejected += 1
    for ell in (-1, 2**MAX_BITS+1, True):
        expect_rejection(normalized_attainers, ell)
        rejected += 1
    cases = (
        (endpoint_data(1, 105, (5, 15, 11))[2] > 0, "attainable is existential"),
        (not attainers(1, 93), "unattained bound can have windows"),
        (endpoint_data(1, 210, (12, 34, 24))[2] > 0, "scaled strict case"),
        (len(normalized_attainers(144)) == 2, "both families at one budget"),
        (not normalized_attainers(37), "next-budget equality loss"),
    )
    for condition, message in cases:
        require(condition, message)
    large_cases = 0
    for n in (10**6, 10**20, 10**36):
        for ell in (4*n*n-1, 4*n*n, 2*n*(n+1)):
            for residual in normalized_attainers(ell):
                require(endpoint_data(1, 3*ell, residual)[2] == 0, "large integers")
                large_cases += 1
    return {"rejected_inputs": rejected, "semantic_cases": len(cases),
            "large_integer_cases": large_cases}


def check_padding():
    cases = 0
    for h in range(1, 5):
        scale = 6**h // 2
        for ell in (35, 36, 40, 144):
            for residual in normalized_attainers(ell):
                word = polynomial(h, residual)
                for remainder in (0, scale-1):
                    budget = scale*ell + remainder
                    allowance = budget - scale*sum(residual)
                    for common in sorted({0, min(1, allowance), allowance}):
                        for rank in range(len(word)):
                            left = [max(-v, 0) for v in word]
                            right = [max(v, 0) for v in word]
                            left[rank] += common
                            right[rank] += common
                            require(sum(left) == sum(right) <= budget, "padded count")
                            require([b-a for a, b in zip(left, right)] == word,
                                    "common padding changed polynomial")
                            cases += 1
    return cases


def main():
    oracle, divisor_trials = divisor_oracle(4096)
    for ell, residuals in oracle.items():
        require(set(normalized_attainers(ell)) == residuals, "divisor census")
    full, full_counts = full_coefficient_oracle(96)
    for ell, residuals in full.items():
        require(set(normalized_attainers(ell)) == residuals, "coefficient census")
    profiles = check_profiles(oracle)
    control_count = controls()
    padding_cases = check_padding()
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {name: sha256((package/name).read_bytes()).hexdigest() for name in names}
    result = {
        "status": "PASS_HIDDEN_WINDOW_ATTAINMENT_BUDGETS",
        "claim_type": "scoped proof with finite corroboration",
        "normalized_budgets": len(oracle),
        "attainable_normalized_budgets": sum(bool(v) for v in oracle.values()),
        "attaining_residuals": sum(len(v) for v in oracle.values()),
        "divisor_trials": divisor_trials,
        "full_coefficient_triples": full_counts[0],
        "eligible_small_residuals": full_counts[1],
        "small_budget_comparisons": full_counts[2],
        "profile_constructions": profiles,
        "controls": control_count,
        "padding_cases": padding_cases,
        "python": platform.python_version(),
        "file_sha256": hashes,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
