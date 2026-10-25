"""Recompute one two-by-two cancellation."""

from __future__ import annotations

import unittest
from fractions import Fraction


class SchurTest(unittest.TestCase):
    def test_identity_interior(self) -> None:
        bare = Fraction(1) * 1 + Fraction(1) * 1
        self.assertEqual(Fraction(2, 4) * bare, Fraction(1))
        interior_left, interior_right = 3, 5
        boundary_left, boundary_right = 2, 4
        row = (Fraction(boundary_left, interior_left), Fraction(boundary_left, interior_right))
        column = (Fraction(interior_left, boundary_right), Fraction(interior_right, boundary_right))
        correction = row[0] * column[0] + row[1] * column[1]
        self.assertEqual(correction, Fraction(1))


if __name__ == "__main__":
    unittest.main()
