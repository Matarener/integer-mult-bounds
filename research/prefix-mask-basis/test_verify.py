"""Recompute the prefix-mask basis through dimension 6."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


def load_module():
    path = Path(__file__).with_name("verify.py")
    spec = importlib.util.spec_from_file_location("prefix_mask_basis", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class PrefixMaskTest(unittest.TestCase):
    def test_small_dimensions(self) -> None:
        module = load_module()
        masks = sum(module.check_dimension(dimension) for dimension in range(1, 7))
        self.assertEqual(masks, (1 << 7) - 2)


if __name__ == "__main__":
    unittest.main()
