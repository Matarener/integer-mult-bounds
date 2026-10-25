"""Recompute the V45 common difference and the joint-price sum."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


def load_module():
    path = Path(__file__).with_name("verify.py")
    spec = importlib.util.spec_from_file_location("v45_margin_ladder", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class MarginLadderTest(unittest.TestCase):
    def test_difference_and_sum(self) -> None:
        module = load_module()
        self.assertEqual(module.common_difference(), 25_371)
        self.assertEqual(module.CLIMB[0] + 3 * 25_371, 22_972)
        self.assertEqual(
            module.joint_price_sum(),
            -8_388_172 + 2 * -10_499_041 + 2 * -8_382_370,
        )


if __name__ == "__main__":
    unittest.main()
