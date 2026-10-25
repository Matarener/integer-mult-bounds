"""Recompute the a=26 scale identity."""

from __future__ import annotations

import unittest
from fractions import Fraction


class ErasureTest(unittest.TestCase):
    def test_scale_26(self) -> None:
        scale = 26
        precision = 1 << (10 * scale)
        width = 1 << (4 * scale)
        box = 1 << (3 * scale)
        band = 4 * box + 2
        self.assertEqual((band - 2) * (band - 2) * width, 16 * precision)
        lower = Fraction(3 * (1 << scale), 4096) - Fraction(1, 2 * box * box)
        self.assertGreater(lower, 32768)
        self.assertEqual(width ** 5, precision ** 2)


if __name__ == "__main__":
    unittest.main()
