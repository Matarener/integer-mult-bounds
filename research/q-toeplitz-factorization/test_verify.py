"""Recompute the order-two inverse at q=1/4."""

from __future__ import annotations

import unittest
from fractions import Fraction


class FactorizationTest(unittest.TestCase):
    def test_order_two(self) -> None:
        q = Fraction(1, 4)
        width = 1 - q * q
        self.assertEqual(width, Fraction(15, 16))
        square = q / width
        signed = -q / width
        self.assertEqual(square + signed, 0)
        self.assertEqual(Fraction(15, 14) / (1 - q), Fraction(10, 7))


if __name__ == "__main__":
    unittest.main()
