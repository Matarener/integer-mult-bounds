#!/usr/bin/env python3
"""Arithmetic of the six-label floor."""


def main():
    subspaces = 1 + 15 + 35 + 15 + 1
    assert subspaces == 67
    assert subspaces ** 3 == 300763
    assert 3 + 3 == 6
    assert 6 + 6 == 12
    assert 3 * 3 == 9
    print("PASS_SIX_LABEL_CENTRAL_FLOOR_TEST")


if __name__ == "__main__":
    main()
