#!/usr/bin/env python3
"""Counts for the ordinary rate."""

from fractions import Fraction


def main():
    assert Fraction(1, 576) * Fraction(575, 576) == Fraction(575, 331776)
    assert 32780 * 17 * 20 // 16 == 696575
    assert 696575 < (1 << 20)
    print("PASS_ORDINARY_RATE_THRESHOLD_TEST")


if __name__ == "__main__":
    main()
