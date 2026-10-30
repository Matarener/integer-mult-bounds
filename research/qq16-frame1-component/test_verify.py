#!/usr/bin/env python3
"""Rank 9 takes the constant branch; a shorter independent list does not."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("qq16_frame1_component", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    if not verify.constant_branch((256, 128, 64, 32, 16, 8, 4, 2, 1)):
        raise SystemExit("the full frame left the constant branch")
    if verify.constant_branch((256, 128, 64, 32, 16, 8, 4, 2)):
        raise SystemExit("a rank-8 frame entered the constant branch")
    print("PASS_QQ16_FRAME1_COMPONENT_TESTS groups=1")


if __name__ == "__main__":
    main()
