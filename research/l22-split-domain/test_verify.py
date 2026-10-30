#!/usr/bin/env python3
"""Counts for the length-22 split domain."""


def main():
    assert 1 << 6 == 64
    assert 11 * 10 // 2 + 11 * 10 // 2 - 63 == 47
    assert (121 - 64 + 1) // 2 == 29
    assert 11 - 2 == 9
    print("PASS_L22_SPLIT_DOMAIN_TEST")


if __name__ == "__main__":
    main()
