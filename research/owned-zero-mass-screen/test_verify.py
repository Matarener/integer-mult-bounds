#!/usr/bin/env python3
"""Arithmetic of the owned-zero unit bill."""

from fractions import Fraction


def main():
    room = 1818624 - 1342656 - 198912
    assert room == 277056
    assert Fraction(room, 5 * 32) == Fraction(8658, 5)
    assert 5 * 32 * Fraction(8658, 5) + 198912 + 1342656 == 1818624
    print("PASS_OWNED_ZERO_MASS_SCREEN_TEST")


if __name__ == "__main__":
    main()
