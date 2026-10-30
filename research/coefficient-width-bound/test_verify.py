"""Recompute the minimum precision parameters."""

from __future__ import annotations

import unittest


class CoefficientTest(unittest.TestCase):
    def test_minimum(self) -> None:
        self.assertEqual((40 - 1).bit_length(), 6)
        self.assertEqual((27 - 1).bit_length(), 5)
        precision, scale, bits, guard = 1, 4, 6, 5
        height = precision + scale + bits + 16
        working = precision + 4 * scale + 4 * bits + 2 * guard + 64
        self.assertEqual((height, working), (27, 115))
        self.assertLess(working, 5 * height)
        self.assertLessEqual(2 * ((working + 2) // 3 + 8), working)


if __name__ == "__main__":
    unittest.main()
