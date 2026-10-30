"""Recompute the 3/80 margin."""

from __future__ import annotations

import unittest
from fractions import Fraction


class MarginTest(unittest.TestCase):
    def test_gap(self) -> None:
        one = Fraction(3, 4)
        cap = Fraction(3, 5)
        square = one * one
        self.assertEqual(square, Fraction(9, 16))
        self.assertGreater(one, cap)
        self.assertEqual(cap - square, Fraction(3, 80))
        self.assertEqual(square + Fraction(3, 80), cap)


if __name__ == "__main__":
    unittest.main()
