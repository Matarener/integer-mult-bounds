#!/usr/bin/env python3
"""Integer 256 stays at exponent 0; an even numerator over 2 reduces."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("qq16_literal_amplitude", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    if verify.first_amplitude(256, 1) != (256, 0, 0):
        raise SystemExit("the initial amplitude moved")
    if verify.first_amplitude(2, 2) != (1, 0, 0):
        raise SystemExit("the dyadic reduction moved")
    print("PASS_QQ16_LITERAL_AMPLITUDE_TESTS groups=1")


if __name__ == "__main__":
    main()
