#!/usr/bin/env python3
"""Copying 1 and then adding half of its negative leaves 1/2."""

import importlib.util
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("qq16_adjacent_copy", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    state = [Fraction(0)] * 712
    state[360] = Fraction(1)
    verify.apply(state, ["add", ["L", 356], ["L", 360], 1, 1])
    verify.apply(state, ["add", ["L", 360], ["L", 356], -1, 2])
    if state[356] != 1 or state[360] != Fraction(1, 2):
        raise SystemExit("the adjacent halving moved")
    print("PASS_QQ16_ADJACENT_COPY_TESTS groups=1")


if __name__ == "__main__":
    main()
