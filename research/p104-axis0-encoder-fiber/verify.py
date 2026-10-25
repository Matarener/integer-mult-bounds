#!/usr/bin/env python3
"""One frozen encoder fiber equals axis-0 multiplication by U.

The fiber is a contiguous slice of the encoder word emitted by the frozen
PR #3979 builder bytes that PR #3996 vendors. This file does not import or
call the PR #3996 checker.
"""
from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
FIXTURE = ROOT / "research/p104-native-channel/inputs/P104-FIXTURE.json"
BUILDER = HERE / "frozen/word_builder.py"
FIXTURE_SHA256 = "516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4"
BUILDER_SHA256 = "27bae82fe247fe49b8fc3b5efbd429e2c8c0ee8f56cc4ace748cbb681a5abacc"
B2_SHA256 = "88e9a726e8c8aec055bfd7cd024883b5c8ecbda0cd6471e591a08c43a108a535"
N = 104
PIVOTS = (0, 1, 3, 6, 22, 31, 93, 103)
BANK = 0
COLUMN = 0


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def load_json(path):
    def pairs(items):
        found = {}
        for key, value in items:
            require(key not in found, "duplicate JSON key in " + str(path))
            found[key] = value
        return found

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rebuild_b2():
    """Integer numerator of B, independent of the word builder."""
    roots = []
    for left, right in itertools.combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[left], row[right] = 2, 2 * sign
            roots.append(tuple(row))
    roots.extend(
        (1,) + tail
        for tail in itertools.product((-1, 1), repeat=7)
        if tail.count(-1) % 2 == 0
    )
    fixture = load_json(FIXTURE)["section4_explicit_P104"]
    removed = {tuple(row) for row in fixture["F0"] + fixture["C"]}
    ports = sorted(set(roots) - removed)
    require(len(ports) == N, "P104 port count")
    order = list(PIVOTS) + [index for index in range(N) if index not in PIVOTS]
    ports = [ports[index] for index in order]
    gram = [[sum(x * y for x, y in zip(left, right)) for right in ports] for left in ports]
    b2 = [[gram[row][column] // 4 for column in range(8, N)] for row in range(8)]
    require(all(entry in (-1, 0, 1) for row in b2 for entry in row), "B numerators")
    digest = hashlib.sha256(
        json.dumps(b2, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    require(digest == B2_SHA256, "B2 digest")
    require(sum(entry != 0 for row in b2 for entry in row) == 384, "B support")
    return b2


def axis0_u_program(b2, bank, column):
    """Half, add B, double: the axis-0 program for U = [[I, B/2], [0, I]]."""
    pivot_count = len(b2)
    width = pivot_count + len(b2[0])

    def at(row):
        return (bank * width + row) * width + column

    program = [("half", at(row)) for row in range(pivot_count, width)]
    for pivot, row in enumerate(b2):
        for offset, value in enumerate(row):
            if value:
                program.append(("add", at(pivot), at(pivot_count + offset), value))
    program.extend(("double", at(row)) for row in range(pivot_count, width))
    return program


def load_encoder(b2):
    require(sha256(BUILDER) == BUILDER_SHA256, "frozen builder bytes")
    spec = importlib.util.spec_from_file_location("frozen_word_builder", BUILDER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    require(callable(getattr(module, "code_word", None)), "builder exports code_word")
    # code_word emits events. Do not call result(), evaluate(), or any checker.
    return list(module.code_word(b2))


def find_slice(word, needle):
    width = len(needle)
    hits = []
    first = needle[0]
    limit = len(word) - width + 1
    for start in range(limit):
        if word[start] != first:
            continue
        if word[start : start + width] == needle:
            hits.append(start)
    return hits


def decode(index):
    owner, offset = divmod(index, N * N)
    row, column = divmod(offset, N)
    return owner, row, column


def interpret_axis0(program, bank, column):
    rows = [{row: Fraction(1)} for row in range(N)]
    for operation in program:
        kind = operation[0]
        require(kind in ("add", "half", "double"), "operation alphabet")
        owner, row, fixed = decode(operation[1])
        require((owner, fixed) == (bank, column), "fiber leaves the column")
        if kind == "add":
            require(len(operation) == 4 and operation[3] in (-1, 1), "unit add")
            source_owner, source_row, source_column = decode(operation[2])
            require((source_owner, source_column) == (bank, column), "add source leaves the column")
            updated = dict(rows[row])
            for coordinate, value in rows[source_row].items():
                total = updated.get(coordinate, Fraction(0)) + operation[3] * value
                if total:
                    updated[coordinate] = total
                else:
                    updated.pop(coordinate, None)
            rows[row] = updated
        else:
            factor = Fraction(1, 2) if kind == "half" else Fraction(2)
            rows[row] = {coordinate: factor * value for coordinate, value in rows[row].items()}
    return rows


def matrix_u(b2, inverse=False):
    rows = [{row: Fraction(1)} for row in range(N)]
    sign = -1 if inverse else 1
    for pivot, row in enumerate(b2):
        for offset, value in enumerate(row):
            if value:
                rows[pivot][8 + offset] = Fraction(sign * value, 2)
    return rows


def matrix_u_transpose(b2, inverse=False):
    rows = [{row: Fraction(1)} for row in range(N)]
    sign = -1 if inverse else 1
    for pivot, row in enumerate(b2):
        for offset, value in enumerate(row):
            if value:
                rows[8 + offset][pivot] = Fraction(sign * value, 2)
    return rows


def receipt():
    require(sha256(FIXTURE) == FIXTURE_SHA256, "fixture bytes")
    b2 = rebuild_b2()
    needle = axis0_u_program(b2, BANK, COLUMN)
    word = load_encoder(b2)
    hits = find_slice(word, needle)
    require(hits == [41600], "encoder contains the bank-0 column-0 axis-0 U fiber once, after the first sweep")
    realized = interpret_axis0(word[hits[0] : hits[0] + len(needle)], BANK, COLUMN)
    require(realized == matrix_u(b2), "fiber map is U")
    require(realized != matrix_u(b2, inverse=True), "fiber is not U inverse")
    require(realized != matrix_u_transpose(b2), "fiber is not U transpose")
    require(realized != matrix_u_transpose(b2, inverse=True), "fiber is not U inverse transpose")
    broken = list(needle)
    for index, operation in enumerate(broken):
        if operation[0] == "add":
            broken[index] = (operation[0], operation[1], operation[2], -operation[3])
            break
    require(interpret_axis0(broken, BANK, COLUMN) != matrix_u(b2), "sign flip must miss U")
    fiber_digest = hashlib.sha256(
        json.dumps(needle, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    return {
        "bank": BANK,
        "column": COLUMN,
        "fiber_digest_sha256": fiber_digest,
        "fiber_events": len(needle),
        "match_offset": hits[0],
        "match_count": len(hits),
        "encoder_events": len(word),
        "map": "U",
        "axis": 0,
        "checker_called": False,
        "new_kappa": False,
    }


def main():
    print("PASS_P104_AXIS0_ENCODER_FIBER " + json.dumps(receipt(), sort_keys=True))


if __name__ == "__main__":
    main()
