#!/usr/bin/env python3
"""Exact certificates for the bare Pascal population and local-ledger model."""

import hashlib
import itertools
import json
import math
from fractions import Fraction as Q
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
MAX_HEIGHT = 65
MAX_DEPTH = 256
SCALE = 10**12


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parameters(height, depth):
    require(type(height) is int and 0 <= height <= MAX_HEIGHT, "height range")
    require(type(depth) is int and 0 <= depth <= MAX_DEPTH, "depth range")


def validate_population(start, depth):
    parameters(len(start) - 1, depth)
    require(all(type(x) is int and 0 <= x < 2**256 for x in start),
            "population entries")
    require(any(start), "empty productive population")


def choose(n, k):
    return math.comb(n, k) if k <= n else 0


def closed_population(start, depth):
    validate_population(start, depth)
    return tuple(sum(choose(depth, h - j) * start[j] for j in range(h + 1))
                 for h in range(len(start)))


def literal_population(start, depth):
    validate_population(start, depth)
    current = tuple(start)
    for _ in range(depth):
        current = (current[0],) + tuple(current[h] + current[h - 1]
                                       for h in range(1, len(current)))
    return current


def optimum(height, depth):
    parameters(height, depth)
    return Q(choose(depth, height),
             sum(choose(depth, k) for k in range(height + 1)))


def power_bounds(rank):
    require(type(rank) is int and 1 <= rank <= 17, "power rank range")
    if rank == 1:
        return Q(1), Q(1)
    # Integer-only certificate: (r^(4983/5000) * SCALE)^5000 is target.
    target = rank**4983 * SCALE**5000
    lower, upper = SCALE, rank * SCALE
    for _ in range(48):
        if upper - lower == 1:
            break
        middle = (lower + upper) // 2
        if middle**5000 <= target:
            lower = middle
        else:
            upper = middle
    require(upper - lower == 1, "integer root bisection exhausted")
    require(lower**5000 <= target <= upper**5000, "integer power certificate")
    return Q(lower, SCALE), Q(upper, SCALE)


def ledger_bounds():
    # Cited PR5037 local invoice, used as a premise, not recounted from a word.
    target = {4: 56, 7: 14, 8: 94, 9: 652, 17: 224}
    paid = {1: 4656, 2: 920, 3: 1386}
    bounds = {r: power_bounds(r) for r in sorted(target.keys() | paid.keys())}
    lower = sum(n * bounds[r][0] for r, n in target.items())
    lower -= sum(n * bounds[r][1] for r, n in paid.items())
    upper = sum(n * bounds[r][1] for r, n in target.items())
    upper -= sum(n * bounds[r][0] for r, n in paid.items())
    omitted = (112 * bounds[17][0], 112 * bounds[17][1])
    require(Q(0) < lower < upper and Q(0) < omitted[0] <= omitted[1],
            "positive local coefficients")
    return (lower, upper), omitted


def enclosure(bounds):
    lower, upper = bounds
    require(lower <= upper, "ordered interval")
    scale = 10**9
    lo = lower.numerator * scale // lower.denominator
    hi = -((-upper.numerator * scale) // upper.denominator)
    return [str(Q(lo, scale)), str(Q(hi, scale))]


def check_small_populations():
    checked, sharp, unique = 0, 0, 0
    for height in range(5):
        for start in itertools.product(range(3), repeat=height + 1):
            if not any(start):
                continue
            for depth in range(13):
                closed = closed_population(start, depth)
                require(closed == literal_population(start, depth), "binomial identity")
                actual = Q(closed[-1], sum(closed))
                best = optimum(height, depth)
                require(actual >= best, "optimal fraction")
                checked += 1
                if depth >= height >= 1:
                    require((actual == best) == (not any(start[1:])), "unique optimum")
                    unique += 1
        pure = (1,) + (0,) * height
        for depth in range(13):
            population = literal_population(pure, depth)
            require(Q(population[-1], sum(population)) == optimum(height, depth),
                    "pure lowest grade attains")
            sharp += 1
    return {"population_depth_cases": checked, "pure_grade_attainers": sharp,
            "uniqueness_cases": unique}


def check_depth_certificate(a, b):
    previous = Q(0)
    for depth in range(MAX_DEPTH + 1):
        fraction = optimum(65, depth)
        require(fraction >= previous, "nondecreasing optimal loss")
        if depth > 65:
            require(fraction > previous, "strict optimal loss growth")
        previous = fraction
    q110, q111 = optimum(65, 110), optimum(65, 111)
    require(a[0] - b[1] * q110 > 0, "depth 110 strict pass")
    require(a[1] - b[0] * q111 < 0, "depth 111 strict failure")
    start = (1,) * 66
    first = literal_population(start, 1)
    require(sum(first) == 131 and first[-1] == 2, "equal population first step")
    initial = (66 * a[0] - b[1], 66 * a[1] - b[0])
    after = (131 * a[0] - 2 * b[1], 131 * a[1] - 2 * b[0])
    require(initial[0] > 0 and after[1] < 0, "equal population loses on reuse")
    return {"first_impossible_depth": 111, "last_possible_depth": 110,
            "optimal_fraction_at_110": str(q110),
            "optimal_fraction_at_111": str(q111),
            "normalized_margin_at_110": enclosure((a[0] - b[1] * q110,
                                                    a[1] - b[0] * q110)),
            "normalized_margin_at_111": enclosure((a[0] - b[1] * q111,
                                                    a[1] - b[0] * q111)),
            "equal_start_initial_margin": enclosure(initial),
            "equal_start_after_one_margin": enclosure(after),
            "monotonicity_depth_cases": MAX_DEPTH + 1}


def rejection_controls():
    invalid = [((), 0), ((0,), 0), ((-1,), 0), ((True,), 0),
               ((2**256,), 0), ((1,) * 67, 0), ((1,), -1), ((1,), 257)]
    for start, depth in invalid:
        try:
            closed_population(start, depth)
        except ValueError:
            continue
        raise ValueError("invalid population accepted")
    # These false extrapolations give different exact answers on new fixtures.
    require(Q(1, 66) != Q(2, 131), "constant boundary fraction control")
    require(optimum(2, 3) != Q(choose(3, 2), 2**3), "untruncated total control")
    require(closed_population((1, 0, 0), 2) != (1, 0, 0), "no shift control")
    require(optimum(2, 3) != optimum(2, 4), "depth independent optimum control")
    largest = (2**256 - 1,) + (0,) * MAX_HEIGHT
    boundary = closed_population(largest, MAX_DEPTH)
    require(boundary == literal_population(largest, MAX_DEPTH), "maximum valid limits")
    require(Q(boundary[-1], sum(boundary)) == optimum(MAX_HEIGHT, MAX_DEPTH),
            "maximum valid attainer")
    return {"invalid_inputs_rejected": len(invalid), "false_shortcuts_rejected": 4,
            "maximum_valid_population_cases": 1}


def source_hashes():
    source_path = PACKAGE / "SOURCES.json"
    require(source_path.stat().st_size < 1024**2, "source manifest size bound")
    manifest = json.loads(source_path.read_text())
    require(len(manifest["files"]) == 4, "four source declarations")
    inputs = [row for row in manifest["files"] if row["usage"] == "input"]
    expected = {"research/bounded-lane-border-core/README.md",
                "research/bounded-lane-border-core/core/PROOF.md"}
    require(len(inputs) == 2 and {row["path"] for row in inputs} == expected,
            "exact two cited source inputs")
    hashes = {}
    for row in inputs:
        path = ROOT / row["path"]
        require(path.stat().st_size < 1024**2, "source size bound")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        require(digest == row["sha256"], "cited input drift: " + row["path"])
        hashes[row["path"]] = digest
    names = ("README.md", "PROOF.md", "verify.py", "TASK.json", "SOURCES.json",
             "VERIFY.json")
    for name in names:
        path = PACKAGE / name
        require(path.stat().st_size < 1024**2, "package size bound")
        hashes[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def main():
    hashes = source_hashes()
    a, b = ledger_bounds()
    scientific = check_depth_certificate(a, b)
    scientific.update(check_small_populations())
    scientific.update(rejection_controls())
    scientific["base_margin"] = enclosure(a)
    scientific["top_grade_debit"] = enclosure(b)
    scientific["passing_fraction_threshold"] = enclosure((a[0] / b[1], a[1] / b[0]))
    print(json.dumps({"schema": "pascal-lane-depth/v1",
                      "status": "PASS_PASCAL_LANE_DEPTH",
                      "scientific": scientific, "sha256": hashes},
                     sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
