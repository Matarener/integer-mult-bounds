#!/usr/bin/env python3
"""Opt-in supplier/assembly saving equality check, not a certificate verifier."""

import argparse
from fractions import Fraction
import json
from pathlib import Path


def check_bindings(data):
    for supplier in ("bit", "complex"):
        saving = Fraction(data[supplier]["saving"])
        parameter = "a_" + supplier
        consumed = Fraction(data["assembly"]["parameters"][parameter])
        if saving != consumed:
            raise ValueError(f"{supplier}.saving does not match assembly.parameters.{parameter}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", type=Path)
    args = parser.parse_args()
    try:
        check_bindings(json.loads(args.certificate.read_bytes()))
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
        parser.exit(1, f"FAIL_SUPPLIER_SAVING_BINDING: {exc}\n")
    print("PASS_SUPPLIER_SAVING_BINDING_ONLY")


if __name__ == "__main__":
    main()
