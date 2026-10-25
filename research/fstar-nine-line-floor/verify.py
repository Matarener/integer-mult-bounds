#!/usr/bin/env python3
"""Exact controls for the analytic seven/nine-row matrix and box proofs.

SPDX-License-Identifier: Apache-2.0
Author: Sagar Thakrar (thakrarsagar), with substantial OpenAI Codex assistance.
These finite controls are not a machine proof of the universal matrix theorem.
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
    authenticated = {}
    rows = [(root, row) for row in manifest["files"] if row["usage"] == "input"]
    rows += [(HERE, row) for row in manifest["frozen_sources"]]
    for base, row in rows:
        raw = (base / row["path"]).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row["sha256"],
                "Input changed: " + row["path"])
        authenticated[row["path"]] = raw
    return authenticated


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
        divisor = rows[cursor][column]
        rows[cursor] = [value / divisor for value in rows[cursor]]
        for i, row in enumerate(rows):
            if i != cursor:
                factor = row[column]
                rows[i] = [x - factor * y for x, y in zip(row, rows[cursor])]
        cursor += 1
    return cursor


def transpose(matrix):
    return list(map(list, zip(*matrix)))


def multiply(left, right):
    return [[sum(x * y for x, y in zip(row, column))
             for column in transpose(right)] for row in left]


def dot(left, right):
    return (left & right).bit_count() & 1


def ordered(matrix, indices):
    return len(set(indices)) == len(indices) and all(
        matrix[i][j] != 0 for position, i in enumerate(indices)
        for j in indices[position + 1:])


def ordered_sets(matrix, size, allowed=None):
    """Keep one genuine orientation per support, with physical rows distinct."""
    allowed = range(len(matrix)) if allowed is None else allowed
    answer = {}
    for subset in combinations(allowed, size):
        order = next((candidate for candidate in permutations(subset)
                      if ordered(matrix, candidate)), None)
        if order is not None:
            answer[subset] = order
    return answer


def independent_sets(matrix, size):
    return [subset for subset in combinations(range(len(matrix)), size)
            if all(not matrix[i][j] and not matrix[j][i]
                   for i, j in combinations(subset, 2))]


def admit(matrix, a0, b0):
    n = len(matrix)
    require(n in (7, 9) and all(len(row) == n for row in matrix), "expected seven or nine square rows")
    require(len(a0) == n and len(b0) == n, "anchor length mismatch")
    require(all(type(mask) is int and 0 <= mask < 8 for mask in a0 + b0), "invalid anchor mask")
    require(all(matrix[i][i] for i in range(n)), "zero diagonal")
    require(rank(matrix) <= 3, "matrix rank exceeds three")
    require(all(a & b for a, b in zip(a0, b0)), "empty tied set")
    require(all(matrix[i][j] or dot(a0[i], b0[j]) == 0
                for i in range(n) for j in range(n)), "SG failed")


def blocks(matrix):
    n = len(matrix)
    first_size = 3 if n == 7 else 4
    for first in ordered_sets(matrix, first_size).values():
        remaining = [i for i in range(n) if i not in first]
        second = next(iter(ordered_sets(matrix, 2, remaining).values()), None)
        if second is not None:
            return first, second
    if n == 9:
        triples = list(ordered_sets(matrix, 3).values())
        for first, second in combinations(triples, 2):
            if set(first).isdisjoint(second):
                return first, second
    raise ValueError("no two-block witness; analytic theorem premise or implementation failed")


def literal_check(matrix, a0, b0, witness):
    order, kept = witness["order"], witness["kept"]
    a, b = witness["a"], witness["b"]
    if len(a) != len(a0) or len(b) != len(a0) or sorted(order) != sorted(kept):
        return False
    if len(set(kept)) != len(kept) or any(not 0 <= i < len(a0) for i in kept):
        return False
    if any(type(a[i]) is not int or type(b[i]) is not int or
           not 0 <= a[i] < 8 or not 0 <= b[i] < 8 or
           a[i] & ~a0[i] or b[i] & ~b0[i] or not dot(a[i], b[i]) for i in kept):
        return False
    return all(matrix[i][j] or not dot(a[i], b[j])
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
    order = list(first) + list(second)
    witness = {"a": a, "b": b, "kept": order, "order": order}
    require(literal_check(matrix, a0, b0, witness), "constructed labels violate the directed box")
    return witness


def construct(matrix, a0, b0):
    admit(matrix, a0, b0)
    return labelled_blocks(matrix, a0, b0, *blocks(matrix))


def fixture(sizes, oracle):
    p0 = [(-1, -3, 0), (1, -1, -2), (3, 3, 3)]
    q0 = [(1, -3, 2), (3, -1, -2), (3, -1, 2)]
    p = [row for row, count in zip(p0, sizes) for _ in range(count)]
    q = [row for row, count in zip(q0, sizes) for _ in range(count)]
    data = oracle.rational_data(p, q)
    matrix = multiply(p, transpose(q))
    groups = [g for g, count in enumerate(sizes) for _ in range(count)]
    expected = [[(8 if g < 2 else 12) if g == h else 0 for h in groups] for g in groups]
    require(matrix == expected, "fixture zero-separated block matrix changed")
    require(matrix == data["M"] and rank(matrix) == data["rank"] == 3, "fixture rank or product changed")
    require(data["gamma"] == 0 and data["tau"] == [2] * sum(sizes), "fixture normalization changed")
    require(data["a0"] == [3 if g < 2 else 7 for g in groups] and
            data["b0"] == [3] * sum(sizes), "fixture anchors changed")
    witness = construct(matrix, data["a0"], data["b0"])
    require(oracle.check_witness(data["a0"], data["b0"], data["arcs"], witness), "frozen definition rejected witness")
    first, second = list(range(sizes[0])), list(range(sizes[0], sizes[0] + sizes[1]))
    sharp = labelled_blocks(matrix, data["a0"], data["b0"], first, second)
    exact_box = sum(sorted(sizes)[-2:])
    require(len(sharp["kept"]) == exact_box and oracle.check_witness(
        data["a0"], data["b0"], data["arcs"], sharp), "sharp witness failed")
    require(all(len({groups[i] for i in subset}) == 3
                for subset in combinations(range(sum(sizes)), exact_box + 1)), "upper-bound premise failed")
    triples = list(ordered_sets(matrix, 3))
    narrow = any(set(left).isdisjoint(right) for left, right in combinations(triples, 2))
    record = {"sizes": list(sizes), "M": matrix, "rank": 3, "gamma": 0,
              "a0": data["a0"], "b0": data["b0"], "tau": data["tau"],
              "constructor_witness": witness, "exact_box": exact_box, "sharp_witness": sharp,
              "has_disjoint_triples": narrow,
              "upper_bound": "every larger subset meets all three zero-separated groups; its triangular label minor has rank3, while target labels have rank at most2"}
    return record, data, p, q


def rejects(action, fragment):
    try:
        action()
    except ValueError as error:
        require(fragment in str(error), "unexpected rejection: " + str(error))
        return
    raise ValueError("failure control accepted: " + fragment)


def boundary_controls(oracle, data, p, q):
    matrix, a0, b0 = data["M"], data["a0"], data["b0"]
    bad = [row[:] for row in matrix]
    bad[0][0] = 0
    rejects(lambda: construct(bad, a0, b0), "zero diagonal")
    bad_a = a0[:]
    bad_a[0] = 0
    rejects(lambda: construct(matrix, bad_a, b0), "empty tied set")
    rejects(lambda: construct(matrix, [1] * 9, [1] * 9), "SG failed")
    groups = [0, 0, 0, 1, 1, 2, 2, 3, 3]
    rank_four = [[int(i == j) for j in groups] for i in groups]
    require(rank(rank_four) == 4 and not ordered_sets(rank_four, 4), "rank boundary changed")
    rejects(lambda: construct(rank_four, [3] * 9, [3] * 9), "rank exceeds three")
    rejects(lambda: blocks(rank_four), "no two-block witness")
    witness = construct(matrix, a0, b0)
    bad_witness = {key: value[:] for key, value in witness.items()}
    bad_witness["a"][witness["kept"][0]] = 8
    require(not literal_check(matrix, a0, b0, bad_witness) and not oracle.check_witness(
        a0, b0, data["arcs"], bad_witness), "out-of-box label accepted")
    scales = [Fraction(-3, 2), Fraction(5, 4), Fraction(7)]
    rescaled = oracle.rational_data([[x*s for x, s in zip(row, scales)] for row in p],
                                   [[x/s for x, s in zip(row, scales)] for row in q])
    require(all(rescaled[key] == data[key] for key in ("M", "a0", "b0", "tau")), "rational rescaling failed")
    old_read = Path.read_bytes
    def counterfeit(path):
        return b'raise RuntimeError("counterfeit executed")\n' if path == HERE / ORACLE else old_read(path)
    with patch.object(Path, "read_bytes", counterfeit):
        rejects(load_oracle, "Input changed: " + ORACLE)
    return ["zero_diagonal", "empty_ties", "SG", "rank_four", "submask",
            "exact_rational_rescaling", "source_corruption_before_execution"]


def orientation_controls(oracle):
    arcs = [(i, j) for i in range(3) for j in range(3) if i != j]
    for pattern in range(64):
        matrix = [[int(i == j) for j in range(3)] for i in range(3)]
        for bit, (i, j) in enumerate(arcs):
            matrix[i][j] = int(bool(pattern & (1 << bit)))
        direct = any(matrix[i][j] and matrix[i][k] and matrix[j][k]
                     for i, j, k in permutations(range(3)))
        require(bool(ordered_sets(matrix, 3)) == direct, "directed predicate mismatch")
    cycle = [[-2, 0, 2], [-8, -2, 0], [0, 2, 8]]
    require(rank(cycle) == 2 and not ordered_sets(cycle, 3), "directed-cycle control failed")
    require(all(cycle[i][j] or cycle[j][i] for i, j in combinations(range(3), 2)), "not an undirected triangle")
    directed = [[1, 1, 1], [0, 1, 1], [0, 0, 1]]
    require(ordered(directed, (0, 1, 2)) and not ordered(directed, (2, 1, 0)), "order reversal was ignored")
    # Definition-level order control; no global SG premise is claimed here.
    witness = {"a": [1]*3, "b": [1]*3, "kept": [0, 1, 2], "order": [0, 1, 2]}
    zeros = [(i, j) for i in range(3) for j in range(3) if i != j and not directed[i][j]]
    require(literal_check(directed, [1]*3, [1]*3, witness) and
            oracle.check_witness([1]*3, [1]*3, zeros, witness), "forward definition witness failed")
    witness["order"] = [2, 1, 0]
    require(not literal_check(directed, [1]*3, [1]*3, witness) and
            not oracle.check_witness([1]*3, [1]*3, zeros, witness), "reversed definition witness accepted")
    return {"all_directed_three_patterns": 64, "rank_two_directed_cycle": cycle,
            "reverse_order_rejected": True}


def cyclic_minor_controls():
    invertible = [[1, 1, 0], [0, 1, 1], [1, 0, 1]]
    inverse = [[Fraction(x, 2) for x in row] for row in [[1, -1, 1], [1, 1, -1], [-1, 1, 1]]]
    identity = [[int(i == j) for j in range(3)] for i in range(3)]
    require(multiply(invertible, inverse) == identity and all(all(row) for row in inverse), "cycle inverse not dense")
    dense_outside = [invertible[i] + identity[i] for i in range(3)]
    dense_outside += [identity[i] + inverse[i] for i in range(3)]
    require(rank(dense_outside) == 3 and ordered(dense_outside, (3, 4, 5)), "invertible cycle extension failed")
    singular = [[1, 1, 0], [0, 1, 1], [-1, 0, 1]]
    left_null = [1, -1, 1]
    require(rank(singular) == 2 and multiply([left_null], singular) == [[0, 0, 0]], "singular cycle null relation failed")
    sparse_columns = [[value if i == j else 0 for i in range(3)]
                      for j in range(3) for value in (-2, -1, 1, 2)]
    require(all(sum(a*b for a, b in zip(left_null, column)) for column in sparse_columns), "one-sparse dependence control failed")
    p_cycle = [[1, 0, 0], [0, 1, 0], [-1, 1, 0]]
    q_cycle = [[1, 0, 0], [1, 1, 0], [0, 1, 1]]
    p = p_cycle + [[1, -1, 1], [0, 1, -1], [0, 0, 1]]
    q = q_cycle + [[0, 0, 1]] * 3
    require(rank(p_cycle) == 2 and rank(q_cycle) == 3 and
            multiply(p_cycle, transpose(q_cycle)) == singular, "cycle factor ranks failed")
    rank_two_factor = multiply(p, transpose(q))
    require(rank(rank_two_factor) == 3 and ordered(rank_two_factor, (3, 4, 5)), "singular cycle extension failed")
    require(all(not rank_two_factor[i][j] for i in range(3) for j in range(3, 6)), "annihilator columns not zero")
    require([row[:3] for row in rank_two_factor[3:]] == identity, "outside sparse restrictions changed")
    return {"invertible_cycle_inverse": [[str(x) for x in row] for row in inverse],
            "singular_cycle": singular, "left_null": left_null,
            "one_sparse_columns_rejected": len(sparse_columns),
            "both_outside_triples_present": True}


def diagonal_reconstruction(matrix, basis):
    require(all(not matrix[i][j] for i in basis for j in basis if i != j), "basis not diagonal")
    require(all(matrix[i][i] for i in basis), "basis diagonal singular")
    return [[sum(Fraction(matrix[u][i]) * matrix[i][v] / matrix[i][i] for i in basis)
             for v in range(len(matrix))] for u in range(len(matrix))]


def basis_support_controls():
    identity = [[int(i == j) for j in range(3)] for i in range(3)]
    x = [[1, 1, 0], [0, 1, 1], [1, 0, 1]]
    xi = [[Fraction(v, 2) for v in row] for row in [[1, -1, 1], [1, 1, -1], [-1, 1, 1]]]
    p = identity + xi + [[1, 2, 1], [1, 0, 1], [0, 1, 2]]
    q = identity + transpose(x) + [[1, 0, 1], [1, 1, 0], [0, 1, 1]]
    matrix = multiply(p, transpose(q))
    require(rank(matrix) == 3 and all(matrix[i][i] for i in range(9)), "dual basis fixture failed")
    six = [row[:6] for row in matrix[:6]]
    require(not ordered_sets(six, 3), "six-row seed has an ordered triple")
    supports = []
    for basis in ((0, 1, 2), (3, 4, 5)):
        require(diagonal_reconstruction(matrix, basis) == matrix, "Schur reconstruction failed")
    for w in (6, 7, 8):
        edges = [(i, j) for i in range(3) for j in range(3, 6)
                 if any(ordered(matrix, order) for order in permutations((w, i, j)))]
        require(edges, "empty auxiliary family")
        for part in (range(3), range(3, 6)):
            incident = {vertex for edge in edges for vertex in edge if vertex in part}
            neighbors = {i for i in part if matrix[w][i] or matrix[i][w]}
            require(incident == neighbors, "auxiliary family support lost a neighbor")
        supports.append({"vertex": w, "edges": [list(edge) for edge in edges]})
    bad = [row[:] for row in matrix]
    bad[6][7] += 1
    require(diagonal_reconstruction(bad, (0, 1, 2)) != bad and rank(bad) > 3, "Schur mutation was invisible")
    return {"six_row_independent_triples": [list(s) for s in independent_sets(six, 3)],
            "two_basis_entry_checks": 162, "auxiliary_families": supports,
            "rank_breaking_entry_mutation_rejected": True}


def nonempty_submasks(mask):
    submask = mask
    while submask:
        yield submask
        submask = (submask - 1) & mask


def family_classification(families, endpoints):
    common = set(range(6))
    for family in families:
        for edge, vertices in enumerate(endpoints):
            if family & (1 << edge):
                common.intersection_update(vertices)
    if common:
        return "common_center"
    if any(a == b and a.bit_count() == 1 for a, b in combinations(families, 2)):
        return "equal_singletons"
    return None


def family_controls():
    endpoints = [{i, 3 + j} for i in range(3) for j in range(3)]
    meeting = [sum(1 << j for j, right in enumerate(endpoints) if left & right) for left in endpoints]
    allowed = [511] * 512
    for family in range(1, 512):
        edge = (family & -family).bit_length() - 1
        allowed[family] = allowed[family ^ (1 << edge)] & meeting[edge]
    counts = {"common_center": 0, "equal_singletons": 0}
    for first in range(1, 512):
        for second in nonempty_submasks(allowed[first]):
            if second < first:
                continue
            for third in nonempty_submasks(allowed[first] & allowed[second]):
                if third < second:
                    continue
                classification = family_classification((first, second, third), endpoints)
                require(classification is not None, "cross-intersecting family classification failed")
                counts[classification] += 1
    require(all(counts.values()), "family control missed a proof branch")
    triangle = [{0, 1}, {1, 2}, {0, 2}]
    require(all(a & b for a, b in combinations(triangle, 2)) and
            family_classification((1, 2, 4), triangle) is None, "bipartiteness control failed")
    return {"nonempty_edge_families": 511, "unordered_family_triples": sum(counts.values()),
            "classification_counts": counts, "nonbipartite_triangle_rejected": True}


def build():
    authenticated = authenticate()
    oracle = load_oracle()
    nine, data, p, q = fixture((3, 3, 3), oracle)
    seven, _data, _p, _q = fixture((3, 2, 2), oracle)
    narrow, _data, _p, _q = fixture((5, 2, 2), oracle)
    require(nine["exact_box"] == 6 and seven["exact_box"] == 5 and
            narrow["exact_box"] == 7 and not narrow["has_disjoint_triples"], "sharp/narrow controls failed")
    return {"schema_version": 1, "status": "PASS_FSTAR_NINE_LINE_FLOOR",
            "scope": "exact controls for an analytic proof; no exhaustive matrix census or formal kernel claim",
            "inputs_sha256": {name: hashlib.sha256(raw).hexdigest() for name, raw in authenticated.items()},
            "fixtures": {"nine_sharp": nine, "seven_sharp": seven, "narrow_three_plus_three_failure": narrow},
            "controls": {"boundaries": boundary_controls(oracle, data, p, q),
                         "orientation": orientation_controls(oracle), "cyclic_minors": cyclic_minor_controls(),
                         "dual_basis_support": basis_support_controls(), "bipartite_families": family_controls()}}


def main():
    require(sys.argv[1:] in ([], ["--emit"]), "usage: verify.py [--emit]")
    receipt = build()
    if sys.argv[1:] == ["--emit"]:
        print(json.dumps(receipt, sort_keys=True, indent=2))
    else:
        require(receipt == json.loads((HERE / "RESULT.json").read_text()), "RESULT.json mismatch")
        print("PASS_FSTAR_NINE_LINE_FLOOR: exact fixtures, proof-branch controls and source binding")


if __name__ == "__main__":
    main()
