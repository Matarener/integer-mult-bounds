#!/usr/bin/env python3
"""Small semantic and corruption controls for the independent classification."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location("fstar_test_" + name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


primary = load("verify")
independent = load("independent")


class ClassificationControls(unittest.TestCase):
    def test_all_triples_agree_and_every_returned_witness_replays(self):
        self.assertEqual(primary.RAW_TYPES, independent.RAW_TYPES)
        for triple in itertools.combinations_with_replacement(range(37), 3):
            witness = primary.triple_witness(triple)
            self.assertEqual(witness is not None, independent.triple_feasible(triple), triple)
            if witness is None:
                continue
            order = witness["order"]
            self.assertEqual(sorted(order), [0, 1, 2])
            types = [primary.RAW_TYPES[t] for t in triple]
            # Replay from scalar equations, without primary.check_witness.
            for position, line in enumerate(order):
                a, b = witness["a"][line], witness["b"][line]
                self.assertEqual(a & ~types[line][0], 0)
                self.assertEqual(b & ~types[line][1], 0)
                self.assertEqual(sum((a >> j & 1) * (b >> j & 1) for j in range(3)) % 2, 1)
                for later in order[position + 1:]:
                    full = sum((types[line][0] >> j & 1) * (types[later][1] >> j & 1)
                               for j in range(3)) % 2
                    if full == 0:
                        restricted = sum((a >> j & 1) * (witness["b"][later] >> j & 1)
                                         for j in range(3)) % 2
                        self.assertEqual(restricted, 0)

    def test_shared_coordinates_cannot_be_canonicalized_one_line_at_a_time(self):
        index = primary.RAW_TYPES.index
        same = (index((3, 3)),) * 3
        differently_placed = (index((3, 3)), index((3, 3)), index((5, 5)))
        # Every individual type has two tied bits, but their relative placement
        # is data: independent per-line relabelling collapses these two cases.
        self.assertIsNone(primary.triple_witness(same))
        self.assertFalse(independent.triple_feasible(same))
        self.assertIsNotNone(primary.triple_witness(differently_placed))
        self.assertTrue(independent.triple_feasible(differently_placed))

    def test_even_nonempty_overlap_does_not_make_a_diagonal_one(self):
        invalid = {"kept": [0, 1, 2], "order": [0, 1, 2],
                   "a": [3, 3, 3], "b": [3, 3, 3]}
        # The intersection is nonempty, but its cardinality is even.
        with self.assertRaisesRegex(ValueError, "diagonal"):
            primary.check_witness([3] * 3, [3] * 3, set(), invalid)
        self.assertFalse(independent.row_consistent(3, ((3, 1), (3, 0))))

    def test_witness_mask_and_order_boundaries(self):
        witness = primary.missing_arc_witness([3] * 3, [3] * 3, 0, 1, 2)
        primary.check_witness([3] * 3, [3] * 3, {(0, 2), (1, 2)}, witness)
        for mask in (-1, 8, 4):
            broken = deepcopy(witness)
            broken["a"][0] = mask
            with self.assertRaises(ValueError):
                primary.check_witness([3] * 3, [3] * 3, set(), broken)
        broken = deepcopy(witness)
        broken["order"] = [0, 1, 1]
        with self.assertRaises(ValueError):
            primary.check_witness([3] * 3, [3] * 3, set(), broken)

    def test_source_corruption_rejected_before_mathematical_work(self):
        with tempfile.TemporaryDirectory(prefix="fstar-v5-auth-") as directory:
            root = Path(directory)
            package = root / "research" / "fixture"
            package.mkdir(parents=True)
            live = root / "live.txt"
            frozen = package / "frozen.txt"
            live.write_bytes(b"live input\n")
            frozen.write_bytes(b"frozen input\n")
            sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
            manifest = {
                "files": [{"path": "live.txt", "usage": "input", "sha256": sha(live)}],
                "frozen_sources": [{"path": "frozen.txt", "sha256": sha(frozen)}],
            }
            (package / "SOURCES.json").write_text(json.dumps(manifest))
            for module in (primary, independent):
                with patch.object(module, "ROOT", root), patch.object(module, "HERE", package):
                    module.authenticate()
                    for path in (live, frozen):
                        original = path.read_bytes()
                        path.write_bytes(original + b"tampered\n")
                        with self.assertRaisesRegex(ValueError, "digest mismatch"):
                            module.authenticate()
                        path.write_bytes(original)
                    empty = dict(manifest, frozen_sources=[])
                    (package / "SOURCES.json").write_text(json.dumps(empty))
                    with self.assertRaises(ValueError):
                        module.authenticate()
                    (package / "SOURCES.json").write_text(json.dumps(manifest))


if __name__ == "__main__":
    unittest.main()
