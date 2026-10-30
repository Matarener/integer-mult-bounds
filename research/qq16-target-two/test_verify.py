#!/usr/bin/env python3
"""Minus one half of -4 takes -4 to -2."""

import importlib.util
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("qq16_target_two", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    state = [Fraction(0)] * 712
    state[39] = Fraction(-4)
    state[343] = Fraction(-4)
    verify.apply(state, ["add", ["L", 39], ["L", 343], -1, 2])
    if state[39] != -2:
        raise SystemExit("the halving moved")
    print("PASS_QQ16_TARGET_TWO_TESTS groups=1")


if __name__ == "__main__":
    main()
