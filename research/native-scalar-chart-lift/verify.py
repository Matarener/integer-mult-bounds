#!/usr/bin/env python3
"""Scalar half of native_all_columns for the selected #5599 word.

The all-width identities are proved in PROOF.md. This program binds that
proof to the selected word and checks the tensor arithmetic on explicit charts.
Finite widths are controls, not a substitute for the common-chart hypothesis.
"""

from fractions import Fraction
from hashlib import sha256
import gzip
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SELECTED = ROOT / "research/p104-helper-subspace-splits/WORD.json.gz"
PREVIOUS = ROOT / "research/p104-helper-subspace-splits/inputs/PR5565-WORD.json.gz"
Q = Fraction


def need(ok, why):
    if not ok:
        raise ValueError(why)


def load_word(path):
    with gzip.open(path, "rb") as handle:
        word = json.loads(handle.read().decode("utf-8"))
    need(word.get("schema") == "p104-productive-source/1", "Unexpected word schema")
    need(isinstance(word.get("public"), int), "Public inventory")
    need(len(word["initial"]) == word["public"] == len(word["final"]), "Boundary length")
    need(isinstance(word.get("program"), list), "Program")
    return word


def walk(program, initial, owned_slots=0):
    """Return scalar-op counts after requiring one common current frame."""
    current = list(initial) + [None] * owned_slots
    counts = {op: 0 for op in ("ADD", "SCALE", "COPY", "MOVE", "INIT", "CLEAR")}
    for event in program:
        need(isinstance(event, list) and event, "Event shape")
        op = event[0]
        need(op in counts, "Unexpected opcode " + str(op))
        role = event[1]
        need(isinstance(role, int) and 0 <= role < len(current), "Role index")
        if op == "MOVE":
            need(len(event) == 5, "MOVE shape")
            source, destination = event[2], event[3]
            need(current[role] == source, "MOVE leaves the recorded chart")
            current[role] = destination
        elif op == "INIT":
            need(len(event) == 3, "INIT shape")
            current[role] = event[2]
        elif op == "CLEAR":
            need(len(event) == 3, "CLEAR shape")
            need(current[role] == event[2], "CLEAR leaves the recorded chart")
            current[role] = None
        else:
            need(len(event) == (4 if op == "SCALE" else 5), op + " shape")
            coefficient, frame = Q(event[-2]), event[-1]
            need(coefficient != 0, "Zero scalar coefficient")
            need(isinstance(frame, int), "Frame tag")
            need(current[role] == frame, "Scalar destination chart")
            if op != "SCALE":
                source = event[2]
                need(isinstance(source, int) and source != role, "Scalar source role")
                need(0 <= source < len(current), "Scalar source index")
                need(current[source] == frame, "Common scalar chart")
        counts[op] += 1
    return counts


def mat_id(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def mat_mul(left, right):
    rows, mid, cols = len(left), len(right), len(right[0])
    out = [[Q(0) for _ in range(cols)] for _ in range(rows)]
    for i in range(rows):
        for k in range(mid):
            if left[i][k] == 0:
                continue
            for j in range(cols):
                out[i][j] += left[i][k] * right[k][j]
    return out


def mat_vec(matrix, vector):
    return [sum(matrix[i][j] * vector[j] for j in range(len(vector))) for i in range(len(matrix))]


def kron(left, right):
    n, m = len(left), len(left[0])
    p, q = len(right), len(right[0])
    out = [[Q(0) for _ in range(m * q)] for _ in range(n * p)]
    for i in range(n):
        for j in range(m):
            for k in range(p):
                for ell in range(q):
                    out[i * p + k][j * q + ell] = left[i][j] * right[k][ell]
    return out


def tensor_pow(matrix, width):
    out = [[Q(1)]]
    for _ in range(width):
        out = kron(out, matrix)
    return out


def inv2(matrix):
    determinant = matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    need(determinant != 0, "Singular specimen chart")
    return [[matrix[1][1] / determinant, -matrix[0][1] / determinant],
            [-matrix[1][0] / determinant, matrix[0][0] / determinant]]


def add_vec(left, right):
    return [a + b for a, b in zip(left, right)]


def scale_vec(coefficient, vector):
    return [coefficient * entry for entry in vector]


def common_pullback(base, width, coefficient):
    chart = tensor_pow(base, width)
    inverse = tensor_pow(inv2(base), width)
    size = len(chart)
    vector_u = [Q(index + 1) for index in range(size)]
    vector_v = [Q(1 if index % 2 == 0 else -3) for index in range(size)]
    physical = add_vec(mat_vec(chart, vector_u), scale_vec(coefficient, mat_vec(chart, vector_v)))
    logical = mat_vec(inverse, physical)
    replay = add_vec(vector_u, scale_vec(coefficient, vector_v))
    scaled = mat_vec(chart, scale_vec(coefficient, vector_u))
    scale_commutes = scaled == scale_vec(coefficient, mat_vec(chart, vector_u))
    inverse_cancels = mat_mul(inverse, chart) == mat_id(size)
    return logical == replay and scale_commutes and inverse_cancels


def mixed_product_step(base):
    """(A⊗B)(C⊗D) = (AC)⊗(BD) on this chart and its inverse, the induction step."""
    inverse = inv2(base)
    left = kron(mat_mul(inverse, base), mat_mul(inverse, base))
    right = mat_mul(kron(inverse, inverse), kron(base, base))
    one_factor = mat_mul(inverse, base) == mat_id(2)
    return one_factor and left == right == mat_id(4)


def cross_chart(source_base, width, coefficient):
    size = 2 ** width
    destination = mat_id(size)
    source = tensor_pow(source_base, width)
    vector_u = [Q(2) for _ in range(size)]
    vector_v = [Q(1)] + [Q(0)] * (size - 1)
    physical = add_vec(mat_vec(destination, vector_u),
                       scale_vec(coefficient, mat_vec(source, vector_v)))
    # Destination is the identity, so the logical vector is the physical sum.
    logical = physical
    replay = add_vec(vector_u, scale_vec(coefficient, vector_v))
    return logical, replay


def check_specimens():
    coefficient = Q(-1, 2)
    pauli_x = [[Q(0), Q(1)], [Q(1), Q(0)]]
    shear = [[Q(1), Q(1)], [Q(0), Q(1)]]
    generic = [[Q(2), Q(3)], [Q(5), Q(7)]]
    phase = [[Q(-1), Q(0)], [Q(0), Q(-1)]]
    for base in (pauli_x, shear, generic):
        need(mixed_product_step(base), "Tensor induction step failed")
        for width in (1, 2, 3):
            need(common_pullback(base, width, coefficient),
                 "Common-chart pullback failed at width " + str(width))
    phase_vs_replay = {}
    for width in (1, 2, 3):
        logical, replay = cross_chart(phase, width, coefficient)
        phase_vs_replay[width] = logical == replay
    # (-I)^{⊗f} = (-1)^f I, so a width-2 test accidentally matches the
    # width-free replay while widths 1 and 3 do not.
    need(phase_vs_replay == {1: False, 2: True, 3: False},
         "Phase-chart trap did not separate widths")
    x_vs_replay = {}
    for width in (1, 2, 3):
        logical, replay = cross_chart(pauli_x, width, coefficient)
        x_vs_replay[width] = logical == replay
    need(x_vs_replay == {1: False, 2: False, 3: False}, "Pauli cross-chart should miss the replay")
    first_factor = kron(pauli_x, mat_id(2))
    both_factors = kron(pauli_x, pauli_x)
    need(first_factor != both_factors, "Width-2 Pauli power collapsed")
    return {"phase_width_equals_replay": phase_vs_replay,
            "pauli_x_width_equals_replay": x_vs_replay,
            "widths_checked": [1, 2, 3],
            "coefficient": str(coefficient)}


def check_walker_controls():
    initial = [4, 4]
    need(walk([["ADD", 0, 1, "1", 4], ["SCALE", 0, "-1", 4]], initial)["ADD"] == 1,
         "Synthetic common-chart block")
    try:
        walk([["ADD", 0, 1, "1", 4]], [4, 5])
    except ValueError as exc:
        need(str(exc) == "Common scalar chart", "Cross-chart diagnostic")
    else:
        raise ValueError("Cross-chart ADD was accepted")
    moved = [["MOVE", 0, 4, 7, False], ["ADD", 0, 1, "1", 7]]
    need(walk(moved, [4, 7])["MOVE"] == 1, "Chart follows MOVE")
    try:
        walk([["MOVE", 0, 4, 7, False], ["ADD", 0, 1, "1", 4]], [4, 7])
    except ValueError as exc:
        need(str(exc) == "Scalar destination chart", "Stale frame after MOVE")
    else:
        raise ValueError("Stale frame tag was accepted")
    return {"synthetic_cross_chart_rejected": True, "stale_frame_rejected": True}


def opcode_counts(word):
    counts = {}
    for event in word["program"]:
        counts[event[0]] = counts.get(event[0], 0) + 1
    return counts


def bind_words():
    selected = load_word(SELECTED)
    previous = load_word(PREVIOUS)
    need(selected["frames"] == previous["frames"], "Split changed the chart list")
    frame_bytes = json.dumps(selected["frames"], separators=(",", ":")).encode()
    walked = walk(selected["program"], selected["initial"], owned_slots=8)
    counted = opcode_counts(selected)
    for op, count in walked.items():
        need(counted.get(op, 0) == count, "Walk dropped an event")
    previous_counts = opcode_counts(previous)
    expected_previous = {"ADD": 20947, "MOVE": 3447, "SCALE": 715, "INIT": 8, "COPY": 8, "CLEAR": 8}
    expected_selected = {"ADD": 21247, "MOVE": 3447, "SCALE": 757, "INIT": 8, "COPY": 8, "CLEAR": 8}
    need(previous_counts == expected_previous, "PR5565 opcode census")
    need(counted == expected_selected, "Selected opcode census")
    need(previous["public"] == 735 and selected["public"] == 748, "Public-field delta")
    need(len(previous["program"]) == 25133 and len(selected["program"]) == 25475, "Event delta")
    mutated = json.loads(json.dumps(selected["program"]))
    for event in mutated:
        if event[0] == "ADD":
            event[-1] = event[-1] + 1
            break
    else:
        raise ValueError("Selected word has no ADD")
    try:
        walk(mutated, selected["initial"], owned_slots=8)
    except ValueError:
        mutated_rejected = True
    else:
        raise ValueError("Retagged ADD was accepted")
    return {"adds": counted["ADD"], "scales": counted["SCALE"], "copies": counted["COPY"],
            "moves": counted["MOVE"], "common_chart_violations": 0,
            "split_delta_add": counted["ADD"] - previous_counts["ADD"],
            "split_delta_scale": counted["SCALE"] - previous_counts["SCALE"],
            "split_delta_move": counted["MOVE"] - previous_counts["MOVE"],
            "split_delta_events": len(selected["program"]) - len(previous["program"]),
            "public_delta": selected["public"] - previous["public"],
            "frames_sha256": sha256(frame_bytes).hexdigest(),
            "tag_mutation_rejected": mutated_rejected}


def main():
    binding = bind_words()
    specimens = check_specimens()
    controls = check_walker_controls()
    need(binding["split_delta_add"] == 300 and binding["split_delta_scale"] == 42
         and binding["split_delta_move"] == 0 and binding["split_delta_events"] == 342
         and binding["public_delta"] == 13, "Split delta left the scalar class")
    need(controls["synthetic_cross_chart_rejected"] and binding["tag_mutation_rejected"],
         "Failure controls")
    print("PASS_NATIVE_SCALAR_CHART_LIFT"
          " adds={adds} scales={scales} copies={copies} moves={moves}"
          " common_chart_violations={common_chart_violations}"
          " split_delta_add={split_delta_add} split_delta_scale={split_delta_scale}"
          " split_delta_move={split_delta_move}".format(**binding))
    print("controls " + json.dumps({"specimens": specimens, "walker": controls,
                                     "frames_sha256": binding["frames_sha256"]},
                                    sort_keys=True))


if __name__ == "__main__":
    main()
