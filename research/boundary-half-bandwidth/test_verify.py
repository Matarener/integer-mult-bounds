"""Recompute one width-2 boundary list."""

from __future__ import annotations

import unittest


class BandTest(unittest.TestCase):
    def test_width_two(self) -> None:
        width = 2
        rows = [0, 1, 7, 8]
        self.assertEqual(rows[-1] - rows[0], 8)
        self.assertEqual(len(rows) - 1, 2 * width - 1)
        self.assertLessEqual(len(rows) - 1, 2 * width)
        self.assertEqual([0, 1] + [7, 8], rows)


if __name__ == "__main__":
    unittest.main()
