#!/usr/bin/env python3
"""A vector outside the intersection is rejected, and the margin formula changes sign with the count."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("rank7_v45_margin", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    if all(verify.even(1, normal) for normal in verify.NORMALS):
        raise SystemExit("the vector 1 was inside every hyperplane")
    if verify.margin(-2038159, 1, 2091300) >= 0:
        raise SystemExit("the one-helper margin was nonnegative")
    if verify.margin(-8388172, 4, 2091300) <= 0:
        raise SystemExit("the four-helper margin was nonpositive")
    print("PASS_RANK7_V45_MARGIN_TESTS groups=1")


if __name__ == "__main__":
    main()
