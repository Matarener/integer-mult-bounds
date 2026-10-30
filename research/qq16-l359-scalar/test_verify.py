#!/usr/bin/env python3
"""A power of two meets the tolerance only while the defect stays at most 2^-72."""

import importlib.util
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("qq16_l359_scalar", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    if verify.completed_defect(0) != Fraction(1, 2**78):
        raise SystemExit("the zero-power defect moved")
    if verify.meets_tolerance(0) is not True or verify.meets_tolerance(8) is not False:
        raise SystemExit("the tolerance split moved")
    try:
        verify.scalar_entry([359, ["1", "0"]])
    except SystemExit:
        print("PASS_QQ16_L359_SCALAR_TESTS groups=1")
        return
    raise SystemExit("a nested entry passed as a scalar")


if __name__ == "__main__":
    main()
