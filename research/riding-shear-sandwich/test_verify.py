"""Recompute one forward and one reverse riding sandwich."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


def load_module():
    path = Path(__file__).with_name("verify.py")
    spec = importlib.util.spec_from_file_location("riding_shear_sandwich", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class SandwichTest(unittest.TestCase):
    def test_examples(self) -> None:
        module = load_module()
        self.assertEqual(module.forward_sandwich(3, 1, 4, 2, 1), (3, 1 + 3 + 4, 4, 2 + 3 + 4))
        self.assertEqual(module.reverse_sandwich(3, 5, 4, 2, 1), (3 - 5 + 2, 5, 4 + 5 - 2, 2))
        self.assertEqual(module.forward_expected(3, 1, 4, 2, 0), (3, 4, 4, 2))


if __name__ == "__main__":
    unittest.main()
