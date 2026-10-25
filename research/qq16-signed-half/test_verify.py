#!/usr/bin/env python3
"""Coefficient -2 times 1/2 writes -1 into an empty register."""

import importlib.util
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("qq16_signed_half", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    state = [Fraction(0)] * 712
    state[360] = Fraction(1, 2)
    verify.apply(state, ["add", ["L", 262], ["L", 360], -2, 1])
    if state[262] != -1:
        raise SystemExit("the signed product moved")
    print("PASS_QQ16_SIGNED_HALF_TESTS groups=1")


if __name__ == "__main__":
    main()
