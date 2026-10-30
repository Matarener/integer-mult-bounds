#!/usr/bin/env python3
"""Minus two times 2 writes -4 into an empty register."""

import importlib.util
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("qq16_shared_four", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    state = [Fraction(0)] * 712
    state[292] = Fraction(2)
    verify.apply(state, ["add", ["L", 18], ["L", 292], -2, 1])
    if state[18] != -4:
        raise SystemExit("the shared four moved")
    print("PASS_QQ16_SHARED_FOUR_TESTS groups=1")


if __name__ == "__main__":
    main()
