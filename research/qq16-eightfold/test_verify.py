#!/usr/bin/env python3
"""Eight times -8 contributes -64."""

import importlib.util
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("qq16_eightfold", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    state = [Fraction(0)] * 712
    state[343] = Fraction(-8)
    verify.apply(state, ["add", ["L", 103], ["L", 343], 8, 1])
    if state[103] != -64:
        raise SystemExit("the first sixty-four moved")
    print("PASS_QQ16_EIGHTFOLD_TESTS groups=1")


if __name__ == "__main__":
    main()
