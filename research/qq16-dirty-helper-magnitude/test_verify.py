#!/usr/bin/env python3
"""Four times the unit times T is the completed defect."""

import importlib.util
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("qq16_dirty_helper_magnitude", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    unit = "1/4"
    if verify.completed(unit, 0) != Fraction(1):
        raise SystemExit("the unit case moved")
    if verify.completed(unit, 3) != Fraction(8):
        raise SystemExit("the scaled case moved")
    print("PASS_QQ16_DIRTY_HELPER_MAGNITUDE_TESTS groups=1")


if __name__ == "__main__":
    main()
