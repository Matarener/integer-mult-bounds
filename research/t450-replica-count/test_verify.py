#!/usr/bin/env python3
"""Counts for the T450 allocation."""


def main():
    histogram = {1: 9983580, 2: 2940300, 3: 936579, 4: 413100, 5: 87495, 8: 32400, 48: 172221}
    assert 10 * (37 + 8) == 450
    assert 450 * 9 == 4050 and 4050 * 408 == 1652400
    assert sum(histogram.values()) == 14565675
    assert sum(rank * count for rank, count in histogram.items()) == 29289600
    print("PASS_T450_REPLICA_COUNT_TEST")


if __name__ == "__main__":
    main()
