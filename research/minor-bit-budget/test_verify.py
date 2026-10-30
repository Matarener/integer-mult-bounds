"""Recompute one 2-by-2 determinant budget."""

from __future__ import annotations

import unittest


class MinorTest(unittest.TestCase):
    def test_two_by_two(self) -> None:
        order, bits = 2, 1
        guard = (order - 1).bit_length()
        budget = order * (order + 1) * bits + order * guard + 2
        self.assertEqual(budget, 10)
        self.assertEqual(abs(3 * 3 - (-3) * 3).bit_length(), 5)
        self.assertLessEqual(5, budget)


if __name__ == "__main__":
    unittest.main()
