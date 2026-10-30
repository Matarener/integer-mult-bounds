#!/usr/bin/env python3
"""The rank-8 sample span sits inside the full span, and a stale transport fails."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p104_tail_flag0_frames", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    old = verify.span([1, 2, 4])
    full = verify.span([1, 2, 4, 8])
    if not set(old) <= set(full):
        raise SystemExit("a smaller span escaped the full span")
    try:
        verify.walk(
            [["transport", "Y34", [1], [1, 2], 1]],
            {"Y34": [2]},
        )
    except SystemExit as exc:
        if "current frame" not in str(exc):
            raise
    else:
        raise SystemExit("a stale transport was accepted")
    print("PASS_P104_TAIL_FLAG0_FRAMES_TESTS groups=1")


if __name__ == "__main__":
    main()
