#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the explicit eight-helper contiguous storage obstruction.

Produced by Nick Petalas. General context: classical dynamic storage allocation;
Ali Romman PR5763 states the split-range interface boundary. No source is imported.
"""

import argparse
from fractions import Fraction
from hashlib import sha256
from itertools import permutations, product
import json
from math import factorial, prod
from pathlib import Path
import sys


# Times are fixed. The last component is width divided by the common scale q.
JOBS = (
    (0, 8, 1), (2, 12, 1), (4, 14, 1), (6, 10, 1),
    (0, 2, 3), (2, 4, 2), (10, 12, 2), (12, 14, 3),
)
CONTIGUOUS = tuple(((x, x + row[2]),) for x, row in zip(
    (0, 1, 4, 2, 1, 2, 2, 0), JOBS))
SPLIT = (
    ((0, 1),), ((1, 2),), ((2, 3),), ((3, 4),),
    ((1, 4),), ((2, 4),), ((0, 1), (3, 4)), ((0, 2), (3, 4)),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def time_overlap(left, right):
    return max(left[0], right[0]) < min(left[1], right[1])


def check_layout(jobs, segments, capacity, contiguous):
    """Check widths, boundaries and pairwise occupied-set intersections."""
    require(len(jobs) == len(segments) == 8, "expected eight helpers")
    require(capacity > 0, "capacity must be positive")
    for i, (row, pieces) in enumerate(zip(jobs, segments)):
        require(row[0] < row[1] and row[2] > 0, "invalid lifetime or width")
        require(1 <= len(pieces) <= 2, "segment count outside bounded model")
        require(not contiguous or len(pieces) == 1, "contiguity violated")
        require(sum(b - a for a, b in pieces) == row[2], "width differs")
        for a, b in pieces:
            require(0 <= a < b <= capacity, "address outside capacity")
        for left, right in zip(pieces, pieces[1:]):
            require(left[1] <= right[0], "own segments intersect or unsorted")
        for j in range(i):
            if time_overlap(row, jobs[j]):
                for a, b in pieces:
                    for c, d in segments[j]:
                        require(b <= c or d <= a, "live address collision")


def scaled_instance(q):
    require(isinstance(q, (int, Fraction)) and q > 0, "positive rational scale required")
    jobs = tuple((a, b, q * w) for a, b, w in JOBS)
    contiguous = tuple(tuple((q * a, q * b) for a, b in row) for row in CONTIGUOUS)
    split = tuple(tuple((q * a, q * b) for a, b in row) for row in SPLIT)
    return jobs, contiguous, split


def check_scales():
    scales = (Fraction(1, 3), Fraction(1, 2), 1, 2, 7, 10**60)
    expected_loads = (4, 4, 3, 4, 3, 4, 4)
    for q in scales:
        jobs, contiguous, split = scaled_instance(q)
        check_layout(jobs, contiguous, 5 * q, True)
        check_layout(jobs, split, 4 * q, False)
        loads = tuple(sum(w for a, b, w in jobs if a <= t < b)
                      for t in range(0, 14, 2))
        require(loads == tuple(q * v for v in expected_loads), "event load differs")
        require(max(loads) == 4 * q, "peak differs")
    # Release at time 2 precedes allocation at time 2.
    require(not time_overlap(JOBS[4], JOBS[5]), "half-open seam overlaps")
    require(time_overlap(JOBS[0], JOBS[4]), "positive overlap omitted")
    return len(scales)


def compressed_layout(order, jobs):
    """Earliest addresses for the overlap orientation induced by a total order."""
    require(len(jobs) == 8 and sorted(order) == list(range(8)), "invalid order")
    bottoms = [0] * 8
    for k, i in enumerate(order):
        bottoms[i] = max((bottoms[j] + jobs[j][2] for j in order[:k]
                          if time_overlap(jobs[i], jobs[j])), default=0)
    capacity = max(bottoms[i] + jobs[i][2] for i in range(8))
    segments = tuple(((bottoms[i], bottoms[i] + jobs[i][2]),) for i in range(8))
    check_layout(jobs, segments, capacity, True)
    return capacity, segments


def check_all_orders():
    minimum = sum(row[2] for row in JOBS)
    count = 0
    for order in permutations(range(8)):
        capacity, _segments = compressed_layout(order, JOBS)
        require(capacity >= 5, "found order below the proved minimum")
        minimum = min(minimum, capacity)
        count += 1
    require(count == factorial(8) == 40320, "incomplete address-order enumeration")
    require(minimum == 5, "contiguous optimum differs")
    return count, minimum


def check_integer_exclusion():
    """Independent coordinate enumeration, without the compression recurrence."""
    choices = tuple(range(5 - row[2]) for row in JOBS)
    require(prod(len(c) for c in choices) == 9216, "coordinate domain differs")
    count = 0
    for bottoms in product(*choices):
        legal = True
        for i in range(8):
            for j in range(i):
                if time_overlap(JOBS[i], JOBS[j]):
                    legal = legal and (bottoms[i] + JOBS[i][2] <= bottoms[j]
                                       or bottoms[j] + JOBS[j][2] <= bottoms[i])
        require(not legal, "found capacity-four coordinate placement")
        count += 1
    require(count == 9216, "incomplete integer-coordinate enumeration")
    return count


def check_controls():
    collision = list(CONTIGUOUS)
    collision[3] = ((1, 2),)
    wrong_width = list(CONTIGUOUS)
    wrong_width[4] = ((1, 3),)
    cases = (
        (CONTIGUOUS, 4, True, "capacity"),
        (tuple(collision), 5, True, "collision"),
        (tuple(wrong_width), 5, True, "width"),
        (SPLIT, 4, True, "contiguity"),
    )
    for segments, capacity, contiguous, expected in cases:
        try:
            check_layout(JOBS, segments, capacity, contiguous)
        except ValueError as error:
            require(expected in str(error), "control failed for another reason")
        else:
            raise ValueError("invalid layout accepted: " + expected)
    # Reverse order exercises the opposite orientation of every overlap edge.
    reverse_capacity, _segments = compressed_layout(tuple(reversed(range(8))), JOBS)
    require(reverse_capacity >= 5, "reverse order violates minimum")
    return len(cases)


def package_hashes():
    package = Path(__file__).resolve().parent
    names = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    result = {}
    for name in names:
        with (package / name).open("rb") as stream:
            raw = stream.read(1024 * 1024 + 1)
        require(len(raw) <= 1024 * 1024, "package file exceeds byte bound")
        result[name] = sha256(raw).hexdigest()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, help="write the generated hash-bound report")
    args = parser.parse_args()
    scales = check_scales()
    order_count, minimum = check_all_orders()
    coordinates = check_integer_exclusion()
    controls = check_controls()
    report = {
        "status": "PASS_CONTIGUOUS_HELPER_STORAGE_GAP",
        "claim_type": "scoped mathematical proof with finite corroboration",
        "unit_contiguous_minimum": minimum,
        "unit_split_minimum": 4,
        "address_orders_checked": order_count,
        "capacity_four_coordinates_checked": coordinates,
        "rational_scales_checked": scales,
        "invalid_layout_controls_rejected": controls,
        "python": sys.version.split()[0],
        "package_sha256": package_hashes(),
        "scope": "Fixed eight-helper family. Positive-real scaling is proved in README.md. "
                 "No physical supplier, source cleanup, kappa or complete multiplication theorem.",
    }
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.receipt is not None:
        require(args.receipt.resolve().parent.is_dir(), "receipt parent does not exist")
        written = args.receipt.write_text(payload, encoding="utf-8")
        require(written == len(payload), "short receipt write")
    print(payload, end="")


if __name__ == "__main__":
    main()
