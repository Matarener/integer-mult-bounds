"""Literal coefficient/rank and optimized actual CLI controls. Apache-2.0."""

import copy
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import common
import independent
import verify


def rejects(function, *args):
    try:
        function(*args)
    except (ValueError, KeyError):
        return
    raise ValueError("negative fixture was accepted")


def mutants(original):
    cases = [copy.deepcopy(original) for _ in range(7)]
    cases[0]["normal_numerator"] = [0] * 8
    cases[1]["pieces"][0]["values"][0] *= -1
    cases[2]["pieces"][0]["labels"][0] ^= 2
    cases[3]["pieces"][0]["binary_basis"] = cases[3]["pieces"][0]["binary_basis"][:3]
    cases[4]["joint_rank_minor"]["determinant"] = 0
    cases[5]["piece_coefficients"][0] = -1
    cases[6]["pieces"][0]["live_indices"][0] = 112
    return cases


def cli_controls(original, cases):
    with tempfile.TemporaryDirectory(
        prefix="p112-rank4-", dir=os.environ.get("TMPDIR")
    ) as tmp:
        root = Path(tmp)
        for i, case in enumerate([original, *cases]):
            path = root / f"witness-{i}.json"
            if i == 0:
                path.write_bytes((common.HERE / "WITNESS.json").read_bytes())
            else:
                path.write_text(json.dumps(case))
            command = [
                sys.executable,
                "-O",
                "-W",
                "error",
                "-B",
                str(common.HERE / "verify.py"),
                "--witness",
                str(path),
            ]
            done = subprocess.run(
                command, capture_output=True, text=True, check=False, timeout=30
            )
            common.require((done.returncode == 0) == (i == 0), "actual CLI control")
            if i:
                common.require("ValueError" in done.stderr, "meaningful CLI rejection")


def main():
    model = common.model()
    data = common.read_json(common.HERE / "WITNESS.json")
    result = verify.check(data, model)
    common.require(result["intersection_dimension"] == 1, "positive exact intersection")
    independent.check(data)
    cases = mutants(data)
    for case in cases:
        rejects(verify.check, case, model)
    for i in (0, 1, 2, 4):
        rejects(independent.check, cases[i])
    common.require(verify.determinant([[1, 2], [2, 4]]) == 0, "singular minor control")
    common.require(
        independent.binary_rank([1, 3, 5, 7]) == 3, "binary relation control"
    )
    duplicate = copy.deepcopy(data)
    duplicate["pieces"][0]["live_indices"][1] = duplicate["pieces"][0]["live_indices"][
        0
    ]
    rejects(verify.check, duplicate, model)
    cli_controls(data, cases)
    print("PASS_P112_RANK4_CONTROLS unit_mutants=8 actual_cli=8")


if __name__ == "__main__":
    main()
