#!/usr/bin/env python3
"""Arithmetic of the six-call floor."""


def main():
    assert 3 + 3 == 6
    assert 3 + 3 > 5
    assert 1 + 31 + 155 + 155 + 31 + 1 == 374
    assert 1 + 63 + 651 + 1395 + 651 + 63 + 1 == 2825
    print("PASS_CENTRAL_TRIPLE_RANK_FLOOR_TEST")


if __name__ == "__main__":
    main()
