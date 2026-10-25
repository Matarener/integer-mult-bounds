#!/usr/bin/env python3
"""A dimension-1 contact requires the size-2 frame to equal the bound."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p104_initial_readers", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    frame = verify.points([1])
    paths = {f"X{index}": [verify.points([index + 1])] for index in range(104)}
    paths["X0"] = [frame, verify.points([1, 2])]
    reads = verify.contacts([(frame, frame)], 1, paths, "X")
    if reads != [1] or (reads[0] & 1) != 1:
        raise SystemExit("the dimension-1 contact moved")
    print("PASS_P104_INITIAL_READERS_TESTS groups=1")


if __name__ == "__main__":
    main()
