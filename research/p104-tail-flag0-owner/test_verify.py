#!/usr/bin/env python3
"""A five-field add has no room for an owner."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p104_tail_flag0_owner", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    event = ["add", "Y34", "X0", "-1/2", [1, 2, 4, 8, 16, 32, 64, 128, 256]]
    if len(event) != 5 or "owner" in event:
        raise SystemExit("the sample add carried an owner")
    print("PASS_P104_TAIL_FLAG0_OWNER_TESTS groups=1")


if __name__ == "__main__":
    main()
