#!/usr/bin/env python3
"""Independent check of the (9, 8) failure and the (10, 10) survival."""

from math import ceil, comb


def main():
    budget = comb(9, 2) + comb(8, 2) - 63
    need = ceil((72 - 64) / 2)
    assert budget == 1 and need == 4
    assert budget + 0 < need
    wide = comb(10, 2) + comb(10, 2) - 63
    wide_need = ceil((100 - 64) / 2)
    assert wide == 27 and wide >= wide_need
    print("PASS_SPLIT_BUDGET_SURVIVORS_TEST")


if __name__ == "__main__":
    main()
