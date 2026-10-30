#!/usr/bin/env python3
"""Closed forms of the three degree gaps."""

from fractions import Fraction


def main():
    assert Fraction(10 ** 6) - Fraction(51 * 20161, 25) == Fraction(23971789, 25)
    assert 58344 + 9909 + 252 == 68505
    assert Fraction(160000) - Fraction(51 * 68505, 25) == Fraction("20249.8")
    assert Fraction(70000) - Fraction(51 * 20445, 25) == Fraction(141461, 5)
    print("PASS_DEGREE_GAP_CLEARANCE_TEST")


if __name__ == "__main__":
    main()
