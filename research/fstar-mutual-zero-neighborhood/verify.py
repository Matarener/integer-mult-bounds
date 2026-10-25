#!/usr/bin/env python3
"""Exact controls for the corrected mutual-zero neighborhood classification.

SPDX-License-Identifier: Apache-2.0
Sagar Thakrar (thakrarsagar), with substantial OpenAI Codex assistance.
Aaron Wang/navinor's PR2890 README is retained unchanged and authenticated;
no predecessor executable or search engine is executed.
"""

from fractions import Fraction
import hashlib
from itertools import combinations, product as cartesian_product
import json
from pathlib import Path
import sys
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "inputs/pr2890-README.md"


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


def source_claim():
    raw = authenticate()[SOURCE]
    lines = raw.decode().splitlines()
    require("Lemma C5" in lines[99] and "G_0[N]` is empty" in lines[101], "retained C5 location changed")
    require("`p(t) = e_2`" in lines[107] and "Lemma C4" in lines[118], "retained coordinate step changed")
    excerpt = "\n".join(lines[99:124]) + "\n"
    return {"path": SOURCE, "C5_start_line": 100, "C4_start_line": 119,
            "lines_100_through_124_sha256": hashlib.sha256(excerpt.encode()).hexdigest(),
            "predecessor_executable_run": False}


def dot(left, right, modulus=0):
    value = sum(x * y for x, y in zip(left, right))
    return value % modulus if modulus else value


def matrix(p, q, modulus=0):
    return [[dot(left, right, modulus) for right in q] for left in p]


def rank(values):
    rows = [[Fraction(value) for value in row] for row in values]
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
                scale = row[column]
                rows[i] = [x - scale * y for x, y in zip(row, rows[cursor])]
        cursor += 1
    return cursor


def inverse(values):
    n = len(values)
    rows = [[Fraction(value) for value in row] + [Fraction(i == j) for j in range(n)]
            for i, row in enumerate(values)]
    for column in range(n):
        pivot = next((i for i in range(column, n) if rows[i][column]), None)
        require(pivot is not None, "singular coordinate change")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        scale = rows[column][column]
        rows[column] = [value / scale for value in rows[column]]
        for i, row in enumerate(rows):
            if i != column:
                scale = row[column]
                rows[i] = [x - scale * y for x, y in zip(row, rows[column])]
    return [row[n:] for row in rows]


def projective(vector, modulus=0):
    values = tuple(value % modulus for value in vector) if modulus else tuple(map(Fraction, vector))
    first = next((value for value in values if value), None)
    require(first is not None, "zero projective vector")
    if modulus:
        return tuple(value * pow(first, -1, modulus) % modulus for value in values)
    return tuple(value / first for value in values)


def mutual_edges(values, vertices=None):
    vertices = range(len(values)) if vertices is None else vertices
    return [(i, j) for i, j in combinations(vertices, 2) if not values[i][j] and not values[j][i]]


def component_check(size, edges):
    """Independently color the literal graph and check each component is complete."""
    adjacent = [set() for _ in range(size)]
    for i, j in edges:
        adjacent[i].add(j)
        adjacent[j].add(i)
    remaining, components, isolates = set(range(size)), [], []
    while remaining:
        start = min(remaining)
        if not adjacent[start]:
            isolates.append(start)
            remaining.remove(start)
            continue
        color, queue = {start: 0}, [start]
        for vertex in queue:
            for neighbor in sorted(adjacent[vertex]):
                if neighbor not in color:
                    color[neighbor] = 1 - color[vertex]
                    queue.append(neighbor)
                require(color[neighbor] != color[vertex], "literal component is not bipartite")
        sides = [[i for i in sorted(color) if color[i] == bit] for bit in (0, 1)]
        require(all(adjacent[i] == set(sides[1 - bit]) for bit in (0, 1) for i in sides[bit]),
                "literal bipartite component is not complete")
        components.append(sides)
        remaining.difference_update(color)
    return components, isolates


def classify(p, q, modulus=0):
    require(len(p) == len(q) and all(len(row) == 2 for row in p + q), "expected paired two-dimensional factors")
    values = matrix(p, q, modulus)
    require(all(values[i][i] for i in range(len(values))), "neighbor diagonal is zero")
    types = [(projective(target, modulus), projective((source[1], -source[0]), modulus))
             for source, target in zip(p, q)]
    require(all(alpha != beta for alpha, beta in types), "own and forbidden directions coincide")
    expected = [(i, j) for i, j in combinations(range(len(p)), 2)
                if types[i] == tuple(reversed(types[j]))]
    actual = mutual_edges(values)
    require(actual == expected, "reciprocal classes disagree with literal mutual zeros")
    components, isolates = component_check(len(p), actual)
    classes = {}
    for i, kind in enumerate(types):
        classes.setdefault(kind, []).append(i)
    return {"edges": actual, "complete_bipartite_components": components, "isolates": isolates,
            "type_classes": [{"own": list(map(str, alpha)), "forbidden": list(map(str, beta)), "vertices": members}
                             for (alpha, beta), members in sorted(classes.items())]}


def dual_coordinates(p, q, center):
    """Use q_center and a basis of ker(p_center) as columns of A."""
    require(all(len(row) == 3 for row in p + q), "expected three-dimensional factors")
    values = matrix(p, q)
    require(values[center][center], "center diagonal is zero")
    pivot = next(i for i, value in enumerate(p[center]) if value)
    columns = [list(map(Fraction, q[center]))]
    for free in range(3):
        if free != pivot:
            vector = [Fraction(0)] * 3
            vector[free] = 1
            vector[pivot] = -Fraction(p[center][free], p[center][pivot])
            columns.append(vector)
    change = [list(row) for row in zip(*columns)]
    inverse_change = inverse(change)
    left = matrix(p, columns)
    right = matrix(q, inverse_change)
    require(matrix(left, right) == values, "dual change altered the matrix")
    require(left[center] == [values[center][center], 0, 0] and right[center] == [1, 0, 0],
            "center normalization failed")
    return left, right, change


def neighborhood(p, q, center):
    values = matrix(p, q)
    require(all(values[i][i] for i in range(len(values))), "neighbor diagonal is zero")
    vertices = [i for i in range(len(values)) if i != center and not values[center][i] and not values[i][center]]
    left, right, change = dual_coordinates(p, q, center)
    require(all(not left[i][0] and not right[i][0] for i in vertices), "mutual neighborhood did not enter two dimensions")
    certificate = classify([left[i][1:] for i in vertices], [right[i][1:] for i in vertices])
    local = [(vertices[i], vertices[j]) for i, j in certificate["edges"]]
    require(local == mutual_edges(values, vertices), "neighborhood indexing changed the graph")
    require(rank([[values[i][j] for j in vertices] for i in vertices]) <= 2, "neighborhood rank exceeded two")
    return {"vertices": vertices, "global_edges": local, "classification": certificate}, left, right, change


def masks(rows):
    return [sum(1 << j for j, value in enumerate(row) if value) for row in rows]


def canonical_unit_data(p, q):
    """Exact canonical normalization for these explicitly 0/+-1 fixtures."""
    require(all(value in (-1, 0, 1) for row in p + q for value in row), "unit-alphabet fixture required")
    require(all(any(row[j] for row in factors) for factors in (p, q) for j in range(3)), "inactive factor column")
    a0, b0 = masks(p), masks(q)
    values = matrix(p, q)
    require(all(values[i][i] for i in range(len(values))), "zero fixture diagonal")
    require(all(((a0[i] & b0[j]).bit_count() & 1) == (values[i][j] % 2)
                for i in range(len(p)) for j in range(len(q))), "scope identity failed")
    return {"column_minima_P": [0, 0, 0], "column_minima_Q": [0, 0, 0], "gamma": 0,
            "a0": a0, "b0": b0, "tau": [(a & b).bit_count() for a, b in zip(a0, b0)]}


def literal_box(values, a0, b0, a, b, order):
    if sorted(order) != list(range(len(values))):
        return False
    if any(type(a[i]) is not int or type(b[i]) is not int or not 0 <= a[i] < 8 or
           not 0 <= b[i] < 8 or a[i] & ~a0[i] or b[i] & ~b0[i] or
           (a[i] & b[i]).bit_count() % 2 != 1 for i in order):
        return False
    return all(values[i][j] or (a[i] & b[j]).bit_count() % 2 == 0
               for k, i in enumerate(order) for j in order[k + 1:])


def counterexamples():
    p0 = [(1, 1, 0), (1, 0, 1), (0, 1, 1)]
    q0 = [(1, 1, -1), (1, -1, 1), (-1, 1, 1)]
    require(matrix(p0, q0) == [[2 * int(i == j) for j in range(3)] for i in range(3)], "2I3 fixture changed")
    require(projective(p0[0]) != projective(q0[0]), "counterexample center became parallel")
    small, left, right, change = neighborhood(p0, q0, 0)
    require(small["vertices"] == [1, 2] and small["global_edges"] == [(1, 2)], "minimal counterexample failed")
    normalized = canonical_unit_data(p0, q0)
    require(normalized["a0"] == [3, 5, 6] and normalized["b0"] == [7] * 3 and normalized["tau"] == [2] * 3,
            "minimal canonical anchors changed")
    p, q = ([row for row in factors for _ in range(4)] for factors in (p0, q0))
    values = matrix(p, q)
    expected = [[2 * int(i // 4 == j // 4) for j in range(12)] for i in range(12)]
    require(values == expected and rank(values) == 3, "twelve-row matrix changed")
    large, _left, _right, _change = neighborhood(p, q, 0)
    require(large["vertices"] == list(range(4, 12)) and len(large["global_edges"]) == 16, "K4,4 neighborhood failed")
    anchors = canonical_unit_data(p, q)
    require(anchors["tau"] == [2] * 12, "twelve-row ties changed")
    labels = [1] * 4 + [4] * 4 + [2] * 4
    require(literal_box(values, anchors["a0"], anchors["b0"], labels, labels, list(range(12))), "full-box twelve witness failed")
    require(projective(left[0]) == projective(right[0]), "dual change did not change parallel status")
    return {"minimal": {"P": p0, "Q": q0, "M": matrix(p0, q0), "canonical": normalized,
                        "neighborhood": small, "center_nonparallel": True,
                        "minimal_vertex_count": 3, "reason_minimal": "An edge in an open neighborhood requires its center and two distinct neighbors."},
            "twelve": {"P": p, "Q": q, "M": values, "rank": 3, "canonical": anchors,
                       "neighborhood": large, "full_box": 12, "labels_a": labels, "labels_b": labels,
                       "order": list(range(12))},
            "dual_change": {"A": [[str(x) for x in row] for row in change],
                            "transformed_P": [[str(x) for x in row] for row in left],
                            "transformed_Q": [[str(x) for x in row] for row in right],
                            "matrix_preserved": True, "center_parallel_after": True}}


def multiple_components():
    directions = [(1, i) for i in range(6)]
    kinds = [(0, 1)] * 2 + [(1, 0)] * 3 + [(2, 3)] + [(3, 2)] * 2 + [(4, 5)]
    p = [(directions[forbidden][1], -1) for own, forbidden in kinds]
    q = [directions[own] for own, forbidden in kinds]
    direct = classify(p, q)
    require([list(map(len, sides)) for sides in direct["complete_bipartite_components"]] == [[2, 3], [1, 2]]
            and direct["isolates"] == [8], "multiple reciprocal components failed")
    outer_p = [(1, 0, 0)] + [(0, *row) for row in p]
    outer_q = [(1, 0, 0)] + [(0, *row) for row in q]
    embedded, _p, _q, _change = neighborhood(outer_p, outer_q, 0)
    require(embedded["classification"]["edges"] == direct["edges"] and rank(matrix(outer_p, outer_q)) == 3,
            "rank-three embedding disagrees")
    rank_one = classify([(1, 0), (2, 0), (-3, 0)], [(1, 0), (2, 1), (3, 2)])
    require(not rank_one["edges"] and rank_one["isolates"] == [0, 1, 2], "rank-one boundary failed")
    empty = neighborhood([(1, 0, 0)], [(1, 0, 0)], 0)[0]
    require(not empty["vertices"] and not empty["classification"]["edges"] and
            not empty["classification"]["isolates"], "empty neighborhood boundary failed")
    return {"P": outer_p, "Q": outer_q, "rank": 3, "neighborhood": embedded,
            "rank_one_isolates": rank_one["isolates"], "empty_neighborhood": empty}


def f2_controls():
    vectors = [(1, 0), (0, 1), (1, 1)]
    kinds = [(p, q) for p in vectors for q in vectors if dot(p, q, 2)]
    require(len(kinds) == 6, "F2 admissible type count changed")
    configurations = subsets = max_edges = 0
    for weights in cartesian_product(range(3), repeat=6):
        if not any(weights):
            continue
        p = [kind[0] for kind, count in zip(kinds, weights) for _ in range(count)]
        q = [kind[1] for kind, count in zip(kinds, weights) for _ in range(count)]
        certificate = classify(p, q, 2)
        configurations += 1
        subsets += max(weights) == 1
        max_edges = max(max_edges, len(certificate["edges"]))
    require(configurations == 728 and subsets == 63, "finite F2 coverage changed")
    return {"admissible_types": [[list(p), list(q)] for p, q in kinds],
            "multiplicity_domain": [0, 1, 2], "nonempty_weighted_configurations": configurations,
            "nonempty_simple_subsets": subsets, "maximum_literal_edges": max_edges,
            "scope": "All six rank2 F2 factor types with multiplicities at most two; a control, not the proof over arbitrary fields."}


def rejects(action, message):
    try:
        action()
    except ValueError as error:
        require(message in str(error), "unexpected failure: " + str(error))
        return
    raise ValueError("failure control accepted: " + message)


def boundary_controls():
    zero = [[int(i == j == 0) for j in range(4)] for i in range(4)]
    require(mutual_edges(zero, [1, 2, 3]) == [(1, 2), (1, 3), (2, 3)] and rank(zero) == 1,
            "zero-diagonal triangle boundary failed")
    rejects(lambda: classify([(0, 0)] * 3, [(0, 0)] * 3), "neighbor diagonal")
    rejects(lambda: component_check(3, [(0, 1), (0, 2), (1, 2)]), "not bipartite")
    cycle_p = [(1, 0), (0, 1), (-1, 1)]
    cycle_q = [(1, 0), (1, 1), (0, 1)]
    cycle = matrix(cycle_p, cycle_q)
    require(cycle == [[1, 1, 0], [0, 1, 1], [-1, 0, 1]] and rank(cycle) == 2,
            "one-way zero cycle changed")
    one_way = [(i, j) for i, j in combinations(range(3), 2) if not cycle[i][j] or not cycle[j][i]]
    require(one_way == [(0, 1), (0, 2), (1, 2)] and not mutual_edges(cycle), "one-way and mutual zeros conflated")
    embedded_p = [(1, 0, 0)] + [(0, *row) for row in cycle_p]
    embedded_q = [(1, 0, 0)] + [(0, *row) for row in cycle_q]
    require(rank(matrix(embedded_p, embedded_q)) == 3 and
            neighborhood(embedded_p, embedded_q, 0)[0]["classification"]["isolates"] == [0, 1, 2],
            "one-way triangle embedding failed")
    require(dot((1, 1, 0), (1, 1, -1)) == 2 and dot((0, 1, 0), (1, 0, 0)) == 0,
            "invalid nonparallel coordinate step no longer changes the diagonal")
    old_read = Path.read_bytes
    def counterfeit(path):
        return b"Counterfeit C5 text\n" if path == HERE / SOURCE else old_read(path)
    with patch.object(Path, "read_bytes", counterfeit):
        rejects(source_claim, "Input changed: " + SOURCE)
    return {"dropped_neighbor_diagonal": {"M": zero, "induced_graph": "triangle"},
            "one_way_zero_boundary": {"P": embedded_p, "Q": embedded_q,
                                      "neighbor_matrix": cycle, "one_way_graph": "triangle", "mutual_edges": []},
            "invalid_coordinate_step_diagonal_before": 2, "invalid_coordinate_step_diagonal_after": 0,
            "zero_diagonal_and_odd_cycle_rejected": True, "source_corruption_rejected_before_text_use": True}


def build():
    authenticated = authenticate()
    result = {"schema_version": 1, "status": "PASS_FSTAR_MUTUAL_ZERO_NEIGHBORHOOD",
              "scope": "Exact counterexamples and finite controls for the analytic corrected classification; no predecessor search replay or twelve-line floor claim.",
              "inputs_sha256": {path: hashlib.sha256(raw).hexdigest() for path, raw in authenticated.items()},
              "source_claim": source_claim(), "counterexamples": counterexamples(),
              "multiple_components": multiple_components(), "F2_controls": f2_controls(),
              "boundaries": boundary_controls()}
    return json.loads(json.dumps(result))


def main():
    require(sys.argv[1:] in ([], ["--emit"]), "usage: verify.py [--emit]")
    result = build()
    if sys.argv[1:] == ["--emit"]:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        require(result == json.loads((HERE / "RESULT.json").read_text()), "RESULT.json mismatch")
        print("PASS_FSTAR_MUTUAL_ZERO_NEIGHBORHOOD: source-bound counterexamples and corrected-classification controls")


if __name__ == "__main__":
    main()
