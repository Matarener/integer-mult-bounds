#!/usr/bin/env python3
"""Exact finite corroboration of the common-reader obstruction in README.md."""

import argparse
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import platform


VECTORS = ((1, 0), (0, 1), (1, 1), (1, -1))
# Row i works at every cut except possibly cut i.
READERS = ((0, 1), (1, 0), (1, -1), (1, 1))
# Each gate is (helper coordinate, source coordinate, sign).
STAGES = (
    ((0, 0, 1),),
    ((0, 0, -1), (1, 1, 1)),
    ((0, 0, 1), (0, 1, 1), (1, 0, 1)),
    ((0, 1, -1), (0, 1, -1), (1, 0, -1), (1, 0, -1)),
    ((0, 0, -1), (0, 1, 1), (1, 0, 1), (1, 1, -1)),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def power_of_two(n):
    return n > 0 and n & (n - 1) == 0


def dyadic(value):
    return power_of_two(F(value).denominator)


def unit(value):
    value = F(value)
    return power_of_two(abs(value.numerator)) and dyadic(value)


def residue(value):
    value = F(value)
    require(dyadic(value), "reduction requires a dyadic coefficient")
    return value.numerator * pow(value.denominator, -1, 3) % 3


def dot(a, b):
    require(len(a) == len(b) == 2, "two coordinates required")
    return a[0] * b[0] + a[1] * b[1]


def response(a, e, b):
    return dot(a, e) * dot(e, b)


def source_column(a, e):
    value = dot(a, e)
    require(unit(value), "reader evaluation is not a dyadic unit")
    index = 0 if e[0] else 1
    require(abs(e[index]) == 1, "fixture needs a unit coordinate")
    b = [F(0), F(0)]
    b[index] = F(1, value * e[index])
    require(all(dyadic(x) for x in b), "source column left the dyadics")
    require(response(a, e, b) == 1, "normalization failed")
    return tuple(b)


def cover(vectors):
    require(1 <= len(vectors) <= 4, "cover size outside finite domain")
    return all(any(dot(a, e) % 3 == 0 for e in vectors)
               for a in product(range(3), repeat=2))


def check_residues():
    require(cover(VECTORS), "four kernels do not cover all rows")
    pairs = 0
    for a in product(range(3), repeat=2):
        failed = next(e for e in VECTORS if dot(a, e) % 3 == 0)
        for b in product(range(3), repeat=2):
            require(response(a, failed, b) % 3 == 0, "bad obstruction")
            pairs += 1
    # Clearing a power-of-two denominator must commute with reduction.
    reductions = 0
    for numerator, exponent in product(range(-16, 17), range(6)):
        x = F(numerator, 2**exponent)
        require(residue(x) * pow(2, exponent, 3) % 3 == numerator % 3,
                "dyadic reduction disagrees with denominator clearing")
        reductions += 1
    return {"residue_row_column_pairs": pairs, "dyadic_reductions": reductions}


def check_subfamilies(readers=READERS):
    require(len(readers) == 4, "four omission witnesses required")
    subsets = normalizations = 0
    for mask in range(1, 15):
        omitted = next(i for i in range(4) if not mask & (1 << i))
        a = readers[omitted]
        require(all(dyadic(x) for x in a), "nondyadic reader")
        for i in range(4):
            if mask & (1 << i):
                source_column(a, VECTORS[i])
                normalizations += 1
        subsets += 1
    for e in VECTORS:
        # A unit entry proves capacity >= 1; zero determinant proves <= 1.
        pivot = next(i for i in range(2) if e[i] == 1)
        a = tuple(int(j == pivot) for j in range(2))
        b = source_column(a, e)
        require(response(a, e, b) == 1, "individual channel absent")
        matrix = [[e[i] * e[j] for j in range(2)] for i in range(2)]
        require(matrix[0][0] * matrix[1][1]
                == matrix[0][1] * matrix[1][0], "rank exceeds one")
    return {"proper_nonempty_subfamilies": subsets,
            "subfamily_normalizations": normalizations, "individual_cuts": 4}


def expected_prefix(e):
    matrix = [[int(i == j) for j in range(4)] for i in range(4)]
    for i, j in product(range(2), repeat=2):
        matrix[2 + i][j] = e[i] * e[j]
    return matrix


def check_symbolic(stages=STAGES):
    require(len(stages) == 5, "five stages required")
    matrix = expected_prefix((0, 0))
    gates = 0
    for index, stage in enumerate(stages):
        require(0 <= len(stage) <= 4, "stage exceeds finite gate domain")
        for helper, source, sign in stage:
            require(helper in (0, 1) and source in (0, 1) and sign in (-1, 1),
                    "invalid scalar ADD")
            for column in range(4):
                matrix[2 + helper][column] += sign * matrix[source][column]
            gates += 1
        e = VECTORS[index] if index < 4 else (0, 0)
        require(matrix == expected_prefix(e), "wrong prefix or dirty endpoint")
    return {"symbolic_prefixes": 5, "unit_scalar_adds": gates}


def check_dirty():
    gates = tuple(g for stage in STAGES for g in stage)
    vectors = updates = 0
    for incoming in product(range(-2, 3), repeat=4):
        state = list(incoming)
        for direction in (1, -1):
            ordered = gates if direction == 1 else tuple(reversed(gates))
            for helper, source, sign in ordered:
                state[2 + helper] += direction * sign * state[source]
                updates += 1
            require(tuple(state) == incoming, "dirty state was not restored")
        vectors += 1
    return {"dirty_integer_inputs": vectors, "dirty_scalar_updates": updates}


def check_rational_contrast():
    a = (F(1), F(2))
    nondyadic = 0
    for e in VECTORS:
        index = 0 if e[0] else 1
        b = [F(0), F(0)]
        b[index] = F(1, dot(a, e) * e[index])
        require(response(a, e, b) == 1, "rational contrast failed")
        nondyadic += int(any(not dyadic(x) for x in b))
    require(nondyadic == 1, "contrast must use exactly one nondyadic column")
    return {"rational_normalizations": 4, "nondyadic_columns": nondyadic}


def expect_rejection(action):
    try:
        action()
    except ValueError:
        return
    raise ValueError("negative control was accepted")


def check_controls():
    controls = []
    for omitted in range(4):
        shorter = tuple(e for i, e in enumerate(VECTORS) if i != omitted)
        require(not cover(shorter), "proper subset still covers rows")
        controls.append("remove-cut-" + str(omitted))
    require(not cover(VECTORS[:3] + (VECTORS[2],)), "duplicate cut accepted")
    controls.append("duplicate-last-cut")
    expect_rejection(lambda: residue(F(1, 3)))
    controls.append("odd-denominator")
    bad = READERS[:3] + ((1, -1),)
    expect_rejection(lambda: check_subfamilies(bad))
    controls.append("wrong-omission-reader")
    scaled = tuple(tuple(3 * x for x in a) for a in READERS)
    expect_rejection(lambda: check_subfamilies(scaled))
    controls.append("nonunit-reader-scaling")
    for stage_index, stage in enumerate(STAGES):
        for gate_index, gate in enumerate(stage):
            deleted = stage[:gate_index] + stage[gate_index + 1:]
            changed = STAGES[:stage_index] + (deleted,) + STAGES[stage_index + 1:]
            expect_rejection(lambda: check_symbolic(changed))
            controls.append("delete-gate-" + str((stage_index, gate_index)))
            h, s, sign = gate
            flipped = stage[:gate_index] + ((h, s, -sign),) + stage[gate_index + 1:]
            changed = STAGES[:stage_index] + (flipped,) + STAGES[stage_index + 1:]
            expect_rejection(lambda: check_symbolic(changed))
            controls.append("flip-gate-" + str((stage_index, gate_index)))
    require(not unit(F(3)) and not unit(F(0)) and unit(F(-1, 8)),
            "unit test lost its arithmetic distinction")
    require(response((1, 0), VECTORS[0], (-1, 0)) != 1,
            "normalization sign fault accepted")
    controls.append("wrong-normalization-sign")
    return controls


def verify():
    result = {}
    for part in (check_residues(), check_subfamilies(), check_symbolic(),
                 check_dirty(), check_rational_contrast()):
        require(not result.keys() & part.keys(), "duplicate evidence key")
        result.update(part)
    controls = check_controls()
    result["rejecting_controls"] = len(controls)
    result["control_names"] = controls
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path,
                        help="write a generated hash-bound receipt to this explicit path")
    args = parser.parse_args()
    result = verify()
    print(json.dumps({k: v for k, v in result.items() if k != "control_names"},
                     sort_keys=True))
    if args.receipt is not None:
        package = Path(__file__).resolve().parent
        names = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
        receipt = {"schema": "common-reader-cut-obstruction/v1",
                   "python": platform.python_version(), "result": result,
                   "sha256": {name: sha256((package / name).read_bytes()).hexdigest()
                              for name in names}}
        payload = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
        require(args.receipt.write_text(payload, encoding="utf-8") == len(payload),
                "short receipt write")
    print("PASS_COMMON_READER_CUT_OBSTRUCTION")


if __name__ == "__main__":
    main()
