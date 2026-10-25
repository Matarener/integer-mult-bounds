#!/usr/bin/env python3
"""Exact finite controls for the twelve-line obstruction reductions.

SPDX-License-Identifier: Apache-2.0
Sagar Thakrar (thakrarsagar), with substantial OpenAI Codex assistance.
Small exact helpers follow the author's PR3435 verifier; the PR3393 oracle
is retained unchanged. This is not a proof by exhaustive rational search.
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


def dot(left, right):
    return sum(x * y for x, y in zip(left, right))


def product(p, q):
    return [[dot(left, right) for right in q] for left in p]


def projective(vector):
    vector = tuple(map(Fraction, vector))
    first = next((value for value in vector if value), None)
    require(first is not None, "zero projective vector")
    return tuple(value / first for value in vector)


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


def partition(p, q, prefixes=(), class_order=None):
    """Exact rank-two class partition; up to two outside prefix rows."""
    matrix = product(p, q)
    require(len(p) == len(q) and all(matrix[i][i] for i in range(len(p))), "zero diagonal")
    require(rank(q) <= 2 and rank(matrix) <= 2, "rank-two plane required")
    require(len(prefixes) <= 2, "at most two prefixes")
    classes = sorted({projective(row) for row in q})
    owner = [classes.index(projective(row)) for row in q]
    forbidden = [{owner[j] for j in range(len(q)) if not matrix[i][j]}
                 for i in range(len(p))]
    require(all(len(values) <= 1 and owner[i] not in values
                for i, values in enumerate(forbidden)), "forbidden class failed")
    restrictions = [[dot(prefix, row) for row in q] for prefix in prefixes]
    require(rank(restrictions) == len(prefixes), "prefix restrictions must be nonzero and independent")
    endpoints = [{owner[j] for j, value in enumerate(row) if not value} for row in restrictions]
    require(all(len(values) <= 1 for values in endpoints), "prefix kernel class failed")
    first = next(iter(endpoints[0]), None) if endpoints else None
    last = next(iter(endpoints[1]), None) if len(endpoints) == 2 else None
    sequence = ([first] if first is not None else [])
    sequence += [i for i in range(len(classes)) if i not in (first, last)]
    sequence += [last] if last is not None else []
    if class_order is not None:
        require(not prefixes and sorted(class_order) == list(range(len(classes))), "invalid class order")
        sequence = list(class_order)
    position = {value: i for i, value in enumerate(sequence)}
    forward, backward = [], []
    for i, zero in enumerate(forbidden):
        to_forward = position[next(iter(zero))] < position[owner[i]] if zero else owner[i] != first
        (forward if to_forward else backward).append(i)
    forward.sort(key=lambda i: (position[owner[i]], i))
    backward.sort(key=lambda i: (-position[owner[i]], i))
    require(ordered(matrix, forward) and ordered(matrix, backward), "rank-two order failed")
    require(sorted(forward + backward) == list(range(len(p))), "partition lost an index")
    for prefix, block in zip(prefixes, (forward, backward)):
        require(all(dot(prefix, q[i]) for i in block), "prefix hits its forbidden class")
    return forward, backward


def parity(left, right):
    return (left & right).bit_count() & 1


def literal_check(matrix, a0, b0, witness):
    order, kept, a, b = (witness[key] for key in ("order", "kept", "a", "b"))
    if len(a) != len(a0) or len(b) != len(b0) or sorted(order) != sorted(kept):
        return False
    if len(set(kept)) != len(kept) or any(not 0 <= i < len(a0) for i in kept):
        return False
    if any(type(a[i]) is not int or type(b[i]) is not int or not 0 <= a[i] < 8 or
           not 0 <= b[i] < 8 or a[i] & ~a0[i] or b[i] & ~b0[i] or
           parity(a[i], b[i]) != 1 for i in kept):
        return False
    return all(matrix[i][j] or not parity(a[i], b[j])
               for k, i in enumerate(order) for j in order[k + 1:])


def labelled_blocks(matrix, a0, b0, first, second):
    require(all(matrix[i][i] for i in range(len(matrix))), "zero diagonal")
    require(rank(matrix) <= 3, "rank exceeds three")
    require(all(a & b for a, b in zip(a0, b0)), "empty tied set")
    require(all(matrix[i][j] or not parity(a0[i], b0[j])
                for i in range(len(matrix)) for j in range(len(matrix))), "SG failed")
    require(set(first).isdisjoint(second) and ordered(matrix, first) and ordered(matrix, second),
            "blocks are not disjoint directed orders")
    a, b = [0] * len(matrix), [0] * len(matrix)
    for i in first:
        tied = a0[i] & b0[i]
        a[i], b[i] = a0[i], tied & -tied
    for i in second:
        tied = a0[i] & b0[i]
        a[i], b[i] = tied & -tied, b0[i]
    kept = list(first) + list(second)
    witness = {"a": a, "b": b, "kept": kept, "order": kept}
    require(literal_check(matrix, a0, b0, witness), "literal directed box failed")
    return witness


def rejects(action, message):
    try:
        action()
    except ValueError as error:
        require(message in str(error), "unexpected failure: " + str(error))
        return
    raise ValueError("failure control accepted: " + message)


def rank_two_controls():
    p = [(1, 0), (1, -1), (0, 1), (1, -1), (0, 1), (1, 0), (1, 2), (2, 1)]
    q = [(1, 0), (1, 0), (0, 1), (0, 1), (1, 1), (1, 1), (1, 0), (0, 1)]
    matrix = product(p, q)
    partitions = [partition(p, q, class_order=order) for order in permutations(range(3))]
    require(len(partitions) == 6 and rank(matrix) == 2, "rank-two fixture failed")
    a, b = (0, 1), (1, 0)
    first, second = partition(p, q, (a, b))
    require(6 in second and 7 in first, "free endpoint rows assigned incorrectly")
    require(not dot(a, q[6]) and not dot(b, q[7]), "endpoint mutation not observable")
    one = partition(p, q, (a,))
    absent = partition(p, q, ((1, 3),))
    empty = partition([(1, 2), (2, 1)], [(1, 0), (0, 1)], ((1, 1),))
    require(sorted(empty[0]) == [0, 1] and not empty[1], "empty block or absent kernel mishandled")
    rejects(lambda: partition(p, q, (a, (0, 2))), "independent")
    rejects(lambda: partition(p, q, ((0, 0),)), "nonzero")
    reversed_failure = any(not ordered(matrix, list(reversed(block)))
                           for blocks in partitions for block in blocks)
    require(reversed_failure, "orientation mutation was invisible")
    scaled = [tuple(Fraction(-2, 3) * x for x in row) for row in q]
    require(partition(p, scaled, (a, b)) == (first, second), "projective scaling changed partition")
    return {"P": p, "Q": q, "rank": 2, "class_orders_checked": 6,
            "two_prefixes": [a, b], "two_prefix_blocks": [first, second],
            "two_prefix_total": 10, "one_prefix_blocks": one, "one_prefix_total": 9,
            "absent_kernel_prefix_blocks": absent, "free_endpoint_rows": [6, 7],
            "empty_block_with_absent_kernel": empty,
            "reverse_order_mutant_rejected": True, "dependent_prefixes_rejected": True}


def repeated_direction_controls():
    basis = [[int(i == j) for j in range(3)] for i in range(3)]
    p = basis + [[1, 1, 1]] * 3 + [[0, 1, 0], [1, 2, 0], [1, 0, 0],
                                   [2, 1, 0], [1, 0, 1], [2, 0, 1]]
    directions = [(0, 1, -1), (1, 0, -1), (1, -1, 0)]
    q = basis + [[1, 1, 1], [1, 1, 0], [1, 0, 0]] + [list(row) for row in directions for _ in range(2)]
    matrix = product(p, q)
    require(rank(matrix) == 3 and all(matrix[i][i] for i in range(12)), "repeated fixture failed")
    require(all(not matrix[i][j] for i in (3, 4, 5) for j in range(6, 12)), "common annihilator failed")
    require(all(matrix[i][j] for i in (3, 4, 5) for j in range(3)), "independent S failed")
    first, second = [1, 6, 10, 11], [3, 4, 5, 0]
    require(ordered(matrix, first) and ordered(matrix, second) and set(first).isdisjoint(second), "repeated branch witness failed")
    require(rank([row[6:] for row in matrix[6:]]) == 2, "Z is not rank two")
    require(all(sum(row) == 0 and sum(x == 0 for x in row) == 1 for row in directions), "coordinate-plane premise failed")
    impossible = [[int(i // 2 == j // 2) for j in range(6)] for i in range(6)]
    require(rank(impossible) == 3, "isolated pair blocks lost rank")
    for target in range(3):
        require(rank([list(row) + [int(i == target)] for i, row in enumerate(directions)]) == 3,
                "isolating one coordinate-plane pair became solvable")
    require(projective([-2, -2, -2]) == projective([Fraction(3, 5)] * 3), "projective equality failed")
    require(ordered([[1] * 3 for _ in range(3)], [0, 1, 2]), "small multiplicity control failed")
    return {"P": p, "Q": q, "rank": 3, "C": [3, 4, 5], "S": [0, 1, 2],
            "Z": list(range(6, 12)), "two_four_blocks": [first, second], "Z_rank": 2,
            "hypothetical_three_pair_blocks_rank": 3, "pair_isolation_inconsistent_systems": 3,
            "multiplicity_three_is_not_a_universal_admission_error": True}


def two_plane_controls():
    p = [(1, 0, 0)] * 2 + [(0, 1, 0)] * 2 + [(1, 1, 0)] * 2
    p += [(0, 1, 1), (0, 1, 2), (0, 1, 3), (0, 1, 4), (1, 0, 1), (1, 0, -1)]
    q = [(1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 2, 0), (1, 3, 0), (1, 4, 0)]
    q += [(0, 1, 0), (0, 1, 1), (0, 1, -1), (0, 1, 2), (0, 0, 1), (0, 0, 1)]
    matrix = product(p, q)
    require(rank(matrix) == 3 and all(matrix[i][i] for i in range(12)), "two-plane diagonal failed")
    require([j for j, value in enumerate(matrix[0]) if not value] == list(range(6, 12)), "six-zero row failed")
    for factors in (p, q):
        directions = [projective(row) for row in factors]
        require(max(directions.count(value) for value in directions) <= 2, "two-plane multiplicity failed")
    y, z = list(range(2, 6)), list(range(6, 10))
    left = partition([p[i][:2] for i in y], [q[i][:2] for i in y])
    right = partition([p[i][1:] for i in z], [q[i][1:] for i in z])
    blocks = [[y[i] for i in a] + [z[i] for i in b] for a, b in zip(left, right)]
    require(all(matrix[i][j] for i in y for j in z), "cross-plane complete rectangle failed")
    require(all(ordered(matrix, block) for block in blocks) and sum(map(len, blocks)) == 8,
            "two-plane concatenation failed")
    return {"P": p, "Q": q, "rank": 3, "zero_row": 0, "Z": list(range(6, 12)),
            "removed_C": [0, 1], "removed_D": [10, 11], "blocks": blocks,
            "total_kept": 8, "cross_rectangle_nonzero": True}


def f2_controls():
    points = list(range(1, 8))
    lines = {p: [q for q in points if not parity(p, q)] for p in points}
    require(all(len(line) == 3 for line in lines.values()), "Fano line size failed")
    patterns = [tuple(0 if q == missing else 2 for q in points) for missing in points]
    patterns += [tuple(1 if q in singles else 2 for q in points) for singles in combinations(points, 2)]
    records = []
    for weights in patterns:
        require(sum(weights) == 12 and max(weights) == 2, "F2 multiplicity pattern failed")
        zeros = {p: sum(weights[q - 1] for q in line) for p, line in lines.items()}
        allowed = [p for p in points if zeros[p] <= 5]
        light = [q for q in points if weights[q - 1] < 2]
        require(allowed == [p for p in points if any(q in lines[p] for q in light)], "pencil classification failed")
        require(len(allowed) == (3 if 0 in weights else 5) and 2 * len(allowed) < 12,
                "F2 residual capacity contradiction failed")
        require(len([p for p in points if zeros[p] <= 6]) == 7, "zero-six relaxation not observable")
        records.append({"Q_weights": weights, "allowed_P": allowed, "P_capacity": 2 * len(allowed)})
    return {"patterns": records, "count": 28, "absent_point_patterns": 7,
            "two_singleton_patterns": 21, "capacity_histogram": {"6": 7, "10": 21},
            "relaxing_zero_cap_to_six_loses_this_contradiction": True}


def core_fixture(oracle):
    p0 = [(-1, -3, 0), (1, -1, -2), (3, 3, 3)]
    q0 = [(1, -3, 2), (3, -1, -2), (3, -1, 2)]
    p, q = ([row for row in factors for _ in range(4)] for factors in (p0, q0))
    data = oracle.rational_data(p, q)
    matrix = product(p, q)
    require(matrix == data["M"] and rank(matrix) == 3 and data["tau"] == [2] * 12, "core normalization failed")
    require(data["a0"] == [3] * 8 + [7] * 4 and data["b0"] == [3] * 12 and data["gamma"] == 0,
            "core anchor values failed")
    first = find_ordered(matrix, 4)
    second = find_ordered(matrix, 4, [i for i in range(12) if i not in first])
    require(first is not None and second is not None, "working fixture two blocks missing")
    witness = labelled_blocks(matrix, data["a0"], data["b0"], first, second)
    require(oracle.check_witness(data["a0"], data["b0"], data["arcs"], witness), "frozen definition disagrees")
    require(all(len({i // 4 for i in subset}) == 3 for subset in combinations(range(12), 9)), "nine-set upper bound failed")
    record = {"P": p, "Q": q, "M": matrix, "rank": 3, "gamma": 0, "a0": data["a0"],
              "b0": data["b0"], "tau": data["tau"], "exact_box": 8, "witness": witness,
              "upper_bound": "Every nine-set meets three zero-separated groups: a triangular rank3 label minor contradicts the rank2 target-label space."}
    return record, data


def rational_eight_control(oracle):
    p = [[1, 0, 0], [0, -1, 1], [-1, 1, 0], [0, 1, 0],
         [-1, 1, -1], [1, 0, 0], [0, 0, 1], [0, 0, 1]]
    q = [[1, 0, 0], [0, 0, 1], [0, 1, 0], [1, 1, 0],
         [1, 0, 0], [1, 1, 1], [0, 1, 1], [0, 0, 1]]
    data = oracle.rational_data(p, q)
    matrix = product(p, q)
    require(rank(matrix) == 3 and all(matrix[i][i] for i in range(8)), "rational lift rank failed")
    require(find_ordered(matrix, 4) is None, "rational lift contains an ordered four")
    require(not any(all(not matrix[i][j] and not matrix[j][i] for i, j in combinations(triple, 2))
                    for triple in combinations(range(8), 3)), "rational lift contains an independent triple")
    require(data["gamma"] == 0 and data["tau"] == [1] * 8, "rational lift normalization failed")
    witness = {"a": data["a0"], "b": data["b0"], "kept": list(range(8)), "order": list(range(8))}
    require(literal_check(matrix, data["a0"], data["b0"], witness) and oracle.check_witness(
        data["a0"], data["b0"], data["arcs"], witness), "full eight-row box witness failed")
    return {"P": p, "Q": q, "M": matrix, "rank": 3, "ordered_four_orders_checked": 1680,
            "independent_triples_checked": 56, "has_ordered_four": False,
            "has_independent_triple": False, "gamma": 0, "tau": data["tau"],
            "a0": data["a0"], "b0": data["b0"], "exact_box": 8, "witness": witness,
            "scope": "Counterexample to the proposed eight-row intermediate lemma; not a box-floor counterexample."}


def odd_anchor_control(oracle):
    p0 = [(-1, -3, 0), (1, -1, -2), (3, 3, 3)]
    q0 = [(1, -3, 2), (3, -1, -2), (3, -1, 2)]
    p, q = ([row for row in factors for _ in range(4)] for factors in (p0, q0))
    p[0] = (-1, -2, 0)
    data = oracle.rational_data(p, q)
    require(data["rank"] == 3 and data["gamma"] == 0 and data["tau"] == [1] + [2] * 11,
            "one-odd fixture normalization failed")
    first, second = list(range(4, 8)), list(range(8, 11))
    witness = labelled_blocks(data["M"], data["a0"], data["b0"], first, second)
    # Keep the original twelve-row global anchors throughout the restriction.
    witness["a"][0], witness["b"][0] = data["a0"][0], data["b0"][0]
    witness["kept"] = witness["order"] = first + [0] + second
    require(literal_check(data["M"], data["a0"], data["b0"], witness) and oracle.check_witness(
        data["a0"], data["b0"], data["arcs"], witness), "full-anchor middle insertion failed")
    require(data["M"][0][0] == 5 and data["a0"][0] == 1 and data["b0"][0] == 3,
            "special odd row changed")
    misplaced = {**witness, "order": first + second + [0]}
    require(not literal_check(data["M"], data["a0"], data["b0"], misplaced) and not oracle.check_witness(
        data["a0"], data["b0"], data["arcs"], misplaced), "odd row after suffix was accepted")
    return {"P": p, "Q": q, "rank": 3, "tau": data["tau"], "global_a0": data["a0"],
            "global_b0": data["b0"], "odd_row": 0, "first_block": first, "second_block": second,
            "total_kept": 8, "witness": witness, "anchors_recomputed_on_subset": False,
            "moving_odd_row_after_suffix_rejected": True}


def boundary_controls(oracle, data):
    matrix, a0, b0 = data["M"], data["a0"], data["b0"]
    first, second = list(range(4)), list(range(4, 8))
    zero = [row[:] for row in matrix]
    zero[0][0] = 0
    rejects(lambda: labelled_blocks(zero, a0, b0, first, second), "zero diagonal")
    empty = a0[:]
    empty[0] = 0
    rejects(lambda: labelled_blocks(matrix, empty, b0, first, second), "empty tied set")
    rejects(lambda: labelled_blocks(matrix, [1] * 12, [1] * 12, first, second), "SG failed")
    rank_four = [[int(i // 3 == j // 3) for j in range(12)] for i in range(12)]
    rejects(lambda: labelled_blocks(rank_four, [3] * 12, [3] * 12, [0], [3]), "rank exceeds three")
    invalid = labelled_blocks(matrix, a0, b0, first, second)
    invalid["a"][0] = 8
    require(not literal_check(matrix, a0, b0, invalid) and not oracle.check_witness(
        a0, b0, data["arcs"], invalid), "submask corruption accepted")
    directed = [[int(i <= j) for j in range(3)] for i in range(3)]
    witness = {"a": [1] * 3, "b": [1] * 3, "kept": [0, 1, 2], "order": [0, 1, 2]}
    arcs = [(i, j) for i in range(3) for j in range(3) if i != j and not directed[i][j]]
    require(literal_check(directed, [1] * 3, [1] * 3, witness), "forward witness failed")
    witness["order"] = [2, 1, 0]
    require(not literal_check(directed, [1] * 3, [1] * 3, witness) and
            not oracle.check_witness([1] * 3, [1] * 3, arcs, witness), "reversed witness accepted")
    cycle = [[1, 1, 0], [0, 1, 1], [-1, 0, 1]]
    require(rank(cycle) == 2 and find_ordered(cycle, 3) is None, "cycle mistaken for a directed order")
    old_read = Path.read_bytes
    def counterfeit(path):
        return b'raise RuntimeError("counterfeit executed")\n' if path == HERE / ORACLE else old_read(path)
    with patch.object(Path, "read_bytes", counterfeit):
        rejects(load_oracle, "Input changed: " + ORACLE)
    return ["zero_diagonal", "empty_ties", "SG", "rank_four", "submask_corruption", "directed_order_reversal",
            "rank_two_directed_cycle", "source_corruption_before_execution"]


def build():
    authenticated = authenticate()
    oracle = load_oracle()
    fixture, data = core_fixture(oracle)
    result = {"schema_version": 1, "status": "PASS_FSTAR_TWELVE_LINE_OBSTRUCTION",
            "scope": "Finite exact controls for analytic residual reductions and the F2 theorem; the rational twelve-line box>=8 target remains open.",
            "inputs_sha256": {path: hashlib.sha256(raw).hexdigest() for path, raw in authenticated.items()},
            "working_fixture": fixture, "rational_eight_counterexample": rational_eight_control(oracle),
            "controls": {"rank_two_partition": rank_two_controls(), "repeated_direction": repeated_direction_controls(),
                         "zero_six_two_plane_combination": two_plane_controls(), "F2_residual_capacity": f2_controls(),
                         "odd_global_anchors": odd_anchor_control(oracle),
                         "boundaries": boundary_controls(oracle, data)}}
    return json.loads(json.dumps(result))


def main():
    require(sys.argv[1:] in ([], ["--emit"]), "usage: verify.py [--emit]")
    result = build()
    if sys.argv[1:] == ["--emit"]:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        require(result == json.loads((HERE / "RESULT.json").read_text()), "RESULT.json mismatch")
        print("PASS_FSTAR_TWELVE_LINE_OBSTRUCTION: exact controls; rational twelve-line target open")


if __name__ == "__main__":
    main()
