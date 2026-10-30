#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent integer-power audit of RESULT.json at saving a = 1/98.

No logarithm, exponential, primary verifier, or predecessor code is imported.
If a = p/q and e = q-p, a grid point L/S is at or below (r/m)^(1-a)
exactly when L^q m^e <= r^e S^q.  Binary search therefore produces
an enclosure using integer comparisons alone.  Nonnegative histogram counts
and positive normalization preserve these bounds on summation.

This also checks the maximal number of extra rank-one children at the target,
with unchanged normalization and no paid-mass credit.  It does not
independently check root brackets, derive histograms, or prove realizability.
Prepared with OpenAI Codex assistance for ToikY; Apache-2.0.
"""

import argparse
import json
from fractions import Fraction
from functools import lru_cache
from pathlib import Path


TARGET = Fraction(1, 98)
PLACES = 18


def require(condition, message):
    if not condition:
        raise ValueError(message)


def positive_int(value):
    return type(value) is int and value > 0


@lru_cache(maxsize=None, typed=True)
def child_cost(rank, width, saving, places=PLACES):
    """Enclose (rank/width)^(1-saving) on a decimal grid, exactly.

    The search invariant is lo^q m^e <= r^e S^q < hi^q m^e.
    Initially lo=0 and hi=S+1, since 0 < r/m <= 1.  At termination
    hi=lo+1; exact equality at lo collapses the enclosure to one point.
    Exact rational endpoint cases avoid unnecessary rounding.
    """
    require(positive_int(rank) and positive_int(width), "positive integer rank/width required")
    require(rank <= width, "rank exceeds width")
    require(type(saving) is Fraction and 0 <= saving <= 1, "saving must be a Fraction in [0, 1]")
    require(positive_int(places), "positive integer decimal precision required")
    if rank == width or saving == 1:
        return Fraction(1), Fraction(1)
    if saving == 0:
        value = Fraction(rank, width)
        return value, value
    power = 1 - saving
    exponent, root = power.numerator, power.denominator
    scale = 10 ** places
    factor = width ** exponent
    right = rank ** exponent * scale ** root
    lo, hi = 0, scale + 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if mid ** root * factor <= right:
            lo = mid
        else:
            hi = mid
    lower = Fraction(lo, scale)
    upper = lower if lo ** root * factor == right else Fraction(hi, scale)
    return lower, upper


def fraction_string(value, label):
    require(type(value) is str, label + " must be a rational string")
    try:
        return Fraction(value)
    except (ValueError, ZeroDivisionError) as error:
        raise ValueError(label + " is not a rational number") from error


def check_document(document):
    """Return independent target enclosures; reject any unproved passing row."""
    require(type(document) is dict, "result must be an object")
    width = document.get("width")
    require(type(width) is int and width == 73, "expected width 73")
    require(fraction_string(document.get("target_a"), "target_a") == TARGET,
            "expected exact target_a = 1/98, corresponding to kappa = 1/99")
    rows = document.get("rows")
    require(type(rows) is list and bool(rows), "nonempty rows required")
    names = set()
    checked = []
    for row in rows:
        require(type(row) is dict, "row must be an object")
        name = row.get("name")
        require(type(name) is str and bool(name) and name not in names, "unique nonempty row name required")
        names.add(name)
        families = row.get("families")
        require(positive_int(families), name + ": positive integer families required")
        histogram = row.get("histogram")
        require(type(histogram) is dict and bool(histogram), name + ": nonempty histogram required")
        lower = upper = Fraction(0)
        for key, count in histogram.items():
            require(type(key) is str and key.isascii() and key.isdigit(), name + ": rank key must be decimal")
            rank = int(key)
            require(str(rank) == key and positive_int(rank), name + ": rank key must be canonical and positive")
            require(2 * rank * rank < width * width, name + ": rank violates the halving guard")
            require(positive_int(count), name + ": count must be a positive integer")
            lo, hi = child_cost(rank, width, TARGET)
            lower += count * lo
            upper += count * hi
        lower /= families
        upper /= families
        reported_lo = fraction_string(row.get("target_moment_lo"), name + ": target_moment_lo")
        reported_hi = fraction_string(row.get("target_moment_hi"), name + ": target_moment_hi")
        require(lower <= reported_lo <= reported_hi <= upper,
                name + ": primary interval is not contained in independent grid enclosure")
        require(reported_hi < 1, name + ": primary interval does not prove target pass")
        require(upper < 1, name + ": independent integer powers do not prove target pass")
        extra = row.get("extra_rank1_children_at_target")
        require(type(extra) is int and extra >= 0, name + ": nonnegative integer extra-child count required")
        one_lo, one_hi = child_cost(1, width, TARGET)
        extra_upper = upper + extra * one_hi / families
        next_lower = lower + (extra + 1) * one_lo / families
        require(extra_upper < 1, name + ": claimed extra-child budget does not pass")
        require(next_lower > 1, name + ": extra-child budget is not proved maximal")
        checked.append({"name": name, "moment_lo": str(lower), "moment_hi": str(upper),
                        "extra_rank1_children_at_target": extra,
                        "with_extra_moment_hi": str(extra_upper),
                        "with_one_more_moment_lo": str(next_lower)})
    return checked


def expect_rejection(callback, label):
    try:
        callback()
    except ValueError:
        return
    raise ValueError("negative control accepted: " + label)


def self_test():
    """Exact calibrations plus malformed-input and false-passing controls."""
    require(child_cost(73, 73, TARGET) == (Fraction(1), Fraction(1)), "unit-ratio calibration")
    require(child_cost(7, 73, Fraction(0)) == (Fraction(7, 73), Fraction(7, 73)), "zero-saving calibration")
    require(child_cost(7, 73, Fraction(1)) == (Fraction(1), Fraction(1)), "unit-saving calibration")
    require(child_cost(9, 25, Fraction(1, 2)) == (Fraction(3, 5), Fraction(3, 5)), "exact-square calibration")
    lo, hi = child_cost(16, 81, Fraction(1, 2))
    require(lo < Fraction(4, 9) < hi and hi - lo == Fraction(1, 10 ** PLACES), "rounded rational-square calibration")
    lo, hi = child_cost(2, 3, Fraction(1, 2))
    require(lo * lo < Fraction(2, 3) < hi * hi, "irrational-square calibration")
    for rank, width, saving in [(0, 73, TARGET), (74, 73, TARGET), (1, 0, TARGET),
                                (True, 73, TARGET), (1, 73, Fraction(-1, 98)),
                                (1, 73, Fraction(99, 98)), (1, 73, 0.5)]:
        expect_rejection(lambda: child_cost(rank, width, saving), "invalid child domain")
    expect_rejection(lambda: child_cost(1, 73, TARGET, 0), "zero precision")
    lo, hi = child_cost(1, 73, TARGET)
    expect_rejection(lambda: child_cost(True, 73, TARGET), "bool rank after integer cache entry")
    fixture = {"width": 73, "target_a": "1/98", "rows": [{
        "name": "positive", "histogram": {"1": 1}, "families": 1,
        "extra_rank1_children_at_target": 68,
        "target_moment_lo": str(lo), "target_moment_hi": str(hi)}]}
    require(len(check_document(fixture)) == 1, "positive document fixture")
    expect_rejection(lambda: check_document({**fixture, "target_a": "1/99"}), "kappa substituted for saving")
    expect_rejection(lambda: check_document({**fixture, "rows": []}), "empty evidence")
    row = fixture["rows"][0]
    for changed in ({"histogram": {"1": -1}}, {"histogram": {"1": True}},
                    {"histogram": {"01": 1}}, {"histogram": {"52": 1}},
                    {"families": 0}, {"target_moment_hi": "2"},
                    {"extra_rank1_children_at_target": -1},
                    {"extra_rank1_children_at_target": True},
                    {"extra_rank1_children_at_target": 67},
                    {"extra_rank1_children_at_target": 69}):
        expect_rejection(lambda: check_document({**fixture, "rows": [{**row, **changed}]}), "invalid row")
    lo, hi = child_cost(51, 73, TARGET)
    failing = {**row, "histogram": {"51": 2},
               "target_moment_lo": str(2 * lo), "target_moment_hi": str(2 * hi)}
    expect_rejection(lambda: check_document({**fixture, "rows": [failing]}), "genuinely failing moment")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result", nargs="?", type=Path, default=Path(__file__).with_name("RESULT.json"))
    parser.add_argument("--self-test", action="store_true", help="run calibrations and negative controls only")
    args = parser.parse_args()
    self_test()
    if args.self_test:
        print("PASS_INDEPENDENT_INTEGER_POWER_CONTROLS")
        return
    result = json.loads(args.result.read_text(encoding="utf-8"))
    checked = check_document(result)
    for row in checked:
        print(json.dumps(row, sort_keys=True))
    print("PASS_INDEPENDENT_INTEGER_POWER_TARGET rows=" + str(len(checked)))


if __name__ == "__main__":
    main()
