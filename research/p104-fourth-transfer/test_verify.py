#!/usr/bin/env python3
"""At dimension 4 a one-point plane intersection carries the signal."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p104_fourth_transfer", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    high = frozenset(range(128))
    wide = frozenset(range(256))
    outside = frozenset(range(128, 256))
    shared = verify.points([1, 2])
    meets = verify.points([1, 4])
    apart = verify.points([8, 16])
    bounds = [(shared, high), (meets, high), (apart, wide), (apart, outside)]
    adjacency = verify.interval_relation(bounds, 4)
    state = verify.transfer([1, 0, 0, 0], [0, 0, 0, 0], adjacency)
    if state != [1, 1, 1, 0]:
        raise SystemExit("the dimension-4 transfer moved")
    print("PASS_P104_FOURTH_TRANSFER_TESTS groups=1")


if __name__ == "__main__":
    main()
