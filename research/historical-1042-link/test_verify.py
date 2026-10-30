#!/usr/bin/env python3
"""The printed #1042 decimal is the checkpoint fraction, not the live one."""

import importlib.util
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("historical_1042_link", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    if Fraction(verify.SHOWN) != Fraction("1672188119205421/1000000000000000000"):
        raise SystemExit("the printed decimal moved")
    section = verify.historical_section(
        "live\n# Historical status through #1042\nbody\n# Historical status through #942\n"
    )
    if section != "# Historical status through #1042\nbody\n":
        raise SystemExit("the section cut moved")
    print("PASS_HISTORICAL_1042_LINK_TESTS groups=1")


if __name__ == "__main__":
    main()
