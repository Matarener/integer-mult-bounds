#!/usr/bin/env python3
"""Arithmetic of the direct-frame capacity gap."""

from fractions import Fraction


def main():
    ports, replicas = 111, 32
    excess = ports * replicas
    assert excess == 3552
    for stages, bill in ((5, Fraction(145, 144)), (9, Fraction(513, 512)), (11, Fraction(781, 780))):
        half = (stages - 1) // 2
        paid = ports * stages * replicas * (14 * half + 1)
        capacity = (1 + 7 * stages) * (2 * half * ports * replicas)
        assert paid - capacity == excess
        assert Fraction(paid, capacity) == bill
    print("PASS_DIRECT_FRAME_STAGE_BILLS_TEST")


if __name__ == "__main__":
    main()
