#!/usr/bin/env python3
"""Generic hook checks source/formula bindings only, never an UNSAT verdict."""

import importlib.util
import json
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("occupancy_verify", HERE / "verify.py")
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)


def main():
    V.sources()
    expected = json.loads((HERE / "RESULT.json").read_text())
    V.M.need(
        [row["template"] for row in expected["cases"]] == [1, 2, 3, 4],
        "named case coverage",
    )
    with tempfile.TemporaryDirectory(prefix="connector-formula-") as temporary:
        path = Path(temporary) / "input.cnf"
        for row in expected["cases"]:
            low = V.M.templates()[row["template"] - 1]
            V.M.need(list(low) == row["low"], "template identity")
            formula = V.M.build(low)
            V.dimacs(formula, path)
            V.M.need(len(formula.variables) == row["variables"], "variable receipt")
            V.M.need(len(formula.clauses) == row["clauses"], "clause receipt")
            V.M.need(V.sha(path) == row["cnf_sha256"], "exact CNF binding")
    print("PASS_CONNECTOR_B_FORMULA_BINDINGS_ONLY no_UNSAT_replay")


if __name__ == "__main__":
    main()
