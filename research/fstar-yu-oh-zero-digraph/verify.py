#!/usr/bin/env python3
"""Exact coloring, matched-unit and general-box certificates for Yu--Oh rays.

SPDX-License-Identifier: Apache-2.0
Sagar Thakrar (thakrarsagar), with substantial OpenAI Codex assistance.
The thirteen-ray construction is due to Yu and Oh (arXiv:1109.4396v1).
The released question is Aaron Wang/navinor's PR2890; the definition-level
oracle is the author's unchanged PR3393 file, authenticated before execution.
"""

from collections import Counter
import hashlib
from itertools import combinations, permutations, product
import json
from pathlib import Path
import sys
import types
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ORACLE = "inputs/pr3393-independent_box.py"
PREDECESSOR = "inputs/pr2890-README.md"


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


def source_question():
    lines = authenticate()[PREDECESSOR].decode().splitlines()
    require("Is `chi(Z) <= 3` forced at rank 3?" in lines[240], "released question moved")
    require("Would `chi(Z) >= 4` even falsify F-star?" in lines[247], "released box question moved")
    excerpt = "\n".join(lines[240:252]) + "\n"
    return {"path": PREDECESSOR, "question_lines": [241, 248],
            "lines_241_through_252_sha256": hashlib.sha256(excerpt.encode()).hexdigest(),
            "predecessor_search_executed": False}


def rays():
    return [vector for vector in product((-1, 0, 1), repeat=3)
            if any(vector) and next(value for value in vector if value) == 1]


def coloring(adjacent, count):
    """Exact backtracking; only global renaming of unused colors is removed."""
    colors = [-1] * len(adjacent)
    nodes = 0

    def visit():
        nonlocal nodes
        nodes += 1
        remaining = [i for i, color in enumerate(colors) if color < 0]
        if not remaining:
            return colors[:]
        vertex = max(remaining, key=lambda i: (
            len({colors[j] for j in adjacent[i] if colors[j] >= 0}), len(adjacent[i]), -i))
        forbidden = {colors[j] for j in adjacent[vertex]}
        for color in range(min(count, 2 + max(colors))):
            if color not in forbidden:
                colors[vertex] = color
                answer = visit()
                if answer is not None:
                    return answer
        colors[vertex] = -1
        return None

    answer = visit()
    return answer, nodes


def face_obstruction(vectors, adjacent):
    axes = [vectors.index(tuple(int(i == j) for j in range(3))) for i in range(3)]
    pairs = [[vectors.index(positive), vectors.index(negative)] for positive, negative in
             [((0, 1, 1), (0, 1, -1)), ((1, 0, 1), (1, 0, -1)), ((1, 1, 0), (1, -1, 0))]]
    bodies = [vectors.index(row) for row in ((1, 1, 1), (1, 1, -1), (1, -1, 1), (1, -1, -1))]
    require(all(j in adjacent[i] for i, j in combinations(axes, 2)), "axes do not force three colors")
    require(all(pair[1] in adjacent[pair[0]] and all(face in adjacent[axes[i]] for face in pair)
                for i, pair in enumerate(pairs)), "face orientation premise failed")
    records = []
    for bits in product((0, 1), repeat=3):
        colors = [-1] * 13
        for i, axis in enumerate(axes):
            colors[axis] = i
        for i, pair in enumerate(pairs):
            available = [color for color in range(3) if color != i]
            colors[pair[0]], colors[pair[1]] = available[bits[i]], available[1 - bits[i]]
        blocked = [body for body in bodies if {colors[j] for j in adjacent[body]} == {0, 1, 2}]
        require(len(blocked) == 1, "three-color obstruction failed")
        records.append({"orientation": bits, "face_colors": [[colors[j] for j in pair] for pair in pairs],
                        "blocked_body": blocked[0], "neighbor_colors": sorted(colors[j] for j in adjacent[blocked[0]])})
    require([vectors[record["blocked_body"]] for record in records] ==
            [(1, -1, 1), (1, -1, -1), (1, 1, 1), (1, 1, -1),
             (1, 1, -1), (1, 1, 1), (1, -1, -1), (1, -1, 1)], "orientation table changed")
    return {"axes": axes, "face_pairs": pairs, "bodies": bodies, "orientations": records,
            "coverage": "After normalizing the three axis colors, each orthogonal face pair has exactly two choices."}


def unit_pivots(supports, adjacent):
    size = len(supports)
    adjacency = [sum(1 << j for j in row) for row in adjacent]
    alpha = [0] * (1 << size)
    independent = [0] * (1 << size)
    for mask in range(1, 1 << size):
        bit = mask & -mask
        vertex = bit.bit_length() - 1
        omit = mask ^ bit
        include = omit & ~adjacency[vertex]
        if 1 + alpha[include] > alpha[omit]:
            alpha[mask], independent[mask] = 1 + alpha[include], bit | independent[include]
        else:
            alpha[mask], independent[mask] = alpha[omit], independent[omit]
    require(all(alpha[(1 << i) | (1 << j)] == 1 for i in range(size) for j in adjacent[i]),
            "bidirectional edge was not excluded from an acyclic class")
    histogram, best = Counter(), None
    choices = [[j for j in range(3) if support & (1 << j)] for support in supports]
    for pivot in product(*choices):
        classes = [sum(1 << i for i, color in enumerate(pivot) if color == j) for j in range(3)]
        value = sum(alpha[group] for group in classes)
        histogram[value] += 1
        if best is None or value > best["value"]:
            kept = independent[classes[0]] | independent[classes[1]] | independent[classes[2]]
            best = {"value": value, "pivot_coordinates": pivot,
                    "kept": [i for i in range(size) if kept & (1 << i)]}
    require(sum(histogram.values()) == 5184 and best["value"] == 12, "matched-unit census changed")
    require(dict(histogram) == {7: 6, 8: 378, 9: 2118, 10: 2046, 11: 588, 12: 48}, "pivot histogram changed")
    labels = [1 << color for color in best["pivot_coordinates"]]
    witness = {"a": labels, "b": labels, "kept": best["kept"], "order": best["kept"]}
    return {"maps": 5184, "histogram": dict(sorted(histogram.items())), "maximum": 12,
            "best": best, "witness": witness,
            "upper_bound": "A matched-unit witness keeping all13 would be a proper three-coloring of the bidirected zero graph."}


def literal_check(values, supports, witness):
    a, b, kept, order = (witness[key] for key in ("a", "b", "kept", "order"))
    if len(a) != len(values) or len(b) != len(values) or sorted(order) != sorted(kept):
        return False
    if len(set(kept)) != len(kept) or any(not 0 <= i < len(values) for i in kept):
        return False
    if any(type(a[i]) is not int or type(b[i]) is not int or not 0 <= a[i] < 8 or
           not 0 <= b[i] < 8 or a[i] & ~supports[i] or b[i] & ~supports[i] or
           (a[i] & b[i]).bit_count() % 2 != 1 for i in kept):
        return False
    return all(values[i][j] or (a[i] & b[j]).bit_count() % 2 == 0
               for k, i in enumerate(order) for j in order[k + 1:])


def full_witness(vectors, values, supports):
    first = [vectors.index(row) for row in ((0, 1, 1), (1, 0, 1), (1, 1, 0))]
    last = [vectors.index(row) for row in ((0, 1, -1), (1, 0, -1), (1, -1, 0))]
    middle = [i for i in range(13) if i not in first + last]
    require(all(values[i][j] for block in (first, last) for i, j in permutations(block, 2)),
            "face block has a zero entry")
    require(all(supports[i].bit_count() % 2 == 1 for i in middle), "middle contains an even diagonal label")
    a, b = supports[:], supports[:]
    for i in first:
        b[i] &= -b[i]
    for i in last:
        a[i] &= -a[i]
    witness = {"a": a, "b": b, "order": first + middle + last, "kept": list(range(13))}
    require(literal_check(values, supports, witness), "full-box literal witness failed")
    return {"maximum": 13, "first": first, "middle": middle, "last": last, "witness": witness,
            "upper_bound": "There are only thirteen lines."}


def rejects(action, message):
    try:
        action()
    except ValueError as error:
        require(message in str(error), "unexpected failure: " + str(error))
        return
    raise ValueError("failure control accepted: " + message)


def controls(oracle, values, supports, arcs, full, unit):
    all_indices = list(range(13))
    unit_labels = [support & -support for support in supports]
    mutants = {
        "matched_units_on_all_thirteen": {"a": unit_labels, "b": unit_labels, "kept": all_indices, "order": all_indices},
        "full_even_anchor_diagonals": {"a": supports, "b": supports, "kept": all_indices, "order": all_indices},
        "reversed_general_witness": {**full, "order": list(reversed(full["order"]))},
        "out_of_box_unit": {**unit, "a": unit["a"][:]},
    }
    mutants["out_of_box_unit"]["a"][unit["kept"][0]] = 8
    for name, witness in mutants.items():
        require(not literal_check(values, supports, witness) and
                not oracle.check_witness(supports, supports, arcs, witness), "semantic mutant accepted: " + name)
    # Each simple graph on three vertices is independently compared with literal color assignments.
    pairs = list(combinations(range(3), 2))
    for mask in range(8):
        adjacent = [set() for _ in range(3)]
        for bit, (i, j) in enumerate(pairs):
            if mask & (1 << bit):
                adjacent[i].add(j)
                adjacent[j].add(i)
        for colors in (1, 2, 3):
            direct = any(all(assignment[i] != assignment[j] for i in range(3) for j in adjacent[i])
                         for assignment in product(range(colors), repeat=3))
            require((coloring(adjacent, colors)[0] is not None) == direct, "coloring control disagrees")
    old_read = Path.read_bytes
    for target, action in ((ORACLE, load_oracle), (PREDECESSOR, source_question)):
        def counterfeit(path):
            return b'raise RuntimeError("counterfeit executed")\n' if path == HERE / target else old_read(path)
        with patch.object(Path, "read_bytes", counterfeit):
            rejects(action, "Input changed: " + target)
    return {"semantic_mutants_rejected": list(mutants), "small_coloring_comparisons": 24,
            "source_corruption_rejected_before_execution": [ORACLE, PREDECESSOR]}


def build():
    authenticated = authenticate()
    oracle = load_oracle()
    vectors = rays()
    values = [[sum(x * y for x, y in zip(left, right)) for right in vectors] for left in vectors]
    supports = [sum(1 << j for j, value in enumerate(row) if value) for row in vectors]
    adjacent = [{j for j in range(13) if i != j and not values[i][j]} for i in range(13)]
    edges = [(i, j) for i, j in combinations(range(13), 2) if j in adjacent[i]]
    require(len(vectors) == 13 and len(edges) == 24 and all(values[i][i] for i in range(13)), "ray graph changed")
    require(all(values[i][j] == values[j][i] for i in range(13) for j in range(13)), "zero graph symmetry failed")
    require(all(tuple(int(i == j) for j in range(3)) in vectors for i in range(3)), "rank-three basis missing")
    normalized = oracle.rational_data(vectors, vectors)
    require(normalized["rank"] == 3 and normalized["gamma"] == 0 and
            normalized["a0"] == normalized["b0"] == supports, "canonical data changed")
    require(Counter(normalized["tau"]) == {1: 3, 2: 6, 3: 4}, "tie histogram changed")
    three, three_nodes = coloring(adjacent, 3)
    four, four_nodes = coloring(adjacent, 4)
    require(three is None and four is not None and all(four[i] != four[j] for i, j in edges), "chromatic result failed")
    unit = unit_pivots(supports, adjacent)
    full = full_witness(vectors, values, supports)
    for witness in (unit["witness"], full["witness"]):
        require(literal_check(values, supports, witness) and oracle.check_witness(
            supports, supports, normalized["arcs"], witness), "frozen definition rejects retained witness")
    result = {"schema_version": 1, "status": "PASS_FSTAR_YU_OH_ZERO_DIGRAPH",
              "scope": "Known Yu-Oh graph, instantiated as a rational three-total decoder: chi(Z)=4, matched-unit value12, general box13. No new graph, global floor or kappa claim.",
              "inputs_sha256": {path: hashlib.sha256(raw).hexdigest() for path, raw in authenticated.items()},
              "source_question": source_question(), "rays": vectors, "P_equals_Q": True, "M": values,
              "rank": 3, "gamma": 0, "a0": supports, "b0": supports, "tau": normalized["tau"],
              "tau_histogram": {1: 3, 2: 6, 3: 4}, "zero_edges": edges, "undirected_edge_count": 24,
              "directed_arc_count": 48, "chromatic_number": 4, "dichromatic_number": 4,
              "dichromatic_reason": "Every zero edge occurs in both directions, so an acyclic induced class is exactly an independent set.",
              "three_color_nodes": three_nodes, "four_color_nodes": four_nodes, "four_coloring": four,
              "three_color_obstruction": face_obstruction(vectors, adjacent), "matched_unit_pivots": unit,
              "general_box": full, "controls": controls(oracle, values, supports, normalized["arcs"], full["witness"], unit["witness"])}
    return json.loads(json.dumps(result))


def main():
    require(sys.argv[1:] in ([], ["--emit"]), "usage: verify.py [--emit]")
    result = build()
    if sys.argv[1:] == ["--emit"]:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        require(result == json.loads((HERE / "RESULT.json").read_text()), "RESULT.json mismatch")
        print("PASS_FSTAR_YU_OH_ZERO_DIGRAPH: chi4, matched-unit12, general-box13; exact retained witnesses")


if __name__ == "__main__":
    main()
