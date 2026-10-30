#!/usr/bin/env python3
"""Closed forms in the chirp budget."""

from fractions import Fraction


def main():
    assert sum(precision - 2 for precision in range(16, 129)) == 7910
    assert Fraction(8, 5) - Fraction(997, 1000) == Fraction(603, 1000)
    assert 3 * 4 + 2 + 2 * 4 == 22
    print("PASS_CHIRP_BUDGET_CLEARANCE_TEST")


if __name__ == "__main__":
    main()
