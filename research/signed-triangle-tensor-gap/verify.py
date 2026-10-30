#!/usr/bin/env python3
"""Exact finite corroboration of the signed subspace-triangle theorem."""

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path


PAIRS = ((0, 1), (0, 2), (1, 2))
LAYOUTS = ((2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (3, 2), (5, 2))
COEFFICIENTS = ((-1, 0), (-1, 2), (0, -1), (0, 0), (0, 1),
                (0, 3), (3, -3), (3, -2), (3, 0))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def vector_code(vector, prime):
    return sum(value * prime ** i for i, value in enumerate(vector))


def span_mask(rows, prime, dimension):
    mask = 0
    for coefficients in itertools.product(range(prime), repeat=len(rows)):
        vector = tuple(sum(c * row[j] for c, row in zip(coefficients, rows))
                       % prime for j in range(dimension))
        mask |= 1 << vector_code(vector, prime)
    need(mask.bit_count() == prime ** len(rows), "Rows must be independent")
    return mask


def subspaces(prime, dimension):
    """Enumerate each reduced-row-echelon basis exactly once."""
    need((prime, dimension) in LAYOUTS, "Unsupported finite calibration")
    spaces = []
    for rank in range(dimension + 1):
        for pivots in itertools.combinations(range(dimension), rank):
            cells = [(i, j) for i in range(rank) for j in range(dimension)
                     if j not in pivots and j > pivots[i]]
            for values in itertools.product(range(prime), repeat=len(cells)):
                rows = [[int(j == pivots[i]) for j in range(dimension)]
                        for i in range(rank)]
                for (i, j), value in zip(cells, values):
                    rows[i][j] = value
                spaces.append((rank, span_mask(rows, prime, dimension)))
    need(len({mask for _, mask in spaces}) == len(spaces), "Duplicate space")
    return spaces


def closure_oracle(dimension):
    """Independent F2 enumeration by repeated adjoining of a vector."""
    known = {1}
    for _ in range(dimension):
        previous = tuple(known)
        for mask in previous:
            members = [x for x in range(1 << dimension) if (mask >> x) & 1]
            for added in range(1 << dimension):
                enlarged = mask
                for member in members:
                    enlarged |= 1 << (member ^ added)
                known.add(enlarged)
    return known


def exhaustive_case(prime, dimension):
    spaces = subspaces(prime, dimension)
    if prime == 2:
        need({mask for _, mask in spaces} == closure_oracle(dimension),
             "RREF and closure enumerations disagree")
    sizes = {prime ** k: k for k in range(dimension + 1)}
    intersections = [[sizes[(a & b).bit_count()] for _, b in spaces]
                     for _, a in spaces]
    distances = [[ra + rb - intersections[i][j] * 2
                  for j, (rb, _) in enumerate(spaces)]
                 for i, (ra, _) in enumerate(spaces)]
    expected = -(3 * dimension // 2)
    minimum = None
    minimizers = 0
    coefficients = set()
    digest = hashlib.sha256()
    for indices in itertools.product(range(len(spaces)), repeat=3):
        ranks = [spaces[i][0] for i in indices]
        credits = [distances[indices[i]][indices[j]] for i, j in PAIRS]
        value = sum(ranks) - sum(credits)
        pairwise_disjoint = all(intersections[indices[i]][indices[j]] == 0
                                for i, j in PAIRS)
        balanced = sorted(ranks) == [dimension // 2, dimension // 2,
                                    (dimension + 1) // 2]
        need(value >= expected, "Linear floor violated")
        need((value == expected) == (pairwise_disjoint and balanced),
             "Equality classification violated")
        if minimum is None or value < minimum:
            minimum = value
        minimizers += int(value == expected)
        if dimension == 2:
            coefficients.add((ranks.count(1) - credits.count(1),
                              ranks.count(2) - credits.count(2)))
        digest.update(f"{indices}:{value}\n".encode())
    need(minimum == expected and minimizers > 0, "Floor not attained")
    if dimension == 2:
        need(tuple(sorted(coefficients)) == COEFFICIENTS, "Power table changed")
    return {"prime": prime, "dimension": dimension, "spaces": len(spaces),
            "ordered_triples": len(spaces) ** 3, "linear_minimum": minimum,
            "minimizers": minimizers, "trace_sha256": digest.hexdigest()}


def attaining_spaces(dimension):
    half = dimension // 2
    first = tuple(1 << j for j in range(half))
    second = tuple(1 << j for j in range(half, dimension))
    third = tuple((1 << j) | (1 << (half + j)) for j in range(half))
    return first, second, third


def binary_rank(rows, dimension):
    basis = [0] * dimension
    rank = 0
    for row in rows:
        value = row
        for pivot in range(dimension - 1, -1, -1):
            if (value >> pivot) & 1:
                if basis[pivot]:
                    value ^= basis[pivot]
                else:
                    basis[pivot] = value
                    rank += 1
                    break
    return rank


def construction_checks():
    for dimension in range(1, 65):
        spaces = attaining_spaces(dimension)
        ranks = [binary_rank(rows, dimension) for rows in spaces]
        distances = []
        for i, j in PAIRS:
            union_rank = binary_rank(spaces[i] + spaces[j], dimension)
            need(union_rank == ranks[i] + ranks[j], "Nonzero intersection")
            distances.append(2 * union_rank - ranks[i] - ranks[j])
        need(sum(ranks) - sum(distances) == -(3 * dimension // 2),
             "Construction misses floor")
    return 64


def power_checks(coefficients):
    need(tuple(sorted(coefficients)) == COEFFICIENTS, "Incomplete power table")
    checks = 0
    for constant, slope in coefficients:
        for a in (Fraction(1), Fraction(3, 2), Fraction(2)):
            need(constant + slope * a >= min(-a, 3 - 3 * a),
                 "Power-envelope endpoint violated")
            checks += 1
    need(2 ** 3 > Fraction(3, 2) ** 4, "Threshold certificate failed")
    return checks


def run_checks():
    cases = [exhaustive_case(prime, dimension) for prime, dimension in LAYOUTS]
    controls = []
    for changed in (COEFFICIENTS[:-1], COEFFICIENTS + ((-9, 0),)):
        try:
            power_checks(changed)
        except ValueError:
            controls.append("omitted_table_row" if len(changed) == 8
                            else "spurious_table_row")
        else:
            raise ValueError("Changed power table accepted")
    # Merely different subspaces need not have zero intersection.
    planes = ((1, 2), (1, 4), (2, 4))
    ranks = [binary_rank(rows, 3) for rows in planes]
    distances = [2 * binary_rank(planes[i] + planes[j], 3) - ranks[i] - ranks[j]
                 for i, j in PAIRS]
    need(sum(ranks) - sum(distances) == 0 > -4,
         "Distinct intersecting planes must not attain the dimension-three floor")
    controls.append("distinct_is_not_disjoint")
    need(Fraction(3, 2) - 3 < -1, "Normalized two-copy advantage missing")
    need(Fraction(3, 1) / Fraction(3, 2) - 3 == -1,
         "Equality at power threshold missing")
    controls.append("strict_threshold")
    local = Path(__file__).resolve().parent
    source_hashes = {name: hashlib.sha256((local / name).read_bytes()).hexdigest()
                     for name in ("README.md", "PROOF.md", "TASK.json",
                                  "SOURCES.json", "VERIFY.json", "verify.py")}
    return {"schema_version": 1, "claim_type": "scoped proof with finite corroboration",
            "linear_optimum": "-floor(3m/2)",
            "two_copy_normalized_power_optimum": "min(-1,3/2^t-3), 0<t<=1",
            "kappa_improvement": False, "cases": cases,
            "ordered_triples": sum(case["ordered_triples"] for case in cases),
            "binary_constructions": construction_checks(),
            "power_endpoint_checks": power_checks(COEFFICIENTS),
            "controls": controls, "source_sha256": source_hashes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Create a generated receipt outside the checkout")
    args = parser.parse_args()
    result = run_checks()
    if args.output is not None:
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        receipt = Path(__file__).with_name("RESULT.json")
        need(json.dumps(json.loads(receipt.read_text()), sort_keys=True)
             == json.dumps(result, sort_keys=True), "Receipt or source mismatch")
    print("PASS_SIGNED_TRIANGLE_TENSOR_GAP "
          f"ordered_triples={result['ordered_triples']} "
          f"constructions={result['binary_constructions']} "
          f"power_endpoint_checks={result['power_endpoint_checks']}")


if __name__ == "__main__":
    main()
