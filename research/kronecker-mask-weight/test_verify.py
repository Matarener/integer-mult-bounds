"""Recompute outer-product weights through width product 6."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


def load_module():
    path = Path(__file__).with_name("verify.py")
    spec = importlib.util.spec_from_file_location("kronecker_mask_weight", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class KroneckerWeightTest(unittest.TestCase):
    def test_small_product(self) -> None:
        module = load_module()
        pairs, colliding = module.check(6)
        expected = sum(
            (1 << left) * (1 << right)
            for left in range(1, 7)
            for right in range(1, 7)
            if left * right <= 6
        )
        self.assertEqual(pairs, expected)
        self.assertGreater(colliding, 0)


if __name__ == "__main__":
    unittest.main()
