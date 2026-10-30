#!/usr/bin/env python3
"""The one window addition takes register 39 from -2 to -4."""

import importlib.util
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("qq16_held_four", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    state = [Fraction(0)] * 712
    state[39] = Fraction(-2)
    state[354] = Fraction(-1)
    verify.apply(state, ["add", ["L", 39], ["L", 354], 2, 1])
    if state[39] != -4 or state[354] != -1:
        raise SystemExit("the window addition moved")
    print("PASS_QQ16_HELD_FOUR_TESTS groups=1")


if __name__ == "__main__":
    main()
