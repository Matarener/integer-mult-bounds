#!/usr/bin/env python3
"""Finite exact controls for the separate written eight-line proof.

SPDX-License-Identifier: Apache-2.0
Sagar Thakrar, with substantial OpenAI Codex assistance.
"""

import argparse
from fractions import Fraction
import hashlib
from itertools import combinations, permutations
import json
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ORACLE = "inputs/pr3393-independent_box.py"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(root=ROOT, package=HERE):
    manifest = json.loads((package / "SOURCES.json").read_text())
    rows = [(root, row) for row in manifest["files"] if row["usage"] == "input"]
    rows += [(package, row) for row in manifest.get("frozen_sources", [])]
    inputs = {}
    for base, row in rows:
        data = (base / row["path"]).read_bytes()
        require(hashlib.sha256(data).hexdigest() == row["sha256"], "Input changed: " + row["path"])
        inputs[row["path"]] = data
    require(ORACLE in inputs, "Missing authenticated independent oracle")
    return inputs


def load_oracle(inputs):
    module = types.ModuleType("frozen_independent_box")
    module.__file__ = str(HERE / ORACLE)
    exec(compile(inputs[ORACLE], module.__file__, "exec"), module.__dict__)
    return module


def rank(matrix):
    rows = [list(map(Fraction, row)) for row in matrix]
    current = 0
    for column in range(len(rows[0]) if rows else 0):
        pivot = next((i for i in range(current, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[current], rows[pivot] = rows[pivot], rows[current]
        divisor = rows[current][column]
        rows[current] = [x / divisor for x in rows[current]]
        for i in range(current + 1, len(rows)):
            multiplier = rows[i][column]
            rows[i] = [x - multiplier * y for x, y in zip(rows[i], rows[current])]
        current += 1
    return current


def product_matrix(P, Q):
    return [[sum(Fraction(x) * y for x, y in zip(p, q)) for q in Q] for p in P]


def zero_arcs(matrix):
    return [(i, j) for i in range(len(matrix)) for j in range(len(matrix))
            if i != j and matrix[i][j] == 0]


def parity(left, right):
    return (left & right).bit_count() & 1


def admit(matrix, A, B):
    require(len(matrix) == len(A) == len(B) == 8 and all(len(row) == 8 for row in matrix),
            "Expected eight lines")
    require(all(type(mask) is int and 0 <= mask < 8 for mask in A + B), "Invalid anchor mask")
    require(all(matrix[i][i] != 0 for i in range(8)), "Zero diagonal")
    require(all(A[i] & B[i] for i in range(8)), "Empty tied set")
    require(rank(matrix) <= 3, "Rank exceeds three")
    require(all(parity(A[i], B[j]) == 0 for i, j in zero_arcs(matrix)), "SG violation")


def forward_nonzero(matrix, order):
    return all(matrix[i][j] != 0 for position, i in enumerate(order) for j in order[position + 1:])


def ordered_triple(matrix):
    return next((list(order) for order in permutations(range(len(matrix)), 3)
                 if forward_nonzero(matrix, order)), None)


def two_block_witness(matrix, A, B, first, last):
    kept = list(first) + list(last)
    require(len(kept) == len(set(kept)), "Overlapping blocks")
    require(forward_nonzero(matrix, first) and forward_nonzero(matrix, last), "Forward zero within block")
    a, b = [0] * len(matrix), [0] * len(matrix)
    for line in kept:
        tied = A[line] & B[line]
        require(tied != 0, "Empty tied set")
        unit = tied & -tied
        a[line], b[line] = (A[line], unit) if line in first else (unit, B[line])
    return {"a": a, "b": b, "kept": kept, "order": kept}


def literal_witness(matrix, A, B, witness):
    a, b, kept, order = (witness[key] for key in ("a", "b", "kept", "order"))
    if len(a) != len(A) or len(b) != len(B) or len(set(kept)) != len(kept):
        return False
    if sorted(kept) != sorted(order) or any(type(i) is not int or not 0 <= i < len(A) for i in kept):
        return False
    if any(type(a[i]) is not int or type(b[i]) is not int or not 0 <= a[i] < 8
           or not 0 <= b[i] < 8 or a[i] & ~A[i] or b[i] & ~B[i]
           or parity(a[i], b[i]) != 1 for i in kept):
        return False
    return all(matrix[i][j] != 0 or parity(a[i], b[j]) == 0
               for position, i in enumerate(order) for j in order[position + 1:])


def construct(matrix, A, B):
    admit(matrix, A, B)
    first = ordered_triple(matrix)
    require(first is not None, "No directed nonzero triple found")
    remaining = [i for i in range(8) if i not in first]
    last = next(([i, j] for i, j in permutations(remaining, 2) if matrix[i][j] != 0), None)
    require(last is not None, "No complementary nonzero edge found")
    witness = two_block_witness(matrix, A, B, first, last)
    require(literal_witness(matrix, A, B, witness), "Constructed witness failed its definition")
    return first, last, witness


def rejected(call, text):
    try:
        call()
    except ValueError as error:
        require(text in str(error), "Unexpected rejection: " + str(error))
    else:
        raise ValueError("Required rejection did not occur: " + text)


def fixture(oracle):
    P0 = [(-1, -3, 0), (1, -1, -2), (3, 3, 3)]
    Q0 = [(1, -3, 2), (3, -1, -2), (3, -1, 2)]
    sizes = (3, 3, 2)
    P = [P0[i] for i, size in enumerate(sizes) for _ in range(size)]
    Q = [Q0[i] for i, size in enumerate(sizes) for _ in range(size)]
    matrix = product_matrix(P, Q)
    data = oracle.rational_data(P, Q)
    A, B = [3] * 6 + [7] * 2, [3] * 8
    require(data["M"] == matrix and data["a0"] == A and data["b0"] == B
            and data["tau"] == [2] * 8 and data["gamma"] == 0, "Frozen normalization differs")
    first, last, witness = construct(matrix, A, B)
    require(oracle.check_witness(A, B, zero_arcs(matrix), witness), "Frozen witness replay failed")
    labels = [1] * 3 + [2] * 3 + [0] * 2
    six = {"a": labels, "b": labels, "kept": list(range(6)), "order": list(range(6))}
    require(literal_witness(matrix, A, B, six) and oracle.check_witness(A, B, zero_arcs(matrix), six),
            "Six-line positive witness failed")
    groups = [0] * 3 + [1] * 3 + [2] * 2
    require(all(len({groups[i] for i in kept}) == 3 for kept in combinations(range(8), 7)),
            "Seven-set block coverage failed")
    require(all(matrix[i][j] == 0 for i in range(8) for j in range(8) if groups[i] != groups[j]),
            "Cross-block zeros failed")
    unit_mutant = {**witness, "a": [1 if i in witness["kept"] else 0 for i in range(8)],
                   "b": [1 if i in witness["kept"] else 0 for i in range(8)]}
    require(not literal_witness(matrix, A, B, unit_mutant), "Symmetric unit mutation was accepted")
    receipt = {"P": P, "Q": Q, "M": [[int(x) for x in row] for row in matrix], "rank": rank(matrix),
               "A": A, "B": B, "tau": [2] * 8, "first": first, "last": last, "five_witness": witness,
               "six_witness": six, "box": 6, "symmetric_unit_mutation_rejected": True,
               "upper_bound": "Every seven-set meets three zero-separated blocks; a triangular rank3 label minor exceeds the two-dimensional target-label span."}
    return matrix, A, B, P, Q, receipt


def admission_controls(oracle, matrix, A, B):
    rank4 = [[int(i // 2 == j // 2) for j in range(8)] for i in range(8)]
    require(rank(rank4) == 4 and ordered_triple(rank4) is None, "Rank-four graph control")
    require(all(parity(3, 3) == 0 for _i, _j in zero_arcs(rank4)), "Rank-four SG control")
    rejected(lambda: admit(rank4, [3] * 8, [3] * 8), "Rank exceeds")
    ones = [1] * 8
    rejected(lambda: admit(matrix, ones, ones), "SG violation")
    require(oracle.find_kept(ones, ones, zero_arcs(matrix), 4) is None,
            "SG-failing all-unit anchors unexpectedly keep four")
    three = two_block_witness(matrix, ones, ones, [0, 1, 2], [])
    require(literal_witness(matrix, ones, ones, three), "All-unit three-witness failed")
    bad_B = B.copy()
    bad_B[0] = 4
    rejected(lambda: admit(matrix, A, bad_B), "Empty tied set")
    bad_matrix = [row.copy() for row in matrix]
    bad_matrix[0][0] = 0
    rejected(lambda: admit(bad_matrix, A, B), "Zero diagonal")
    return {"rank4_has_no_ordered_triple": True, "rank4_admission_rejected": True,
            "sg_failing_anchors_box": 3, "empty_ties_rejected": True, "zero_diagonal_rejected": True}


def directed_controls():
    P = [(1, 1, 0), (1, 3, 0), (3, 1, 0)]
    Q = [(1, -3, 0), (1, -1, 0), (3, -1, 0)]
    matrix = product_matrix(P, Q)
    require(rank(matrix) == 2 and all(matrix[i][i] for i in range(3)), "Directed cycle rank")
    require(all(matrix[i][j] or matrix[j][i] for i, j in combinations(range(3), 2)), "Missing graph triangle")
    require(ordered_triple(matrix) is None, "Unordered triangle was confused with directed triple")
    rejected(lambda: two_block_witness(matrix, [3] * 3, [3] * 3, [0, 1, 2], []), "Forward zero")
    circulant = [[int(i == j or (j - i) % 8 in (2, 3)) for j in range(8)] for i in range(8)]
    require(ordered_triple(circulant) is None and rank(circulant) > 3, "Circulant boundary")
    require(all(any(circulant[i][j] or circulant[j][i] for i, j in combinations(triple, 2))
                for triple in combinations(range(8), 3)), "Circulant has an independent triple")
    return {"rank2_directed_cycle": [[int(x) for x in row] for row in matrix],
            "unordered_triangle_is_insufficient": True, "circulant_rank": rank(circulant),
            "circulant_has_no_ordered_triple_or_independent_triple": True}


def check_schur(matrix, indices):
    require(all(matrix[i][i] != 0 and all(i == j or matrix[i][j] == 0 for j in indices)
                for i in indices), "Schur basis is not invertible diagonal")
    for u in range(len(matrix)):
        for v in range(len(matrix)):
            reconstructed = sum(Fraction(matrix[u][i]) * matrix[i][v] / matrix[i][i] for i in indices)
            require(matrix[u][v] == reconstructed, "Schur identity mismatch")


def trace_product(left, right):
    return sum(left[i][j] * right[j][i] for i in range(len(left)) for j in range(len(left)))


def algebra_controls(matrix, P, Q):
    check_schur(matrix, [0, 3, 6])
    altered = [row.copy() for row in matrix]
    altered[1][2] += 1
    rejected(lambda: check_schur(altered, [0, 3, 6]), "Schur identity mismatch")
    terms = [[[q[i] * p[j] for j in range(3)] for i in range(3)] for p, q in zip(P, Q)]
    require(all(trace_product(terms[i], terms[j]) == matrix[i][j] * matrix[j][i]
                for i in range(8) for j in range(8)), "Rank-factor trace identity")
    require(all(trace_product(terms[i], terms[i]) == matrix[i][i] ** 2 > 0 for i in range(8)),
            "Positive diagonal trace identity")
    symmetric = [[1, 2, 0], [2, -1, 3], [0, 3, 2]]
    skew = [[0, 1, 2], [-1, 0, 3], [-2, -3, 0]]
    require(trace_product(symmetric, symmetric) == sum(x * x for row in symmetric for x in row),
            "Symmetric trace sign")
    require(trace_product(skew, skew) == -sum(x * x for row in skew for x in row) == -28,
            "Skew trace sign")
    return {"schur_entries_checked": 64, "schur_altered_entry_rejected": True,
            "factor_trace_pairs_checked": 64, "skew_trace_square": -28,
            "symmetric_trace_square": trace_product(symmetric, symmetric)}


def source_control():
    from unittest.mock import patch
    original = Path.read_bytes
    def counterfeit(path):
        return b"raise RuntimeError('unauthenticated oracle executed')\n" if path == HERE / ORACLE else original(path)
    with patch.object(Path, "read_bytes", counterfeit):
        rejected(build, "Input changed: " + ORACLE)
    return True


def build():
    inputs = authenticate()
    oracle = load_oracle(inputs)
    matrix, A, B, P, Q, receipt = fixture(oracle)
    result = {"schema_version": 1, "scope": "Finite controls supporting the separate analytic proof",
              "fixture": receipt, "admission_controls": admission_controls(oracle, matrix, A, B),
              "directed_controls": directed_controls(), "algebra_controls": algebra_controls(matrix, P, Q),
              "oracle_sha256": hashlib.sha256(inputs[ORACLE]).hexdigest(),
              "source_corruption_rejected_before_execution": source_control(),
              "formal_proof_claimed": False, "exhaustive_matrix_census_claimed": False}
    return json.loads(json.dumps(result))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    receipt = build()
    if args.emit:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        require(receipt == json.loads((HERE / "RESULT.json").read_text()), "Receipt mismatch")
        print("PASS_FSTAR_EIGHT_LINE_CONTROLS constructed=5 fixture_box=6")


if __name__ == "__main__":
    main()
