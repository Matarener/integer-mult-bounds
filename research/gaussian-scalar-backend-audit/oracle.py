#!/usr/bin/env python3
"""Certified rational pi and exp(-pi*f) scalar intervals, stdlib only.

Read one query, a query list, or {"queries": [...]} from stdin or --input.
Every query has {"id": ..., "factor": "nonnegative rational", "bits": >=16}.
No files are written without --output. --self-test needs no query input.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def rational(value):
    require(isinstance(value, (int, str)) and not isinstance(value, bool),
            "factor must be an integer or exact rational string")
    try:
        result = Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError("invalid rational factor") from exc
    require(result >= 0, "factor must be nonnegative")
    return result


def fraction_text(value):
    return f"{value.numerator}/{value.denominator}"


def interval_json(lower, upper):
    return {"lower": fraction_text(lower), "upper": fraction_text(upper)}


def validate_bits(bits):
    require(isinstance(bits, int) and not isinstance(bits, bool) and bits >= 16,
            "bits must be an integer at least 16")


def outward_dyadic(lower, upper, bits):
    """Round to a denominator dividing 2^bits, outwards, using integers."""
    require(lower <= upper, "reversed interval")
    scale = 1 << bits
    low_integer = (lower.numerator * scale) // lower.denominator
    high_integer = -((-upper.numerator * scale) // upper.denominator)
    result = Fraction(low_integer, scale), Fraction(high_integer, scale)
    require(result[0] <= lower <= upper <= result[1], "outward rounding failure")
    return result


def pi_bounds(tolerance):
    """pi = 3 sum binom(2k,k)/(16^k(2k+1)); positive ratio < 1/4."""
    require(tolerance > 0, "pi tolerance must be positive")
    total, term, k = Fraction(0), Fraction(3), 0
    while True:
        total += term
        next_term = term * Fraction((2 * k + 1) ** 2,
                                    8 * (k + 1) * (2 * k + 3))
        tail = Fraction(4, 3) * next_term
        require(0 < next_term < term / 4, "pi ratio check failed")
        if tail <= tolerance:
            return total, total + tail, {"terms": k + 1,
                                        "tail_bound": fraction_text(tail)}
        term = next_term
        k += 1


def certified_pi(bits):
    validate_bits(bits)
    return pi_bounds(Fraction(1, 1 << bits))


def alternating_exp_bounds(y, tolerance):
    """Alternating Taylor bounds for e^-y, where 0 <= y <= 1/4."""
    require(0 <= y <= Fraction(1, 4), "Taylor argument outside [0,1/4]")
    require(tolerance > 0, "Taylor tolerance must be positive")
    if y == 0:
        return Fraction(1), Fraction(1), 0
    term = y
    total = 1 - y
    lower, upper, degree = total, Fraction(1), 1
    while upper - lower > tolerance:
        degree += 1
        term = term * y / degree
        if degree % 2:
            total -= term
            lower = total
        else:
            total += term
            upper = total
    require(0 <= lower <= upper <= 1, "Taylor interval outside [0,1]")
    return lower, upper, degree


def exp_negative_interval(x_lower, x_upper, bits):
    """Enclose e^-x for every x in the supplied nonnegative rational interval.

    Required input width <= 2^-bits/16. Exponential is evaluated by a small
    alternating series followed by outward-rounded interval squaring.
    """
    validate_bits(bits)
    epsilon = Fraction(1, 1 << bits)
    require(0 <= x_lower <= x_upper, "invalid exponent interval")
    require(x_upper - x_lower <= epsilon / 16, "exponent interval too wide")
    reductions, divisor = 0, 1
    while x_upper > Fraction(divisor, 4):
        reductions += 1
        divisor *= 2
    y_lower, y_upper = x_lower / divisor, x_upper / divisor
    local_tolerance = Fraction(1, 1 << (bits + reductions + 6))
    lower, _, high_degree = alternating_exp_bounds(y_upper, local_tolerance)
    _, upper, low_degree = alternating_exp_bounds(y_lower, local_tolerance)
    work_bits = bits + reductions + 8
    lower, upper = outward_dyadic(lower, upper, work_bits)
    for _ in range(reductions):
        lower, upper = outward_dyadic(lower * lower, upper * upper, work_bits)
    lower, upper = outward_dyadic(lower, upper, bits + 2)
    require(0 <= lower <= upper <= 1, "exponential interval outside [0,1]")
    require(upper - lower <= epsilon, "exponential width budget exceeded")
    return lower, upper, {"range_reductions": reductions,
                          "working_bits": work_bits,
                          "taylor_degrees": [high_degree, low_degree],
                          "final_dyadic_bits": bits + 2}


def certified_exp_pi(factor, bits):
    """Return exp lower, upper, pi lower, upper, and certificate metadata."""
    validate_bits(bits)
    require(isinstance(factor, Fraction) and factor >= 0,
            "API factor must be a nonnegative Fraction")
    epsilon = Fraction(1, 1 << bits)
    shortcut = 3 * factor >= bits
    pi_tolerance = epsilon / (16 * (max(Fraction(1), factor) if not shortcut else 1))
    p_lower, p_upper, pi_metadata = pi_bounds(pi_tolerance)
    require(3 < p_lower < p_upper < 4, "pi coarse bounds failed")
    if factor == 0:
        lower = upper = Fraction(1)
        metadata = {"method": "zero-exact"}
    elif shortcut:
        lower, upper = Fraction(0), epsilon
        metadata = {"method": "large-factor-shortcut",
                    "inequality": "pi>3, exp(1)>2, 3*factor>=bits"}
    elif p_upper * factor <= epsilon / 4:
        # e^-x >= 1-x, all x>=0. This also avoids huge tiny-factor denominators
        # in the Taylor recurrence and repeated interval arithmetic.
        lower, upper = outward_dyadic(1 - p_upper * factor, Fraction(1), bits + 2)
        metadata = {"method": "tiny-factor-shortcut",
                    "inequality": "1-x<=exp(-x)<=1 for x>=0",
                    "final_dyadic_bits": bits + 2}
    else:
        lower, upper, metadata = exp_negative_interval(p_lower * factor,
                                                      p_upper * factor, bits)
        metadata["method"] = "alternating-taylor-dyadic-squaring"
    require(0 <= lower <= upper <= 1, "output interval outside [0,1]")
    require(upper - lower <= epsilon, "requested absolute precision not attained")
    require(p_upper - p_lower <= epsilon, "pi precision not attained")
    metadata["pi_series"] = pi_metadata
    metadata["absolute_width_bound"] = fraction_text(epsilon)
    metadata["actual_width"] = fraction_text(upper - lower)
    return lower, upper, p_lower, p_upper, metadata


def solve_query(query):
    require(isinstance(query, dict), "query must be an object")
    require(set(query) == {"id", "factor", "bits"}, "query requires exactly id,factor,bits")
    query_id = query["id"]
    require(isinstance(query_id, (str, int)) and not isinstance(query_id, bool),
            "id must be a string or integer")
    factor, bits = rational(query["factor"]), query["bits"]
    lower, upper, pi_lower, pi_upper, metadata = certified_exp_pi(factor, bits)
    return {"id": query_id, "factor": fraction_text(factor), "bits": bits,
            "pi": interval_json(pi_lower, pi_upper),
            "exp_negative_pi_factor": interval_json(lower, upper),
            "certificate": metadata}


def solve_document(document):
    if isinstance(document, dict) and set(document) == {"queries"}:
        queries = document["queries"]
    elif isinstance(document, list):
        queries = document
    else:
        queries = [document]
    require(isinstance(queries, list), "queries must be a list")
    results = [solve_query(query) for query in queries]
    return {"schema": "independent-rational-gaussian-scalar-v1", "results": results,
            "summary": {"queries": len(results),
                        "RESULT": "CERTIFIED: rational absolute-width enclosures",
                        "methods": {method: sum(r["certificate"]["method"] == method for r in results)
                                    for method in sorted({r["certificate"]["method"] for r in results})}}}


def self_test():
    checks = []

    def checked(name, condition):
        require(condition, f"self-test failed: {name}")
        checks.append(name)

    cases = [
        ("zero", Fraction(0), 16),
        ("tiny", Fraction(1, 1 << 4096), 128),
        ("one-seventh", Fraction(1, 7), 53),
        ("unit", Fraction(1), 80),
        ("three-halves", Fraction(3, 2), 128),
        ("near-shortcut-below", Fraction(64, 3) - Fraction(1, 1 << 20), 64),
        ("shortcut-equality", Fraction(64, 3), 64),
        ("near-shortcut-above", Fraction(64, 3) + Fraction(1, 1 << 20), 64),
        ("huge", Fraction(10 ** 1000, 7), 128),
    ]
    examples = []
    intervals = {}
    for name, f, bits in cases:
        lower, upper, pi_lower, pi_upper, metadata = certified_exp_pi(f, bits)
        epsilon = Fraction(1, 1 << bits)
        checked(name + ":width", 0 <= lower <= upper <= 1 and upper - lower <= epsilon)
        checked(name + ":pi-width", 3 < pi_lower < pi_upper < 4 and pi_upper - pi_lower <= epsilon)
        intervals[name] = (lower, upper)
        examples.append({"id": name, "bits": bits,
                         "factor": fraction_text(f), "method": metadata["method"],
                         "exp": interval_json(lower, upper),
                         "pi": interval_json(pi_lower, pi_upper)})
    checked("zero:exact-one", intervals["zero"] == (1, 1))
    checked("tiny:uses-shortcut", examples[1]["method"] == "tiny-factor-shortcut")
    checked("huge:uses-shortcut", examples[-1]["method"] == "large-factor-shortcut")
    checked("shortcut:boundary-monotone", intervals["near-shortcut-below"][0]
            <= intervals["shortcut-equality"][1])
    pi16 = certified_pi(16)
    pi160 = certified_pi(160)
    checked("pi:known-rational-window", Fraction(314159, 100000) < pi160[0]
            < pi160[1] < Fraction(314160, 100000))
    checked("pi:precision-nesting", pi16[0] <= pi160[0] <= pi160[1] <= pi16[1])
    checked("pi:omitted-tail-point-rejected", pi16[0] < pi160[0])
    # A pi-omitting exponential is disjoint from the correct f=1 enclosure.
    missing_pi = exp_negative_interval(Fraction(1), Fraction(1), 80)
    checked("control:pi-omission-rejected", intervals["unit"][1] < Fraction(1, 4)
            < Fraction(1, 3) < missing_pi[0])
    # Positive exponent has reciprocal bounds, both strictly above one.
    checked("control:sign-flip-rejected", 1 / intervals["unit"][1] > 1
            and intervals["unit"][1] < 1)
    exact_y = Fraction(1, 4)
    local = alternating_exp_bounds(exact_y, Fraction(1, 1 << 96))
    truncated_even = 1 - exact_y + exact_y * exact_y / 2
    checked("control:exp-tail-omission-rejected", local[1] < truncated_even)
    rounded = outward_dyadic(Fraction(1, 3), Fraction(1, 3), 16)
    checked("control:rounding-direction", rounded[0] < Fraction(1, 3) < rounded[1]
            and rounded[1] - rounded[0] == Fraction(1, 1 << 16))
    checked("control:inward-rounded-points-rejected", rounded[0] != Fraction(1, 3)
            and rounded[1] != Fraction(1, 3))
    # Independent small-argument Taylor bounds agree with the squaring routine.
    reduced = exp_negative_interval(exact_y, exact_y, 80)
    checked("exp:direct-small-argument-overlap", max(local[0], reduced[0])
            <= min(local[1], reduced[1]))
    a = certified_exp_pi(Fraction(1, 3), 96)
    b = certified_exp_pi(Fraction(2, 3), 96)
    whole = certified_exp_pi(Fraction(1), 96)
    checked("exp:additive-factor-product-overlap", max(a[0] * b[0], whole[0])
            <= min(a[1] * b[1], whole[1]))
    for invalid in [
        {"id": "bad-factor", "factor": "-1/7", "bits": 16},
        {"id": "bad-bits", "factor": "1/7", "bits": 15},
        {"id": "bool-bits", "factor": "1/7", "bits": True},
        {"id": "float-factor", "factor": 0.5, "bits": 16},
    ]:
        rejected = False
        try:
            solve_query(invalid)
        except ValueError:
            rejected = True
        checked("input:" + invalid["id"] + "-rejected", rejected)
    return {"schema": "independent-rational-gaussian-self-test-v1",
            "RESULT": "PASS", "checks": checks, "check_count": len(checks),
            "examples": examples,
            "controls": ["pi omission", "exponent sign", "pi positive tail",
                         "exponential alternating tail", "outward dyadic rounding"],
            "scope": "offline scalar correctness; no physical-preparation speed or integration claim"}


def reject_float(value):
    raise ValueError("JSON floating numbers are not accepted; use exact rational strings")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    require(not (args.self_test and args.input is not None), "self-test does not accept input")
    if args.self_test:
        result = self_test()
    else:
        source = args.input.read_text(encoding="utf-8") if args.input is not None else sys.stdin.read()
        result = solve_document(json.loads(source, parse_float=reject_float, parse_constant=reject_float))
    serialized = canonical(result) + "\n"
    if args.output is not None:
        args.output.write_text(serialized, encoding="ascii")
        summary = (result["summary"] if "summary" in result else
                   {"RESULT": result["RESULT"], "check_count": result["check_count"]})
        print(canonical({"summary": summary,
                         "canonical_json_sha256": hashlib.sha256(serialized.encode("ascii")).hexdigest()}))
    else:
        sys.stdout.write(serialized)


if __name__ == "__main__":
    main()
