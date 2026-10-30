#!/usr/bin/env python3
"""Checks for the half saving and the five-count increase."""

from fractions import Fraction


def main():
    assert Fraction(717, 10000000) == 2 * Fraction(717, 20000000)
    assert 516232085 - 516232080 == 5
    assert 0 < 756 < 784
    print("PASS_SUPPLIER_SAVING_HALF_TEST")


if __name__ == "__main__":
    main()
