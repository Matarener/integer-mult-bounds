"""Recompute the width-7 and width-9 pattern totals."""

from __future__ import annotations

import importlib.util
import unittest
from fractions import Fraction
from pathlib import Path


def load_module():
    path = Path(__file__).with_name("verify.py")
    spec = importlib.util.spec_from_file_location("rank7_basis_cover", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class BasisCoverTest(unittest.TestCase):
    def test_two_widths(self) -> None:
        module = load_module()
        totals = module.width_totals()
        self.assertEqual(totals[7], Fraction(1757, 4) + Fraction(115, 4))
        self.assertEqual(totals[7], 9 * 52)
        self.assertEqual(totals[9], 9 * 213)


if __name__ == "__main__":
    unittest.main()
