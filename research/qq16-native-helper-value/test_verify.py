#!/usr/bin/env python3
"""Four and eight times the unit times 256 recover the stored fractions."""

import importlib.util
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("qq16_native_helper_value", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    if verify.scaled("1/1048576", "256", 4) != Fraction(1, 1024):
        raise SystemExit("the data error moved")
    if verify.scaled("1/1048576", "256", 8) != Fraction(1, 512):
        raise SystemExit("the injection moved")
    print("PASS_QQ16_NATIVE_HELPER_VALUE_TESTS groups=1")


if __name__ == "__main__":
    main()
