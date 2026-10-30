#!/usr/bin/env python3
"""A numeric width bound names a factor; a big-O width does not."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("stock_routing_factor", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    if verify.names_constant_factor("a constant number of old width-$O(w)$ interchanges"):
        raise SystemExit("big-O width was treated as a named factor")
    if not verify.names_constant_factor("routing width at most 4w is too narrow a pattern"):
        if not verify.names_constant_factor("width at most 4 times w"):
            raise SystemExit("an explicit width bound was missed")
    if not verify.names_constant_factor("c_R = 4"):
        raise SystemExit("a named c_R was missed")
    print("PASS_STOCK_ROUTING_FACTOR_TESTS groups=1")


if __name__ == "__main__":
    main()
