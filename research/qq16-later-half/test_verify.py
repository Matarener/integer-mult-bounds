#!/usr/bin/env python3
"""Minus one half of 1 takes 1 to 1/2."""

import importlib.util
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("qq16_later_half", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    state = [Fraction(0)] * 712
    state[356] = Fraction(1)
    state[292] = Fraction(1)
    verify.apply(state, ["add", ["L", 356], ["L", 292], -1, 2])
    if state[356] != Fraction(1, 2):
        raise SystemExit("the later half moved")
    print("PASS_QQ16_LATER_HALF_TESTS groups=1")


if __name__ == "__main__":
    main()
