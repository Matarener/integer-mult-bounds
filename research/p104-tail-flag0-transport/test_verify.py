#!/usr/bin/env python3
"""A matching record needs the same compressed columns and rank."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p104_tail_flag0_transport", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    record = {
        "direction": "promote",
        "old_compressed": [1],
        "new_compressed": [1, 2],
        "rank": 1,
        "recipe": {"rank": 1},
    }
    if not verify.matches(record, "promote", [1], [1, 2]):
        raise SystemExit("the matching record was rejected")
    record["rank"] = 2
    if verify.matches(record, "promote", [1], [1, 2]):
        raise SystemExit("a rank-2 record was accepted")
    print("PASS_P104_TAIL_FLAG0_TRANSPORT_TESTS groups=1")


if __name__ == "__main__":
    main()
