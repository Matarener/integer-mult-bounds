#!/usr/bin/env python3
"""Arithmetic checks for the odd-pair block."""

from fractions import Fraction


def main():
    assert 8 * 7 == 56
    assert 5586 - 8 == 5578
    assert Fraction(26201033, 21393090) > Fraction(21, 20)
    print("PASS_ODD_PAIR_BLOCK_RANK_TEST")


if __name__ == "__main__":
    main()
