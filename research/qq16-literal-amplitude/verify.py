#!/usr/bin/env python3
"""Read the initial amplitude assigned to register 359.

The literal path stores the scalar 256 and scales the constant vector by it.
The 26,099 events are not replayed.
"""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
NATIVE = ROOT / "research/qq16-native-dirty-fault/native.py"
CHECKER = ROOT / "research/qq16-native-dirty-fault/verify.py"
RECEIPT = ROOT / "research/qq16-native-dirty-fault/RESULT.json"
MARKER = "PASS_QQ16_LITERAL_AMPLITUDE first=256 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_QQ16_LITERAL_AMPLITUDE " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def first_amplitude(numerator, denominator):
    """First component of the constant vector scaled by a dyadic."""
    require(denominator > 0 and denominator & (denominator - 1) == 0, "dyadic coefficient")
    real, imag = numerator, 0
    exponent = denominator.bit_length() - 1
    while exponent and real % 2 == 0 and imag % 2 == 0:
        real //= 2
        imag //= 2
        exponent -= 1
    return real, imag, exponent


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "research/qq16-native-dirty-fault/native.py",
        "research/qq16-native-dirty-fault/verify.py",
        "research/qq16-native-dirty-fault/RESULT.json",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def evaluate():
    authenticate()
    formula = NATIVE.read_text(encoding="utf-8")
    checker = CHECKER.read_text(encoding="utf-8")
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    require("ONE = ((1,) * DIM, (0,) * DIM, 0)" in formula, "the constant vector moved")
    require("while exponent and all(x % 2 == 0 for x in real + imag):" in formula, "the dyadic reduction moved")
    require("return vector((n*x for x in value[0]), (n*x for x in value[1]),\n                  value[2] + d.bit_length()-1)" in formula, "the scaling formula moved")
    require("initial[112], initial[359] = Q(1), Q(256)" in checker, "the initial scalar moved")
    require("state = [N.scaled(N.ONE, x) for x in initial]" in checker, "the initial expansion moved")
    literal = receipt["literal_check"]
    require(literal["T"] == "256", "the stored scalar moved")
    require(set(literal) == {"T", "u", "eta", "max_data_error", "coordinates"}, "the receipt gained an amplitude")
    real, imag, exponent = first_amplitude(256, 1)
    return {
        "register": 359,
        "scalar": "256",
        "first_real": real,
        "first_imag": imag,
        "exponent": exponent,
        "amplitude_stored": False,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
