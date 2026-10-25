#!/usr/bin/env python3
"""Arithmetic checks for the format widths."""


def main():
    assert 32 * 32 == 1024
    assert 103 * 32 == 3296
    assert 2 * 3296 == 6592
    assert 3296 < 2**12 and 6592 < 2**13
    print("PASS_FORMAT_WIDTH_BOUND_TEST")


if __name__ == "__main__":
    main()
