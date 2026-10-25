#!/usr/bin/env python3
"""Mass checks for the four-end histogram."""

from fractions import Fraction


def main():
    assert 2400 + 2 * 446 + 3 * 416 + 4 * 142 + 5 * 82 + 8 * 8 == 5582
    assert 7232 - 5582 == 1650
    assert Fraction(1690198050302, 10**15) < Fraction(1690198050303, 10**15)
    assert Fraction(1690198051, 1000000000000) / Fraction(169005411, 100000000000) - 1 < Fraction(852, 10000000)
    print("PASS_K8_FOUR_END_CEILING_TEST")


if __name__ == "__main__":
    main()
