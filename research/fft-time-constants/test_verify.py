#!/usr/bin/env python3
"""Independent invoice constants through width 256."""


def ceil_log2(number):
    floor = number.bit_length() - 1
    return floor if (1 << floor) == number else floor + 1


def main():
    assert 8 * 2 * 16 == 256
    assert 8 * 64 == 512
    assert 64 == 4 ** 3
    for width in range(3, 257):
        beta = ceil_log2(width)
        digit_count = (width + beta - 1) // beta
        ell = ceil_log2(2 * digit_count)
        ring = 1 << ell
        precision = 2 * beta + ell
        scale = width * beta * beta
        assert ring * beta < 8 * width
        assert ell + 1 <= 2 * beta
        assert precision <= 4 * beta
        assert ring * (ell + 1) * precision * precision <= 256 * scale
        assert ring * precision ** 3 <= 512 * scale
        assert precision ** 3 <= 64 * scale
    print("PASS_FFT_TIME_CONSTANTS_TEST")


if __name__ == "__main__":
    main()
