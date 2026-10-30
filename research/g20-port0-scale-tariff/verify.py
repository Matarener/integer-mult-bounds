#!/usr/bin/env python3
"""Bind one G20 port-0 owner marker to the proved physical scale tariff.

The checker recomputes the rational word, the modular/exact witness, the
histogram gaps and the conditional fibre bill. It does not execute tape
machines or admit a caller invoice.
"""
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PASS = "PASS_G20_PORT0_ENTRY_SCALE_TARIFF_GAP"

UNIT_SCALE = {"2", "1/2", "-1", "-2", "-1/2"}
UNIT_SHEAR = {"1", "-1"}
CONTRACTS = {
    "research/signed-dyadic-scaling/PROOF.md": (
        "(p,a*x modQ,z)",
        "a in {2,1/2,-1,-2,-1/2}",
    ),
    "research/signed-dyadic-scaling/README.md": (
        "2048V transitions and64V visited cells",
    ),
    "research/fixed-tape-ordered-shear/README.md": (
        "(y+x) mod Q",
        "at most 442V",
    ),
    "research/fixed-tape-affine-shear/README.md": (
        "y+c*x+C mod Q",
        "0<=c,C<Q",
        "1024V transitions and 64V visited cells",
    ),
}


def fail(message):
    raise SystemExit("FAIL: " + message)


def load_frozen():
    return json.loads((PACKAGE / "FROZEN.json").read_text(encoding="utf-8"))


def word_sha(operations):
    raw = json.dumps(operations, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def right_product(operations):
    matrix = [[Fraction(int(i == j)) for j in range(8)] for i in range(8)]
    for op in operations:
        if op[0] == "SCALE":
            _, index, unit = op
            unit = Fraction(unit)
            for row in matrix:
                row[index] *= unit
        elif op[0] == "ADD":
            _, source, target, coefficient = op
            coefficient = Fraction(coefficient)
            for row in matrix:
                row[target] += coefficient * row[source]
        else:
            fail("unknown operation " + repr(op))
    return matrix


def is_identity(matrix):
    return all(matrix[row][col] == int(row == col) for row in range(8) for col in range(8))


def is_scalar(matrix, value):
    return all(matrix[row][col] == (value if row == col else 0) for row in range(8) for col in range(8))


def histogram_total(histogram, kind):
    return sum(histogram[kind].values())


def classify(histogram):
    scale = histogram["SCALE"]
    add = histogram["ADD"]
    scale_outside = {key: count for key, count in scale.items() if key not in UNIT_SCALE}
    add_outside_shear = {key: count for key, count in add.items() if key not in UNIT_SHEAR}
    add_nonintegral = {key: count for key, count in add.items() if "/" in key}
    return {
        "scale_factor_total": histogram_total(histogram, "SCALE"),
        "add_factor_total": histogram_total(histogram, "ADD"),
        "scale_outside_unit_scale": scale_outside,
        "scale_outside_unit_scale_total": sum(scale_outside.values()),
        "add_outside_unit_shear": add_outside_shear,
        "add_outside_unit_shear_total": sum(add_outside_shear.values()),
        "add_nonintegral": add_nonintegral,
        "add_nonintegral_total": sum(add_nonintegral.values()),
    }


def conditional_bill(factor_count):
    """One named cover-kernel call per factor, row and lane, times 2048V."""
    per_call_transitions = 2048
    rows = 127
    transition_coefficient = factor_count * rows * per_call_transitions
    return {
        "hypothesis": (
            "Each named cover-kernel call is one in-place unit_scale fibre "
            "of volume V=PQS, executed sequentially. This presentation is not "
            "supplied by the marker."
        ),
        "factor_count": factor_count,
        "rows_times_lanes": "127*f^2",
        "transitions_per_fibre": per_call_transitions,
        "visited_cells_per_fibre": 64,
        "transition_coefficient_times_f_squared_V": transition_coefficient,
        "sequential_visited_cells": "64V",
        "invoice": False,
    }


def witness():
    modulus = 5
    entry = 3
    exact_double = 2 * entry
    modular_double = exact_double % modulus
    exact_half = Fraction(1, 2) * entry
    modular_half = (pow(2, -1, modulus) * entry) % modulus
    if modular_double == exact_double or modular_half == exact_half:
        fail("modular and exact images unexpectedly agree")
    return {
        "modulus": modulus,
        "input": entry,
        "exact_double": exact_double,
        "modular_double": modular_double,
        "exact_half": str(exact_half),
        "modular_half": modular_half,
    }


def check_contracts():
    for relative, needles in CONTRACTS.items():
        text = (ROOT / relative).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                fail("missing contract sentence in " + relative + ": " + needle)


def evaluate(frozen):
    entry = frozen["entry"]
    twin = frozen["return_twin"]
    if word_sha(entry["operations"]) != entry["word_sha256"]:
        fail("entry word hash")
    if word_sha(twin["operations"]) != twin["word_sha256"]:
        fail("return word hash")
    if entry["operations"] != [["SCALE", index, "1/2"] for index in range(7, -1, -1)]:
        fail("entry word is not eight half-scales")
    if twin["operations"] != [["SCALE", index, "2"] for index in range(8)]:
        fail("return word is not eight doublings")
    entry_matrix = right_product(entry["operations"])
    return_matrix = right_product(twin["operations"])
    if not is_scalar(entry_matrix, Fraction(1, 2)):
        fail("entry product")
    if not is_scalar(return_matrix, 2):
        fail("return product")
    if not is_identity(right_product(entry["operations"] + twin["operations"])):
        fail("entry then return does not restore the cover")
    if not is_identity(right_product(twin["operations"] + entry["operations"])):
        fail("return then entry does not restore the cover")
    factors = frozen["marker_count_factors"]
    if factors[0] * factors[1] * factors[2] * factors[3] != frozen["marker_count"]:
        fail("marker count")
    if frozen["marker_count"] != 7548:
        fail("expected 7548 markers")
    if "not the retained literal physical head map" not in frozen["ambient_layout_note"]:
        fail("layout note")
    if "half*N^2+row*N+active[i]*f+lane" not in frozen["ordered_shift_address"]:
        fail("address formula")
    classes = classify(frozen["marker_factor_histogram"])
    published = frozen["published_selected_operation_totals"]
    if classes["add_factor_total"] != published["ADD"] or classes["scale_factor_total"] != published["SCALE"]:
        fail("histogram does not match the published selected-word totals")
    if classes["scale_outside_unit_scale_total"] == 0 or classes["add_nonintegral_total"] == 0:
        fail("family gap disappeared")
    entry_coefficients = {op[2] for op in entry["operations"]}
    if not entry_coefficients <= UNIT_SCALE:
        fail("entry marker left the proved unit_scale set")
    bill = conditional_bill(len(entry["operations"]))
    if bill["transition_coefficient_times_f_squared_V"] != 2080768:
        fail("conditional coefficient")
    check_contracts()
    return {
        "schema_version": 1,
        "status": PASS,
        "marker": {
            "event_index": entry["event_index"],
            "call_index": entry["call_index"],
            "stage": entry["stage"],
            "owner": entry["owner"],
            "owner_bank": entry["owner_bank"],
            "port": entry["port"],
            "phase": entry["phase"],
            "direction": entry["direction"],
            "word_sha256": entry["word_sha256"],
            "factor_count": len(entry["operations"]),
            "coefficient": "1/2",
        },
        "return_twin_event_index": twin["event_index"],
        "rational_restoration": "entry then return and return then entry are the identity on Q^8",
        "modular_exact_witness": witness(),
        "conditional_unit_scale_bill": bill,
        "family_histogram": classes,
        "unpriced_presentation": [
            "literal physical head map",
            "cache COPY/CLEAR",
            "carry",
            "low-type commit",
            "padding",
            "tape movement",
            "descriptor P,Q,S production",
        ],
        "kappa": None,
        "source_result_sha256": frozen["route_binding_result_sha256"],
        "source_words_sha256": frozen["route_binding_words_sha256"],
    }


def controls(frozen):
    broken_hash = json.loads(json.dumps(frozen))
    broken_hash["entry"]["word_sha256"] = "0" * 64
    try:
        evaluate(broken_hash)
    except SystemExit as exc:
        if not str(exc).startswith("FAIL: entry word hash"):
            fail("hash control raised " + str(exc))
    else:
        fail("hash control accepted a bad digest")

    outside = json.loads(json.dumps(frozen))
    outside["entry"]["operations"][0][2] = "1/4"
    outside["entry"]["word_sha256"] = word_sha(outside["entry"]["operations"])
    try:
        evaluate(outside)
    except SystemExit as exc:
        if "eight half-scales" not in str(exc):
            fail("quarter control raised " + str(exc))
    else:
        fail("quarter control accepted a 1/4 scale")

    short = json.loads(json.dumps(frozen))
    short["marker_factor_histogram"]["ADD"] = {"1": 1, "-1": 1}
    short["marker_factor_histogram"]["SCALE"] = {"1/2": 1}
    short["published_selected_operation_totals"] = {"ADD": 2, "SCALE": 1}
    try:
        evaluate(short)
    except SystemExit as exc:
        if "family gap" not in str(exc):
            fail("gap control raised " + str(exc))
    else:
        fail("gap control accepted a fully covered histogram")


def main():
    frozen = load_frozen()
    receipt = evaluate(frozen)
    controls(frozen)
    encoded = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if "--emit" in sys.argv:
        sys.stdout.write(encoded)
        return
    saved = (PACKAGE / "RESULT.json").read_text(encoding="utf-8")
    if saved != encoded:
        fail("RESULT.json does not match the recomputed receipt")
    print(PASS)


if __name__ == "__main__":
    main()
