"""Recompute XOR-mask subsequence lengths through dimension 4."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


def load_module():
    path = Path(__file__).with_name("verify.py")
    spec = importlib.util.spec_from_file_location("xor_mask_lds", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class XorMaskTest(unittest.TestCase):
    def test_small_masks(self) -> None:
        module = load_module()
        self.assertEqual(module.mask_lengths(4), (1 << 5) - 2)
        self.assertEqual(module.composition_pairs(3), sum(1 << (2 * n) for n in range(1, 4)))


if __name__ == "__main__":
    unittest.main()
