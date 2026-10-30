#!/usr/bin/env python3
"""Compare the four stored L359 scalars with the F0 output tolerance.

The fault checker writes one rational into register 359. This package reads
that source and its receipt. It does not replay the 26,099-event word.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
FAULT = ROOT / "research/qq16-producer-dirty-fault"
TRANSFER = ROOT / "research/qq16-producer-defect-transfer/README.md"
MARKER = "PASS_QQ16_L359_SCALAR meets=1 no_new_kappa"
EXPONENTS = (0, 8, 64, 256)
BETA = 64


def fail(message):
    raise SystemExit("FAIL_QQ16_L359_SCALAR " + message)


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
        "research/qq16-producer-dirty-fault/verify.py",
        "research/qq16-producer-dirty-fault/RESULT.json",
        "research/qq16-producer-defect-transfer/README.md",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def completed_defect(exponent):
    return 4 * Fraction(1, 2**80) * 2**exponent


def meets_tolerance(exponent):
    return completed_defect(exponent) <= Fraction(1, 2**(BETA + 8))


def scalar_entry(entry):
    require(type(entry) is list and len(entry) == 2, "a response entry is not a pair")
    require(type(entry[0]) is int and type(entry[1]) is str, "a response entry is not a register scalar")
    Fraction(entry[1])


def evaluate():
    authenticate()
    source = (FAULT / "verify.py").read_text(encoding="utf-8")
    receipt = json.loads((FAULT / "RESULT.json").read_text(encoding="utf-8"))
    transfer = TRANSFER.read_text(encoding="utf-8")
    require("WIDTH = 712" in source, "the state width moved")
    require("value = [Q(0)] * WIDTH" in source, "the unit state moved")
    require("initial[359] = magnitude" in source, "the L359 assignment moved")
    require("for exponent in (0, 8, 64, 256):" in source, "the stored exponents moved")
    require("magnitude, u = Q(2**exponent), Q(1, 2**80)" in source, "the magnitude formula moved")
    require("epsF <= H 2^(-beta-8)" in transfer, "the F0 tolerance moved")
    require("not producer-interior range certificates" in transfer, "the endpoint limit moved")
    require(receipt["dirty_input"] == 359 and receipt["completed_defect_formula"] == "4*u*T", "the receipt target moved")
    cases = receipt["cases"]
    require([case["dirty_power_of_two"] for case in cases] == list(EXPONENTS), "the case order moved")
    meets = []
    for case in cases:
        exponent = case["dirty_power_of_two"]
        require(Fraction(case["u"]) == Fraction(1, 2**80), "the relative unit moved")
        require(Fraction(case["completed_data_defect"]) == completed_defect(exponent), "a stored defect left 4*u*T")
        meets.append(meets_tolerance(exponent))
    for entry in receipt["unit_fault_final_response"]:
        scalar_entry(entry)
    require(meets == [True, False, False, False], "the tolerance comparison moved")
    return {
        "register": 359,
        "width": 712,
        "exponents": list(EXPONENTS),
        "beta": BETA,
        "tolerance": str(Fraction(1, 2**(BETA + 8))),
        "meets_tolerance": meets,
        "meeting_count": 1,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
