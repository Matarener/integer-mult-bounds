"""Recompute the idle segments of stages 2, 4 and 6."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


def load_module():
    path = Path(__file__).with_name("verify.py")
    spec = importlib.util.spec_from_file_location("idle_rank_sum", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class IdleRankTest(unittest.TestCase):
    def test_openings(self) -> None:
        module = load_module()
        owned = module.segments((2, 4, 6), {2, 4, 6})
        self.assertEqual(owned, [16, 8, 8, 16])
        self.assertEqual(sum(owned), 8 * (9 - 3))
        ridden = module.segments((2,), set())
        self.assertEqual(ridden[0], 16)
        self.assertEqual(sum(ridden), 8 * 9)


if __name__ == "__main__":
    unittest.main()
