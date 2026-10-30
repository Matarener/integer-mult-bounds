#!/usr/bin/env python3
"""Fourteen rank-3 children and fourteen rank-5 children weigh the same as twenty-eight rank-4 children."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("r480_leaver_rank_bill", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    if verify.exchange(verify.SELECTED, {1: 2412, 2: 418, 3: 418, 4: 170, 5: 68, 8: 8}) != {3: -14, 4: 28, 5: -14}:
        raise SystemExit("the exchange moved")
    if 14 * (3 + 5) != 28 * 4:
        raise SystemExit("the exchange mass moved")
    print("PASS_R480_LEAVER_RANK_BILL_TESTS groups=1")


if __name__ == "__main__":
    main()
