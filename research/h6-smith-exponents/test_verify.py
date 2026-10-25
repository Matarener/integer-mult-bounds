#!/usr/bin/env python3
"""Arithmetic checks for the H6 Smith factors."""


def main():
    assert 11 * 19 == 209
    assert 11 * 19 * 23 == 4807
    assert 336 + 208 + 16 == 560
    assert 30400 + 560 == 30960
    assert (11**336) * (209**208) * (4807**16) == (11**560) * (19**224) * (23**16)
    print("PASS_H6_SMITH_EXPONENTS_TEST")


if __name__ == "__main__":
    main()
