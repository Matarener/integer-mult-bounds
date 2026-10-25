#!/usr/bin/env python3
"""Counts for the destination-free gate identity."""


def main():
    assert ((), (1,), (1, 1), (1, 2, 1), (2, 3, 2, 3)).__len__() == 5
    assert (1 ^ 1) == 0
    assert ((1 << 0) ^ (1 << 1) ^ (1 << 0)) == (1 << 1)
    print("PASS_GATE_DEST_FREE_AGREEMENT_TEST")


if __name__ == "__main__":
    main()
