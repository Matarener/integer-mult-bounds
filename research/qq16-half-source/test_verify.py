#!/usr/bin/env python3
"""Sixty-four times -1 contributes -64."""

import importlib.util
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("qq16_half_source", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    state = [Fraction(0)] * 712
    state[103] = Fraction(-64)
    state[354] = Fraction(-1)
    verify.apply(state, ["add", ["L", 103], ["L", 354], 64, 1])
    if state[103] != -128:
        raise SystemExit("the half contribution moved")
    if Fraction(1, 2) * Fraction(-1) != Fraction(-1, 2):
        raise SystemExit("the preceding half moved")
    print("PASS_QQ16_HALF_SOURCE_TESTS groups=1")


if __name__ == "__main__":
    main()
