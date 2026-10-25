#!/usr/bin/env python3
"""The rank-2 frame design meets every frame, and 27 rank-4 terms miss the floor."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("tetrad_effective_rank", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    paired = verify.pair_design()
    if verify.frame_counts(paired) != [4] * 28 or verify.effective(paired) != 2:
        raise SystemExit("the rank-2 design moved")
    if not (27 * 4 < verify.FLOOR == 28 * 4 == 112):
        raise SystemExit("the copy floor moved")
    print("PASS_TETRAD_EFFECTIVE_RANK_TESTS groups=1")


if __name__ == "__main__":
    main()
