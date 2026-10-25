#!/usr/bin/env python3
"""Checks for the QQ16 quarter-turn and invoice."""

from fractions import Fraction


def main():
    turned = (Fraction(-(-3), 2), Fraction(5, 2))
    assert turned == (Fraction(3, 2), Fraction(5, 2))
    assert 11076 * (4 + 2 + 4) == 110760
    assert 483082 - 110760 == 372322
    assert 528 * 4 == 2112
    assert 712 * 2 + 2 == 1426
    print("PASS_QQ16_OUTPUT_TURN_TEST")


if __name__ == "__main__":
    main()
