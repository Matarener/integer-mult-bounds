#!/usr/bin/env python3
"""Exact paired-color grouping checks; produced by Nick Petalas, Apache-2.0."""

import argparse
from fractions import Fraction
import hashlib
import json
from math import comb
from pathlib import Path
import sys


MAX_COLORS = 256
PACKAGE_FILES = (
    "README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, low, high):
    require(type(value) is int and low <= value <= high, "integer out of domain")


def first_batch_count(colors):
    integer(colors, 1, MAX_COLORS)
    return (2 * colors + 2) // 3


def grouping(colors, batches):
    integer(colors, 1, MAX_COLORS)
    integer(batches, first_batch_count(colors), colors)
    result = [[2 * color, 2 * color + 1] for color in range(batches)]
    for index in range(colors - batches):
        color = batches + index
        result[2 * index].append(2 * color)
        result[2 * index + 1].append(2 * color + 1)
    return result


def inventory(colors, groups):
    integer(colors, 1, MAX_COLORS)
    require(isinstance(groups, (list, tuple)), "groups must be a sequence")
    require(1 <= len(groups) <= 2 * colors, "invalid batch count")
    entries = []
    incidences = 0
    for batch in groups:
        require(isinstance(batch, (list, tuple)) and 1 <= len(batch) <= 3,
                "batch capacity or emptiness")
        for target in batch:
            integer(target, 0, 2 * colors - 1)
            entries.append(target)
        incidences += len({target // 2 for target in batch})
    require(sorted(entries) == list(range(2 * colors)), "targets not a partition")
    return len(groups), incidences


def partitions(targets):
    """Canonical set partitions with block size at most three; no recursion."""
    integer(targets, 1, 10)
    counts = [1] + [0] * targets
    for size in range(1, targets + 1):
        counts[size] = counts[size - 1]
        if size >= 2:
            counts[size] += (size - 1) * counts[size - 2]
        if size >= 3:
            counts[size] += comb(size - 1, 2) * counts[size - 3]
    stack = [(0, ())]
    # At depth k there are exactly counts[k] canonical partial partitions.
    for _ in range(sum(counts)):
        require(bool(stack), "enumeration ended before its exact node bound")
        target, blocks = stack.pop()
        if target == targets:
            yield blocks
            continue
        stack.append((target + 1, blocks + ((target,),)))
        for index in range(len(blocks)):
            if len(blocks[index]) < 3:
                changed = blocks[:index] + (blocks[index] + (target,),) + blocks[index + 1:]
                stack.append((target + 1, changed))
    require(not stack, "enumeration exceeded its exact node bound")


def exhaustive_frontiers():
    rows = []
    for colors in range(1, 6):
        minima = {}
        count = 0
        for blocks in partitions(2 * colors):
            batches, incidences = inventory(colors, blocks)
            minima[batches] = min(minima.get(batches, 2 * colors + 1), incidences)
            count += 1
        require(min(minima) == first_batch_count(colors), "capacity lower bound")
        for batches in range(first_batch_count(colors), colors + 1):
            require(minima[batches] == 2 * colors - batches, "frontier mismatch")
        for batches in range(colors + 1, 2 * colors + 1):
            require(minima[batches] >= colors, "dominated range mismatch")
        rows.append({"colors": colors, "partitions": count,
                     "minimum_incidences": minima})
    return rows


def constructive_checks():
    cases = 0
    equality_colors = []
    for colors in range(1, MAX_COLORS + 1):
        first = first_batch_count(colors)
        for batches in range(first, colors + 1):
            actual = inventory(colors, grouping(colors, batches))
            require(actual == (batches, 2 * colors - batches), "bad construction")
            cases += 1
        dense_bill = 24 * colors - 6 * first
        require(9 * dense_bill <= 10 * 18 * colors, "sharp ratio failed")
        equality = 9 * dense_bill == 10 * 18 * colors
        require(equality == (colors % 3 == 0), "ratio equality classification")
        if equality:
            equality_colors.append(colors)
    return {"groupings": cases, "sharp_ratio_equality_colors": equality_colors}


def price_checks(rows):
    prices = tuple(Fraction(value, 2) for value in (1, 2, 3, 4, 6, 12, 24))
    cases = 0
    for row in rows:
        colors = row["colors"]
        first = first_batch_count(colors)
        for setup in prices:
            for color_price in prices:
                bills = [setup * batches + color_price * incidences
                         for batches, incidences in row["minimum_incidences"].items()]
                chosen = colors if setup < color_price else first
                expected = setup * chosen + color_price * (2 * colors - chosen)
                require(min(bills) == expected, "price endpoint failed")
                if setup == color_price:
                    for batches in range(first, colors + 1):
                        actual = row["minimum_incidences"][batches]
                        require(setup * batches + color_price * actual == expected,
                                "equal-price tie failed")
                cases += 1
    return cases


def rejection_checks():
    bad = (
        (0, [[0, 1]]), (True, [[0, 1]]), (1, []), (1, [[]]),
        (1, [[0, 0]]), (1, [[0]]), (1, [[0, 2]]), (1, [[False, 1]]),
        (2, [[0, 1, 2, 3]]), (1, "01"),
    )
    for colors, groups in bad:
        try:
            inventory(colors, groups)
        except ValueError:
            continue
        raise ValueError("malformed grouping accepted")
    for colors, batches in ((3, 1), (3, 4), (1, True), (257, 200)):
        try:
            grouping(colors, batches)
        except ValueError:
            continue
        raise ValueError("out-of-domain constructor input accepted")
    return len(bad) + 4


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, help="write generated evidence outside the package")
    args = parser.parse_args()
    package = Path(__file__).resolve().parent
    if args.receipt is not None:
        destination = args.receipt.resolve()
        require(not destination.is_relative_to(package), "receipt must be outside package")
    rows = exhaustive_frontiers()
    construction = constructive_checks()
    result = {"status": "PASS_PAIRED_COLOR_BATCH_FRONTIER",
              "claim_type": "scoped written proof with finite corroboration",
              "exhaustive_frontiers": rows, "construction": construction,
              "price_cases": price_checks(rows), "rejection_controls": rejection_checks(),
              "python": sys.version.split()[0], "optimized": sys.flags.optimize,
              "source_sha256": {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
                                for name in PACKAGE_FILES}}
    dense = inventory(3, [[0, 1, 4], [2, 3, 5]])
    separate = inventory(3, [[0, 1], [2, 3], [4, 5]])
    require(6 * dense[0] + 12 * dense[1] == 60, "dense witness")
    require(6 * separate[0] + 12 * separate[1] == 54, "optimal witness")
    result["sharp_witness"] = {"dense_bill": 60, "optimal_bill": 54, "ratio": "10/9"}
    encoded = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.receipt is not None:
        args.receipt.write_text(encoded, encoding="utf-8")
    print(encoded, end="")


if __name__ == "__main__":
    main()
