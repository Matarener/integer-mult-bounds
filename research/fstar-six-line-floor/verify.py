#!/usr/bin/env python3
"""Exact finite controls for the written six-line proof, not a formal proof.

SPDX-License-Identifier: Apache-2.0
Sagar Thakrar, with substantial OpenAI Codex assistance.
"""

import argparse
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import independent_box as box


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(root=ROOT, package=HERE):
    manifest = json.loads((package / "SOURCES.json").read_text())
    inputs = {}
    rows = [(root, row) for row in manifest["files"] if row["usage"] == "input"]
    rows += [(package, row) for row in manifest.get("frozen_sources", [])]
    for base, row in rows:
        data = (base / row["path"]).read_bytes()
        require(hashlib.sha256(data).hexdigest() == row["sha256"],
                "Input changed: " + row["path"])
        inputs[row["path"]] = data
    require("inputs/pr2914-engine.py" in inputs, "Missing authenticated source engine")
    return inputs


def admitted_data(P, Q):
    data = box.rational_data(P, Q)
    require(len(P) == 6, "The stated theorem uses six lines")
    require(all(tau >= 1 for tau in data["tau"]), "Every line must have tau >= 1")
    return data


def reference_check(inputs, fixture):
    name = "inputs/pr2914-engine.py"
    module = types.ModuleType("frozen_definition_engine")
    module.__file__ = str(HERE / name)
    # Execute the already authenticated bytes, not a second filesystem read.
    exec(compile(inputs[name], module.__file__, "exec"), module.__dict__)
    model = module.model(*box.core_fixture())
    anchors = module.anchor_data(model)
    for key in ("a0", "b0", "tau", "gamma"):
        require(anchors[key] == fixture[key], "Source normalization differs: " + key)
    require(model["M"] == fixture["M"], "Source matrix differs")
    require(module.scope_identity(model, anchors), "Source scope identity failed")
    require(module.replay_witness(model, fixture["witness"]), "Source witness replay failed")
    require(module.in_box(model, anchors, fixture["witness"])[0], "Source box check failed")
    return {"engine_sha256": hashlib.sha256(inputs[name]).hexdigest(),
            "matrix_anchors_scope_and_witness": True,
            "predecessor_enumeration_executed": False}


def affine_controls():
    count = 0
    possible = list(product(range(8), range(2)))
    for size in range(5):
        for equations in combinations(possible, size):
            for allowed in range(8):
                answer = box.linear_solution(allowed, equations)
                truth = [x for x in range(8) if not x & ~allowed
                         and all(box.dot(x, a) == b for a, b in equations)]
                require((answer is None) == (not truth), "Affine feasibility mismatch")
                require(answer is None or answer in truth, "Affine solution mismatch")
                count += 1
    return {"systems": count, "equations_per_system_at_most": 4,
            "independent_submask_truth_table": True}


def witness_controls(fixture):
    anchors, arcs = [3, 3], {(0, 1)}
    witness = box.kept_witness(anchors, anchors, arcs)
    require(witness is not None and witness["order"] == [1, 0], "One-way order control")
    wrong = {**witness, "order": [0, 1]}
    require(not box.check_witness(anchors, anchors, arcs, wrong), "Wrong order accepted")
    require(box.check_witness(anchors, anchors, (), wrong), "Omitted-arc control is inactive")
    bad = {**fixture["witness"], "a": fixture["witness"]["a"].copy()}
    bad["a"][0] |= 4
    require(box.dot(bad["a"][0], bad["b"][0]) == 1, "Submask mutant lost its diagonal")
    require(not box.check_witness(fixture["a0"], fixture["b0"], fixture["arcs"], bad),
            "Out-of-anchor label accepted")
    return {"wrong_forward_order_rejected": True, "omitted_zero_arc_detected": True,
            "parity_preserving_submask_mutation_rejected": True}


def necessity_controls():
    rows = [(1, 0, 0)] * 2 + [(0, 2, 0)] * 2 + [(0, 0, 2)] * 2
    data = box.rational_data(rows, rows)
    value, witness = box.maximum_box(data["a0"], data["b0"], data["arcs"])
    require(data["rank"] == 3 and data["tau"] == [1, 1, 0, 0, 0, 0] and value == 2,
            "Tau-necessity fixture differs")
    try:
        admitted_data(rows, rows)
    except ValueError as error:
        require("tau" in str(error), "Wrong admission failure")
    else:
        raise ValueError("Tau-zero input was admitted")
    arcs = [(i, j) for i in range(6) for j in range(6) if i != j]
    value2, _ = box.maximum_box([3] * 6, [3] * 6, arcs)
    rank = box.rational_rank([[int(i == j) for j in range(6)] for i in range(6)])
    require(rank == 6 and value2 == 2, "Abstract rank-necessity control differs")
    P, Q = box.core_fixture()
    P[0] = (0, 0, 0)
    try:
        admitted_data(P, Q)
    except ValueError as error:
        require("zero diagonal" in str(error), "Wrong zero-diagonal failure")
    else:
        raise ValueError("Zero diagonal was admitted")
    return {"tau_necessity": {"rank": 3, "tau": data["tau"], "box": value,
                              "witness": witness, "admission_rejected": True},
            "rank_necessity": {"matrix": "I6", "rank": rank, "box": value2,
                               "scope": "abstract anchors and zero arcs; no three-total realization"},
            "zero_diagonal_rejected": True}


def rational_controls(fixture):
    P, Q = box.core_fixture()
    factors = [Fraction(-3, 8), Fraction(5, 4), Fraction(7, 2)]
    scaled_p = [[Fraction(x) * factors[j] for j, x in enumerate(row)] for row in P]
    scaled_q = [[Fraction(x) / factors[j] for j, x in enumerate(row)] for row in Q]
    unchanged = admitted_data(scaled_p, scaled_q)
    for key in ("M", "rank", "gamma", "a0", "b0", "tau", "arcs"):
        require(unchanged[key] == fixture[key], "Reciprocal column rescaling changed " + key)
    shifted = admitted_data([[Fraction(x, 8) for x in row] for row in P],
                            [[Fraction(x, 2) for x in row] for row in Q])
    require(shifted["gamma"] == -4, "Rational global valuation shift differs")
    require(shifted["a0"] == fixture["a0"] and shifted["b0"] == fixture["b0"]
            and shifted["tau"] == fixture["tau"], "Rational anchors changed")
    require(shifted["M"] == [[Fraction(x, 16) for x in row] for row in fixture["M"]],
            "Rational matrix scaling differs")
    return {"reciprocal_signed_rational_columns": True, "global_gamma_shift": -4,
            "zero_entries_retained": True}


def duplicate_blocker_control():
    """Actual rational rows refute a shared-physical-blocker inference."""
    P = [(1, 0, 1), (1, 2, 1), (0, 1, 1),
         (1, -1, -2), (1, -1, -4), (1, -1, -2)]
    Q = [(1, -3, 2), (1, -7, 2), (1, 1, 0),
         (1, 1, -1), (-1, 1, -1), (1, 1, -1)]
    data = admitted_data(P, Q)
    require(data["gamma"] == 0 and data["rank"] == 3, "Duplicate-blocker normalization")
    require(data["a0"] == [5, 5, 6, 3, 3, 3] and data["b0"] == [3, 3, 3, 7, 7, 7],
            "Duplicate-blocker anchors differ")
    require(data["tau"] == [1, 1, 1, 2, 2, 2], "Duplicate-blocker tied sets differ")
    matrix = data["M"]
    blockers = {3: 0, 4: 1, 5: 0}
    for even, blocker in blockers.items():
        other = 1 - blocker
        require(matrix[even][blocker] == matrix[blocker][even] == 0,
                "Required physical blocker does not block")
        require(matrix[even][other] != 0 and matrix[other][even] != 0,
                "Different physical duplicate unexpectedly blocks")
        require(matrix[even][2] == matrix[2][even] == 0, "Unique blocker does not block")
    require(box.rational_rank([Q[3], Q[4]]) == 2,
            "Control must have nonproportional even target rows")
    require(box.dot(data["a0"][0], data["b0"][1]) == 1
            and box.dot(data["a0"][1], data["b0"][0]) == 1,
            "Odd pair is not forced nonzero by SG")
    require(matrix[0][1] != 0 and matrix[1][0] != 0 and matrix[4][3] == 4,
            "Required pair entries are not nonzero")
    labels = [1, 1, 0, 2, 2, 0]
    witness = {"a": labels, "b": labels, "kept": [0, 1, 3, 4], "order": [0, 1, 4, 3]}
    require(box.check_witness(data["a0"], data["b0"], data["arcs"], witness),
            "Repaired odd-pair plus even-pair witness failed")
    wrong = {**witness, "order": [0, 1, 3, 4]}
    require(not box.check_witness(data["a0"], data["b0"], data["arcs"], wrong),
            "Reversing the only admissible even-pair direction was accepted")
    # If all even edges were absent, the unique blocker and three evens
    # would form this diagonal minor. This is a contradiction, not a realization.
    indices = [2, 3, 4, 5]
    forced_minor = [[matrix[i][i] if i == j else 0 for j in indices] for i in indices]
    require(box.rational_rank(forced_minor) == 4, "No-even-edge rank contradiction failed")
    return {"P": P, "Q": Q, "M": [[int(x) for x in row] for row in matrix],
            "a0": data["a0"], "b0": data["b0"], "tau": data["tau"], "rank": 3,
            "physical_blockers": [[i, j] for i, j in blockers.items()],
            "even_target_row_rank": 2, "witness": witness,
            "wrong_even_pair_direction_rejected": True,
            "no_even_edge_forced_minor_rank": 4,
            "no_even_edge_minor_is_counterfactual": True}


def authentication_control():
    # Intercept only the frozen input read; all actual files remain untouched.
    from unittest.mock import patch
    original = Path.read_bytes
    target = HERE / "inputs/pr2914-engine.py"
    def corrupted(path):
        data = original(path)
        return b"raise RuntimeError('counterfeit source executed')\n" if path == target else data
    with patch.object(Path, "read_bytes", corrupted):
        try:
            build()
        except ValueError as error:
            require("Input changed: inputs/pr2914-engine.py" in str(error),
                    "Unexpected source corruption error")
        else:
            raise ValueError("Changed source was accepted")
    return True


def build():
    inputs = authenticate()
    fixture = box.fixture_certificate()
    admitted_data(*box.core_fixture())
    receipt = {"schema_version": 1,
            "scope": "finite independent checks supporting the separate written proof",
            "sharp_fixture": fixture, "source_comparison": reference_check(inputs, fixture),
            "affine_controls": affine_controls(), "witness_controls": witness_controls(fixture),
            "necessity_controls": necessity_controls(), "rational_controls": rational_controls(fixture),
            "duplicate_blocker_control": duplicate_blocker_control(),
            "source_corruption_rejected_before_execution": authentication_control(),
            "exhaustive_six_line_census_claimed": False, "formal_proof_claimed": False}
    return json.loads(json.dumps(receipt))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print deterministic receipt")
    args = parser.parse_args()
    receipt = build()
    if args.emit:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        require(receipt == json.loads((HERE / "RESULT.json").read_text()), "Receipt mismatch")
        print("PASS_FSTAR_SIX_LINE_FINITE_CONTROLS box=4 rank=3 tau=2x6")


if __name__ == "__main__":
    main()
