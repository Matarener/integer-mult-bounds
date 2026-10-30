#!/usr/bin/env python3
"""One half times -1 contributes -1/2."""

import importlib.util
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("qq16_final_part", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    state = [Fraction(0)] * 712
    state[354] = Fraction(-1, 2)
    state[258] = Fraction(-1)
    verify.apply(state, ["add", ["L", 354], ["L", 258], 1, 2])
    if state[354] != -1:
        raise SystemExit("the final contribution moved")
    print("PASS_QQ16_FINAL_PART_TESTS groups=1")


if __name__ == "__main__":
    main()
