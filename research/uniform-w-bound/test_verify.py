#!/usr/bin/env python3
"""One shrinking child under the role count stays below the allowance."""

import importlib.util
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("uniform_w_bound", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    value = verify.normalized(4, (1,), 4, 4, Fraction(1))
    if value != 1:
        raise SystemExit("the one-child recurrence changed")
    if verify.half_psi_square((2, 2, 2, 2), 2) != 2:
        raise SystemExit("the half-width Psi square changed")
    print("PASS_UNIFORM_W_BOUND_TESTS groups=1")


if __name__ == "__main__":
    main()
