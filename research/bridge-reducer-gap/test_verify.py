"""Recompute one reduced product and one interrupted product."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


def load_module():
    path = Path(__file__).with_name("verify.py")
    spec = importlib.util.spec_from_file_location("bridge_reducer_gap", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ReducerTest(unittest.TestCase):
    def test_two_products(self) -> None:
        module = load_module()
        success = module.multiply(module.elementary(0, 1, 1), module.elementary(2, 3, 1))
        status, operations = module.reduce(success)
        self.assertEqual(status, "reduced")
        self.assertEqual(module.replay(success, operations), module.identity())
        interrupted = module.multiply(module.elementary(0, 2, -1), module.elementary(2, 0, -1))
        self.assertEqual(module.reduce(interrupted)[0], "interrupted")
        self.assertEqual(module.leibniz(interrupted), 1)


if __name__ == "__main__":
    unittest.main()
