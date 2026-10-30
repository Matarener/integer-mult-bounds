#!/usr/bin/env python3
"""Arithmetic of the core section histogram."""


def main():
    assert 1 + 15 + 96 + 15 == 127
    assert 3780 * 1 == 3780
    assert 3780 * 15 == 56700
    assert 3780 * 96 == 362880
    print("PASS_CORE_SECTION_CAPACITY_TEST")


if __name__ == "__main__":
    main()
