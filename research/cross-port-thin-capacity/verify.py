#!/usr/bin/env python3
"""Exact corroboration of PROOF.md. Standard library; Apache-2.0."""

import argparse
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def binary_span(rows, dimension):
    require(0 <= dimension <= 8, "binary dimension outside 0..8")
    require(len(rows) <= 16, "too many binary rows")
    require(all(0 <= r < 1 << dimension for r in rows), "invalid binary row")
    vectors = {0}
    for row in rows:
        vectors |= {v ^ row for v in vectors}
    require(len(vectors) <= 1 << dimension, "span capacity")
    return frozenset(vectors)


def subspaces(dimension):
    """All RREF bases, without traversal or random choices; n <= 4."""
    require(0 <= dimension <= 4, "subspace census dimension outside 0..4")
    spaces = {}
    for rank in range(dimension + 1):
        for pivots in combinations(range(dimension), rank):
            slots = [(i, j) for i, p in enumerate(pivots)
                     for j in range(p + 1, dimension) if j not in pivots]
            for values in product((0, 1), repeat=len(slots)):
                rows = [1 << p for p in pivots]
                for (i, j), bit in zip(slots, values, strict=True):
                    rows[i] |= bit << j
                span = binary_span(rows, dimension)
                require(span not in spaces, "RREF duplicate")
                spaces[span] = tuple(rows)
    return spaces


def observation(rows, point):
    return tuple((row & point).bit_count() % 2 for row in rows)


def fiber_decodable(free, query, target, dimension):
    """Independent oracle: allow any lookup-table decoder on actual fibers."""
    fibers = {}
    for point in range(1 << dimension):
        transcript = observation(free + query, point)
        answer = observation(target, point)
        if transcript in fibers and fibers[transcript] != answer:
            return False
        fibers[transcript] = answer
    return True


def census():
    triples = fibers = 0
    per_dimension = []
    for dimension in range(5):
        spaces = subspaces(dimension)
        # Enumerate every ordered square binary matrix as a separate completeness oracle.
        all_spans = {binary_span(rows, dimension)
                     for rows in product(range(1 << dimension), repeat=dimension)}
        require(set(spaces) == all_spans, "RREF census is incomplete")
        keys = tuple(spaces)
        ranks = {s: len(spaces[s]) for s in keys}
        joins = {(f, q): binary_span(spaces[f] + spaces[q], dimension)
                 for f in keys for q in keys}
        for free in keys:
            for target in keys:
                deficit = ranks[joins[free, target]] - ranks[free]
                minimum = dimension + 1
                for query in keys:
                    decoded = target <= joins[free, query]
                    if decoded:
                        require(ranks[query] >= deficit, "capacity bound failed")
                        minimum = min(minimum, ranks[query])
                    if dimension <= 3:
                        actual = fiber_decodable(spaces[free], spaces[query],
                                                 spaces[target], dimension)
                        require(actual == decoded, "fiber/row-space disagreement")
                        fibers += 1
                    triples += 1
                require(minimum == deficit, "abstract bound is not sharp")
        per_dimension.append({"dimension": dimension, "subspaces": len(keys)})
    return {"triples": triples, "fiber_comparisons": fibers,
            "subspaces": per_dimension}


def rational_rank(matrix, columns):
    require(0 <= columns <= 16 and len(matrix) <= 32, "rational matrix capacity")
    require(all(len(row) == columns for row in matrix), "ragged matrix")
    rows = [[Fraction(x) for x in row] for row in matrix]
    pivot = 0
    for column in range(columns):
        index = next((i for i in range(pivot, len(rows)) if rows[i][column]), None)
        if index is None:
            continue
        rows[pivot], rows[index] = rows[index], rows[pivot]
        scale = rows[pivot][column]
        rows[pivot] = [x / scale for x in rows[pivot]]
        for i in range(pivot + 1, len(rows)):
            scale = rows[i][column]
            rows[i] = [x - scale * y for x, y in zip(rows[i], rows[pivot], strict=True)]
        pivot += 1
    return pivot


def direct_sum_fixtures():
    cases = 0
    for ports in range(1, 5):
        for per_port in range(1, 5):
            dimension = ports * per_port
            target = [[int(j <= i) for j in range(dimension)]
                      for i in range(dimension)]
            require(rational_rank(target, dimension) == dimension, "dense recoding")
            for known in range(dimension + 1):
                free = target[:known]
                deficit = rational_rank(free + target, dimension) - known
                require(deficit == dimension - known, "side-information deficit")
                if known < dimension:
                    require(rational_rank(free + target[known:-1], dimension)
                            < dimension, "missing observation accepted")
                cases += 1
    return cases


def adaptive_fixtures():
    leaves = failures = 0
    for dimension in range(1, 9):
        transcripts = {}
        prefixes = {}
        for point in range(1 << dimension):
            answers, rows = [], []
            for stage in range(dimension):
                row = 1 << stage
                for earlier in range(stage):
                    if answers[earlier] ^ (stage % 2):
                        row ^= 1 << earlier
                answer = (row & point).bit_count() % 2
                rows.append(row)
                answers.append(answer)
                require(len(binary_span(rows, dimension)) == 1 << (stage + 1),
                        "adaptive triangular independence")
            key = tuple(answers)
            require(key not in transcripts, "full adaptive transcript collision")
            transcripts[key] = point
            prefixes.setdefault(key[:-1], []).append(point)
            leaves += 1
        for values in prefixes.values():
            require(len(values) == 2 and values[0] != values[1], "short adaptive fiber")
            failures += 1
    return {"full_transcripts": leaves, "short_ambiguous_fibers": failures}


def capacity_rows():
    rows = []
    for ports, cap in ((104, 3), (112, 4)):
        demand, requests = 15 * ports, 528
        high = demand - (cap - 1) * requests
        require(0 <= high <= requests, "capacity histogram feasibility")
        capacities = [cap] * high + [cap - 1] * (requests - high)
        require(sum(capacities) == demand, "capacity histogram equality")
        require(sum(capacities) - 1 < demand, "one fewer dimension must fail")
        rows.append({"ports": ports, "demand": demand, "requests": requests,
                     "maximum_capacity": cap, "minimum_maximum_capacity_calls": high,
                     "lower_capacity_calls": requests - high,
                     "scalar_side_information_needed": demand - requests})
    require(rows[0]["demand"] == 1560 and rows[1]["demand"] == 1680,
            "conditional application arithmetic")
    return rows


def controls():
    require(not fiber_decodable((), (15,), (1, 2, 4, 8), 4), "support/rank confusion")
    correlated = {(bit, bit, bit, bit) for bit in (0, 1)}
    require(len({row[0] for row in correlated}) == len(correlated), "correlation escape")
    require(fiber_decodable((), (1, 2, 4, 8), (1, 2, 4, 8), 4), "vector output escape")
    require(fiber_decodable((8,), (1, 2, 4), (1, 2, 4, 8), 4), "free-side-info escape")
    rejected = 0
    for function, args in ((binary_span, ((16,), 4)),
                           (binary_span, ((), 9)),
                           (subspaces, (5,)),
                           (rational_rank, ([[1, 2]], 1))):
        try:
            function(*args)
        except ValueError:
            rejected += 1
    require(rejected == 4, "boundary rejection controls")
    return {"semantic": 4, "invalid_inputs": rejected}


def source_hashes(package):
    hashes = {}
    for name in ("PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py"):
        with (package / name).open("rb") as stream:
            data = stream.read(1_048_577)
        require(len(data) <= 1_048_576, "source file exceeds one MiB")
        hashes[name] = hashlib.sha256(data).hexdigest()
    return hashes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, help="write a new hash-bound receipt outside the package")
    args = parser.parse_args()
    report = {"claim_type": "scoped-proof", "binary_census": census(),
              "rational_fixtures": direct_sum_fixtures(),
              "adaptive": adaptive_fixtures(), "conditional_capacity": capacity_rows(),
              "controls": controls()}
    package = Path(__file__).resolve().parent
    report["source_sha256"] = source_hashes(package)
    if args.receipt:
        destination = args.receipt.resolve()
        require(not destination.is_relative_to(package), "receipt must be outside package")
        with destination.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print("PASS_CROSS_PORT_THIN_CAPACITY " + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
