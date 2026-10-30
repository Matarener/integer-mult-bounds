#!/usr/bin/env python3
"""Exact controls for the analytic eleven-row matrix and directed-box proof.

SPDX-License-Identifier: Apache-2.0
Sagar Thakrar (thakrarsagar), with substantial OpenAI Codex assistance.
Shared small checker patterns follow the author's PR3420 verifier. The frozen
PR3393 oracle is unchanged and authenticated before any execution.
"""

from fractions import Fraction
import hashlib
from itertools import combinations, permutations
import json
from pathlib import Path
import sys
import types
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ORACLE = "inputs/pr3393-independent_box.py"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(root=ROOT):
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    rows = [(root, row) for row in manifest["files"] if row["usage"] == "input"]
    rows += [(HERE, row) for row in manifest["frozen_sources"]]
    result = {}
    for base, row in rows:
        raw = (base / row["path"]).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "Input changed: " + row["path"])
        result[row["path"]] = raw
    return result


def load_oracle():
    raw = authenticate()[ORACLE]
    module = types.ModuleType("frozen_box")
    exec(compile(raw, str(HERE / ORACLE), "exec"), module.__dict__)
    return module


def rank(matrix):
    rows = [[Fraction(value) for value in row] for row in matrix]
    cursor = 0
    for column in range(len(rows[0]) if rows else 0):
        pivot = next((i for i in range(cursor, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[cursor], rows[pivot] = rows[pivot], rows[cursor]
        scale = rows[cursor][column]
        rows[cursor] = [value / scale for value in rows[cursor]]
        for i, row in enumerate(rows):
            if i != cursor:
                multiplier = row[column]
                rows[i] = [x - multiplier * y for x, y in zip(row, rows[cursor])]
        cursor += 1
    return cursor


def product(p, q):
    return [[sum(x*y for x, y in zip(left, right)) for right in q] for left in p]


def projective(vector):
    vector = tuple(map(Fraction, vector))
    first = next((value for value in vector if value), None)
    require(first is not None, "zero projective vector")
    return tuple(value / first for value in vector)


def parity(left, right):
    return (left & right).bit_count() & 1


def ordered(matrix, indices):
    return len(indices) == len(set(indices)) and all(matrix[i][j]
        for position, i in enumerate(indices) for j in indices[position + 1:])


def find_ordered(matrix, size, allowed=None):
    allowed = range(len(matrix)) if allowed is None else allowed
    for subset in combinations(allowed, size):
        for order in permutations(subset):
            if ordered(matrix, order):
                return order
    return None


def admit(matrix, a0, b0):
    require(len(matrix) == 11 and all(len(row) == 11 for row in matrix), "expected eleven square rows")
    require(len(a0) == len(b0) == 11, "anchor length mismatch")
    require(all(type(mask) is int and 0 <= mask < 8 for mask in a0 + b0), "invalid anchor mask")
    require(all(matrix[i][i] for i in range(11)), "zero diagonal")
    require(rank(matrix) <= 3, "matrix rank exceeds three")
    require(all(a & b for a, b in zip(a0, b0)), "empty tied set")
    require(all(matrix[i][j] or not parity(a0[i], b0[j])
                for i in range(11) for j in range(11)), "SG failed")


def literal_check(matrix, a0, b0, witness):
    order, kept, a, b = (witness[key] for key in ("order", "kept", "a", "b"))
    if len(a) != len(a0) or len(b) != len(a0) or sorted(order) != sorted(kept):
        return False
    if len(set(kept)) != len(kept) or any(not 0 <= i < len(a0) for i in kept):
        return False
    if any(type(a[i]) is not int or type(b[i]) is not int or
           not 0 <= a[i] < 8 or not 0 <= b[i] < 8 or a[i] & ~a0[i] or b[i] & ~b0[i]
           or parity(a[i], b[i]) != 1 for i in kept):
        return False
    return all(matrix[i][j] or not parity(a[i], b[j])
               for position, i in enumerate(order) for j in order[position + 1:])


def labelled_blocks(matrix, a0, b0, first, second):
    require(set(first).isdisjoint(second) and ordered(matrix, first) and ordered(matrix, second),
            "blocks are not disjoint ordered nonzero subsets")
    a, b = [0] * len(matrix), [0] * len(matrix)
    for i in first:
        tied = a0[i] & b0[i]
        a[i], b[i] = a0[i], tied & -tied
    for i in second:
        tied = a0[i] & b0[i]
        a[i], b[i] = tied & -tied, b0[i]
    kept = list(first) + list(second)
    witness = {"a": a, "b": b, "kept": kept, "order": kept}
    require(literal_check(matrix, a0, b0, witness), "two-block labels violate the directed box")
    return witness


def construct(matrix, a0, b0):
    admit(matrix, a0, b0)
    first = find_ordered(matrix, 4)
    require(first is not None, "ordered-four theorem failed on admitted matrix")
    second = find_ordered(matrix, 3, [i for i in range(11) if i not in first])
    require(second is not None, "seven-row complement theorem failed")
    return labelled_blocks(matrix, a0, b0, first, second)


def core_fixture(oracle):
    sizes = (4, 4, 3)
    p0 = [(-1, -3, 0), (1, -1, -2), (3, 3, 3)]
    q0 = [(1, -3, 2), (3, -1, -2), (3, -1, 2)]
    p = [row for row, count in zip(p0, sizes) for _ in range(count)]
    q = [row for row, count in zip(q0, sizes) for _ in range(count)]
    data = oracle.rational_data(p, q)
    matrix = product(p, q)
    groups = [g for g, count in enumerate(sizes) for _ in range(count)]
    expected = [[(8 if g < 2 else 12) if g == h else 0 for h in groups] for g in groups]
    require(matrix == expected == data["M"] and rank(matrix) == 3, "core matrix changed")
    require(data["gamma"] == 0 and data["tau"] == [2] * 11 and
            data["a0"] == [3] * 8 + [7] * 3 and data["b0"] == [3] * 11, "core normalization changed")
    witness = construct(matrix, data["a0"], data["b0"])
    sharp = labelled_blocks(matrix, data["a0"], data["b0"], list(range(4)), list(range(4, 8)))
    require(len(witness["kept"]) == 7 and len(sharp["kept"]) == 8, "core witness sizes failed")
    require(all(oracle.check_witness(data["a0"], data["b0"], data["arcs"], value)
                for value in (witness, sharp)), "frozen definition disagrees")
    require(all(len({groups[i] for i in subset}) == 3 for subset in combinations(range(11), 9)),
            "nine-set rank obstruction premise failed")
    record = {"P": list(map(list, p)), "Q": list(map(list, q)), "sizes": list(sizes), "M": matrix, "rank": 3, "gamma": 0,
              "a0": data["a0"], "b0": data["b0"], "tau": data["tau"],
              "theorem_witness": witness, "exact_box": 8, "eight_witness": sharp,
              "upper_bound": "any nine-set meets three zero-separated groups, forcing a triangular rank3 label minor; all target labels lie in a rank2 space",
              "sharpness_at_seven": False}
    return record, data, p, q


def rejects(action, message):
    try:
        action()
    except ValueError as error:
        require(message in str(error), "unexpected failure control: " + str(error))
        return
    raise ValueError("failure control accepted: " + message)


def boundary_controls(oracle, data, p, q):
    matrix, a0, b0 = data["M"], data["a0"], data["b0"]
    zero_diag = [row[:] for row in matrix]
    zero_diag[0][0] = 0
    rejects(lambda: construct(zero_diag, a0, b0), "zero diagonal")
    empty_tie = a0[:]
    empty_tie[0] = 0
    rejects(lambda: construct(matrix, empty_tie, b0), "empty tied set")
    rejects(lambda: construct(matrix, [1] * 11, [1] * 11), "SG failed")
    groups = [0]*3 + [1]*3 + [2]*3 + [3]*2
    rank_four = [[int(i == j) for j in groups] for i in groups]
    require(rank(rank_four) == 4 and find_ordered(rank_four, 4) is None, "rank boundary failed")
    rejects(lambda: construct(rank_four, [3]*11, [3]*11), "rank exceeds three")
    witness = construct(matrix, a0, b0)
    witness["a"][witness["kept"][0]] = 8
    require(not literal_check(matrix, a0, b0, witness) and not oracle.check_witness(
        a0, b0, data["arcs"], witness), "submask corruption accepted")
    scales = [Fraction(-3, 2), Fraction(5, 4), Fraction(7)]
    scaled = oracle.rational_data([[x*s for x, s in zip(row, scales)] for row in p],
                                 [[x/s for x, s in zip(row, scales)] for row in q])
    require(all(scaled[key] == data[key] for key in ("M", "a0", "b0", "tau")), "rational scaling changed canonical data")
    old_read = Path.read_bytes
    def counterfeit(path):
        return b'raise RuntimeError("counterfeit executed")\n' if path == HERE / ORACLE else old_read(path)
    with patch.object(Path, "read_bytes", counterfeit):
        rejects(load_oracle, "Input changed: " + ORACLE)
    return ["zero_diagonal", "empty_ties", "SG", "rank_four_no_ordered_four", "submask",
            "exact_rational_rescaling", "source_corruption_before_execution"]


def class_orders(p, q):
    """Literal finite class-order construction used only by the rank-two control."""
    require(all(len(row) == 2 for row in p + q), "expected two-coordinate factors")
    matrix = product(p, q)
    require(all(matrix[i][i] for i in range(len(matrix))) and rank(matrix) <= 2, "rank-two premise failed")
    classes = sorted({projective(row) for row in q})
    owner = [classes.index(projective(row)) for row in q]
    forbidden = [{owner[j] for j in range(len(q)) if not matrix[i][j]} for i in range(len(p))]
    require(all(len(values) <= 1 and owner[i] not in values for i, values in enumerate(forbidden)), "forbidden class premise failed")
    result = []
    for order in permutations(range(len(classes))):
        position = {value: i for i, value in enumerate(order)}
        kept = [i for value in order for i in range(len(p)) if owner[i] == value and
                (not forbidden[i] or position[next(iter(forbidden[i]))] < position[value])]
        require(ordered(matrix, kept), "class-order construction failed")
        result.append(kept)
    return matrix, result


def rank_two_controls():
    qtypes = [(1, 0), (0, 1), (1, 1), (1, -1)]
    ptypes = [(1, 0), (1, -1), (1, 1), (0, 1)]
    sizes = (3, 3, 3, 2)
    p = [row for row, count in zip(ptypes, sizes) for _ in range(count)]
    q = [tuple(Fraction((-2 if k % 2 else 3), 5) * x for x in row)
         for row, count in zip(qtypes, sizes) for k in range(count)]
    matrix, orders = class_orders(p, q)
    require(len(orders) == 24 and sum(map(len, orders)) == 132, "half-size mass changed")
    require(max(map(len, orders)) >= 6 and any(not ordered(matrix, tuple(reversed(order)))
                                             for order in orders), "orientation control did not fail")
    no_forbidden = p[:]
    no_forbidden[0] = (1, 2)
    _matrix, augmented = class_orders(no_forbidden, q)
    require(all(0 in order for order in augmented) and sum(map(len, augmented)) == 144,
            "a row without a forbidden class was not always retained")
    # A three-copy direction is legal at small sizes; no global multiplicity rule is used.
    low = [[1]*3 for _ in range(3)]
    require(rank(low) == 1 and ordered(low, (0, 1, 2)) and find_ordered(low, 4) is None, "low-size duplicate control failed")
    return {"rows": 11, "rank": 2, "projective_classes": 4, "class_orders": 24,
            "total_retained": 132, "average_retained": "11/2", "largest_retained": max(map(len, orders)),
            "no_forbidden_class_total_retained": 144,
            "reverse_order_failure_observed": True, "three_copy_small_size_allowed": True}


def repeated_pair_controls():
    basis = [[int(i == j) for j in range(3)] for i in range(3)]
    p = basis + [[1, 1, 1]]*2 + [[0, 1, 0], [1, 2, 0], [1, 0, 0], [2, 1, 0], [1, 0, 1], [2, 0, 1]]
    qdirections = [(0, 1, -1), (1, 0, -1), (1, -1, 0)]
    q = basis + [[1, 1, 1], [1, 1, 0]] + [list(row) for row in qdirections for _ in range(2)]
    matrix = product(p, q)
    require(rank(matrix) == 3 and all(matrix[i][i] for i in range(11)), "repeated-pair fixture failed")
    for factors in (p, q):
        directions = [projective(row) for row in factors]
        require(max(directions.count(value) for value in directions) == 2, "fixture uses a three-copy shortcut")
    scaled = [row[:] for row in p]
    scaled[3] = [Fraction(-2) * x for x in p[3]]
    scaled[4] = [Fraction(3, 5) * x for x in p[4]]
    require(projective(scaled[3]) == projective(scaled[4]) == (1, 1, 1) and
            ordered(product(scaled, q), (1, 5, 9, 10)), "projective rescaling failed")
    require(all(matrix[3][i] and matrix[4][i] for i in range(3)) and
            all(not matrix[3][i] and not matrix[4][i] for i in range(5, 11)), "S/Z partition failed")
    z = [row[5:] for row in matrix[5:]]
    require(rank(z) == 2 and ordered(matrix, (1, 5, 9, 10)), "actual pair-branch four-block failed")
    require(all(sum(row) == 0 and sum(value == 0 for value in row) == 1 for row in qdirections), "coordinate-plane premise failed")
    require(rank(qdirections) == 2 and all(sum(q[i][j] == 0 for i in range(5, 11)) == 2
                                         for j in range(3)), "coordinate zero counts failed")
    impossible = [[int(i//2 == j//2) for j in range(6)] for i in range(6)]
    require(rank(impossible) == 3, "three rank-one blocks lost rank")
    for target in range(3):
        augmented = [list(row) + [int(i == target)] for i, row in enumerate(qdirections)]
        require(rank(augmented) == 3, "impossible isolated pair constraints became solvable")
    return {"P": p, "Q": q, "rank": 3, "S": [0, 1, 2], "repeated_P_pair": [3, 4],
            "Z": list(range(5, 11)), "Z_rank": 2, "ordered_four": [1, 5, 9, 10],
            "coordinate_pair_directions": [list(row) for row in qdirections],
            "coordinate_zero_counts": [2, 2, 2], "hypothetical_three_block_rank": 3,
            "inconsistent_pair_isolation_systems": 3, "signed_rational_direction_rescaling": True}


def cross(left, right):
    a, b, c = left
    d, e, f = right
    return [b*f-c*e, c*d-a*f, a*e-b*d]


def unique_pairs(neighborhoods):
    owners = {}
    for line, points in enumerate(neighborhoods):
        for pair in combinations(sorted(points), 2):
            require(pair not in owners, "point pair lies on two lines")
            owners[pair] = line
    return len(owners)


def incidence(p, q):
    require(len({projective(row) for row in p}) == len(p), "repeated line direction")
    require(len({projective(row) for row in q}) == len(q), "repeated point direction")
    matrix = product(p, q)
    neighborhoods = [[j for j, value in enumerate(row) if not value] for row in matrix]
    return neighborhoods, unique_pairs(neighborhoods)


def incidence_controls():
    q = [[1, i, i*i] for i in range(11)]
    p = [cross(q[i], q[(i+1) % 11]) for i in range(11)]
    neighborhoods, pairs = incidence(p, q)
    require([len(points) for points in neighborhoods] == [2]*11 and pairs == 11, "conic incidence control failed")
    rejects(lambda: incidence([p[0]] + p[:-1], q), "repeated line direction")
    rejects(lambda: incidence(p, [q[0]] + q[:-1]), "repeated point direction")
    abstract = [[(i+j) % 11 for j in range(4)] for i in range(11)]
    required = sum(len(list(combinations(points, 2))) for points in abstract)
    available = len(list(combinations(range(11), 2)))
    require(required == 66 and available == 55 and required > available, "incidence contradiction arithmetic changed")
    rejects(lambda: unique_pairs(abstract), "point pair lies on two lines")
    return {"realizable_conic_points": 11, "realizable_distinct_lines": 11,
            "realizable_pair_uses": 11, "required_pairs_at_four_zeros": 66,
            "available_point_pairs": 55, "distinct_line_and_point_mutants_rejected": True,
            "abstract_four_point_neighborhood_collision_rejected": True}


def orientation_controls(oracle):
    arcs = [(i, j) for i in range(4) for j in range(4) if i != j]
    for pattern in range(4096):
        matrix = [[int(i == j) for j in range(4)] for i in range(4)]
        for bit, (i, j) in enumerate(arcs):
            matrix[i][j] = int(bool(pattern & (1 << bit)))
        direct = any(matrix[a][b] and matrix[a][c] and matrix[a][d] and
                     matrix[b][c] and matrix[b][d] and matrix[c][d]
                     for a, b, c, d in permutations(range(4)))
        require(bool(find_ordered(matrix, 4)) == direct, "directed-four predicate mismatch")
    directed = [[int(i <= j) for j in range(3)] for i in range(3)]
    zeros = [(i, j) for i in range(3) for j in range(3) if i != j and not directed[i][j]]
    witness = {"a": [1]*3, "b": [1]*3, "kept": [0, 1, 2], "order": [0, 1, 2]}
    require(literal_check(directed, [1]*3, [1]*3, witness) and
            oracle.check_witness([1]*3, [1]*3, zeros, witness), "forward definition control failed")
    witness["order"] = [2, 1, 0]
    require(not literal_check(directed, [1]*3, [1]*3, witness) and
            not oracle.check_witness([1]*3, [1]*3, zeros, witness), "reversed definition control accepted")
    cycle = [[-2, 0, 2], [-8, -2, 0], [0, 2, 8]]
    require(rank(cycle) == 2 and find_ordered(cycle, 3) is None, "directed cycle mistaken for a triple")
    groups = [0]*3 + [1]*2 + [2]*2
    seven = [[int(i == j) for j in groups] for i in groups]
    require(rank(seven) == 3 and find_ordered(seven, 3) is not None and
            find_ordered(seven, 4) is None, "rank-three seven-row boundary failed")
    return {"all_directed_four_patterns": 4096, "forward_definition_and_reverse_mutant": True,
            "rank_two_directed_triangle_has_no_ordered_triple": True,
            "seven_row_rank_three_has_three_but_not_four": True}


def build():
    authenticated = authenticate()
    oracle = load_oracle()
    fixture, data, p, q = core_fixture(oracle)
    return {"schema_version": 1, "status": "PASS_FSTAR_ELEVEN_LINE_FLOOR",
            "scope": "finite exact controls for the analytic theorem; no exhaustive matrix search or formal kernel claim",
            "inputs_sha256": {path: hashlib.sha256(raw).hexdigest() for path, raw in authenticated.items()},
            "working_fixture": fixture,
            "controls": {"boundaries": boundary_controls(oracle, data, p, q),
                         "orientation": orientation_controls(oracle), "rank_two_class_order": rank_two_controls(),
                         "repeated_direction": repeated_pair_controls(), "zero_line_incidence": incidence_controls()}}


def main():
    require(sys.argv[1:] in ([], ["--emit"]), "usage: verify.py [--emit]")
    result = build()
    if sys.argv[1:] == ["--emit"]:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        require(result == json.loads((HERE / "RESULT.json").read_text()), "RESULT.json mismatch")
        print("PASS_FSTAR_ELEVEN_LINE_FLOOR: exact construction, proof-branch controls and source binding")


if __name__ == "__main__":
    main()
