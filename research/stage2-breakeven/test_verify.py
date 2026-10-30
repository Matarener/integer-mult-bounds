"""Recompute the stage-2 price sum and the class gap."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


def load_module():
    path = Path(__file__).with_name("verify.py")
    spec = importlib.util.spec_from_file_location("stage2_breakeven", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Stage2Test(unittest.TestCase):
    def test_sum_and_gap(self) -> None:
        module = load_module()
        self.assertEqual(module.price_sum(), -2_101_683 * 2 - 2_106_679 * 3)
        self.assertEqual(module.price_gap(), 4_996)
        self.assertEqual(-(-2_101_683) - 2_091_300, 10_383)


if __name__ == "__main__":
    unittest.main()
