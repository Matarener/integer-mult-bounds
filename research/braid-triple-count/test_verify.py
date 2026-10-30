"""Recompute the 112-port binomial coefficients by Pascal's triangle."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


def load_module():
    path = Path(__file__).with_name("verify.py")
    spec = importlib.util.spec_from_file_location("braid_triple_count", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def pascal(n: int, k: int) -> int:
    row = [1]
    for _ in range(n):
        row = [1] + [row[index] + row[index + 1] for index in range(len(row) - 1)] + [1]
    return row[k]


class BraidCountTest(unittest.TestCase):
    def test_binomials(self) -> None:
        module = load_module()
        self.assertEqual(module.binomial(112, 2), pascal(112, 2))
        self.assertEqual(module.binomial(112, 3), pascal(112, 3))
        self.assertEqual(pascal(112, 3), 227920)
        self.assertEqual(229936 - pascal(112, 3), 2016)


if __name__ == "__main__":
    unittest.main()
