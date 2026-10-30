#!/usr/bin/env python3
"""Minus two times -1/2 takes 1 to 2."""

import importlib.util
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("qq16_source_two", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    state = [Fraction(0)] * 712
    state[292] = Fraction(1)
    state[295] = Fraction(-1, 2)
    verify.apply(state, ["add", ["L", 292], ["L", 295], -2, 1])
    if state[292] != 2:
        raise SystemExit("the doubling moved")
    print("PASS_QQ16_SOURCE_TWO_TESTS groups=1")


if __name__ == "__main__":
    main()
