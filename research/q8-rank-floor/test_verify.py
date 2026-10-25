#!/usr/bin/env python3
"""The ten-call pair that the rank floor removes."""


def main():
    assert 2 * 10 + 0 >= 6 * 4 - 4
    assert 2 * 10 + 10 >= 6 * 4 - 0
    assert 0 < 4
    print("PASS_Q8_RANK_FLOOR_TEST")


if __name__ == "__main__":
    main()
