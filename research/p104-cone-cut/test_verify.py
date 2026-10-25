#!/usr/bin/env python3
"""One expansion step adds the neighbors and leaves a disjoint edge out."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p104_cone_cut", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    adjacency = [0b011, 0b011, 0b100]
    backward = verify.expand(0b001, adjacency)
    forward = 0b100
    if backward != 0b011 or (forward & backward) != 0:
        raise SystemExit("the cone expansion moved")
    print("PASS_P104_CONE_CUT_TESTS groups=1")


if __name__ == "__main__":
    main()
