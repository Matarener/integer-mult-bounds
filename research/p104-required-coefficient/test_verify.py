#!/usr/bin/env python3
"""Equal frames are a direct contact, and -4/8 is -1/2."""

import importlib.util
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p104_required_coefficient", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    one = verify.points([1])
    extended = verify.points([1, 2])
    if verify.shared([one], [one]) != 1 or verify.shared([one], [extended]) != 0:
        raise SystemExit("the direct contact moved")
    if Fraction(-4, 8) != Fraction(-1, 2):
        raise SystemExit("the coefficient scale moved")
    print("PASS_P104_REQUIRED_COEFFICIENT_TESTS groups=1")


if __name__ == "__main__":
    main()
