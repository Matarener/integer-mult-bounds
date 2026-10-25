#!/usr/bin/env python3
"""Minus two times 1/4 is -1/2, and half of that is -1/4."""

import importlib.util
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("qq16_leading_half", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    state = [Fraction(0)] * 712
    state[360] = Fraction(1, 4)
    verify.apply(state, ["add", ["L", 274], ["L", 360], -2, 1])
    verify.apply(state, ["add", ["L", 280], ["L", 274], 1, 2])
    if state[274] != Fraction(-1, 2) or state[280] != Fraction(-1, 4):
        raise SystemExit("the leading half moved")
    print("PASS_QQ16_LEADING_HALF_TESTS groups=1")


if __name__ == "__main__":
    main()
