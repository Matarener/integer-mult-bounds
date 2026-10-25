#!/usr/bin/env python3
"""The stock receipt leaves the selected coefficient null.

The checker reads the fourteen stage fields. It does not recompute a cutoff
margin and does not treat 57604 as a selected coefficient.
"""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_STOCK_COEFFICIENT_ABSENT stages=14 coefficient_null=true no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_STOCK_COEFFICIENT_ABSENT " + message)


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
        "research/selected-bootstrap-stock-audit/README.md",
        "research/selected-bootstrap-stock-audit/RESULT.json",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def evaluate():
    authenticate()
    note = (ROOT / "research/selected-bootstrap-stock-audit/README.md").read_text(encoding="utf-8")
    require("The actual\nselected coefficients remain unknown." in note, "the unknown-coefficient sentence moved")
    require("It does not measure or derive sigma." in note, "the sigma sentence moved")
    require(
        "neither `sigma_j=sigma_0+j*57604` nor use of 252 as a selected\nsigma is discharged here." in note,
        "the 57604 sentence moved",
    )
    receipt = json.loads((ROOT / "research/selected-bootstrap-stock-audit/RESULT.json").read_text(encoding="utf-8"))
    boundary = receipt["source_boundary"]
    require(boundary["actual_stage_stock_coefficients"] is None, "the boundary coefficient appeared")
    require(boundary["completed_inner_leaf_external_extra_stock"] == 0, "inner borrowing is not zero")
    require(boundary["selected_additive_57604_recurrence"] == "NOT_ESTABLISHED", "the 57604 recurrence was established")
    require(boundary["historical_candidate"] == {"halving_levels": 4, "m": 120, "new_stock_coefficient": 57604}, "the historical candidate moved")
    require(boundary["selected_candidate"] == {"m": 73}, "the selected candidate gained a coefficient")
    require(boundary["status"] == "NOT_ESTABLISHED", "the boundary status moved")
    stages = []
    for name in ("bootstrap", "conservative_bootstrap"):
        branch = receipt["branches"][name]
        require(len(branch["stages"]) == 7, name + " stage count moved")
        stages.extend(branch["stages"])
    require(len(stages) == 14, "the stage count moved")
    require(all(stage["actual_stock_coefficient"] is None for stage in stages), "a stage coefficient appeared")
    return {
        "stages": 14,
        "coefficient_null": True,
        "inner_borrowing": 0,
        "recurrence_57604": "NOT_ESTABLISHED",
        "selected_width": 73,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
