#!/usr/bin/env python3
"""Integer comparisons for the displayed rank deficits."""


def main():
    step = 2 ** 50
    assert 339 * step > 20 * 22587335000000
    assert 73 * step > 20 * 19906842167500
    print("PASS_MANUSCRIPT_EXPONENT_TEST")


if __name__ == "__main__":
    main()
