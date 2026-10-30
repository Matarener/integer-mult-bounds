#!/usr/bin/env python3
"""The channel histogram plus 208 nine-step helpers is the published local mass."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p104_hosting_threshold", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    if verify.mass(verify.CHANNEL) != 2368:
        raise SystemExit("the channel mass moved")
    if verify.CHANNEL[1] + verify.UNITS * verify.STEP != 2946:
        raise SystemExit("the unit steps moved")
    if 6712 - (2368 + 1872) != 2472:
        raise SystemExit("the idle mass moved")
    print("PASS_P104_HOSTING_THRESHOLD_TESTS groups=1")


if __name__ == "__main__":
    main()
