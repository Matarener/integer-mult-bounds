#!/usr/bin/env python3
"""Independent acceptance of the PR #4019 separated-A2 composition argument.

This checker does not import that package. It re-derives the two rational
identities from PROOF.md, classifies each frozen site, and counts the
projected-cleanup record split. It does not replay the recursive frame bill.
"""

import gzip
import hashlib
import json
from fractions import Fraction
from itertools import permutations
from pathlib import Path

HERE = Path(__file__).resolve().parent
V = 112

PINS = {
    "base": "5ca4be99851f8878cbfe0fd6c454df926b11218f17feefa1664721cf03156699",
    "extra": "965268a9be73d3f62e7ef680d18f108cf064bfe1f44b82157baa61443232904e",
}
RECEIPT_SHA256 = "cbfefac6c10f68b55208458cf2d07b2a67f2f9ece037fa53fa7070647a21b82e"

# Section, three increasing indices, removed position, whether the site is the
# credited PR #3998 contraction rather than one of the seven new witnesses.
SITES = (
    ("A", (1858, 1859, 1860), 2, True),
    ("B", (4, 53, 54), 0, False),
    ("B", (7, 49, 50), 0, False),
    ("restore", (20, 21, 36), 2, False),
    ("restore", (22, 23, 38), 2, False),
    ("restore", (26, 27, 51), 2, False),
    ("restore", (30, 31, 62), 2, False),
    ("restore", (32, 33, 73), 2, False),
)


class Rejected(Exception):
    pass


def require(condition, message):
    if not condition:
        raise Rejected(message)


def no_duplicates(pairs):
    answer = {}
    for key, value in pairs:
        require(key not in answer, "duplicate JSON key " + str(key))
        answer[key] = value
    return answer


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def is_target(register):
    return V <= register < 2 * V


def coefficient(gate):
    require(gate[0] in ("add", "scale"), "scalar alphabet")
    index = 3 if gate[0] == "add" else 2
    numerator, denominator = gate[index:index + 2]
    require(type(numerator) is int and type(denominator) is int and denominator != 0
            and numerator != 0, "nonzero rational coefficient")
    return Fraction(numerator, denominator)


def touched(gate):
    if gate[0] == "add":
        require(len(gate) == 6, "add layout")
        registers = gate[1:3]
    elif gate[0] == "scale":
        require(len(gate) == 5, "scale layout")
        registers = gate[1:2]
    else:
        raise Rejected("unexpected event " + str(gate[0]))
    require(all(type(register) is int and 0 <= register < 704 for register in registers),
            "register domain")
    return set(registers)


def apply_matrix(gates, registers):
    """Left-action of chronological ADDs on the ordered register basis."""
    index = {register: place for place, register in enumerate(registers)}
    matrix = [[Fraction(place == column) for column in range(3)] for place in range(3)]
    for gate in gates:
        require(gate[0] == "add", "identity alphabet")
        weight = coefficient(gate)
        destination, source = index[gate[1]], index[gate[2]]
        for column in range(3):
            matrix[destination][column] += weight * matrix[source][column]
    return matrix


def endpoint(gates, x_reg, y_reg, z_reg, start):
    value = {x_reg: start[0], y_reg: start[1], z_reg: start[2]}
    for gate in gates:
        value[gate[1]] += coefficient(gate) * value[gate[2]]
    return (value[x_reg], value[y_reg], value[z_reg])


def add_gate(destination, source, weight):
    return ["add", destination, source, weight.numerator, weight.denominator, []]


def check_stated_endpoints():
    """PROOF.md's two endpoint formulas, on exact rationals, including a nonzero start."""
    x_reg, y_reg, z_reg = 0, 1, 2
    samples = (
        (Fraction(2), Fraction(-3), (Fraction(5), Fraction(-2), Fraction(7))),
        (Fraction(1, 2), Fraction(4), (Fraction(0), Fraction(1), Fraction(-3))),
        (Fraction(-1), Fraction(-1), (Fraction(9), Fraction(1, 3), Fraction(4))),
    )
    for weight_a, weight_b, start in samples:
        identity_one = [
            add_gate(y_reg, z_reg, weight_a),
            add_gate(x_reg, y_reg, weight_b),
            add_gate(x_reg, z_reg, -weight_a * weight_b),
        ]
        right_one = [add_gate(x_reg, y_reg, weight_b), add_gate(y_reg, z_reg, weight_a)]
        expect_one = (start[0] + weight_b * start[1], start[1] + weight_a * start[2], start[2])
        identity_two = [
            add_gate(x_reg, z_reg, weight_a * weight_b),
            add_gate(x_reg, y_reg, weight_b),
            add_gate(y_reg, z_reg, weight_a),
        ]
        right_two = [add_gate(y_reg, z_reg, weight_a), add_gate(x_reg, y_reg, weight_b)]
        expect_two = (
            start[0] + weight_b * start[1] + weight_a * weight_b * start[2],
            start[1] + weight_a * start[2],
            start[2],
        )
        for gates, right, expect in (
            (identity_one, right_one, expect_one),
            (identity_two, right_two, expect_two),
        ):
            require(endpoint(gates, x_reg, y_reg, z_reg, start) == expect, "stated endpoint")
            require(endpoint(right, x_reg, y_reg, z_reg, start) == expect, "stated right-hand side")
            require(apply_matrix(gates, [x_reg, y_reg, z_reg])
                    == apply_matrix(right, [x_reg, y_reg, z_reg]), "matrix form")
    wrong = [add_gate(y_reg, z_reg, Fraction(1)), add_gate(x_reg, y_reg, Fraction(1)),
             add_gate(x_reg, z_reg, Fraction(1))]
    require(endpoint(wrong, x_reg, y_reg, z_reg, (Fraction(0), Fraction(0), Fraction(1)))
            != (Fraction(0), Fraction(1), Fraction(1)), "wrong sign must miss the identity-one endpoint")


def classify(gates):
    """Match one ordered triple to exactly one of the two proof identities."""
    require(len(gates) == 3 and all(gate[0] == "add" for gate in gates), "three ADDs")
    edges = [(gate[1], gate[2], coefficient(gate)) for gate in gates]
    registers = []
    for register in [edge[0] for edge in edges] + [edge[1] for edge in edges]:
        if register not in registers:
            registers.append(register)
    require(len(registers) == 3 and len({(edge[0], edge[1]) for edge in edges}) == 3,
            "three distinct directed edges")
    matches = []
    for x_reg, y_reg, z_reg in permutations(registers):
        first, second, third = edges
        if (first[0] == y_reg and first[1] == z_reg and second[0] == x_reg and second[1] == y_reg
                and third[0] == x_reg and third[1] == z_reg and third[2] == -first[2] * second[2]):
            matches.append(("id1_remove_last", x_reg, y_reg, z_reg, first[2], second[2]))
        if (first[0] == x_reg and first[1] == z_reg and second[0] == x_reg and second[1] == y_reg
                and third[0] == y_reg and third[1] == z_reg and first[2] == third[2] * second[2]):
            matches.append(("id2_remove_first", x_reg, y_reg, z_reg, third[2], second[2]))
    require(len(matches) == 1, "expected exactly one identity match")
    return matches[0]


def predicted_replacement(kind, gates):
    if kind == "id1_remove_last":
        return [gates[1], gates[0]]
    require(kind == "id2_remove_first", "unknown identity")
    return [gates[2], gates[1]]


def same_add(left, right):
    return left[:5] == right[:5]


def frames_same_span(left, right):
    return sorted(left) == sorted(right)


def load_words():
    words = {}
    for name, digest in PINS.items():
        path = HERE / "inputs" / ("BORROW-WORD-" + name + ".json.gz")
        require(path.is_file() and not path.is_symlink(), "missing word " + name)
        raw = path.read_bytes()
        require(sha256(raw) == digest, "word byte pin " + name)
        words[name] = json.loads(gzip.decompress(raw), object_pairs_hook=no_duplicates)
    receipt_path = HERE / "inputs" / "data.json"
    raw_receipt = receipt_path.read_bytes()
    require(sha256(raw_receipt) == RECEIPT_SHA256, "published receipt pin")
    receipt = json.loads(raw_receipt, object_pairs_hook=no_duplicates)
    require(set(receipt) == {"schema_version", "providers"} and receipt["schema_version"] == 1,
            "receipt schema")
    return words, receipt


def audit_provider(word, receipt):
    occupied = set()
    forward_new = cleanup_new = known_swaps = 0
    for section, indices, central, known in SITES:
        require(section in word and isinstance(word[section], list), "missing section")
        require(indices[0] < indices[1] < indices[2] < len(word[section]), "site indices")
        gates = [word[section][index] for index in indices]
        kind, x_reg, y_reg, z_reg, _weight_a, _weight_b = classify(gates)
        expected_central = 2 if kind == "id1_remove_last" else 0
        require(central == expected_central, "removed position disagrees with the identity")
        replacement = predicted_replacement(kind, gates)
        registers = sorted({x_reg, y_reg, z_reg})
        require(apply_matrix(gates, registers) == apply_matrix(replacement, registers),
                "replacement operator")
        frames = [tuple(gate[-1]) for gate in gates]
        require(frames[0] == frames[1] == frames[2], "common ordered source frame")
        require(all(tuple(gate[-1]) == frames[0] for gate in replacement),
                "replacement keeps the source frame")
        support = {x_reg, y_reg, z_reg}
        require(occupied.isdisjoint(support), "site supports overlap")
        occupied.update(support)
        for index in range(indices[0], indices[-1] + 1):
            if index in indices:
                continue
            require(touched(word[section][index]).isdisjoint(support), "intervening dependency")
        if section == "A":
            require(indices[0] >= word["prelude_events"], "prelude barrier")
        if section == "B":
            require(not any(indices[0] < warp[0] <= indices[-1] for warp in word["warps"]),
                    "native warp barrier")
        if section == "restore":
            require(all(not is_target(gate[1]) for gate in gates), "restore site writes a target")
        if kind == "id2_remove_first":
            require(is_target(gates[0][1]) and gates[0][1] == gates[1][1] and is_target(gates[1][1]),
                    "B contraction's first two ADDs must write the same target")
            require(not is_target(gates[2][1]), "B contraction must keep one helper ADD")
        published = next(site for site in receipt["sites"] if tuple(site["indices"]) == indices)
        require(published["gates"] == gates, "receipt gates differ from the frozen word")
        require(published["removed_position"] == central, "receipt removed position")
        if known:
            require(all(same_add(left, right) and frames_same_span(left[-1], right[-1])
                        for left, right in zip(published["replacement"], replacement)),
                    "known-site replacement edges")
            if published["replacement"] != replacement:
                known_swaps += 1
        else:
            require(published["replacement"] == replacement, "new-site replacement")
            forward_new += 1
            if not is_target(gates[central][1]):
                cleanup_new += 1
                require(len([gate for gate in gates if not is_target(gate[1])])
                        == len([gate for gate in replacement if not is_target(gate[1])]) + 1,
                        "restore projection should drop one record")
            else:
                require([gate[:5] for gate in gates if not is_target(gate[1])]
                        == [gate[:5] for gate in replacement if not is_target(gate[1])],
                        "target deletion must preserve the helper ADD")
    require((forward_new, cleanup_new) == (7, 5), "seven forward and five cleanup records")
    require(known_swaps == 1, "the credited site's ordered-frame swap is part of the publication")
    require(len(occupied) == 24, "eight disjoint three-register supports")
    return forward_new, cleanup_new


def expect_rejected(label, function):
    try:
        function()
    except Rejected:
        return
    raise Rejected("negative control escaped: " + label)


def negative_controls(words):
    word = words["base"]
    broken = json.loads(json.dumps(word))
    broken["B"][4][3] = -broken["B"][4][3]
    expect_rejected("wrong sign", lambda: classify([broken["B"][index] for index in (4, 53, 54)]))
    dependent = json.loads(json.dumps(word))
    dependent["B"][5][2] = 518
    expect_rejected(
        "intervening read",
        lambda: require(touched(dependent["B"][5]).isdisjoint({196, 518, 588}), "intervening dependency"),
    )
    expect_rejected(
        "wrong endpoint sign",
        lambda: require(
            endpoint(
                [add_gate(1, 2, Fraction(1)), add_gate(0, 1, Fraction(1)), add_gate(0, 2, Fraction(1))],
                0, 1, 2, (Fraction(0), Fraction(0), Fraction(1)),
            ) == (Fraction(0), Fraction(1), Fraction(1)),
            "wrong sign must miss the identity-one endpoint",
        ),
    )


def main():
    check_stated_endpoints()
    words, receipt = load_words()
    require(set(receipt["providers"]) == {"base", "extra"}, "both providers")
    for name in ("base", "extra"):
        forward, cleanup = audit_provider(words[name], receipt["providers"][name])
        require((forward, cleanup) == (7, 5), name)
    negative_controls(words)
    print("PASS_A2_COMPOSITION_AUDIT providers=2 sites=8 new_forward_adds=7 "
          "new_cleanup_adds=5 known_frame_order_swaps=2 controls=3 no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except Rejected as error:
        raise SystemExit("FAIL_A2_COMPOSITION_AUDIT " + str(error))
