"""Recompute the square comparison and the p=101 tail."""

from __future__ import annotations

import unittest


class ErrorSumTest(unittest.TestCase):
    def test_opening(self) -> None:
        self.assertGreater(99 * 99, 2 * 70 * 70)
        self.assertEqual(2 * 70 - 99, 41)
        precision = 101
        self.assertLess(18 * precision, 1 << 11)
        self.assertLess(4 * 70, 41 * (1 << (15 * precision - 2)))


if __name__ == "__main__":
    unittest.main()
