#!/usr/bin/env python3
"""Minus one over 128 times -128 restores one."""

import importlib.util
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("qq16_restore_source", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    state = [Fraction(0)] * 712
    state[103] = Fraction(-64)
    state[354] = Fraction(-1)
    verify.apply(state, ["add", ["L", 103], ["L", 354], 64, 1])
    if state[103] != -128:
        raise SystemExit("the second write moved")
    if Fraction(-1, 128) * state[103] != 1:
        raise SystemExit("the restoration product moved")
    print("PASS_QQ16_RESTORE_SOURCE_TESTS groups=1")


if __name__ == "__main__":
    main()
