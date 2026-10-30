#!/usr/bin/env python3
"""Minus one times 1/2 writes -1/2 into an empty register."""

import importlib.util
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("qq16_negative_half", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    state = [Fraction(0)] * 712
    state[356] = Fraction(1, 2)
    verify.apply(state, ["add", ["L", 295], ["L", 356], -1, 1])
    if state[295] != Fraction(-1, 2):
        raise SystemExit("the negative half moved")
    print("PASS_QQ16_NEGATIVE_HALF_TESTS groups=1")


if __name__ == "__main__":
    main()
