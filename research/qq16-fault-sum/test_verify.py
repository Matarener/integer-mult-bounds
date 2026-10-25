#!/usr/bin/env python3
"""Four times 1 takes -4 to 0."""

import importlib.util
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("qq16_fault_sum", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    state = [Fraction(0)] * 712
    state[39] = Fraction(-4)
    state[359] = Fraction(1)
    verify.apply(state, ["add", ["L", 39], ["L", 359], 4, 1])
    if state[39] != 0 or state[359] != 1:
        raise SystemExit("the fault sum moved")
    print("PASS_QQ16_FAULT_SUM_TESTS groups=1")


if __name__ == "__main__":
    main()
