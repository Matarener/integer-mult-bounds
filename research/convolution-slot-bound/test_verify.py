"""Recompute the length-four all-ones convolution."""

from __future__ import annotations

import unittest


class SlotTest(unittest.TestCase):
    def test_all_ones(self) -> None:
        length, left_bits, right_bits = 4, 1, 1
        output = [0] * (2 * length - 1)
        for i in range(length):
            for j in range(length):
                output[i + j] += 1
        self.assertEqual(max(output), 4)
        guard = (length - 1).bit_length()
        self.assertEqual(guard, 2)
        self.assertLess(max(output), 1 << (left_bits + right_bits + guard))


if __name__ == "__main__":
    unittest.main()
