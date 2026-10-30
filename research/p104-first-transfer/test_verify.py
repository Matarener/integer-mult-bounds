#!/usr/bin/env python3
"""Equal dimension-1 lines share a read, and a different line does not."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p104_first_transfer", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    line = verify.points([1])
    other = verify.points([2])
    bounds = [(line, line), (line, line), (other, other)]
    adjacency = verify.interval_relation(bounds, 1)
    state = verify.transfer([0, 0, 0], [1, 0, 0], adjacency)
    if state[0] != 1 or state[1] != 1 or state[2] != 0:
        raise SystemExit("the dimension-1 transfer moved")
    print("PASS_P104_FIRST_TRANSFER_TESTS groups=1")


if __name__ == "__main__":
    main()
