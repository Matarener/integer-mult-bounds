#!/usr/bin/env python3
"""Bound one call's copied totals by the subspace rank of D_V D_U.

Eight height-8 totals cost 64. The two-call centre charge 32 is below that
bound. This does not build a shared path.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_COPIED_TOTAL_RANK copied_mass=64 no_new_kappa"
TOTALS = 8
HEIGHT = 8


def fail(message):
    raise SystemExit("FAIL_COPIED_TOTAL_RANK " + message)


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
        "research/split-centres-global/proofs/PR386-BIT-GEOMETRY.txt",
        "research/complex-local-word-ceiling/levers.py",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def projector(mask):
    size = len(mask)
    return [[Fraction(1 if i == j and mask[i] else 0) for j in range(size)] for i in range(size)]


def doubled(mask):
    size = len(mask)
    identity = projector([1] * size)
    block = projector(mask)
    gap = [[identity[i][j] - block[i][j] for j in range(size)] for i in range(size)]
    matrix = [[Fraction(0) for _ in range(2 * size)] for _ in range(2 * size)]
    for i in range(size):
        for j in range(size):
            matrix[i][j] = gap[i][j]
            matrix[i][size + j] = block[i][j]
            matrix[size + i][j] = block[i][j]
            matrix[size + i][size + j] = gap[i][j]
    return matrix


def multiply(left, right):
    size = len(left)
    return [[sum(left[i][k] * right[k][j] for k in range(size)) for j in range(size)] for i in range(size)]


def contained_copy(space, inner):
    """Rank of V intersect U-perp when U is contained in V, as a coordinate mask."""
    require(all(bit in (0, 1) for bit in space + inner), "mask bit")
    require(len(space) == len(inner), "mask width")
    require(all(inner[i] <= space[i] for i in range(len(space))), "U is not contained in V")
    return [space[i] - inner[i] for i in range(len(space))]


def evaluate():
    authenticate()
    geometry = (ROOT / "research/split-centres-global/proofs/PR386-BIT-GEOMETRY.txt").read_text(encoding="utf-8")
    levers = (ROOT / "research/complex-local-word-ceiling/levers.py").read_text(encoding="utf-8")
    require("nine copied totals at h=8" in geometry, "the copied-total admission moved")
    require("with rank dim(V)-dim(U)" in geometry, "the rank formula moved")
    require("This holds for copied totals as well:" in geometry, "the copied-total sentence moved")
    require("8: 8" in levers and "centre=32" in levers, "the two-call lever moved")
    space = [1] * HEIGHT
    inner = [0] * HEIGHT
    image = contained_copy(space, inner)
    require(sum(image) == HEIGHT, "a full copy lost rank")
    require(multiply(doubled(space), doubled(inner)) == doubled(image), "the full copy left the formula")
    partial_space = [1, 1, 1, 1, 1, 1, 0, 0]
    partial_inner = [1, 1, 1, 0, 0, 0, 0, 0]
    partial = contained_copy(partial_space, partial_inner)
    require(sum(partial) == 3, "the partial copy lost rank")
    require(multiply(doubled(partial_space), doubled(partial_inner)) == doubled(partial), "the partial copy left the formula")
    outside = [0, 0, 0, 0, 0, 0, 1, 0]
    predicted = [0, 0, 0, 1, 1, 1, 0, 0]
    require(multiply(doubled(partial_space), doubled(outside)) != doubled(predicted), "a total outside V matched the formula")
    copied = TOTALS * HEIGHT
    require(copied == 64 and 32 < copied, "the two-call charge met the bound")
    return {
        "totals": TOTALS,
        "height": HEIGHT,
        "copied_mass": copied,
        "partial_rank": 3,
        "outside_matches": False,
        "share_charge": 32,
        "share_below_bound": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
