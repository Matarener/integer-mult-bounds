"""Recompute one bridge, its inverse, and its determinant."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


def load_module():
    path = Path(__file__).with_name("verify.py")
    spec = importlib.util.spec_from_file_location("bridge_block_form", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class BridgeFormTest(unittest.TestCase):
    def test_one_bridge(self) -> None:
        module = load_module()
        found = module.bridge(1, 0, 3)
        self.assertEqual(found[1][0], 3)
        self.assertEqual(found[4][5], -3)
        self.assertEqual(
            module.multiply(found, module.bridge(1, 0, -3)),
            module.identity(8),
        )
        self.assertEqual(module.determinant(module.elementary(1, 0, 3)), 1)


if __name__ == "__main__":
    unittest.main()
