#!/usr/bin/env python3
"""A contained copy keeps the subspace rank, and an outside bit does not."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("copied_total_rank", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    image = verify.contained_copy([1, 1, 0], [1, 0, 0])
    if image != [0, 1, 0]:
        raise SystemExit("the contained rank moved")
    try:
        verify.contained_copy([1, 0], [1, 1])
    except SystemExit:
        print("PASS_COPIED_TOTAL_RANK_TESTS groups=1")
        return
    raise SystemExit("an uncontained pair was accepted")


if __name__ == "__main__":
    main()
