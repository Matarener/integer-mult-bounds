#!/usr/bin/env python3
"""Arithmetic checks for the row-ledger terms."""

from fractions import Fraction


def main():
    assert 367 * 27 == 9909
    assert 9 * 28 == 252
    assert 2 * 512 == 1024
    assert 2 * 2642 + 9909 + 252 + 1024 == 16469
    assert 2 * (64 * 64 + 1) + 9909 + 252 == 18355
    assert 10**6 - Fraction(51, 25) * 20161 == Fraction(23971789, 25)
    assert Fraction("12556.14") - Fraction("4362.14") == 8194
    print("PASS_STOCK_RHO_LEDGER_TEST")


if __name__ == "__main__":
    main()
