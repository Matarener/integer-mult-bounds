#!/usr/bin/env python3
"""Arithmetic of the six-owner repair count."""


def main():
    assert 112 - 8 == 104
    assert 3 * 2 + 1 == 7
    assert [104 * block for block in range(1, 7)] == [104, 208, 312, 416, 520, 624]
    print("PASS_SIX_OWNER_REPAIR_COUNT_TEST")


if __name__ == "__main__":
    main()
