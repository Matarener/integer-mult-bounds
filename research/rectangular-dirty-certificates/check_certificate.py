"""Check rectangular closure equations without elimination or search."""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from typed_words import (Q, advance, combine, compile_problem, path_row,
                         projection, require, scalar, witness)


def linear_combination(basis, encoded, dimension):
    require(type(encoded) is list and len(encoded) == len(basis), "coordinate count")
    row = [Q(0)] * dimension
    for c, b in zip(encoded, basis, strict=True):
        row = combine(row, b, scalar(c, certificate=True))
    return row


def check(problem, certificate):
    model = compile_problem(problem)
    require(type(certificate) is dict and type(certificate.get("equal")) is bool,
            "certificate must contain Boolean equal")
    if not certificate["equal"]:
        require(set(certificate) == {"equal", "output", "word", "input", "coefficient"},
                "negative certificate keys")
        return witness(problem, certificate)
    require(set(certificate) == {"equal", "basis", "initial", "closure"}, "positive certificate keys")
    paths = certificate["basis"]
    d = len(model["types"])
    require(type(paths) is list and len(paths) <= d, "basis bound")
    basis = []
    for path in paths:
        require(type(path) is dict and set(path) == {"output", "word"}, "path keys")
        row, _ = path_row(model, path["output"], path["word"])
        require(not any(projection(model, row)), "nonzero final projection")
        basis.append(row)
    initial, closure = certificate["initial"], certificate["closure"]
    require(type(initial) is list and len(initial) == len(model["roles"]), "initial count")
    for expected, encoded in zip(model["output"], initial, strict=True):
        require(expected == linear_combination(basis, encoded, d), "initial-span equation")
    require(type(closure) is dict and set(closure) == set(model["arrows"]), "closure alphabet")
    for a, rows in closure.items():
        require(type(rows) is list and len(rows) == len(basis), "closure row count")
        for b, encoded in zip(basis, rows, strict=True):
            require(advance(model, b, a) == linear_combination(basis, encoded, d),
                    "closure equation")
    return {"equal": True, "states": d, "basis_rows": len(basis)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("problem", type=Path)
    parser.add_argument("certificate", type=Path)
    args = parser.parse_args()
    for path in (args.problem, args.certificate):
        require(path.stat().st_size <= 16_000_000, "input file too large")
    print(json.dumps(check(json.loads(args.problem.read_text()),
                           json.loads(args.certificate.read_text())), sort_keys=True))


if __name__ == "__main__":
    main()
