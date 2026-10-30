#!/usr/bin/env python3
"""A scale by -1 flips the coefficient, and an addition uses the source."""

import importlib.util
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("qq16_cut_coefficient", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    state = [Fraction(0)] * 712
    state[359] = Fraction(1)
    verify.apply(state, ["scale", ["L", 359], 1, -1])
    if state[359] != -1:
        raise SystemExit("the sign flip moved")
    state[103] = Fraction(-128)
    verify.apply(state, ["add", ["L", 359], ["L", 103], -1, 128])
    if state[359] != 0:
        raise SystemExit("the restoring addition moved")
    print("PASS_QQ16_CUT_COEFFICIENT_TESTS groups=1")


if __name__ == "__main__":
    main()
