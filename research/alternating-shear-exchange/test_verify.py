"""Recompute the two alternating shear products."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


def load_module():
    path = Path(__file__).with_name("verify.py")
    spec = importlib.util.spec_from_file_location("alternating_shear_exchange", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ShearExchangeTest(unittest.TestCase):
    def test_products(self) -> None:
        module = load_module()
        forward_triple = module.multiply(module.FORWARD, module.multiply(module.REVERSE, module.FORWARD))
        reverse_triple = module.multiply(module.REVERSE, module.multiply(module.FORWARD, module.REVERSE))
        self.assertEqual(forward_triple, ((0, -1), (1, 0)))
        self.assertEqual(reverse_triple, forward_triple)
        self.assertEqual(module.exchange(module.schedules((4, -7))[0]), (4, -7))


if __name__ == "__main__":
    unittest.main()
