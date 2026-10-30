"""Recompute the precision-101 obstruction and the 4464 witness."""

from __future__ import annotations

import unittest
from fractions import Fraction


class DomainTest(unittest.TestCase):
    def test_precision_101(self) -> None:
        precision = 101
        scale = (8 * precision - 1).bit_length()
        self.assertEqual(scale, 10)
        root = 1
        while root * root * scale < 16 * precision:
            root += 1
        self.assertEqual(root, 13)
        spacing = 4 * root + 11
        self.assertEqual(scale * spacing, 630)
        self.assertGreater(scale * spacing, precision)

    def test_witness(self) -> None:
        precision, scale, spacing, width = 4464, 16, 279, 69
        self.assertEqual(scale * spacing, precision)
        self.assertGreater(spacing - 2, 4 * width)
        self.assertEqual(66 * 66, 4356)
        self.assertEqual(67 * 67, 4489)
        self.assertLess(66 * 66, 16 * precision // scale)
        self.assertGreater(67 * 67, 16 * precision // scale)
        self.assertLess(Fraction(1, 4 * spacing), Fraction(1, 2 * spacing - 1))


if __name__ == "__main__":
    unittest.main()
