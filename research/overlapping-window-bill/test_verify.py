#!/usr/bin/env python3
"""Arithmetic of the six-window gate bill."""


def main():
    readers = 3 + 4 + 3 + 4 + 3 + 4
    assert 2 * readers + 4 * 7 == 70
    assert 2 * readers + 6 * 7 == 84
    assert 2 * readers + 12 * 7 == 126
    assert 84 - 70 == 14
    assert 4 + 1 + 1 == 6
    assert 4 + 9 + 1 == 14
    print("PASS_OVERLAPPING_WINDOW_BILL_TEST")


if __name__ == "__main__":
    main()
