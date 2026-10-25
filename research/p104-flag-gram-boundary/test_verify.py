#!/usr/bin/env python3
"""The flag-0 dot product, without the channel files."""

import importlib.util
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p104_flag_gram_boundary", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    source = (0, 0, 0, 0, 0, 2, 0, -2)
    target = (1, -1, -1, -1, -1, 1, -1, -1)
    if verify.inner(target, source) != 1 or Fraction(1, 2) != Fraction(verify.inner(target, source), 2):
        raise SystemExit("the flag-0 inner product changed")
    if len(verify.roots()) != 120:
        raise SystemExit("the root list changed size")
    print("PASS_P104_FLAG_GRAM_BOUNDARY_TESTS groups=2")


if __name__ == "__main__":
    main()
