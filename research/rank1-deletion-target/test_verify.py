#!/usr/bin/env python3
"""Mass checks for the rank-1 deletion."""


def main():
    assert 5586 - 2412 == 3174
    assert 7232 - 3174 == 4058
    assert 2 * 51 * 51 < 73 * 73 <= 2 * 52 * 52
    print("PASS_RANK1_DELETION_TARGET_TEST")


if __name__ == "__main__":
    main()
