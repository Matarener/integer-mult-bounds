#!/usr/bin/env python3
"""Counts for the T360 role gap."""


def main():
    assert 488 * 9 * 408 == 1791936
    assert 360 * 9 * 408 == 1321920
    assert 1791936 - 1321920 == 470016
    assert 437757 - 323069 == 114688
    print("PASS_T360_ROLE_GAP_TEST")


if __name__ == "__main__":
    main()
