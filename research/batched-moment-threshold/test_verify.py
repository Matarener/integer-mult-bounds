#!/usr/bin/env python3
"""Controls for the direct batched-moment enclosures.

Three independent checks:

1. High-precision Decimal logarithms (single-operation, so no cancellation)
   agree with the rational enclosures used here.
2. The published savings pass and a saving above each certified sharp
   bracket fails, on both child lists.
3. The binary64 logarithm evaluation agrees with the certified interval on
   both sides and the published sufficient bound, recomputed exactly, is
   below one.

No kappa, supplier or selected-frontier claim.
"""

import importlib.util
import json
from decimal import Decimal, getcontext
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("batched_moment_threshold", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)

MARKER = "PASS_BATCHED_MOMENT_THRESHOLD_TESTS"


def fail(message):
    raise SystemExit("FAIL_BATCHED_MOMENT_THRESHOLD_TESTS " + message)


def require(condition, message):
    if not condition:
        fail(message)


def decimal_log_check(moment):
    getcontext().prec = 120
    for u in moment.inverses:
        low, high = verify.log_rational_bounds(u, 200)
        observed = (Decimal(u.numerator) / Decimal(u.denominator)).ln()
        tolerance = Decimal(10) ** -100
        require(Decimal(low.numerator) / Decimal(low.denominator) - tolerance <= observed,
                "Decimal logarithm below the rational enclosure: " + str(u))
        require(observed <= Decimal(high.numerator) / Decimal(high.denominator) + tolerance,
                "Decimal logarithm above the rational enclosure: " + str(u))


def float_check(moment, saving):
    for a in (Q(0), saving):
        low, high = moment.bounds(a)
        observed = sum(float(w) * float(u) ** float(a)
                       for w, u in zip(moment.weights, moment.inverses))
        require(float(low) - 1e-15 <= observed <= float(high) + 1e-15,
                "binary64 moment outside the certified interval")


def decision_check(moment, saving):
    require(moment.bounds(saving)[1] < 1, "published saving failed a control")
    above = saving + Q(1, 10**7)
    require(moment.bounds(above)[0] > 1, "a saving 1e-7 above the published one still passed")
    low, high = moment.threshold_bracket(top=verify.THRESHOLD_SEARCH_TOP)
    require(low < high, "empty threshold bracket")
    require(moment.bounds(low)[1] < 1, "threshold bracket lower endpoint fails")
    require(moment.bounds(high)[0] > 1, "threshold bracket upper endpoint holds")
    require(saving < low, "published saving is not below the sharp bracket")


def main():
    verify.authenticate()
    bit, bit_cert, _ = verify.bit_moment()
    complex_moment, _ = verify.complex_moment()
    decimal_log_check(bit)
    decimal_log_check(complex_moment)
    float_check(bit, verify.BIT_SAVING)
    float_check(complex_moment, verify.COMPLEX_SAVING)
    decision_check(bit, verify.BIT_SAVING)
    decision_check(complex_moment, verify.COMPLEX_SAVING)
    for moment, cert, saving in ((bit, bit_cert, verify.BIT_SAVING),
                                 (complex_moment, None, verify.COMPLEX_SAVING)):
        if cert is not None:
            bound, _, _ = verify.check_sufficient_route(cert, moment, saving)
            require(bound < 1, "published sufficient bound is not below one")
    stored = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
    require(stored == verify.evaluate(), "RESULT.json moved under the controls")
    print(MARKER + " logs=decimal_checked ranks=" + str(len(bit.weights))
          + "/" + str(len(complex_moment.weights)) + " controls=pass")


if __name__ == "__main__":
    main()
