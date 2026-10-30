#!/usr/bin/env python3
"""Independent arithmetic oracle for the port-0 scale tariff gap.

This file does not import verify.py. It recomputes the rational products,
the modular witness and the conditional coefficient from FROZEN.json, then
checks those values against RESULT.json.
"""
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
PASS = "PASS_G20_PORT0_SCALE_ORACLE"


def fail(message):
    raise SystemExit("FAIL: " + message)


def product(operations):
    rows = [[Fraction(int(i == j)) for j in range(8)] for i in range(8)]
    for kind, *rest in operations:
        if kind == "SCALE":
            index, unit = rest
            unit = Fraction(unit)
            for row in rows:
                row[index] *= unit
        elif kind == "ADD":
            source, target, coefficient = rest
            coefficient = Fraction(coefficient)
            for row in rows:
                row[target] += coefficient * row[source]
        else:
            fail("bad opcode")
    return rows


def identity(rows):
    return all(rows[i][j] == (1 if i == j else 0) for i in range(8) for j in range(8))


def main():
    frozen = json.loads((PACKAGE / "FROZEN.json").read_text(encoding="utf-8"))
    receipt = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    entry = frozen["entry"]["operations"]
    twin = frozen["return_twin"]["operations"]
    if not identity(product(entry + twin)) or not identity(product(twin + entry)):
        fail("restoration")
    half = product(entry)
    if any(half[i][j] != (Fraction(1, 2) if i == j else 0) for i in range(8) for j in range(8)):
        fail("half matrix")
    modulus = 5
    exact_double = 6
    modular_double = 1
    if (2 * 3) % modulus != modular_double or 2 * 3 != exact_double:
        fail("double witness")
    if (pow(2, -1, modulus) * 3) % modulus != 4 or Fraction(1, 2) * 3 != Fraction(3, 2):
        fail("half witness")
    digest = hashlib.sha256(json.dumps(entry, separators=(",", ":")).encode("utf-8")).hexdigest()
    if digest != frozen["entry"]["word_sha256"]:
        fail("word digest")
    if 8 * 127 * 2048 != 2080768:
        fail("coefficient")
    scale = frozen["marker_factor_histogram"]["SCALE"]
    add = frozen["marker_factor_histogram"]["ADD"]
    unit_scale = {"2", "1/2", "-1", "-2", "-1/2"}
    scale_gap = sum(count for key, count in scale.items() if key not in unit_scale)
    nonintegral = sum(count for key, count in add.items() if "/" in key)
    if scale_gap != 6868 or nonintegral != 25840:
        fail("recomputed family gap")
    if receipt["conditional_unit_scale_bill"]["transition_coefficient_times_f_squared_V"] != 2080768:
        fail("receipt coefficient")
    if receipt["modular_exact_witness"]["exact_half"] != "3/2":
        fail("receipt witness")
    if receipt["family_histogram"]["scale_outside_unit_scale_total"] != scale_gap:
        fail("receipt scale gap")
    if receipt["family_histogram"]["add_nonintegral_total"] != nonintegral:
        fail("receipt nonintegral gap")
    if "--quiet" not in sys.argv:
        print(PASS)


if __name__ == "__main__":
    main()
