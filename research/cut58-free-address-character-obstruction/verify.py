"""Exact cut58 relation. No predecessor executable or census is run.

Produced by Nick Petalas. Apache-2.0.
"""

from hashlib import sha256
from itertools import product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = "research/cut58-address-swap-menu/operators.json"
INPUT_SHA256 = "9704ae3c0c1fbb93526970b05a63f486f376961edd019ba526249477d2aa0ab3"
ACTIVE = (0, 1, 2, 3, 10, 11)
LEFT = "PWKPW"
RIGHT = "TWKPK"
FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_source():
    data = (ROOT / INPUT).read_bytes()
    require(len(data) <= 65536, "source capacity")
    require(sha256(data).hexdigest() == INPUT_SHA256, "source SHA256")
    source = json.loads(data)
    for name in "KWTP":
        entry = source[name]
        require(len(entry["rows"]) == len(entry["alpha"]) == len(entry["quad"]) == 12,
                "twelve-bit operator")
        require(all(row.bit_count() == 1 for row in entry["rows"]), "bit permutation")
        require(sorted(entry["rows"]) == [1 << i for i in range(12)], "invertible permutation")
    return source


def scalar_phase(entry, point):
    linear = sum(entry["alpha"][i] for i in range(12) if point >> i & 1)
    quadratic = sum((entry["quad"][i] & point).bit_count() & 1
                    for i in range(12) if point >> i & 1)
    return (entry["constant"] + linear + 2 * quadratic) % 4


def literal(word, point, source):
    require(0 <= point < 4096 and 1 <= len(word) <= 10, "literal domain")
    phase = global_phase = 0
    for name in reversed(word):
        entry = source[name]
        phase += scalar_phase(entry, point)
        global_phase += entry["global_phase"]
        point = sum(((row & point).bit_count() & 1) << i
                    for i, row in enumerate(entry["rows"])) ^ entry["offset"]
    return point, phase % 4, global_phase % 4


def add(left, right, scale=1):
    result = left.copy()
    for mask, coefficient in right.items():
        result[mask] = (result.get(mask, 0) + scale * coefficient) % 4
    return {mask: coefficient for mask, coefficient in result.items() if coefficient}


def multiply(left, right):
    require(len(left) <= 64 and len(right) <= 64, "polynomial capacity")
    result = {}
    for a, x in left.items():
        for b, y in right.items():
            result[a | b] = (result.get(a | b, 0) + x * y) % 4
    return {mask: coefficient for mask, coefficient in result.items() if coefficient}


def polynomial_phase(entry, coordinates):
    result = {0: entry["constant"]}
    for index, bit in enumerate(ACTIVE):
        result = add(result, coordinates[index], entry["alpha"][bit])
        for other, other_bit in enumerate(ACTIVE):
            if entry["quad"][bit] >> other_bit & 1:
                result = add(result, multiply(coordinates[index], coordinates[other]), 2)
    return result


def compile_word(word, source):
    coordinates = [{1 << i: 1} for i in range(6)]
    phase = {}
    global_phase = 0
    for name in reversed(word):
        entry = source[name]
        phase = add(phase, polynomial_phase(entry, coordinates))
        updated = []
        for bit in ACTIVE:
            input_bit = entry["rows"][bit].bit_length() - 1
            require(input_bit in ACTIVE, "active permutation closure")
            value = coordinates[ACTIVE.index(input_bit)]
            updated.append(add({0: 1}, value, -1) if entry["offset"] >> bit & 1
                           else value.copy())
        coordinates = updated
        global_phase = (global_phase + entry["global_phase"]) % 4
    return coordinates, phase, global_phase


def closed_form(point):
    bits = tuple((point >> bit) & 1 for bit in ACTIVE)
    a0, a1, b0, b1, c0, c1 = bits
    output_bits = (b0, b1, 1 - c0, 1 - c1, a0, a1)
    output = point & sum(1 << bit for bit in range(4, 10))
    output += sum(value << bit for value, bit in zip(output_bits, ACTIVE))
    phase = (3 + 2 * a1 + 3 * (b0 + b1) + 3 * c0 + c1
             + 2 * (a0 * b0 + a1 * b1)) % 4
    return output, phase


def check_relation(source):
    expected_coordinates = [{4: 1}, {8: 1}, {0: 1, 16: 3},
                            {0: 1, 32: 3}, {1: 1}, {2: 1}]
    expected_phase = {0: 3, 2: 2, 4: 3, 8: 3, 16: 3, 32: 1, 5: 2, 10: 2}
    left = compile_word(LEFT, source)
    right = compile_word(RIGHT, source)
    require(left[:2] == right[:2], "symbolic projective relation")
    require(left[0] == expected_coordinates and left[1] == expected_phase, "closed form")
    require((left[2], right[2]) == (1, 3), "global phases outside tensor powers")
    for point in range(4096):
        a = literal(LEFT, point, source)
        b = literal(RIGHT, point, source)
        require(a[:2] == b[:2] == closed_form(point), "literal basis and closed form")
        require((a[2] - b[2]) % 4 == 2, "literal negative sign")
    return left[2], right[2]


def word_sign(word, assignment):
    exponent = sum(assignment["KWTP".index(name)] for name in word)
    return exponent % 2


def check_characters():
    permitted = []
    free_permitted = []
    for assignment in product(range(2), repeat=4):
        compatible = word_sign(LEFT, assignment) == word_sign(RIGHT, assignment)
        require(compatible == (sum(assignment) % 2 == 0), "parity relation")
        if compatible:
            permitted.append(assignment)
            if assignment[3] == 0:
                free_permitted.append(assignment)
    for assignment in ((0, 1, 0, 0), (0, 0, 1, 0)):
        require(word_sign(LEFT, assignment) != word_sign(RIGHT, assignment),
                "free-ADDRESS extension must reject chi_W and chi_T")
    survivor = (1, 1, 0, 0)
    require(word_sign(LEFT, survivor) == word_sign(RIGHT, survivor),
            "this relation does not decide chi_KW")
    return permitted, free_permitted


def check_boundaries(source, global_phases):
    a = literal(LEFT, 0, source)
    b = literal(RIGHT, 0, source)
    require((a[1] + a[2] - b[1] - b[2]) % 4 != 0, "unsigned identity is false")
    require(literal(LEFT.replace("P", "", 1), 1, source)[:2]
            != literal(LEFT, 1, source)[:2],
            "omitting ADDRESS changes the new word")
    require(a[:2] == b[:2], "discarding outer phase would lose the negative sign")
    for multiplicity in range(1, 9):
        actual = (global_phases[0] - global_phases[1]) % 4
        misplaced = multiplicity * actual % 4
        require(actual == 2, "all-f scalar sign")
        if multiplicity % 2 == 0:
            require(misplaced != actual, "global phase cannot move inside tensor")
    for assignment in ((0, 1, 0, 1), (0, 0, 1, 1)):
        require(word_sign(LEFT, assignment) == word_sign(RIGHT, assignment),
                "a nontrivial ADDRESS sign escapes this obstruction")


def receipt_hashes():
    result = {INPUT: INPUT_SHA256}
    for name in FILES:
        data = (HERE / name).read_bytes()
        require(len(data) <= 1048576, "package file capacity")
        result[name] = sha256(data).hexdigest()
    return result


def main():
    source = load_source()
    phases = check_relation(source)
    permitted, free_permitted = check_characters()
    check_boundaries(source, phases)
    result = {
        "status": "PASS_CUT58_FREE_ADDRESS_CHARACTER_OBSTRUCTION",
        "relation": "PWKPW = -TWKPK",
        "claim_type": "scoped proof with exact finite corroboration",
        "literal_basis_columns": 4096,
        "character_assignments": 16,
        "assignments_not_excluded_by_this_relation": permitted,
        "free_ADDRESS_assignments_not_excluded": free_permitted,
        "excluded_free_ADDRESS_characters": ["chi_W", "chi_T"],
        "chi_KW_extension": "not decided",
        "tensor_multiplicity": "every positive integer, by the written proof",
        "new_kappa": False,
        "sha256": receipt_hashes(),
    }
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
