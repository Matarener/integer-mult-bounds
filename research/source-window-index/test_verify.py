"""Recompute one three-over-four window."""

from __future__ import annotations

import unittest


class WindowTest(unittest.TestCase):
    def test_three_over_four(self) -> None:
        denominator, numerator, low, high = 3, 4, 1, 3
        start = -((-denominator * (2 * low - 1)) // (2 * numerator))
        stop = -((-denominator * (2 * high - 1)) // (2 * numerator))
        self.assertEqual((start, stop), (1, 2))
        images = [
            (2 * numerator * index + denominator) // (2 * denominator)
            for index in range(-1, 4)
        ]
        self.assertEqual(images, [-1, 0, 1, 3, 4])
        self.assertEqual([index for index, image in zip(range(-1, 4), images) if low <= image < high], [1])


if __name__ == "__main__":
    unittest.main()
