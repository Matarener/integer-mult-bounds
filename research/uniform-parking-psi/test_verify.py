#!/usr/bin/env python3
"""Psi at one half is the role-normalized count divided by the square root."""

import importlib.util
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("uniform_parking_psi", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    below = verify.psi_half(1, 1, 4, 4)
    above = verify.psi_half(1, 2, 1, 4)
    if below != Fraction(1, 8) or above != 1:
        raise SystemExit("the half-exponent evaluation changed")
    print("PASS_UNIFORM_PARKING_PSI_TESTS groups=1")


if __name__ == "__main__":
    main()
