#!/usr/bin/env python3
"""Checks for the short scientific count."""

from fractions import Fraction


def main():
    value = Fraction("1e-10000")
    assert len("1e-10000") == 8
    assert value.denominator.bit_length() == 33220
    assert abs(-10000) > 60
    print("PASS_COUNT_EXPONENT_BUDGET_TEST")


if __name__ == "__main__":
    main()
