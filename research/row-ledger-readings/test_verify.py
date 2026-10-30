#!/usr/bin/env python3
"""Closed forms of the two row readings."""


def main():
    assert 367 * 27 + 9 * 28 + 2 * 512 == 11185
    assert 2 * 2642 + 11185 == 16469
    assert -(-43 * 2642 // 26) + 11185 == 15555
    assert 16469 < 20161
    print("PASS_ROW_LEDGER_READINGS_TEST")


if __name__ == "__main__":
    main()
