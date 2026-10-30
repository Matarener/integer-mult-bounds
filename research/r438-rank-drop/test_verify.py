#!/usr/bin/env python3
"""Counts for the R438 profile."""


def main():
    histogram = {1: 1298, 2: 1342, 3: 79, 4: 44, 5: 93, 6: 11, 7: 9}
    assert sum(histogram.values()) == 2876
    assert sum(rank * count for rank, count in histogram.items()) == 4989
    assert 9 * 7 + 24 + 9 * 5 == 132
    assert 9 * 8 == 72
    assert 5758 + 5619 + 1499 + 347 == 13223
    print("PASS_R438_RANK_DROP_TEST")


if __name__ == "__main__":
    main()
