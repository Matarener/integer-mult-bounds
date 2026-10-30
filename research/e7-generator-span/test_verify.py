"""Recompute the printed generator span and the odd overlaps."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


def load_module():
    path = Path(__file__).with_name("verify.py")
    spec = importlib.util.spec_from_file_location("e7_generator_span", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class GeneratorSpanTest(unittest.TestCase):
    def test_span_and_odds(self) -> None:
        module = load_module()
        self.assertEqual(len(module.span(module.GENERATORS)), 128)
        odd = [
            generator
            for generator in module.GENERATORS
            if not module.even_overlap(generator, module.NORMAL)
        ]
        self.assertEqual(odd, [66, 36, 1])


if __name__ == "__main__":
    unittest.main()
