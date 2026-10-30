#!/usr/bin/env python3
"""Counts for the T740 histogram."""


def main():
    histogram = {1: 16417896, 2: 4835160, 3: 1540174, 4: 679321, 5: 143992, 6: 3, 8: 53280, 48: 283185}
    assert sum(histogram.values()) == 23953011
    assert sum(rank * count for rank, count in histogram.items()) == 48165120
    assert 740 * 9 == 6660 and 6660 * 408 == 2717280
    print("PASS_T740_HISTOGRAM_MASS_TEST")


if __name__ == "__main__":
    main()
