#!/usr/bin/env python3
"""Shared frames make the literal and interval relations agree on a toy graph."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p104_literal_missing", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    quotients = verify.quotient_subspaces()
    if [len(group) for group in quotients] != [1, 31, 155, 155, 31, 1]:
        raise SystemExit("the quotient census changed")
    same = frozenset({0, 1})
    other = frozenset({0, 2})
    bounds = [(same, same), (same, same), (other, other)]
    literal = verify.literal_relation(bounds, 1, quotients)
    interval = verify.interval_relation(bounds, 1)
    if literal != interval or literal != [0b011, 0b011, 0b100]:
        raise SystemExit("the toy relations disagreed")
    print("PASS_P104_LITERAL_MISSING_TESTS groups=1")


if __name__ == "__main__":
    main()
