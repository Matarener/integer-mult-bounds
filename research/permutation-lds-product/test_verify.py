"""Recompute permutation products through order 4."""

from __future__ import annotations

import importlib.util
import math
import unittest
from pathlib import Path


def load_module():
    path = Path(__file__).with_name("verify.py")
    spec = importlib.util.spec_from_file_location("permutation_lds_product", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class PermutationProductTest(unittest.TestCase):
    def test_small_orders(self) -> None:
        module = load_module()
        pairs = sharp = 0
        for order in range(1, 5):
            found_pairs, found_sharp = module.check_order(order)
            pairs += found_pairs
            sharp += found_sharp
        self.assertEqual(pairs, sum(math.factorial(order) ** 2 for order in range(1, 5)))
        self.assertGreater(sharp, 0)


if __name__ == "__main__":
    unittest.main()
