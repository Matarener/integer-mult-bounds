#!/usr/bin/env python3
"""Counts for the Q8 attainment."""


def main():
    assert 5 * 2 < 11 <= 5 * 3
    assert 5 * 4 < 22 <= 5 * 6
    assert 3 * 1 == 3 and 3 * 2 == 6
    print("PASS_Q8_BOUND_ATTAINMENT_TEST")


if __name__ == "__main__":
    main()
