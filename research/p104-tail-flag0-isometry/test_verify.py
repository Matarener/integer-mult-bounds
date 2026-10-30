#!/usr/bin/env python3
"""A repeated vector reduces, and the zero vector stays zero."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p104_tail_flag0_isometry", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    if verify.canon([1, 1, 2]) != (2, 1):
        raise SystemExit("the reduced basis moved")
    if verify.convert(0, [1], [1]) != 0:
        raise SystemExit("zero left the origin")
    print("PASS_P104_TAIL_FLAG0_ISOMETRY_TESTS groups=1")


if __name__ == "__main__":
    main()
