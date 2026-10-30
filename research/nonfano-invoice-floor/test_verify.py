#!/usr/bin/env python3
"""Counts for the non-Fano invoice floor."""


def main():
    assert (8 - 1) + 4 * (6 - 1) + (6 - 1) == 32
    assert 32 > 30
    assert 6 + 3 * 6 + 3 + 6 == (30 - 3) + 6
    assert 6 + 5 * 3 + 3 + 4 == 30 - 2
    print("PASS_NONFANO_INVOICE_FLOOR_TEST")


if __name__ == "__main__":
    main()
