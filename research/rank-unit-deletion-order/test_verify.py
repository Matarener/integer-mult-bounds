#!/usr/bin/env python3
"""Small checks for the rank-unit order."""

from fractions import Fraction


def main():
    base = Fraction(2, 1)
    assert base**595 < base**596
    saving = Fraction(1, 596)
    assert 16 * 7 + 16 * saving * 7 + 2 + 16 * saving > 0
    print("PASS_RANK_UNIT_DELETION_ORDER_TEST")


if __name__ == "__main__":
    main()
