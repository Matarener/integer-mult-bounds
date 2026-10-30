#!/usr/bin/env python3
"""Failure controls for the shear recurrence inequality."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("shear_recurrence", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main() -> None:
    receipt = verify.run_checks()
    if receipt["strict_supplier_inequality"] is not False or receipt["length_B"] != 4:
        raise SystemExit("the faithful bill was reported as a strict supplier pass")
    if verify.forms_obey(1):
        raise SystemExit("control: l1 factor 1 must reject a two-entry shear")
    base = verify.b_matrix()
    if verify.shortest_word_length(base, 3) is not None:
        raise SystemExit("control: length 3 must not reach B")
    if verify.moment_clears_one(4) == "below":
        raise SystemExit("control: four rank-1 letters must not satisfy M<1")
    if verify.moment_clears_one(5) != "above":
        raise SystemExit("control: five letters must lie strictly above 1")
    # A length-4 word cannot be B^2: its (1,1) entry is already 29 > 16.
    values = verify.diagonal_entries(2)
    if not values[2] > 2 ** 4:
        raise SystemExit("control: B^2 no longer rules out length 4")
    # A spectator write is a different endpoint: Y^2 does not fix Y.
    if verify.matmul(verify.Y, verify.Y) == verify.Y:
        raise SystemExit("control: a written spectator collapsed")
    got_first, got_second = verify.diagonal_endpoint(verify.X, verify.Y)
    if got_second != verify.Y or got_first != verify.matmul(base, verify.X):
        raise SystemExit("control: diagonal endpoint drifted")
    print("PASS_SL2Z_SHEAR_RECURRENCE_TESTS groups=6")


if __name__ == "__main__":
    main()
