#!/usr/bin/env python3
"""Arithmetic checks for the C5 floors."""

from fractions import Fraction


def main():
    weights = (2, 8, 1, 7, 2, 3, 3, 4, 6)
    assert sum(weights) == 36
    assert Fraction(36, 16) == Fraction(9, 4)
    assert 20 * Fraction(9, 4) == 45
    assert 45 - Fraction(159, 16) == Fraction(561, 16)
    assert Fraction(561, 16) > Fraction(180, 7)
    print("PASS_C5_CANCELLATION_FLOORS_TEST")


if __name__ == "__main__":
    main()
