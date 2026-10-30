#!/usr/bin/env python3
"""Permutation-table oracle for the source-defined canonical lifts.

No primary/predecessor executable is imported. Gaussian sparse vectors are
integer pairs with a common dyadic denominator. Apache-2.0; ToikY with
substantial OpenAI Codex assistance, not independent human/kernel review.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PINS = {
    "PROOF.md": "111e31099e97d4f9a376d77ca1159d6ba89e2a6b7dd36d8386888c9b91639e25",
    "README.md": "06163fba5ef8fcca2a6940313ffb506320206ce47d2cf1c4eceb8fd0d8039bfd",
    "RECIPES.json": "64b85f6aef485026eebaec7acddb41999f57e074b0dfde8077b6543700cd684b",
    "exact_phase.py": "e3d76b3373ff40a83a4b212b3fe1c0b431b3cfdc807da601d6e7f273c02c6d30",
    "SOURCE-CREDITS.md": "d4a13d8b8ed9cdb594f00efb3d1a336e09d934423330f02a1514308a720c278b",
    "NOTICE-PR3945.md": "6881464d7731757b63275f056cb9ef8406db04e76c73093d3e5b418529a879cc",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def weight(value):
    return bin(value).count("1")


def parity(value):
    return weight(value) % 2


def tables(columns):
    """Invert a complete permutation, without primary binary elimination."""
    n = len(columns)
    require(all(type(c) is int and 0 <= c < 1 << n for c in columns), "column domain")
    rows = [sum(((column >> row) & 1) << index for index, column in enumerate(columns))
            for row in range(n)]
    forward = tuple(sum(parity(row & x) << index for index, row in enumerate(rows))
                    for x in range(1 << n))
    require(len(set(forward)) == 1 << n, "invertible binary permutation")
    inverse = tuple(dict((y, x) for x, y in enumerate(forward))[y] for y in range(1 << n))
    inverse_columns = tuple(inverse[1 << i] for i in range(n))
    form = [[(parity(a & b) + int(i == j)) % 2
             for j, b in enumerate(inverse_columns)] for i, a in enumerate(inverse_columns)]
    canonical = []
    normal = []
    for x, y in enumerate(forward):
        active = [i for i in range(n) if y & (1 << i)]
        phase = sum(form[i][i] for i in active)
        phase += 2*sum(form[i][j] for i in active for j in active if i < j)
        canonical.append(phase % 4)
        normal.append((weight(y)-weight(x)) % 4)
    differences = [(a-b) % 4 for a, b in zip(canonical, normal)]
    require(all(d in (0, 2) for d in differences), "same quadratic parity")
    tag = sum((differences[1 << i]//2) << i for i in range(n))
    require(all(d == 2*parity(tag & x) for x, d in enumerate(differences)),
            "canonical versus functorial input tag")
    return {"columns": tuple(columns), "perm": forward, "back": inverse,
            "canonical": tuple(canonical), "normal": tuple(normal), "tag": tag,
            "inverse_columns": inverse_columns}


def pullback(columns, character):
    return sum(parity(column & character) << index for index, column in enumerate(columns))


def check_pair(first, second, product):
    """Chronology first then second; operator product is second*first."""
    character = first["tag"] ^ pullback(first["columns"], second["tag"]) ^ product["tag"]
    for x, y in enumerate(first["perm"]):
        require(second["perm"][y] == product["perm"][x], "binary product")
        require((first["normal"][x]+second["normal"][y]) % 4 == product["normal"][x],
                "strict J composition with full phase")
        defect = (first["canonical"][x]+second["canonical"][y]-product["canonical"][x]) % 4
        require(defect == 2*parity(character & x), "explicit cocycle coboundary")
    return character


def signed_table(data, sign):
    if sign == 1:
        return data["perm"], data["canonical"], data["columns"], data["tag"]
    require(sign == -1, "signed word alphabet")
    phase = tuple((-data["canonical"][x]) % 4 for x in data["back"])
    tag = pullback(data["inverse_columns"], data["tag"])
    return data["back"], phase, data["inverse_columns"], tag


def word_checks(actual):
    sequence = [(actual[index], sign) for index, sign in
                [(0, 1), (2, -1), (1, 1), (3, -1), (0, -1), (1, -1), (2, 1), (3, 1)]]
    n = len(actual[0]["columns"])
    permutation = tuple(range(1 << n))
    phases = (0,)*(1 << n)
    columns = tuple(1 << i for i in range(n))
    section_tag = 0
    checks = 0
    for data, sign in sequence:
        gate_perm, gate_phase, gate_columns, gate_tag = signed_table(data, sign)
        section_tag ^= pullback(columns, gate_tag)
        columns = tuple(gate_perm[column] for column in columns)
        phases = tuple((phase+gate_phase[y]) % 4 for phase, y in zip(phases, permutation))
        permutation = tuple(gate_perm[y] for y in permutation)
        combined = tables(columns)
        for x in range(1 << n):
            require(permutation[x] == combined["perm"][x], "signed-word product")
            require(phases[x] == (combined["normal"][x]+2*parity(section_tag & x)) % 4,
                    "signed-word section tag")
            residual = section_tag ^ combined["tag"]
            require(phases[x] == (combined["canonical"][x]+2*parity(residual & x)) % 4,
                    "signed-word canonical tag")
            checks += 1
    return checks


def rotate(value, phase):
    real, imag = value
    return ((real, imag), (-imag, real), (-real, -imag), (imag, -real))[phase % 4]


def coordinate_gates(state, count):
    for axis in range(count):
        result = {}
        for x, (real, imag) in state.items():
            for y, addition in ((x, (real-imag, real+imag)),
                                (x ^ (1 << axis), (real+imag, imag-real))):
                a, b = result.get(y, (0, 0))
                result[y] = (a+addition[0], b+addition[1])
        state = {x: value for x, value in result.items() if value != (0, 0)}
    return state


def frame_column(data, count, x, mode):
    """All versions have denominator 2^count; compare integer numerators."""
    inverse_x = data["back"][x]
    original = mode == "canonical"
    phases = data["canonical"] if original else data["normal"]
    value = rotate((1, 0), -phases[inverse_x])
    if mode == "compensated":
        value = rotate(value, 2*parity(data["tag"] & inverse_x))
    state = coordinate_gates({inverse_x: value}, count)
    result = {}
    for y, value in state.items():
        phase = phases[y]
        if mode == "compensated":
            phase += 2*parity(data["tag"] & y)
        result[data["perm"][y]] = rotate(value, phase)
    return result


def two_branch_check(tag):
    """The inverse branch carries a necessary global i, even on one C gate."""
    checked = 0
    for u in (1, 16):
        branch = parity(tag & u)
        for x in range(512):
            before = 2*parity(tag & x)
            actual = {x: rotate((1, 1), before+2*parity(tag & x)),
                      x ^ u: rotate((1, -1), before+2*parity(tag & (x ^ u)))}
            if branch:
                inverse = {x: (1, -1), x ^ u: (1, 1)}
                expected = {y: rotate(value, 1) for y, value in inverse.items()}
                require(actual != inverse, "missing global i must change the operator")
            else:
                expected = {x: (1, 1), x ^ u: (1, -1)}
            require(actual == expected, "literal two-branch central-C retag")
            checked += 1
    return checked


def audit():
    for name, pin in PINS.items():
        require(hashlib.sha256((HERE/"source"/name).read_bytes()).hexdigest() == pin,
                "independent source bytes: " + name)
    items = json.loads((HERE/"source/RECIPES.json").read_bytes())["items"]
    columns = sorted({tuple(item["G_columns"]) for item in items if item["kind"] == "warp"})
    require(len(items) == 40 and len(columns) == 4, "changed-interface source inventory")
    actual = [tables(g) for g in columns]
    for data in actual:
        inverse = tables(data["inverse_columns"])
        for x, y in enumerate(data["perm"]):
            require((data["normal"][x]+inverse["normal"][y]) % 4 == 0,
                    "J inverse equals its adjoint")
        check_pair(data, inverse, tables(tuple(1 << i for i in range(9))))
    for first in actual:
        for second in actual:
            product = tables(tuple(second["perm"][column] for column in first["columns"]))
            check_pair(first, second, product)
    witness_columns = (1, 2, 8, 32, 44, 128, 59, 66, 489)
    witness = next(data for data in actual if data["columns"] == witness_columns)
    witness_inverse = tables(witness["inverse_columns"])
    require(witness["tag"] == 144 and witness_inverse["tag"] == 68,
            "source-defined witness normalization tags")
    require(check_pair(witness, witness_inverse, tables(tuple(1 << i for i in range(9)))) == 256,
            "credited inverse-defect witness")
    branch_checks = two_branch_check(witness["tag"])
    signed_checks = word_checks(actual)

    group = {}
    for candidate in itertools.product(range(8), repeat=3):
        # A permutation test screens the 512 matrices without trusting elimination.
        image = {sum(parity(row & x) << i for i, row in enumerate(
            [sum(((c >> r) & 1) << j for j, c in enumerate(candidate)) for r in range(3)]))
                 for x in range(8)}
        if len(image) == 8:
            group[candidate] = tables(candidate)
    require(len(group) == 168, "complete GL(3,2)")
    pair_states = 0
    frame_states = 0
    naive_differences = 0
    for first in group.values():
        for second in group.values():
            product_columns = tuple(second["perm"][column] for column in first["columns"])
            check_pair(first, second, group[product_columns])
            pair_states += 8
        for count in range(4):
            for x in range(8):
                correct = frame_column(first, count, x, "canonical")
                require(frame_column(first, count, x, "compensated") == correct,
                        "mandatory central-C frame compensation")
                if frame_column(first, count, x, "naive") != correct:
                    naive_differences += 1
                frame_states += 1
    require(naive_differences > 0, "unretagged J substitution must not be accepted")
    return {"changed_interface_maps": 4, "actual_basis_states_per_map": 512,
            "actual_ordered_pairs": 16, "signed_word_prefix_state_checks": signed_checks,
            "gl3_maps": 168, "gl3_ordered_pairs": 28224, "gl3_pair_state_checks": pair_states,
            "gl3_frame_column_checks": frame_states, "naive_frame_column_mismatches": naive_differences,
            "central_C_branch_column_checks": branch_checks,
            "witness_input_tag": 144, "witness_inverse_input_tag": 68,
            "credited_inverse_defect": 256, "native_action_replaced": False, "new_kappa": False}


if __name__ == "__main__":
    print("PASS_INDEPENDENT_NATIVE_LIFT_PHASE_TAGS " + json.dumps(audit(), sort_keys=True))
