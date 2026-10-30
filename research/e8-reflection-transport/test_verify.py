"""Recompute the first reflection on its own root."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


def load_module():
    path = Path(__file__).with_name("verify.py")
    spec = importlib.util.spec_from_file_location("e8_reflection_transport", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ReflectionTest(unittest.TestCase):
    def test_first_root_negates(self) -> None:
        module = load_module()
        roots, _labels = module.a8_model()
        scalar = module.oriented_roots(roots)
        pair = tuple(3 if coordinate == 0 else -3 if coordinate == 1 else 0 for coordinate in range(9))
        alpha = scalar[roots.index(pair)]
        image = module.reflect(alpha, alpha)
        self.assertEqual(image, tuple(-entry for entry in alpha))
        self.assertEqual(module.canonical(image), module.canonical(alpha))
        self.assertEqual(module.dot(alpha, alpha), 8)


if __name__ == "__main__":
    unittest.main()
