#!/usr/bin/env python3
"""Counts for the ceiling bracket."""

from fractions import Fraction


def main():
    lower = Fraction(52814190909, 31250000000000)
    upper = Fraction(1690054109089, 1000000000000000)
    assert upper - lower == Fraction(1, 10 ** 15)
    print("PASS_CEILING_BRACKET_GAP_TEST")


if __name__ == "__main__":
    main()
