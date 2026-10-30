#!/usr/bin/env python3
"""The maximum absolute row sum is the larger stored value."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("qq16_endpoint_bound", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    if verify.maximum([{"l1": "47"}, {"l1": "49"}, {"l1": "2"}]) != 49:
        raise SystemExit("the maximum moved")
    print("PASS_QQ16_ENDPOINT_BOUND_TESTS groups=1")


if __name__ == "__main__":
    main()
