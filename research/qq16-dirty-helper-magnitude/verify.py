#!/usr/bin/env python3
"""Read the dirty-helper magnitude in the F0 scalar fault receipt.

The receipt sets L359 = T and checks four powers of two against 4*u*T.
It does not replay the 26,099-event word.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
FAULT = ROOT / "research/qq16-producer-dirty-fault"
MARKER = "PASS_QQ16_DIRTY_HELPER_MAGNITUDE helper=L359 formula=4uT cases=4 no_new_kappa"
FAULT_EVENT = ["scalar", ["add", ["L", 39], ["L", 359], 4, 1], 1]


def fail(message):
    raise SystemExit("FAIL_QQ16_DIRTY_HELPER_MAGNITUDE " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def completed(unit, power):
    return 4 * Fraction(unit) * Fraction(2) ** power


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "research/qq16-producer-dirty-fault/README.md",
        "research/qq16-producer-dirty-fault/RESULT.json",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def evaluate():
    authenticate()
    readme = (FAULT / "README.md").read_text(encoding="utf-8")
    result = json.loads((FAULT / "RESULT.json").read_text(encoding="utf-8"))
    require("dirty helper `L359 = T`" in readme, "the helper assignment moved")
    require("`L39 = -4T`, `L359 = T`" in readme, "the pre-fault state moved")
    require(result["fault_event"] == FAULT_EVENT, "the fault instruction moved")
    require(result["fault_index_zero_based"] == 24438, "the fault index moved")
    require(result["dirty_input"] == 359 and result["data_input"] == 112, "the input registers moved")
    require(result["prefix_dirty_source_coefficient"] == "1", "the helper coefficient moved")
    require(result["prefix_dirty_target_coefficient"] == "-4", "the target coefficient moved")
    require(result["completed_defect_formula"] == "4*u*T", "the defect formula moved")
    require(result["all_480_helpers_exact_after_fault"] is True, "the helper restoration moved")
    for case in result["cases"]:
        require(
            Fraction(case["completed_data_defect"]) == completed(case["u"], case["dirty_power_of_two"]),
            "a stored case left 4*u*T",
        )
    return {
        "helper": "L359",
        "magnitude": "T",
        "target_before_fault": "-4T",
        "fault_index": 24438,
        "formula": "4*u*T",
        "cases_match_formula": len(result["cases"]),
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
