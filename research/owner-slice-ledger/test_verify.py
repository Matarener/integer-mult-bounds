#!/usr/bin/env python3
"""Capacity arithmetic of the owner bins."""


def main():
    assert 144 * 480 == 69120
    assert 8 * 10752 + 16 * 7168 + 32 * 7168 + 48 * 7168 == 774144
    assert 9 + 4 + 9 + 9 == 31
    print("PASS_OWNER_SLICE_LEDGER_TEST")


if __name__ == "__main__":
    main()
