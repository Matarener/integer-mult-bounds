#!/usr/bin/env python3
"""A climb's old frame is not its destination."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("qq16_prefix_writes", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    addition = ["scalar", ["add", ["L", 359], ["L", 103], -1, 128], 1]
    if verify.destination(addition) != (359, "add"):
        raise SystemExit("the addition destination moved")
    fault = ["scalar", ["add", ["L", 39], ["L", 359], 4, 1], 1]
    if verify.destination(fault)[0] == 359:
        raise SystemExit("the fault source was counted as a write")
    climb = ["climb", "A", 99, 359, 368, 1]
    if verify.destination(climb) != (99, "climb"):
        raise SystemExit("the climb frame was counted as a register")
    print("PASS_QQ16_PREFIX_WRITES_TESTS groups=1")


if __name__ == "__main__":
    main()
