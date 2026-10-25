#!/usr/bin/env python3
"""Mutation controls for the two scientific programs.

Each case mutates one parsed parameter and records whether the decision
procedure rejects it.  The decision procedure (verify.compute with
manuscript=False) is separated from the manuscript cross-check, so the
controls exercise the mathematics rather than the displayed comparison.
Explicit raises are used throughout, so the controls stay meaningful under -O.
"""

import copy
import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent

MARKER = "PASS_PARKING_PSI_EXPONENT_THRESHOLD_CONTROLS"


def load(name):
    spec = importlib.util.spec_from_file_location(name, PACKAGE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def outcome(verify, params, manuscript):
    try:
        verify.compute(params, manuscript=manuscript)
    except SystemExit:
        return "rejected"
    return "accepted"


def main():
    verify = load("verify")
    independent = load("independent")

    verify.authenticate()
    base = verify.parse_params()

    # The two parsers must agree on the four published integers.
    parsed = independent.parse()
    if parsed["m"] != base["m"]:
        raise SystemExit("FAIL_CONTROLS modulus disagreement")
    for name, key in (("bit", "b"), ("complex", "c")):
        if parsed["eta"][key] != base["nodes"][name]["eta"]:
            raise SystemExit("FAIL_CONTROLS eta disagreement on " + name)
        if parsed["s"][key] != base["nodes"][name]["s"]:
            raise SystemExit("FAIL_CONTROLS child count disagreement on " + name)

    cases = []

    def case(label, expected, mutate, manuscript=False):
        params = copy.deepcopy(base)
        mutate(params)
        cases.append((label, expected, outcome(verify, params, manuscript)))

    def scale_eta(node, factor):
        def mutate(params):
            params["nodes"][node]["eta"] *= factor
        return mutate

    def set_exponent(value):
        def mutate(params):
            params["exponent"] = value
        return mutate

    case("bit deficit divided by 10^6", "rejected", scale_eta("bit", Fraction(1, 10 ** 6)))
    case("complex deficit divided by 10^6", "rejected", scale_eta("complex", Fraction(1, 10 ** 6)))
    case("bit deficit zeroed", "rejected", scale_eta("bit", Fraction(0)))

    case("exponent one half", "rejected", set_exponent(Fraction(1, 2)))
    case("exponent nine tenths", "rejected", set_exponent(Fraction(9, 10)))
    case("exponent one", "rejected", set_exponent(Fraction(1)))
    case("exponent 1-2^-38", "rejected", set_exponent(1 - Fraction(1, 2 ** 38)))
    case("exponent 1-2^-42 decision", "accepted", set_exponent(1 - Fraction(1, 2 ** 42)))
    case("exponent 1-2^-45 decision", "accepted", set_exponent(1 - Fraction(1, 2 ** 45)))

    def bump_child(params):
        params["nodes"]["bit"]["s"] += 1

    case("bit child count raised by one", "rejected", bump_child)

    def coarse_modulus(params):
        params["m"] = 10 ** 58

    case("modulus raised, decision only", "accepted", coarse_modulus)

    # The displayed comparison is strictly weaker than the exact decision:
    # 1-2^-42 clears Psi < 1 but fails eta > 20*2^-50 on the complex node.
    case("exponent 1-2^-42 under the displayed comparison", "rejected",
         set_exponent(1 - Fraction(1, 2 ** 42)), manuscript=True)

    failures = [(label, expected, actual) for label, expected, actual in cases
                if expected != actual]
    if failures:
        raise SystemExit("FAIL_CONTROLS " + json.dumps(failures))

    print("controls:", len(cases), "cases")
    print(MARKER)


if __name__ == "__main__":
    main()
