#!/usr/bin/env python3
"""Arithmetic checks for the H6 sector dimensions."""


def main():
    ranks = (1, 8, 35, 112, 84)
    pairs = ((1, 0), (3, 0), (1, 2), (3, 2), (1, 4), (3, 4))
    dimensions = tuple(2 * ranks[left] * ranks[right] for left, right in pairs)
    assert sum(ranks) == 240
    assert dimensions == (16, 224, 560, 7840, 1344, 18816)
    assert sum(dimensions) == 28800
    assert sum(dimensions[:3]) == 800
    assert 17 * 9424 == 160208 and 17 * 20400 == 346800
    print("PASS_H6_SECTOR_DIMENSIONS_TEST")


if __name__ == "__main__":
    main()
