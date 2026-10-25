#!/usr/bin/env python3
"""Two times -1/8 contributes -1/4."""

import importlib.util
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("qq16_eighth_value", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    state = [Fraction(0)] * 712
    state[354] = Fraction(-1, 4)
    state[280] = Fraction(-1, 8)
    verify.apply(state, ["add", ["L", 354], ["L", 280], 2, 1])
    if state[354] != Fraction(-1, 2):
        raise SystemExit("the second quarter moved")
    print("PASS_QQ16_EIGHTH_VALUE_TESTS groups=1")


if __name__ == "__main__":
    main()
