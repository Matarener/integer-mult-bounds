"""Recompute the 530 residual constant."""

from __future__ import annotations

import unittest


class MarginTest(unittest.TestCase):
    def test_residual_constant(self) -> None:
        precision = 101
        self.assertEqual(66 * 8, 528)
        self.assertEqual(528 + 2, 530)
        self.assertLessEqual(2, 2 * precision * precision)
        exponent = 32768 * precision
        self.assertLessEqual((530 * precision * precision).bit_length(), exponent)
        self.assertLessEqual((128 * precision * precision - 1).bit_length(), exponent)


if __name__ == "__main__":
    unittest.main()
