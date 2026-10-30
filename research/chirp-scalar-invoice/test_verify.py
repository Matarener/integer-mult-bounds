#!/usr/bin/env python3
"""Independent scalar-word sum for one chirp row."""


def main():
    length = 5
    copies = 3
    precision = 16
    level = length + 1
    kernel = 4 * copies * level
    endpoints = 8 * copies
    twists = 12 * copies
    ring = copies * (12 * level + 8)
    total = kernel + endpoints + twists + ring
    assert total == copies * (16 * level + 28)
    cells = 2 * (precision + 2) * copies
    assert total * (precision + 2) == cells * (8 * level + 14)
    assert 4 + 12 == 16
    assert 8 + 12 + 8 == 28
    print("PASS_CHIRP_SCALAR_INVOICE_TEST")


if __name__ == "__main__":
    main()
