"""Recompute the precision-101 storage spare."""

from __future__ import annotations

import unittest


class SpareTest(unittest.TestCase):
    def test_precision_101(self) -> None:
        precision = 101
        guard = (precision + 1).bit_length()
        budget = 8 * precision + 8 * guard + 32
        prefix_bits = 8 * precision + 18 + (precision * precision).bit_length()
        self.assertEqual(guard, 7)
        self.assertEqual(budget, 896)
        self.assertEqual(prefix_bits, 840)
        self.assertEqual(budget - prefix_bits, 56)


if __name__ == "__main__":
    unittest.main()
