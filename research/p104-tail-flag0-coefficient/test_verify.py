#!/usr/bin/env python3
"""The off-diagonal formula is -1/2 and the diagonal formula is 0."""

import importlib.util
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p104_tail_flag0_coefficient", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    if verify.correction(34, 0, 1) != Fraction(-1, 2):
        raise SystemExit("the off-diagonal formula moved")
    if verify.correction(0, 0, 2) != Fraction(0):
        raise SystemExit("the diagonal formula moved")
    print("PASS_P104_TAIL_FLAG0_COEFFICIENT_TESTS groups=1")


if __name__ == "__main__":
    main()
