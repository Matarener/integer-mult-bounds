#!/usr/bin/env python3
"""One addition chain, without the channel file."""

import importlib.util
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p104_flag_relay", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    program = [
        ["add", "G0", "X0", -2, []],
        ["add", "Q0", "G0", 1, []],
        ["copy", "C", "Q0", []],
        ["add", "D17", "C", 1, []],
        ["add", "Y34", "D17", "-1/4", []],
    ]
    state, _first, arrived = verify.replay(program, ["X0", "G0", "Q0", "C", "D17", "Y34"])
    if state["Y34"]["X0"] != Fraction(1, 2) or arrived[("X0", "Y34")] != 4:
        raise SystemExit("the sample relay changed")
    print("PASS_P104_FLAG_RELAY_TESTS groups=1")


if __name__ == "__main__":
    main()
