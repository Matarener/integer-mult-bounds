#!/usr/bin/env python3
"""Check the frozen S3 tensor and selected affine-data admission boundary."""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIMIT = 4_000_000
BASE_PROFILE = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_json(path: Path, compressed: bool = False):
    raw = path.read_bytes()
    need(len(raw) <= LIMIT, "input size")
    if compressed:
        raw = gzip.decompress(raw)
    need(len(raw) <= LIMIT, "expanded input size")
    return json.loads(raw)


def check_pins() -> None:
    sources = read_json(HERE / "SOURCES.json")
    for row in sources["retained_files"]:
        raw = (HERE / row["local_path"]).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row["sha256"], "source pin")


def integer(value) -> bool:
    return type(value) is int


def role(value) -> bool:
    return (type(value) is list and len(value) == 2
            and value[0] in ("L", "C") and integer(value[1])
            and 0 <= value[1] < (704 if value[0] == "L" else 8))


def check_scalar(gate: list) -> None:
    need(type(gate) is list and 2 <= len(gate) <= 5, "scalar shape")
    op = gate[0]
    need(role(gate[1]), "scalar target")
    if op == "add":
        need(len(gate) == 5 and role(gate[2]), "add source")
        numerator, denominator = gate[3:]
    elif op == "scale":
        need(len(gate) == 4, "scale shape")
        numerator, denominator = gate[2:]
    elif op == "copy":
        need(len(gate) == 3 and role(gate[2]), "copy source")
        return
    else:
        need(op == "clear" and len(gate) == 2, "nonlinear or unknown scalar")
        return
    need(integer(numerator) and integer(denominator), "fixed scalar coefficient")
    need(denominator != 0, "scalar denominator")


def classify(events: list) -> dict:
    need(type(events) is list and len(events) == 24767, "fixed event count")
    counts = Counter()
    scalars = Counter()
    profile = Counter()
    for event in events:
        need(type(event) is list and 2 <= len(event) <= 6, "event shape")
        tag = event[0]
        counts[tag] += 1
        if tag == "scalar":
            need(len(event) == 3 and integer(event[2]), "scalar frame")
            check_scalar(event[1])
            scalars[event[1][0]] += 1
        elif tag == "phase":
            need(len(event) == 2 and type(event[1]) is str, "phase marker")
        elif tag in ("climb", "adapter", "residual_adapter"):
            need(type(event[1]) is str, "fixed operator direction")
            need(all(integer(v) for v in event[2:]), "fixed operator indices")
            need(len(event) == {"climb": 6, "adapter": 4}.get(tag, len(event)),
                 "operator shape")
            if tag == "climb":
                need(1 <= event[5] <= 9, "child address rank")
                profile[event[5]] += 1
            if tag == "residual_adapter":
                need(len(event) in (4, 5), "residual shape")
        else:
            need(tag == "center" and len(event) == 5, "unknown event")
            need(all(integer(v) for v in event[1:]), "fixed center indices")
            profile[event[4]] += 1
    need(dict(profile) == BASE_PROFILE, "selected paid profile")
    return {"events": dict(sorted(counts.items())), "scalars": dict(sorted(scalars.items()))}


def tensor_coefficients(candidate: dict) -> tuple:
    arrays = []
    for key in ("left_forms", "right_forms", "output_forms"):
        rows = candidate[key]
        need(type(rows) is list and len(rows) == 9, "nine tensor terms")
        need(all(type(row) is list and len(row) == 6 for row in rows), "six coordinates")
        need(all(type(x) is str and len(x) <= 16 for row in rows for x in row),
             "rational strings")
        arrays.append(tuple(tuple(Fraction(x) for x in row) for row in rows))
    return tuple(arrays)


def tensor_product(x: tuple, y: tuple, arrays: tuple) -> tuple:
    left, right, output = arrays
    terms = tuple(sum(a * b for a, b in zip(row, x))
                  * sum(a * b for a, b in zip(other, y))
                  for row, other in zip(left, right))
    return tuple(sum(terms[t] * output[t][k] for t in range(9)) for k in range(6))


def tensor_check(candidate: dict) -> dict:
    arrays = tensor_coefficients(candidate)
    group = tuple(tuple(g) for g in candidate["group_order"])
    need(len(group) == 6 and set(group) == {
        (0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)}, "S3")
    zero = (0,) * 6
    mixed = []
    for i in range(6):
        x = tuple(int(k == i) for k in range(6))
        for j in range(6):
            y = tuple(int(k == j) for k in range(6))
            composed = tuple(group[i][group[j][k]] for k in range(3))
            expected = tuple(int(g == composed) for g in group)
            value = tensor_product(x, y, arrays)
            difference = tuple(a - b - c + d for a, b, c, d in zip(
                value, tensor_product(x, zero, arrays),
                tensor_product(zero, y, arrays), tensor_product(zero, zero, arrays)))
            need(value == expected == difference, "S3 mixed data difference")
            mixed.append(group.index(composed))
    return {"nonzero_mixed_basis_differences": len(mixed), "output_indices": mixed}


def fixed_coefficient_control(candidate: dict) -> int:
    arrays = tensor_coefficients(candidate)
    fixed_x = (2, -3, 5, 7, -11, 13)
    dirty = (17, -19, 23, -29, 31, -37)
    for i in range(6):
        for j in range(6):
            y = tuple(int(k == i) for k in range(6))
            other = tuple(int(k == j) for k in range(6))
            combined = tuple(a + b for a, b in zip(y, other))
            left = tensor_product(fixed_x, combined, arrays)
            right = tuple(a + b for a, b in zip(
                tensor_product(fixed_x, y, arrays), tensor_product(fixed_x, other, arrays)))
            need(left == right, "fixed-coefficient linear case is outside exclusion")
            restored = tuple((z + value) - value for z, value in zip(dirty, left))
            need(restored == dirty, "dirty output cancellation")
    return 36


def rejection_controls(program: dict, candidate: dict) -> list:
    rejected = []
    gate = next(e[1] for e in program["forward"] if e[0] == "scalar" and e[1][0] == "add")
    for name, replacement in (("data-coefficient", ["L", 0]), ("boolean-coefficient", True)):
        bad = list(gate)
        bad[3] = replacement
        try:
            check_scalar(bad)
        except ValueError:
            rejected.append(name)
    try:
        check_scalar(["multiply", ["L", 0], ["L", 1]])
    except ValueError:
        rejected.append("data-product-opcode")
    bad_candidate = dict(candidate)
    bad_candidate["output_forms"] = [["0"] * 6] + candidate["output_forms"][1:]
    try:
        tensor_check(bad_candidate)
    except ValueError:
        rejected.append("omitted-S3-term")
    need(len(rejected) == 4, "all semantic controls rejected")
    return rejected


def main() -> None:
    check_pins()
    program = read_json(HERE / "inputs/LOCAL-PROGRAMS.json.gz", compressed=True)
    need(set(program) == {"forward", "backward"}, "orientations")
    candidate = read_json(HERE / "inputs/S3-RESULT.json")
    result = {"status": "PASS_S3_SELECTED_AFFINE_BOUNDARY_NO_NEW_KAPPA",
              "orientations": {key: classify(program[key]) for key in sorted(program)},
              "tensor": tensor_check(candidate),
              "fixed_coefficient_linear_controls": fixed_coefficient_control(candidate),
              "controls": rejection_controls(program, candidate),
              "scope": "No literal affine-data embedding of twelve-independent-input S3 convolution; no universal S3 exclusion"}
    need(json.dumps(result, sort_keys=True) == json.dumps(
        read_json(HERE / "RESULT.json"), sort_keys=True), "typed stored result")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
