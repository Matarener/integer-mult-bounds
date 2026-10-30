#!/usr/bin/env python3
"""Exact fixed-weight aggregation of the cited packed-bit gap product."""

import argparse
from fractions import Fraction
import hashlib
from itertools import combinations
import json
from math import comb
from pathlib import Path


MAX_LENGTH = 128
MAX_RADIX = 65536
EXHAUSTIVE_LENGTH = 14
RADICES = (4, 6, 64, 128)
PACKAGE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def agreement_rows(length, radix):
    """Return S[m,w] = B**max(m-1,0) times the total agreement."""
    require(type(length) is int and 0 <= length <= MAX_LENGTH,
            "length must be an integer in [0,128]")
    require(type(radix) is int and 4 <= radix <= MAX_RADIX and radix % 2 == 0,
            "radix must be an even integer in [4,65536]")
    rows = [[0] * (length + 1) for _ in range(length + 1)]
    rows[0][0] = 1
    if length >= 1:
        rows[1][0:2] = [1, 1]
    if length >= 2:
        rows[2][0:3] = [radix, 2 * radix, radix - 2]
    for m in range(3, length + 1):
        for w in range(m + 1):
            value = (radix + 1) * rows[m - 1][w] - radix * rows[m - 2][w]
            if w:
                value += ((radix - 2) * rows[m - 1][w - 1]
                          + radix * rows[m - 2][w - 1])
            require(value >= 0, "negative agreement count")
            rows[m][w] = value
    return rows


def pattern_total(length, weight, radix):
    """Enumerate the predecessor's product, without its code or automaton."""
    total = 0
    patterns = 0
    for positions in combinations(range(length), weight):
        product = 1
        span = 0
        for index in range(1, weight):
            gap = positions[index] - positions[index - 1]
            product *= radix ** gap - 2
            span += gap
        total += product * radix ** (max(length - 1, 0) - span)
        patterns += 1
    require(patterns == comb(length, weight), "incomplete source enumeration")
    return total, patterns


def density(rows, length, weight, radix):
    require(0 <= weight <= length < len(rows), "invalid slice")
    denominator = radix ** max(length - 1, 0) * comb(length, weight)
    return 1 - Fraction(rows[length][weight], denominator)


def exhaustive_check():
    patterns = 0
    slices = 0
    for radix in RADICES:
        rows = agreement_rows(EXHAUSTIVE_LENGTH, radix)
        for length in range(EXHAUSTIVE_LENGTH + 1):
            for weight in range(length + 1):
                total, count = pattern_total(length, weight, radix)
                require(total == rows[length][weight],
                        f"coefficient mismatch at B={radix},m={length},w={weight}")
                patterns += count
                slices += 1
    return {"enumerated_source_patterns": patterns, "checked_slices": slices,
            "radices": list(RADICES), "maximum_enumerated_length": EXHAUSTIVE_LENGTH}


def boundary_check():
    cases = 0
    for radix in RADICES:
        rows = agreement_rows(MAX_LENGTH, radix)
        for length in range(MAX_LENGTH + 1):
            scale = radix ** max(length - 1, 0)
            require(rows[length][0] == scale, "zero-weight boundary")
            if length:
                require(rows[length][1] == length * scale, "one-bit boundary")
                require(rows[length][length] == (radix - 2) ** (length - 1),
                        "all-ones boundary")
                require(sum(rows[length]) == 2 * (2 * radix - 1) ** (length - 1),
                        "unrestricted-source marginal")
            cases += 1
    return cases


def controls():
    rows = agreement_rows(10, 64)
    delta = density(rows, 3, 2, 64)
    require(delta == Fraction(43, 2048), "three-pattern hand calculation")
    require(delta != 1 - Fraction(127, 128) ** 2,
            "unrestricted average cannot replace a slice average")
    require(delta != Fraction(1, 32), "fixed-weight maximum is not its mean")
    require(delta != 1 - Fraction(rows[3][2], 64 ** 2),
            "normalization must include the binomial source count")
    rejected = 0
    for length, radix in ((-1, 64), (129, 64), (1, 3), (1, 5),
                          (1, 65538), (True, 64), (1, True)):
        try:
            agreement_rows(length, radix)
        except ValueError:
            rejected += 1
    require(rejected == 7, "invalid-domain controls must reject")
    return 3 + rejected


def evidence():
    result = exhaustive_check()
    result["boundary_rows"] = boundary_check()
    result["negative_controls"] = controls()
    rows = agreement_rows(10, 64)
    result["examples_B64"] = [
        {"m": m, "w": w, "failure_density": str(density(rows, m, w, 64))}
        for m, w in ((3, 2), (10, 2), (10, 5), (10, 10))
    ]
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
             "VERIFY.json", "verify.py")
    result["sha256"] = {
        name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest()
        for name in names
    }
    result["claim_type"] = "scoped proof conditional on the cited gap-product theorem"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="create a new receipt; never overwrite")
    args = parser.parse_args()
    result = evidence()
    encoded = (json.dumps(result, sort_keys=True, indent=2) + "\n").encode("utf-8")
    if args.write is not None:
        with args.write.open("xb") as output:
            require(output.write(encoded) == len(encoded), "incomplete receipt write")
    else:
        require((PACKAGE / "RESULT.json").read_bytes() == encoded,
                "receipt or source bytes differ; regenerate outside the checkout")
    print("PASS_PACKED_FIXED_WEIGHT_REPAIR "
          f"patterns={result['enumerated_source_patterns']} "
          f"slices={result['checked_slices']} controls={result['negative_controls']}")


if __name__ == "__main__":
    main()
