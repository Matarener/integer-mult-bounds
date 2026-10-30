#!/usr/bin/env python3
"""One quarter of -1 takes 1/2 down to 1/4."""

import importlib.util
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("qq16_quarter_value", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    state = [Fraction(0)] * 712
    state[360] = Fraction(1, 2)
    state[262] = Fraction(-1)
    verify.apply(state, ["add", ["L", 360], ["L", 262], 1, 4])
    if state[360] != Fraction(1, 4):
        raise SystemExit("the quartering moved")
    print("PASS_QQ16_QUARTER_VALUE_TESTS groups=1")


if __name__ == "__main__":
    main()
