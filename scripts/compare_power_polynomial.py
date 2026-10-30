#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Classify a common-base invoice difference for every power 0 < t < 1.

Use classical Euclid and Sturm arithmetic over Q. No numerical roots are used.
The invoice interface retains zxv's comparator and predecessor credits.
Ali Romman with substantial OpenAI Codex assistance. See the linked proof guide.
"""

import argparse
from fractions import Fraction as Q
from functools import reduce
import json
from math import gcd, lcm
from pathlib import Path
import runpy
import sys

INVOICES = runpy.run_path(str(Path(__file__).with_name("compare_recursive_invoices.py")))
require = INVOICES["require"]


def trim(poly):
    values = list(poly)
    while values and not values[-1]:
        values.pop()
    return tuple(values)


def primitive(poly):
    """Remove positive rational content; retain the sign at every real point."""
    poly = trim(poly)
    if not poly:
        return ()
    denominator = lcm(*(Q(c).denominator for c in poly))
    integers = [int(c * denominator) for c in poly]
    content = gcd(*integers)
    return tuple(c // content for c in integers)


def divide(a, b):
    a, b = list(map(Q, trim(a))), trim(b)
    require(bool(b), "Polynomial division by zero")
    quotient = [Q(0)] * max(0, len(a) - len(b) + 1)
    while a and len(a) >= len(b):
        offset, factor = len(a) - len(b), a[-1] / b[-1]
        quotient[offset] = factor
        for i, coefficient in enumerate(b):
            a[offset + i] -= factor * coefficient
        a = list(trim(a))
    return trim(quotient), trim(a)


def derivative(poly):
    return trim(i * c for i, c in enumerate(poly) if i)


def value(poly, x):
    result = Q(0)
    for coefficient in reversed(poly):
        result = result * x + coefficient
    return result


def poly_gcd(a, b):
    a, b = primitive(a), primitive(b)
    while b:
        a, b = b, primitive(divide(a, b)[1])
    return a


def variations(sequence, x):
    signs = [1 if v > 0 else -1 for p in sequence if (v := value(p, x))]
    return sum(a != b for a, b in zip(signs, signs[1:]))


def distinct_roots(poly, left, right):
    """Count roots after square-free reduction; endpoints must not be roots."""
    common = poly_gcd(poly, derivative(poly))
    square_free, remainder = divide(poly, common)
    require(not remainder, "Inexact square-free quotient")
    square_free = primitive(square_free)
    require(value(square_free, left) and value(square_free, right), "Root at Sturm endpoint")
    sequence = [square_free]
    if len(square_free) > 1:
        sequence.append(derivative(square_free))
    while len(sequence[-1]) > 1:
        remainder = divide(sequence[-2], sequence[-1])[1]
        require(bool(remainder), "Unexpected repeated root after square-free reduction")
        sequence.append(primitive(-c for c in remainder))
    a, b = variations(sequence, left), variations(sequence, right)
    return {"square_free": list(square_free), "left_variations": a,
            "right_variations": b, "distinct_roots": a - b}


def common_base(ranks):
    """Find the primitive integer base of the first rank, then check all ranks."""
    number = next((r for r in ranks if r > 1), 2)
    factors, divisor = {}, 2
    while divisor * divisor <= number:
        while number % divisor == 0:
            factors[divisor] = factors.get(divisor, 0) + 1
            number //= divisor
        divisor = 3 if divisor == 2 else divisor + 2
    if number > 1:
        factors[number] = 1
    divisor = gcd(*factors.values())
    base = reduce(lambda a, item: a * item[0] ** (item[1] // divisor), factors.items(), 1)
    exponents = {}
    for rank in ranks:
        remaining, power = rank, 0
        while remaining > 1 and remaining % base == 0:
            remaining //= base
            power += 1
        require(remaining == 1, "Uncancelled ranks are not powers of one integer base")
        exponents[rank] = power
    return base, exponents


def classify_polynomial(poly, base):
    """Keep endpoint zeros separate from the open-interval order."""
    original = trim(poly)
    if not original:
        return {"classification": "equal", "interior_roots": 0, "odd_interior_roots": 0,
                "endpoint_multiplicities": {"1": 0, str(base): 0}, "root_counts": []}
    current = primitive(original)
    endpoints = {}
    for endpoint in (1, base):
        multiplicity = 0
        while not value(current, endpoint):
            current, remainder = divide(current, (-endpoint, 1))
            require(not remainder, "Inexact endpoint quotient")
            current = primitive(current)
            multiplicity += 1
        endpoints[str(endpoint)] = multiplicity
    counts = []
    while len(current) > 1:
        counts.append(distinct_roots(current, 1, base))
        current = poly_gcd(current, derivative(current))
    roots = counts[0]["distinct_roots"] if counts else 0
    odd = sum((-1) ** j * row["distinct_roots"] for j, row in enumerate(counts))
    require(0 <= odd <= roots, "Invalid root multiplicity count")
    # A degree-d nonzero polynomial cannot vanish at d+1 distinct sample points.
    for denominator in range(2, len(original) + 2):
        sample = 1 + Q(base - 1, denominator)
        sample_value = value(original, sample)
        if sample_value:
            break
    require(bool(sample_value), "No nonzero polynomial sample")
    classification = ("crossing" if odd else
                      "nonnegative_with_equality" if roots and sample_value > 0 else
                      "nonpositive_with_equality" if roots else
                      "uniformly_higher" if sample_value > 0 else "uniformly_lower")
    return {"classification": classification, "interior_roots": roots,
            "odd_interior_roots": odd, "endpoint_multiplicities": endpoints,
            "root_counts": counts, "sample": {"x": str(sample), "value": str(sample_value)}}


def compare(old, new):
    invoice = INVOICES["compare_invoices"](old, new)
    delta = {int(r): n for r, n in invoice["signed_net_delta"].items()}
    base, exponents = common_base(delta)
    poly = [0] * (max(exponents.values(), default=0) + 1)
    for rank, count in delta.items():
        poly[exponents[rank]] = count
    require(len(poly) <= 30, "Polynomial degree exceeds the invoice rank limit")
    return {"schema": "integer-mult-power-polynomial/v1", "contract": invoice["contract"],
            "quantity": invoice["quantity"], "signed_net_delta": invoice["signed_net_delta"],
            "base": base, "polynomial_ascending": poly, "exponent_domain": "0 < t < 1",
            "substitution": "x = base^t; 1 < x < base", **classify_polynomial(poly, base),
            "scope": "Declared invoice arithmetic only. No circuit, ownership, compiler or kappa admission."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("old")
    parser.add_argument("new")
    args = parser.parse_args()
    try:
        old, old_pin = INVOICES["load_invoice"](args.old)
        new, new_pin = INVOICES["load_invoice"](args.new)
        report = compare(old, new)
        report["inputs"] = {"old": old_pin, "new": new_pin}
        print(json.dumps(report, indent=2, sort_keys=True))
    except (OSError, ValueError, TypeError, RecursionError) as error:
        print("Polynomial comparison failed: " + str(error), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
