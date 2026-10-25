#!/usr/bin/env python3
"""Price a plane-port endpoint against the line-port coverage law.

Coordinate factors are exponents modulo 4. A dirty spectator stays in place.
The naive rank-2 charge is screened with the published ceiling.
"""

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
CEILING_DIR = ROOT / "research/complex-local-word-ceiling"
sys.path.insert(0, str(CEILING_DIR))
import ceiling as ceiling_model  # noqa: E402

MARKER = "PASS_PLANE_PORT_ENDPOINT naive_saving=false no_new_kappa"
WORD = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
GRID = Fraction(1, 10**12)
NAIVE = {7: 224, 2: 112}
NAIVE_CHARGE = 224


def fail(message):
    raise SystemExit("FAIL_PLANE_PORT_ENDPOINT " + message)


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
        "research/complex-local-word-ceiling/ceiling.py",
        "research/complex-local-word-ceiling/README.md",
        "research/split-centres-global/proofs/INHERITED-COMPLEX-GEOMETRY.txt",
        "research/plane-port-copy-budgets/README.md",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def coordinate(index):
    value = [0, 0, 0]
    value[index] = 1
    return tuple(value)


def multiply(left, right):
    return tuple((a + b) % 4 for a, b in zip(left, right))


def square(value):
    return multiply(value, value)


def endpoint(port, dirty, repair):
    """Return the exchanged operator for a port and one dirty spectator."""
    factor = (0, 0, 0)
    for index in port:
        factor = multiply(factor, coordinate(index))
    repair_factor = square(factor)
    # C_E^{-2} equals C_E^2 because that square has order two.
    state = multiply(multiply((1, 1, 0), repair_factor), dirty)
    if repair:
        state = multiply(state, repair_factor)
    return state


def evaluate():
    authenticate()
    geometry = (ROOT / "research/split-centres-global/proofs/INHERITED-COMPLEX-GEOMETRY.txt").read_text(encoding="utf-8")
    ceiling_note = (CEILING_DIR / "README.md").read_text(encoding="utf-8")
    plane_note = (ROOT / "research/plane-port-copy-budgets/README.md").read_text(encoding="utf-8")
    require("The final Y endpoint is C_all C_q^(-1)." in geometry, "the endpoint sentence moved")
    require("C_all C_q^(-2)=C_all X_q" in geometry, "the line-port repair moved")
    require("| Two unpaid coordinates per live family | 3.77 | 0.00634 |" in ceiling_note, "the lever row moved")
    require("112 rank-2 queries, C = 224" in plane_note, "the naive charge moved")
    dirty = square(coordinate(2))
    delivered = multiply((1, 1, 0), dirty)
    line = endpoint((0,), dirty, True)
    plane = endpoint((0, 1), dirty, True)
    omitted = endpoint((0, 1), dirty, False)
    require(line == plane == delivered, "the repaired endpoint missed C_all on the dirty spectator")
    require(line[2] == 2 and plane[2] == 2, "the spectator was cleared")
    require(omitted != delivered, "omitting the repair still delivered C_all")
    base = ceiling_model.ceiling(WORD, 73, 896, 9, 64, grid=GRID)[1]
    ideal = ceiling_model.ceiling(WORD, 73, 896, 9, 64, grid=GRID, unpaid=2)[1]
    require(abs(float(ideal / base) - 3.77) < 0.005, "the ideal ratio left the published 3.77")
    model = ceiling_model.model(NAIVE, 73, 896, 9, NAIVE_CHARGE, unpaid=2)
    require(model["deficit"] == Fraction(-224, 9), "the naive deficit moved")
    try:
        ceiling_model.ceiling(NAIVE, 73, 896, 9, NAIVE_CHARGE, grid=GRID, unpaid=2)
    except ValueError as error:
        require(str(error) == "relaxation has no positive saving", "the naive screen changed")
    else:
        fail("the naive charge had a positive saving")
    return {
        "line_unpaid": [0],
        "plane_unpaid": [0, 1],
        "dirty_spectator_survives": True,
        "omitted_repair_misses": True,
        "ideal_ceiling": str(ideal),
        "ideal_ratio_rounds_to_published": True,
        "naive_charge": NAIVE_CHARGE,
        "naive_deficit": "-224/9",
        "naive_positive_saving": False,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
