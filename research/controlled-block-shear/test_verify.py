"""Recompute the block-shear split through dimension 6."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


def load_module():
    path = Path(__file__).with_name("verify.py")
    spec = importlib.util.spec_from_file_location("controlled_block_shear", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class BlockShearTest(unittest.TestCase):
    def test_small_dimensions(self) -> None:
        module = load_module()
        positive = negative = 0
        for dimension in range(2, 7):
            found_positive, found_negative = module.check_dimension(dimension)
            positive += found_positive
            negative += found_negative
        self.assertEqual(positive, sum(dimension * (dimension - 1) // 2 for dimension in range(2, 7)))
        self.assertEqual(negative, positive)


if __name__ == "__main__":
    unittest.main()
