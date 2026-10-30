#!/usr/bin/env python3
"""Coefficient 1 copies -1 into an empty register."""

import importlib.util
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("qq16_whole_source", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    state = [Fraction(0)] * 712
    state[262] = Fraction(-1)
    verify.apply(state, ["add", ["L", 258], ["L", 262], 1, 1])
    if state[258] != -1:
        raise SystemExit("the copied value moved")
    print("PASS_QQ16_WHOLE_SOURCE_TESTS groups=1")


if __name__ == "__main__":
    main()
