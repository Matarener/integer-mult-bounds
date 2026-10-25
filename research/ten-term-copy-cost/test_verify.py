#!/usr/bin/env python3
"""Root counts and the ten-term bound."""

from math import comb


def main():
    assert comb(9, 2) + comb(9, 3) == 120
    assert comb(8, 2) * 2 + 2 ** 7 // 2 == 120
    assert 9 * (10 - 1 - 1) == 72
    print("PASS_TEN_TERM_COPY_COST_TEST")


if __name__ == "__main__":
    main()
