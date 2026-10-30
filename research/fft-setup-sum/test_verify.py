#!/usr/bin/env python3
"""Independent setup sum through width 256."""


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
        square = precision * precision
        cube = square * precision
        total = ring * (ell + 1) * square + ring * cube + cube
        scale = width * beta * beta
        assert 7 * total <= 1017 * scale
        if 7 * total == 1017 * scale:
            equalities.append((width, total))
    assert equalities == [(7, 9153)]
    assert 256 + 512 + 64 == 832
    print("PASS_FFT_SETUP_SUM_TEST")


if __name__ == "__main__":
    main()
