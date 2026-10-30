#!/usr/bin/env python3
"""Exact table movement for a largest-radix-first cached chirp stream.

Produced by Nick Petalas. Apache-2.0.
"""

from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from math import prod
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def domain(radices, width):
    need(isinstance(radices, tuple) and 1 <= len(radices) <= 64, "axis count")
    need(type(width) is int and 1 <= width <= 64, "word width")
    for radix in radices:
        need(type(radix) is int and 2 <= radix <= 65536, "radix range")
        need(radix & (radix - 1) == 0, "dyadic radix")
    need(prod(radices).bit_length() <= 1025, "arithmetic capacity")


def largest_first(radices):
    domain(radices, 1)
    pivot = max(range(len(radices)), key=radices.__getitem__)
    return (pivot,) + tuple(k for k in range(len(radices)) if k != pivot)


def exact_travel(radices, width):
    """Closed formula, including initialization and final return to cell zero."""
    domain(radices, width)
    total = prod(radices)
    movement = 2 * radices[0]
    prefix = 1
    for k in range(len(radices) - 1):
        prefix *= radices[k]
        movement += 2 * (radices[k] + 1) * (total // prefix)
    prefix = radices[0]
    for j in range(1, len(radices)):
        movement += (radices[j] - 1) * (total // prefix)
        prefix *= radices[j]
    return movement * width


def literal_travel(radices, width):
    """Execute every table read, sweep, carry and final table-head return."""
    domain(radices, width)
    total = prod(radices)
    need(total <= 131072, "enumeration capacity")
    offsets = [0] * len(radices)
    for k in range(1, len(radices)):
        offsets[k] = offsets[k - 1] + radices[k - 1] * width
    digits = [0] * len(radices)
    head = movement = 0
    # Initialization is the first record's complete reverse-axis table read.
    for record in range(total):
        changed = len(radices) - 1
        if record:
            for k in range(len(radices)):
                digits[k] += 1
                if digits[k] < radices[k]:
                    changed = k
                    break
                digits[k] = 0
        for k in range(changed, -1, -1):
            entry = offsets[k] + digits[k] * width
            movement += abs(entry - head) + width
            head = entry + width
    need(head == radices[0] * width, "last read is the last axis-zero entry")
    return movement + head


def check_bound(radices, width):
    domain(radices, width)
    need(radices[0] == max(radices), "a largest radix must be fastest")
    movement = exact_travel(radices, width)
    need(movement <= 7 * prod(radices) * width, "seven-volume movement bound")
    return movement


def phase_stream(radices, order):
    """Cache exact chirp exponents, with emitted coordinates in original axes."""
    domain(radices, 1)
    axes = len(radices)
    need(tuple(sorted(order)) == tuple(range(axes)), "axis permutation")
    total = prod(radices)
    need(total <= 4096, "phase enumeration capacity")
    modulus = 2 * max(radices)
    digits = [0] * axes
    cache = [0] * axes
    for record in range(total):
        changed = axes - 1
        if record:
            for k in range(axes):
                axis = order[k]
                digits[axis] += 1
                if digits[axis] < radices[axis]:
                    changed = k
                    break
                digits[axis] = 0
        for k in range(changed, -1, -1):
            axis = order[k]
            entry = -(2 * axis + 1) * (modulus // (2 * radices[axis]))
            cache[k] = (entry * digits[axis] ** 2
                        + (cache[k + 1] if k + 1 < axes else 0)) % modulus
        yield tuple(digits), cache[0]


def check_phases():
    cases = ((2, 8), (4, 2, 8), (2, 4, 2, 16), (8, 4, 2), (2,))
    records = 0
    for radices in cases:
        modulus = 2 * max(radices)
        expected = {}
        for coordinate in product(*(range(t) for t in radices)):
            expected[coordinate] = sum(
                -(2 * k + 1) * (modulus // (2 * t)) * coordinate[k] ** 2
                for k, t in enumerate(radices)) % modulus
        actual = {}
        for coordinate, phase in phase_stream(radices, largest_first(radices)):
            need(coordinate not in actual, "each named coordinate appears once")
            actual[coordinate] = phase
        need(actual == expected, "named-coordinate quadratic phase equality")
        records += len(actual)
    return len(cases), records


def rejects(call, message):
    try:
        call()
    except ValueError:
        return
    raise ValueError("control accepted: " + message)


def check_controls():
    rejects(lambda: check_bound((2, 512), 1), "largest-radix premise")
    rejects(lambda: literal_travel((65536, 4), 1), "enumeration cap")
    rejects(lambda: exact_travel((3, 4), 1), "non-dyadic input")
    rejects(lambda: exact_travel((), 1), "empty axes")
    rejects(lambda: exact_travel((2,), 0), "zero width")
    rejects(lambda: exact_travel((True,), 1), "Boolean radix")
    rejects(lambda: list(phase_stream((2, 8), (0, 0))), "duplicate axis")
    correct = literal_travel((512, 2), 1)
    need(correct - 512 != exact_travel((512, 2), 1), "omitted return rejected")
    need(correct - 1 != exact_travel((512, 2), 1), "missing move rejected")
    # The same integer tuple cannot be interpreted in the old axis order.
    rows = list(phase_stream((2, 8), (1, 0)))
    need(rows[1][0] == (0, 1) and rows[1][0] != (1, 0), "layout control")
    return 10


def check_movements():
    cases = ordered = 0
    for axes in range(1, 6):
        for radices in product((2, 4, 8), repeat=axes):
            if prod(radices) > 8192:
                continue
            for width in (1, 3, 8):
                need(literal_travel(radices, width) == exact_travel(radices, width),
                     "independent literal/formula movement equality")
                cases += 1
            order = largest_first(radices)
            arranged = tuple(radices[k] for k in order)
            check_bound(arranged, 1)
            ordered += 1
    for axes in range(1, 65):
        radices = (2,) * axes
        expected = 7 * 2 ** axes - 10
        need(exact_travel(radices, 1) == expected, "sharp binary family")
        check_bound(radices, 1)
    skew = [literal_travel(t, 1) for t in ((2, 512), (512, 2))]
    need(skew == [264708, 3078], "complete skew-layout comparison")
    return cases, ordered, skew


def authenticate():
    package = Path(__file__).resolve().parent
    root = package.parents[1]
    sources = json.loads((package / "SOURCES.json").read_text())
    inputs = [row for row in sources["files"] if row["usage"] == "input"]
    need(len(inputs) == 1, "one attributed predecessor input")
    row = inputs[0]
    need(row["path"] == "research/pr4100-chirp-odometer-tariff/README.md",
         "predecessor path")
    need(sha256((root / row["path"]).read_bytes()).hexdigest() == row["sha256"],
         "predecessor bytes")
    return {name: sha256((package / name).read_bytes()).hexdigest() for name in
            ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
             "verify.py")}


def main():
    hashes = authenticate()
    cases, ordered, skew = check_movements()
    phase_cases, records = check_phases()
    controls = check_controls()
    print(json.dumps({
        "status": "PASS_CHIRP_RADIX_ORDER",
        "literal_movement_cases": cases,
        "largest_first_layouts": ordered,
        "sharp_binary_dimensions": 64,
        "phase_cases": phase_cases,
        "named_phase_records": records,
        "controls": controls,
        "skew_closed_table_moves_per_P": skew,
        "skew_ratio_after": str(Fraction(skew[1], 1024)),
        "uniform_table_constant_including_return": 7,
        "package_sha256": hashes,
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
