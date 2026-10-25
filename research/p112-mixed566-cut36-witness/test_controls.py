"""Behavioral coefficient, cut, rank and source controls. Apache-2.0."""

import copy
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from verify import GEOMETRY, HERE, binary_rank, model, read_json, require


def cli(witness, directory, expected_error=None):
    path = directory / "mutant.json"
    path.write_text(json.dumps(witness) + "\n")
    result = subprocess.run(
        [
            sys.executable,
            *(["-O"] if sys.flags.optimize else []),
            "-B",
            str(HERE / "verify.py"),
            "--witness",
            str(path),
        ],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if expected_error is None:
        require(result.returncode == 0, "positive CLI control: " + result.stderr)
    else:
        require(
            result.returncode != 0 and expected_error in result.stderr,
            "mutant was not rejected at expected gate: " + result.stderr,
        )


def witness_mutants(original, roots, labels, live):
    result = []
    mutant = copy.deepcopy(original)
    mutant["cut_full_indices"].pop()
    result.append((mutant, "36 live cut sites"))
    mutant = copy.deepcopy(original)
    mutant["cut_full_indices"][0] = next(i for i in range(120) if i not in live)
    mutant["cut_full_indices"].sort()
    result.append((mutant, "36 live cut sites"))
    mutant = copy.deepcopy(original)
    mutant["cut_full_indices"][1] = mutant["cut_full_indices"][0]
    result.append((mutant, "common cut"))
    mutant = copy.deepcopy(original)
    mutant["pieces"][0]["values"][0] *= -1
    result.append((mutant, "two exact restricted codeword identities"))
    mutant = copy.deepcopy(original)
    mutant["pieces"][1]["coefficient_column"][1] = 1
    result.append((mutant, "two exact restricted codeword identities"))
    mutant = copy.deepcopy(original)
    mutant["pieces"][0]["values"][0] = True
    result.append((mutant, "nonzero exact piece values"))
    mutant = copy.deepcopy(original)
    mutant["pieces"][0]["coefficient_column"] = [0, 0]
    result.append((mutant, "exact coefficient column"))
    mutant = copy.deepcopy(original)
    mutant["schema_version"] = True
    result.append((mutant, "witness version"))
    support = original["pieces"][0]["support_full_indices"]
    candidates = sorted(set(live) - set(original["cut_full_indices"]) - set(support))
    replacement = next(
        i
        for i in candidates
        if binary_rank([labels[j] for j in support[1:] + [i]]) == 6
    )
    mutant = copy.deepcopy(original)
    mutant["pieces"][0]["support_full_indices"] = sorted(support[1:] + [replacement])
    result.append((mutant, "binary support ranks 5,6,6"))
    require(len(roots) == 120 and len(result) == 9, "bounded mutation inventory")
    return result


def main():
    original = read_json(HERE / "WITNESS.json")
    roots, labels, live = model()
    with tempfile.TemporaryDirectory(prefix="mixed566-controls-") as temporary:
        directory = Path(temporary)
        cli(original, directory)
        gauge = copy.deepcopy(original)
        gauge["pieces"][1]["values"] = [-x for x in gauge["pieces"][1]["values"]]
        gauge["pieces"][1]["coefficient_column"] = [
            -x for x in gauge["pieces"][1]["coefficient_column"]
        ]
        cli(gauge, directory)
        mutants = witness_mutants(original, roots, labels, live)
        for witness, error in mutants:
            cli(witness, directory, error)
        source = directory / GEOMETRY
        source.parent.mkdir(parents=True)
        source.write_text("raise RuntimeError('untrusted source must not run')\n")
        try:
            model(directory)
        except ValueError as error:
            require(str(error) == "geometry SHA256", "source failure boundary")
        else:
            raise ValueError("corrupted source accepted")
        source.unlink()
        source.symlink_to(Path(__file__).resolve())
        try:
            model(directory)
        except ValueError as error:
            require(str(error) == "regular geometry input", "symlink failure boundary")
        else:
            raise ValueError("linked source accepted")
    require(not os.path.exists(temporary), "owned control fixtures removed")
    print(
        "PASS_CONTROLS: two valid CLI fixtures, nine rejecting CLI mutants, two source controls"
    )


if __name__ == "__main__":
    main()
