#!/usr/bin/env python3
"""Counts for the product exponent."""

from fractions import Fraction


def main():
    assert Fraction(8, 5) - Fraction(997, 1000) == Fraction(603, 1000)
    assert Fraction(603, 1000) < 1 - Fraction(576, 332929)
    assert Fraction(8, 5) - Fraction(1, 40) > 1
    print("PASS_PRODUCT_EXPONENT_GAP_TEST")


if __name__ == "__main__":
    main()
