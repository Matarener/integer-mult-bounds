#!/usr/bin/env python3
"""The fault addition writes 0, and a later zero source leaves it there."""

import importlib.util
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("qq16_later_zero", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    state = [Fraction(0)] * 712
    state[39] = Fraction(-4)
    state[359] = Fraction(1)
    state[93] = Fraction(0)
    verify.apply(state, ["add", ["L", 39], ["L", 359], 4, 1])
    verify.apply(state, ["add", ["L", 39], ["L", 93], -256, 1])
    if state[39] != 0 or state[359] != 1:
        raise SystemExit("the later value moved")
    print("PASS_QQ16_LATER_ZERO_TESTS groups=1")


if __name__ == "__main__":
    main()
