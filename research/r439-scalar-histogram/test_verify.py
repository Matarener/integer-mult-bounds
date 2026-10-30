#!/usr/bin/env python3
"""Predicate checks for a shared histogram and distinct ADD counts."""

from verify import adds_differ, rank_mass


def main():
    assert rank_mass({1: 1323, 7: 19}) == 1323 + 133
    assert adds_differ([11783, 11515])
    assert not adds_differ([11500, 11500])
    print("PASS_R439_SCALAR_HISTOGRAM_TEST")


if __name__ == "__main__":
    main()
