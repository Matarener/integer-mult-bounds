#!/usr/bin/env python3
"""The logarithm bound accepts the motif deficit and rejects a one-unit deficit."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("uniform_exponent_bound", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    rank_sum = 177176569088785861287000000
    deficit = 2659138713000000
    if not verify.psi_below_one(deficit, rank_sum, 10**6):
        raise SystemExit("the motif deficit was rejected")
    if verify.psi_below_one(1, rank_sum, 10**6):
        raise SystemExit("a one-unit deficit was accepted")
    print("PASS_UNIFORM_EXPONENT_BOUND_TESTS groups=1")


if __name__ == "__main__":
    main()
