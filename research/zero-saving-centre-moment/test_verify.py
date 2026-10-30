#!/usr/bin/env python3
"""Closed form of the zero-saving centre moment."""

from fractions import Fraction


def main():
    assert Fraction(112 - Fraction(896, 9), 73 * Fraction(896, 9)) == Fraction(1, 584)
    assert 1 + Fraction(1, 584) == Fraction(585, 584)
    print("PASS_ZERO_SAVING_CENTRE_MOMENT_TEST")


if __name__ == "__main__":
    main()
