#!/usr/bin/env python3
"""Counts for the T488 composition profile."""


def main():
    assert 65088 * 488 == 31762944
    assert 488 * 9 == 4392
    assert 896 * 488 == 437248
    assert 4392 * 408 == 1791936
    print("PASS_T488_MOMENT_STRADDLE_TEST")


if __name__ == "__main__":
    main()
