#!/usr/bin/env python3
"""Two paying calls clear two labels, and a third label remains."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("line_port_unpaid_cap", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    cleared, dirty = verify.schedule(2, 2)
    blocked, _dirty = verify.schedule(3, 2)
    if cleared != 0 or dirty != [1, 0]:
        raise SystemExit("two labels were not cleared")
    if blocked != 1:
        raise SystemExit("the extra label was cleared")
    print("PASS_LINE_PORT_UNPAID_CAP_TESTS groups=1")


if __name__ == "__main__":
    main()
