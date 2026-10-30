#!/usr/bin/env python3
"""Exact finite corroboration of the written infinite-stage tail proof.

Produced by Nick Petalas. Apache-2.0.
"""

from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import sys

import oracle

MAX_K = 128
PACKAGE_FILES = (".gitattributes", "README.md", "SOURCES.json", "TASK.json",
                 "VERIFY.json", "oracle.py", "verify.py")
EXPECTED_NUMERATOR = (71728, 321557, 54309, -248256, -75276, 15552)
EXPECTED_SHIFT = (476748, 48011339, 26053149, 5264496, 469044, 15552)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_k(k):
    if type(k) is not int or not 1 <= k <= MAX_K:
        raise ValueError("K must be an integer in 1..128")


def grouped_slots(k):
    validate_k(k)
    slots = {3: Q(12 * k + 6), 4: Q(58 * k - 43, 8)}
    for p in range(1, k):
        slots[6 * p] = Q(24 * p)
    return slots


def rational_cost(k):
    validate_k(k)
    width = 6 * k + 4
    return sum(2 * mass * Q(width - cap, width + cap)
               for cap, mass in grouped_slots(k).items())


def jensen_cost(k):
    validate_k(k)
    active = Q(12 * (2 * k + 1) * (6 * k + 1), 6 * k + 7)
    bridge_copy = Q(3 * k * (58 * k - 43), 4 * (3 * k + 4))
    idle = Q(24 * k * (k - 1) * (k + 3), 5 * k + 1)
    return active + bridge_copy + idle


def multiply(*factors):
    require(len(factors) <= 5, "polynomial factor limit")
    result = [1]
    for factor in factors:
        require(1 <= len(factor) <= 6, "polynomial degree limit")
        require(len(result) + len(factor) <= 7, "product degree limit")
        out = [0] * (len(result) + len(factor) - 1)
        for i, left in enumerate(result):
            for j, right in enumerate(factor):
                out[i + j] += left * right
        result = out
    return result


def numerator():
    # Denominator is 4(3K+4)(5K+1)(6K+7).
    active = multiply([432], [1, 2], [1, 6], [4, 3], [1, 5])
    bridge = multiply([27], [0, 1], [-43, 58], [1, 5], [7, 6])
    idle = multiply([864], [0, -1, 1], [3, 1], [4, 3], [7, 6])
    deficit = multiply([-500], [-5, 6], [4, 3], [1, 5], [7, 6])
    return tuple(sum(part[i] if i < len(part) else 0
                     for part in (active, bridge, idle, deficit)) for i in range(6))


def shifted(coefficients):
    require(len(coefficients) == 6, "degree-five certificate required")
    return tuple(sum(coefficients[j] * comb(j, i) * 7 ** (j - i)
                     for j in range(i, 6)) for i in range(6))


def evaluate(coefficients, value):
    require(len(coefficients) <= 6, "degree limit")
    result = 0
    for coefficient in reversed(coefficients):
        result = result * value + coefficient
    return result


def proof_certificate(coefficients):
    require(tuple(coefficients) == numerator(), "wrong cleared numerator")
    shift = shifted(coefficients)
    require(all(coefficient > 0 for coefficient in shift), "tail positivity failed")
    return shift


def finite_checks():
    for k in range(1, MAX_K + 1):
        require(grouped_slots(k) == oracle.schedule(k), "literal schedule differs")
        width = 6 * k + 4
        require(all(0 < cap < width and mass > 0
                    for cap, mass in grouped_slots(k).items()), "illegal slot")
        require(rational_cost(k) >= jensen_cost(k), "Jensen bound failed")
        require(oracle.weighted_reciprocal_gap(k) >= 0, "reciprocal bound failed")
        denominator = 4 * (3 * k + 4) * (5 * k + 1) * (6 * k + 7)
        deficit = Q(6 * k - 5, 8)
        require(9 * jensen_cost(k) - 1000 * deficit
                == Q(evaluate(numerator(), k), denominator), "rational identity failed")
        if k >= 7:
            require(Q(9, 1000) * jensen_cost(k) > deficit, "tail bound failed")
            require(Q(9, 1000) * oracle.schedule_cost_lower(k) > deficit,
                    "independent integral lower bound failed")
    return {"literal_schedule_cases": MAX_K, "tail_cases": MAX_K - 6,
            "polynomial_identity_cases": MAX_K}


def reject(operation):
    try:
        operation()
    except ValueError:
        return
    raise ValueError("rejection control was accepted")


def controls():
    count = 0
    for k in (0, -1, True, Q(7), MAX_K + 1):
        reject(lambda: grouped_slots(k))
        reject(lambda: oracle.schedule(k))
        count += 2
    for index in range(6):
        bad = list(EXPECTED_NUMERATOR)
        bad[index] += 1
        reject(lambda: proof_certificate(bad))
        count += 1
    reject(lambda: oracle.midpoint_log_lower(Q(1, 2)))
    reject(lambda: oracle.midpoint_log_lower(2, 0))
    count += 2
    k = 7
    literal = oracle.schedule(k)
    missing_bridge = dict(literal)
    missing_bridge[4] -= 6 * (k - 1)
    missing_bank = dict(literal)
    missing_bank[6] -= 12
    wrong_active = dict(literal)
    wrong_active[3] -= 3 * (2 * k + 1)
    for mutant in (missing_bridge, missing_bank, wrong_active):
        require(mutant != grouped_slots(k), "schedule mutant survived")
        count += 1
    require(evaluate(EXPECTED_NUMERATOR, 6) < 0,
            "K=6 must not be certified by this polynomial")
    return count + 1


def main():
    require(len(sys.argv) == 1, "this verifier accepts no arguments")
    coefficients = numerator()
    require(coefficients == EXPECTED_NUMERATOR, "numerator coefficients differ")
    require(proof_certificate(coefficients) == EXPECTED_SHIFT, "shift coefficients differ")
    result = finite_checks()
    result["rejection_and_scope_controls"] = controls()
    result["cleared_numerator_ascending"] = coefficients
    result["shift_at_seven_ascending"] = EXPECTED_SHIFT
    result["tail_bound"] = "9/1000"
    result["K7_lower_cost"] = str(jensen_cost(7))
    root = Path(__file__).resolve().parent
    result["sha256"] = {name: sha256((root / name).read_bytes()).hexdigest()
                        for name in PACKAGE_FILES}
    print(json.dumps(result, sort_keys=True))
    print("PASS_EISENSTEIN_STAGE_TAIL s>=15 X<9/1000 no_new_kappa")


if __name__ == "__main__":
    main()
