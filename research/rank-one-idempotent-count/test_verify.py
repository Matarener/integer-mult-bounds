#!/usr/bin/env python3
"""Arithmetic of the three-bit projector count."""


def main():
    assert (8 - 1) * (8 // 2) == 28
    assert (8 - 1) * (8 - 1) == 49
    assert 49 - 28 == 21
    print("PASS_RANK_ONE_IDEMPOTENT_COUNT_TEST")


if __name__ == "__main__":
    main()
