#!/usr/bin/env python3
"""A nonzero entry is missing only while its output bit is clear."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p104_missing_pair", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    if not verify.pair_is_missing(0, -4, 0):
        raise SystemExit("a clear bit was kept")
    if verify.pair_is_missing(1, -4, 0) or verify.pair_is_missing(0, 0, 0):
        raise SystemExit("a present bit or a zero entry was reported missing")
    print("PASS_P104_MISSING_PAIR_TESTS groups=1")


if __name__ == "__main__":
    main()
