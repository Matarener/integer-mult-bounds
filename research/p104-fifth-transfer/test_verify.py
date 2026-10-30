#!/usr/bin/env python3
"""At dimension 5 an arrival intersection of 32 carries the signal and 16 does not."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p104_fifth_transfer", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    wide = frozenset(range(32))
    narrow = frozenset(range(16))
    left = frozenset({0, 1, 2, 3})
    right = frozenset({0, 4, 5, 6})
    bounds = [(left, wide), (right, wide), (right, narrow)]
    at_four = verify.interval_relation(bounds, 4)
    at_five = verify.interval_relation(bounds, 5)
    state = verify.transfer([1, 0, 0], [0, 0, 0], at_five)
    narrow_at_four = (at_four[0] >> 2) & 1
    narrow_at_five = (at_five[0] >> 2) & 1
    if state != [1, 1, 0] or narrow_at_four != 1 or narrow_at_five != 0:
        raise SystemExit("the dimension-5 transfer moved")
    print("PASS_P104_FIFTH_TRANSFER_TESTS groups=1")


if __name__ == "__main__":
    main()
