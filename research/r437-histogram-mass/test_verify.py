#!/usr/bin/env python3
"""Counts for the R437 histogram."""


def main():
    histogram = {1: 380160, 2: 400864, 3: 22176, 4: 26592, 5: 29376, 6: 17376, 7: 26496, 34: 64, 42: 352}
    assert sum(histogram.values()) == 903456
    assert sum(rank * count for rank, count in histogram.items()) == 1808352
    assert 32 * 3933 == 125856 and 32 * 888 == 28416
    assert FractionCheck()
    print("PASS_R437_HISTOGRAM_MASS_TEST")


def FractionCheck():
    from fractions import Fraction
    coefficient = Fraction(868314126713557740143, 500000000000000000000000)
    return coefficient == Fraction(1736628253427115480286, 10**24)


if __name__ == "__main__":
    main()
