#!/usr/bin/env python3
"""Arithmetic of the FFT parameter bounds."""

from fractions import Fraction


def main():
    assert Fraction(8, 5) - Fraction(1, 500) == Fraction(799, 500)
    assert 1 - Fraction(1, 500) + Fraction(1, 10000) == Fraction(9981, 10000)
    assert Fraction(99827619697, 100000000000) - Fraction(9981, 10000) == Fraction(17619697, 100000000000)
    assert 65535 + 1 == 65536
    print("PASS_FFT_WORD_PARAMETER_BOUNDS_TEST")


if __name__ == "__main__":
    main()
