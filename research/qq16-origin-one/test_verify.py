#!/usr/bin/env python3
"""Minus two scaled by minus one half is one."""

import importlib.util
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("qq16_origin_one", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    state = [Fraction(0)] * 712
    state[359] = Fraction(1)
    verify.apply(state, ["add", ["L", 357], ["L", 359], -2, 1])
    verify.apply(state, ["scale", ["L", 357], 1, -2])
    if state[357] != 1:
        raise SystemExit("the origin scale moved")
    print("PASS_QQ16_ORIGIN_ONE_TESTS groups=1")


if __name__ == "__main__":
    main()
