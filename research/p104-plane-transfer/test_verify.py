#!/usr/bin/env python3
"""A carried signal spreads across one plane and stops at a different plane."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p104_plane_transfer", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    plane = verify.points([1, 2])
    other = verify.points([1, 4])
    bounds = [(plane, plane), (plane, plane), (other, other)]
    adjacency = verify.interval_relation(bounds, 2)
    state = verify.transfer([1, 0, 0], [0, 0, 0], adjacency)
    if state != [1, 1, 0]:
        raise SystemExit("the plane transfer moved")
    print("PASS_P104_PLANE_TRANSFER_TESTS groups=1")


if __name__ == "__main__":
    main()
