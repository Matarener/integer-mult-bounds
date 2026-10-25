#!/usr/bin/env python3
"""The logarithm bound accepts the complex deficit and rejects a one-unit deficit."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("uniform_complex_exponent", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    rank_sum = 1873807244636671267308000000
    deficit = 6871402692000000
    if not verify.ratio_below_power(deficit, rank_sum, 10**6):
        raise SystemExit("the complex deficit was rejected")
    if verify.ratio_below_power(1, rank_sum, 10**6):
        raise SystemExit("a one-unit deficit was accepted")
    print("PASS_UNIFORM_COMPLEX_EXPONENT_TESTS groups=1")


if __name__ == "__main__":
    main()
