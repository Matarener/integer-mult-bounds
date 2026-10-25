#!/usr/bin/env python3
"""Independent budgets at three deviations."""

from math import comb


def main():
    for deviation, even_budget, cross in ((0, 27, 100), (6, 63, 64), (7, 76, 51)):
        left = 10 + deviation
        right = 10 - deviation
        assert comb(left, 2) + comb(right, 2) - 63 == even_budget
        assert left * right == cross
    assert 51 < 64 <= 64
    print("PASS_BIT0_BUDGET_GAP_TEST")


if __name__ == "__main__":
    main()
