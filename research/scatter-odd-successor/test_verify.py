#!/usr/bin/env python3
"""An odd count emits one ADD and an even count emits none."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("scatter_odd_successor", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    word = {"v": 1, "R": 0, "ret": [2]}
    once = verify.successor_coefficients(word, [[0]])
    twice = verify.successor_coefficients(word, [[0, 0]])
    thrice = verify.successor_coefficients(word, [[0, 0, 0]])
    if once != [[1]] or twice != [[0]] or thrice != [[1]]:
        raise SystemExit("the odd-multiplicity coefficients changed")
    print("PASS_SCATTER_ODD_SUCCESSOR_TESTS groups=1")


if __name__ == "__main__":
    main()
