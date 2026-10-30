"""Recompute the precision-101 contraction and the full precision-1 tail."""

from __future__ import annotations

import unittest


class TailTest(unittest.TestCase):
    def test_precision_101(self) -> None:
        precision = 101
        modulus = 16 * precision
        self.assertLess(2 * (modulus - 1) ** modulus, modulus ** modulus)
        self.assertEqual(512 * precision * precision, modulus * (32 * precision))
        self.assertLess(32 * precision, 1 << (16 * precision))

    def test_full_precision_one(self) -> None:
        # J=512 and g=1/16, so the tail integer is 32*(15**512) against 16**512.
        self.assertLess(32 * 15 ** 512, 16 ** 512)
        self.assertLess(32 * 15 ** 512 * (1 << 16), 16 ** 512)


if __name__ == "__main__":
    unittest.main()
