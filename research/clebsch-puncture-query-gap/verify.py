#!/usr/bin/env python3
"""Exact finite certificate for a fixed binary query matrix.

Produced by Nick Petalas. Apache-2.0. Standard library only.
"""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


ORDER = 16
SIZE = 1 << ORDER
GENERATORS = (1, 2, 4, 8, 15)
LOCAL_SOURCES = (
    "README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py"
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_mask(mask):
    require(type(mask) is int and 0 <= mask < SIZE, "invalid vertex mask")


def vertices(mask):
    validate_mask(mask)
    return [i for i in range(ORDER) if (mask >> i) & 1]


def graph():
    adjacency = [sum(1 << (v ^ g) for g in GENERATORS) for v in range(ORDER)]
    for v in range(ORDER):
        require(not ((adjacency[v] >> v) & 1), "loop")
        for w in range(ORDER):
            expected = (v ^ w).bit_count() in (1, 4)
            require(bool((adjacency[v] >> w) & 1) == expected, "graph definition")
            if expected:
                require(adjacency[v] & adjacency[w] == 0, "triangle")
    return adjacency


def binary_rank(rows):
    """Pivot elimination, with at most 16 rows and 16 pivots per row."""
    require(len(rows) <= ORDER, "too many rows")
    basis = [0] * ORDER
    rank = 0
    for row in rows:
        validate_mask(row)
        for pivot in range(ORDER - 1, -1, -1):
            if (row >> pivot) & 1:
                if basis[pivot]:
                    row ^= basis[pivot]
                else:
                    basis[pivot] = row
                    rank += 1
                    break
    return rank


def span_rank(rows):
    """Independent full span enumeration; the full row code has only 64 words."""
    span = {0}
    for row in rows:
        if row not in span:
            span |= {word ^ row for word in span}
            require(len(span) <= 64, "unexpected rank above six")
    require(len(span).bit_count() == 1, "nonlinear row span")
    return len(span).bit_length() - 1


def quadratic(x):
    weight = x.bit_count()
    return (weight * (weight - 1) // 2) & 1


def code_checks(matrix):
    features = [1 | (x << 1) | (quadratic(x) << 5) for x in range(ORDER)]
    weights = Counter()
    for coefficient in range(64):
        word = sum(((features[x] & coefficient).bit_count() & 1) << x
                   for x in range(ORDER))
        weights[word.bit_count()] += 1
    require(dict(weights) == {0: 1, 8: 30, 16: 1, 6: 16, 10: 16}, "code weights")
    for x in range(ORDER):
        for y in range(ORDER):
            require((1 ^ quadratic(x ^ y)) == ((matrix[x] >> y) & 1),
                    "quadratic fitting identity")
    require(binary_rank(matrix) == 6, "full rank")
    return sorted(weights.items())


def odd_components(mask, adjacency):
    unseen = mask
    odd = 0
    for _ in range(ORDER):
        if not unseen:
            break
        component = unseen & -unseen
        frontier = component
        for _ in range(ORDER):
            following = 0
            for v in range(ORDER):
                if (frontier >> v) & 1:
                    following |= adjacency[v]
            following &= unseen & ~component
            if not following:
                break
            component |= following
            frontier = following
        require(component & unseen == component, "component escaped support")
        odd += component.bit_count() & 1
        unseen ^= component
    require(unseen == 0, "component bound exhausted")
    return odd


def matching_bounds(adjacency):
    """Constructive matching DP versus independent odd-component upper bounds."""
    matching = [0] * SIZE
    score = [odd_components(mask, adjacency) + mask.bit_count() for mask in range(SIZE)]
    for bit in range(ORDER):
        for mask in range(SIZE):
            if (mask >> bit) & 1:
                score[mask] = max(score[mask], score[mask ^ (1 << bit)])
    for mask in range(1, SIZE):
        first = mask & -mask
        v = first.bit_length() - 1
        rest = mask ^ first
        best = matching[rest]
        for w in range(ORDER):
            if (rest & adjacency[v]) >> w & 1:
                best = max(best, 1 + matching[rest ^ (1 << w)])
        matching[mask] = best
        require(2 * best == 2 * mask.bit_count() - score[mask],
                "matching witness disagrees with odd-component bound")
    return matching


def census(matrix, matching):
    histogram = Counter()
    positive = Counter()
    digest = hashlib.sha256()
    for mask in range(SIZE):
        rows = [matrix[v] & mask for v in vertices(mask)]
        rank = binary_rank(rows)
        require(rank == span_rank(rows), "independent rank disagreement")
        n = mask.bit_count()
        bill = n - matching[mask]
        histogram[n, rank, bill] += 1
        digest.update(bytes((n, rank, bill)))
        if bill > rank:
            positive[n, bill - rank] += 1
        if n >= 11:
            require(rank == 6, "deletion robustness")
    expected = {(13, 1): 560, (14, 1): 120, (15, 2): 16, (16, 2): 1}
    require(dict(positive) == expected, "strict-saving classification")
    return {
        "subsets": SIZE,
        "histogram": [list(key) + [value] for key, value in sorted(histogram.items())],
        "strict_savings": [list(key) + [value] for key, value in sorted(positive.items())],
        "ordered_census_sha256": digest.hexdigest(),
    }


def fitting_check(mask, queries, decoders, adjacency):
    validate_mask(mask)
    labels = vertices(mask)
    require(len(queries) == 6 and len(decoders) == len(labels), "factor dimensions")
    for query in queries:
        validate_mask(query)
        require(query & ~mask == 0, "query outside support")
    for v, decoder in zip(labels, decoders):
        require(type(decoder) is int and 0 <= decoder < 64, "invalid decoder")
        row = 0
        for k in range(6):
            if (decoder >> k) & 1:
                row ^= queries[k]
        expected = (adjacency[v] | (1 << v)) & mask
        require(row == expected, "factorization does not realize full-parity matrix")


def construct_witness(matrix, adjacency):
    mask = (1 << 13) - 1
    queries = []
    for v in vertices(mask):
        row = matrix[v] & mask
        if binary_rank(queries + [row]) > len(queries):
            queries.append(row)
    coordinates = {}
    for coefficient in range(64):
        row = 0
        for k in range(6):
            if (coefficient >> k) & 1:
                row ^= queries[k]
        coordinates[row] = coefficient
    require(len(coordinates) == 64, "dependent queries")
    decoders = [coordinates[matrix[v] & mask] for v in vertices(mask)]
    fitting_check(mask, queries, decoders, adjacency)
    return {"vertex_mask": mask, "queries": queries, "decoders": decoders}


def literal_inputs(witness, adjacency):
    mask = witness["vertex_mask"]
    require(mask == (1 << 13) - 1, "literal fixture support")
    count = 0
    for data in range(1 << 13):
        values = [((query & data).bit_count() & 1) for query in witness["queries"]]
        for v, decoder in enumerate(witness["decoders"]):
            observed = sum(values[k] for k in range(6) if (decoder >> k) & 1) & 1
            neighbor_value = (adjacency[v] & mask & data).bit_count() & 1
            require(observed ^ neighbor_value == ((data >> v) & 1), "literal recovery")
            count += 1
    return count


def reject_controls(witness, adjacency):
    rejected = 0
    for invalid in (-1, SIZE, True, "1"):
        try:
            vertices(invalid)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid support accepted")
    mask = witness["vertex_mask"]
    queries = witness["queries"]
    decoders = witness["decoders"]
    mutants = [
        (queries[:-1], decoders),
        ([queries[0] ^ 1] + queries[1:], decoders),
        ([queries[0] | (1 << 15)] + queries[1:], decoders),
        (queries, [decoders[0] ^ 1] + decoders[1:]),
        (queries, decoders[:-1]),
        (queries, [64] + decoders[1:]),
    ]
    for candidate, readers in mutants:
        try:
            fitting_check(mask, candidate, readers, adjacency)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid factorization accepted")
    return rejected


def result(package):
    adjacency = graph()
    matrix = [adjacency[v] | (1 << v) for v in range(ORDER)]
    weights = code_checks(matrix)
    matching = matching_bounds(adjacency)
    evidence = census(matrix, matching)
    witness = construct_witness(matrix, adjacency)
    evidence.update({
        "schema": "clebsch-puncture-query-gap/v1",
        "claim_type": "finite certificate and scoped deletion-robustness proof",
        "source_sha256": {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
                          for name in LOCAL_SOURCES},
        "row_code_weight_distribution": weights,
        "witness": witness,
        "literal_recoveries": literal_inputs(witness, adjacency),
        "rejection_controls": reject_controls(witness, adjacency),
    })
    return evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", type=Path, help="write a newly generated receipt outside the package")
    args = parser.parse_args()
    package = Path(__file__).resolve().parent
    evidence = result(package)
    if args.emit is not None:
        destination = args.emit.resolve()
        require(not destination.is_relative_to(package), "emit to an external run directory")
        destination.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    else:
        expected = json.loads((package / "RESULT.json").read_text(encoding="utf-8"))
        require(json.dumps(expected, sort_keys=True) == json.dumps(evidence, sort_keys=True),
                "receipt mismatch")
    print("PASS_CLEBSCH_PUNCTURE_QUERY_GAP subsets=65536 first_saving=13 "
          "strict_saving_subsets=697 literal_recoveries=106496 controls=10")


if __name__ == "__main__":
    main()
