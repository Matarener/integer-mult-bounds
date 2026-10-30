#!/usr/bin/env python3
"""A changed operation reaches the payload, and the private key does not."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("canonical_gauge_field", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    kept = verify.canonical_word({"ops": [[1, 2, 3]], "_gauge_ann": [9]})
    if b"_gauge_ann" in kept:
        raise SystemExit("the private key was serialized")
    other = verify.canonical_word({"ops": [[1, 2, 4]], "_gauge_ann": [9]})
    if kept == other:
        raise SystemExit("the operation change disappeared")
    print("PASS_CANONICAL_GAUGE_FIELD_TESTS groups=1")


if __name__ == "__main__":
    main()
