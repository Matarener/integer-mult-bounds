#!/usr/bin/env python3
"""The two-call profile keeps four shared copies and half a restoration."""

import importlib.util
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("shared_centre_k2", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    ideal, ideal_centre = verify.profile(2, 0)
    charged, charged_centre = verify.profile(2, 1)
    if ideal[8] != 4 or ideal_centre != 32:
        raise SystemExit("the ideal profile is not four copies at centre 32")
    if charged[8] != Fraction(9, 2) or charged_centre != 36:
        raise SystemExit("the charged profile is not nine halves at centre 36")
    if verify.above_tenth(Fraction(6, 5), 1) is not True:
        raise SystemExit("a tenth of gain was rejected")
    if verify.above_tenth(Fraction(109, 100), 1) is not False:
        raise SystemExit("a gain under a tenth passed")
    print("PASS_SHARED_CENTRE_K2_TESTS groups=1")


if __name__ == "__main__":
    main()
