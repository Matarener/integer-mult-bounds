#!/usr/bin/env python3
"""At dimension 3 a line intersection carries the signal and a point intersection does not."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p104_third_transfer", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    high = frozenset(range(128))
    wide = frozenset(range(256))
    shared = verify.points([1, 2])
    meets = verify.points([1, 4])
    apart = verify.points([8, 16])
    bounds = [(shared, high), (meets, high), (apart, wide)]
    adjacency = verify.interval_relation(bounds, 3)
    state = verify.transfer([1, 0, 0], [0, 0, 0], adjacency)
    if state != [1, 1, 0]:
        raise SystemExit("the dimension-3 transfer moved")
    print("PASS_P104_THIRD_TRANSFER_TESTS groups=1")


if __name__ == "__main__":
    main()
