"""Recompute one published minor by an independent expansion."""

from __future__ import annotations

import importlib.util
import unittest
from itertools import permutations
from pathlib import Path


def load_module():
    path = Path(__file__).with_name("verify.py")
    spec = importlib.util.spec_from_file_location("e8_minor_units", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def expand(rows):
    total = 0
    for perm in permutations(range(8)):
        sign = 1
        for left in range(8):
            for right in range(left + 1, 8):
                if perm[left] > perm[right]:
                    sign = -sign
        term = sign
        for row, column in enumerate(perm):
            term *= rows[row][column]
        total += term
    return total


class MinorTest(unittest.TestCase):
    def test_first_single(self) -> None:
        module = load_module()
        roots, _labels = module.a8_model()
        oriented = module.oriented_roots(roots)
        witness = module.load()[1]["single_types"][0]
        value = expand([oriented[index] for index in witness["rows"]])
        self.assertEqual(value, -512)
        self.assertEqual(abs(value) & (abs(value) - 1), 0)


if __name__ == "__main__":
    unittest.main()
