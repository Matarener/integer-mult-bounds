"""Recompute the weighted pair and the six-output gate total."""

from __future__ import annotations

import importlib.util
import unittest
from itertools import product
from pathlib import Path


def load_module():
    path = Path(__file__).with_name("verify.py")
    spec = importlib.util.spec_from_file_location("window_chain_source_count", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class WindowChainTest(unittest.TestCase):
    def test_weighted_pair_and_gate_total(self) -> None:
        best = None
        for counts in product(range(3), repeat=3):
            if sum(counts) % 2 or counts[0] + counts[1] == 0 or counts[1] + counts[2] == 0:
                continue
            cost = counts[0] * 1 + counts[1] * 9 + counts[2] * 1
            if best is None or cost < best:
                best = cost
        self.assertEqual(best + 4, 6)
        masks = ((1, 2, 4), (3, 2, 4))
        reader_ones = sum(row.bit_count() for reader in masks for row in reader)
        self.assertEqual(2 * (3 * reader_ones) + 4 * 7, 70)
        module = load_module()
        self.assertEqual(module.hitting_number(tuple((index, index + 1) for index in range(6))), 3)


if __name__ == "__main__":
    unittest.main()
