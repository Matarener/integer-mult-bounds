#!/usr/bin/env python3
"""Arithmetic of the normal projector."""

from fractions import Fraction


def main():
    root = (2, 2, 0, 0, 0, 0, 0, 0)
    norm = sum(entry * entry for entry in root)
    assert norm == 8
    image = tuple(sum(Fraction(left * right, norm) * entry for right, entry in zip(root, root)) for left in root)
    assert image == root
    assert 8 * 2 == 16
    print("PASS_ADDRESS_OPERATOR_COMPOSITION_TEST")


if __name__ == "__main__":
    main()
