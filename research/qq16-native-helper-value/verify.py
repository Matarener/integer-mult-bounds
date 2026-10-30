#!/usr/bin/env python3
"""Read the concrete helper value in the native dirty-fault receipt.

The literal check sets T to 256. The stored data error and injection equal
4*u*T and 8*u*T. The 1,004 frame vectors are not reconstructed.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
NATIVE = ROOT / "research/qq16-native-dirty-fault"
MARKER = "PASS_QQ16_NATIVE_HELPER_VALUE T=256 error=1/1024 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_QQ16_NATIVE_HELPER_VALUE " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def scaled(unit, magnitude, factor):
    return factor * Fraction(unit) * Fraction(magnitude)


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "research/qq16-native-dirty-fault/README.md",
        "research/qq16-native-dirty-fault/RESULT.json",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def evaluate():
    authenticate()
    readme = (NATIVE / "README.md").read_text(encoding="utf-8")
    result = json.loads((NATIVE / "RESULT.json").read_text(encoding="utf-8"))
    require("`L359=Tχ`" in readme, "the helper assignment moved")
    require("512-entry constant vector" in readme, "the constant-vector sentence moved")
    require(result["dirty_register"] == 359, "the dirty register moved")
    require(result["fault_index"] == 24438, "the fault index moved")
    require(result["data_error"] == "4*u*T", "the data-error formula moved")
    require(result["local_relative_allowance"] == "8*u*T", "the allowance formula moved")
    literal = result["literal_check"]
    require(literal["T"] == "256", "the literal magnitude moved")
    require(scaled(literal["u"], literal["T"], 4) == Fraction(literal["max_data_error"]), "the data error left 4*u*T")
    require(scaled(literal["u"], literal["T"], 8) == Fraction(literal["eta"]), "the injection left 8*u*T")
    require(result["meaning"] == "permissive completed-ADD fault, not a concrete rounding failure", "the fault meaning moved")
    return {
        "helper": "L359",
        "literal_T": "256",
        "unit": literal["u"],
        "max_data_error": literal["max_data_error"],
        "injection": literal["eta"],
        "vector": "constant payload",
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
