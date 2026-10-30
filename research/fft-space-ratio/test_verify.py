#!/usr/bin/env python3
"""Independent packed-record ratio through width 256."""


def ceil_log2(number):
    floor = number.bit_length() - 1
    return floor if (1 << floor) == number else floor + 1


def main():
    equalities = []
    for width in range(3, 257):
        beta = ceil_log2(width)
        digit_count = (width + beta - 1) // beta
        ell = ceil_log2(2 * digit_count)
        ring = 1 << ell
        precision = 2 * beta + ell
        record = ring * (precision + 2)
        assert 7 * record <= 88 * width
        if 7 * record == 88 * width:
            equalities.append(width)
    assert equalities == [7]
    print("PASS_FFT_SPACE_RATIO_TEST")


if __name__ == "__main__":
    main()
