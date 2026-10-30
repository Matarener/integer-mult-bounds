#!/usr/bin/env python3
"""Nine coordinate calls still hit three identity targets when one dirty auxiliary is idle.

An eight-call word that uses only coordinate projectors cannot. The published
span test leaves dimensions 4, 5 and 6 open for a general eight-call word.
"""

import hashlib
import json
from fractions import Fraction
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MODEL = ROOT / "research/bit-three-register-lower-bound/README.md"
DIRTY = ROOT / "research/bit-dirty-auxiliary-registers/README.md"
REVIEW = ROOT / "docs/research/community-efficient1000-review.md"
MARKER = "PASS_THREE_DATA_AUX_DIRECT calls=9 coordinate_eight=false no_new_kappa"
ZERO = (0,) * 9


def fail(message):
    raise SystemExit("FAIL_THREE_DATA_AUX_DIRECT " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "research/bit-three-register-lower-bound/README.md",
        "research/bit-dirty-auxiliary-registers/README.md",
        "docs/research/community-efficient1000-review.md",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def basis_frame(index):
    entries = [0] * 9
    entries[index * 3 + index] = 1
    return tuple(entries)


def identity_frame():
    return tuple(basis_frame(0)[i] + basis_frame(1)[i] + basis_frame(2)[i] for i in range(9))


def matrix_rank(entries):
    rows = [[Fraction(entries[i * 3 + j]) for j in range(3)] for i in range(3)]
    rank = 0
    for column in range(3):
        pivot = next((i for i in range(rank, 3) if rows[i][column] != 0), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = [value / scale for value in rows[rank]]
        for other in range(3):
            if other != rank and rows[other][column] != 0:
                factor = rows[other][column]
                rows[other] = [value - factor * base for value, base in zip(rows[other], rows[rank])]
        rank += 1
    return rank


def add_poly(left, right):
    out = dict(left)
    for key, value in right.items():
        out[key] = out.get(key, 0) ^ value
        if out[key] == 0:
            del out[key]
    return out


def mul_poly(left, right):
    out = {}
    for left_key, left_value in left.items():
        for right_key, right_value in right.items():
            key = tuple(a + b for a, b in zip(left_key, right_key))
            out[key] = out.get(key, 0) ^ (left_value & right_value)
            if out[key] == 0:
                del out[key]
    return out


def identity_operator():
    return [[{ZERO: 1} if i == j else {} for j in range(4)] for i in range(4)]


def coordinate_factor(frame, register):
    operator = identity_operator()
    operator[register][register] = {frame: 1}
    return operator


def multiply(left, right):
    out = [[{} for _ in range(4)] for _ in range(4)]
    for i in range(4):
        for k in range(4):
            for j in range(4):
                out[i][j] = add_poly(out[i][j], mul_poly(left[i][k], right[k][j]))
    return out


def direct_word():
    operator = identity_operator()
    for register in range(3):
        for index in range(3):
            operator = multiply(operator, coordinate_factor(basis_frame(index), register))
    return operator


def coordinate_eight_possible():
    for counts in product(range(9), repeat=4):
        if sum(counts) == 8 and all(counts[register] >= 3 for register in range(3)):
            return True
    return False


def saving_spans(address_dimension, data_registers, calls):
    if calls >= address_dimension * data_registers:
        return []
    return list(range(address_dimension + 1, calls - 2 + 1))


def evaluate():
    authenticate()
    model = MODEL.read_text(encoding="utf-8")
    dirty = DIRTY.read_text(encoding="utf-8")
    review = REVIEW.read_text(encoding="utf-8")
    require("Arbitrary free address maps between calls are outside this" in model, "the excluded address maps moved")
    require("The theorem makes no claim for extra" in model, "the extra-register exclusion moved")
    require("Three data registers, eight calls, one dirty auxiliary." in dirty, "the open eight-call case moved")
    require("Spans four, five and" in dirty, "the remaining spans moved")
    require("through length eleven" in review, "the GL3 census length moved")
    require("mixed-root UT4(F2)" in review, "the mixed-root tariff moved")
    require(matrix_rank(identity_frame()) == 3, "the identity target is not rank three")
    require(all(matrix_rank(basis_frame(index)) == 1 for index in range(3)), "a coordinate frame is not rank one")
    operator = direct_word()
    target = {identity_frame(): 1}
    restored = {ZERO: 1}
    for register in range(3):
        require(operator[register][register] == target, "a data target is not the identity frame")
    require(operator[3][3] == restored, "the auxiliary is not restored")
    for i in range(4):
        for j in range(4):
            if i != j:
                require(operator[i][j] == {}, "an off-diagonal entry survived")
    require(coordinate_eight_possible() is False, "eight coordinate calls covered every data register")
    require(saving_spans(3, 3, 8) == [4, 5, 6], "the eight-call span window moved")
    require(saving_spans(3, 2, 5) == [], "the two-register five-call window is not empty")
    return {
        "roles": 4,
        "data_registers": 3,
        "calls": 9,
        "auxiliary_restored": True,
        "data_targets_identity": True,
        "coordinate_eight_call_possible": False,
        "eight_call_spans": [4, 5, 6],
        "two_register_five_call_spans": [],
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
