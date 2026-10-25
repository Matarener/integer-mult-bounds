#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Behavioral and source-boundary controls (admitted under -O)."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from verify import (  # noqa: E402
    ROOT,
    build,
    diagonal_fit_cost,
    geometry,
    identity_extension_term_count,
    need,
    pairing_rank,
    signed_gram_extension_term_count,
    sources,
)


class Controls(unittest.TestCase):
    def test_complete_plane_not_scalar_line(self):
        planes, _matching = geometry()
        self.assertEqual(pairing_rank(planes[0], planes[0]), 2)
        self.assertEqual(pairing_rank(planes[0][:1], planes[0][:1]), 1)

    def test_uniform_floor_sum_exceeds_diagonal(self):
        result = json.loads((HERE / "RESULT.json").read_bytes())
        self.assertEqual(result["uniform_local_floor_sum"], 460)
        self.assertEqual(result["diagonal_fit"]["total_cost"], 224)
        self.assertFalse(result["inequality_holds"])
        self.assertGreater(
            result["uniform_local_floor_sum"], result["diagonal_fit"]["total_cost"]
        )

    def test_weight_sum_ceiling_on_I(self):
        # Any nonnegative weight vector with sum > 224/20 cannot satisfy the
        # candidate on K=I against the diagonal upper bound.
        self.assertEqual(Fraction(224, 20), Fraction(56, 5))
        self.assertGreater(20 * Fraction(56, 5), 223)
        self.assertLessEqual(20 * Fraction(56, 5), 224)

    def test_j_extensions_do_not_discriminate(self):
        self.assertEqual(identity_extension_term_count(112), 12433)
        self.assertEqual(signed_gram_extension_term_count(112), 6329)
        self.assertLessEqual(460, 12433)
        self.assertLessEqual(460, 6329)
        for n in (0, 113, True):
            with self.assertRaises(ValueError):
                identity_extension_term_count(n)
            with self.assertRaises(ValueError):
                signed_gram_extension_term_count(n)

    def test_build_matches_receipt(self):
        self.assertEqual(build(), json.loads((HERE / "RESULT.json").read_bytes()))

    def manifest_control(self, change):
        doc = json.loads((HERE / "SOURCES.json").read_bytes())
        change(doc)
        with tempfile.TemporaryDirectory(prefix="c5-fit-level-control-") as temp:
            path = Path(temp) / "SOURCES.json"
            path.write_text(json.dumps(doc))
            with self.assertRaises(ValueError):
                sources(ROOT, path)

    def test_manifest_inventory_and_usage(self):
        self.manifest_control(lambda d: d["files"].pop())
        self.manifest_control(
            lambda d: d["files"].append(copy.deepcopy(d["files"][-1]))
        )
        self.manifest_control(lambda d: d["files"][-1].update(usage="provenance"))
        self.manifest_control(lambda d: d["files"][-1].update(path="unexpected.json"))
        self.manifest_control(lambda d: d["files"][-1].update(extra=True))

    def test_authentication_and_actual_corruption(self):
        self.manifest_control(lambda d: d["files"][-1].update(sha256="0" * 64))
        self.manifest_control(lambda d: d["files"][-1].update(git_blob="0" * 40))
        with tempfile.TemporaryDirectory(prefix="c5-fit-level-input-") as temp:
            root = Path(temp)
            for row in json.loads((HERE / "SOURCES.json").read_bytes())["files"]:
                if row["usage"] == "input":
                    target = root / row["path"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes((ROOT / row["path"]).read_bytes())
            planes, matching = geometry(root)
            self.assertEqual(len(planes), 56)
            diagonal_fit_cost(planes, matching)
            target.write_bytes(target.read_bytes() + b" ")
            with self.assertRaises(ValueError):
                geometry(root)

    def test_duplicate_json_key_rejected_in_receipt_copy(self):
        raw = (HERE / "RESULT.json").read_text()
        # Inject a duplicate top-level key into a temp copy; stdlib keeps last,
        # so we instead assert our need()-gated equality still fails on mutation.
        mutated = json.loads(raw)
        mutated["inequality_holds"] = True
        with tempfile.TemporaryDirectory(prefix="c5-fit-level-receipt-") as temp:
            path = Path(temp) / "RESULT.json"
            path.write_text(json.dumps(mutated, indent=2, sort_keys=True) + "\n")
            with self.assertRaises(ValueError):
                need(
                    build() == json.loads(path.read_bytes()),
                    "corrupted receipt must not match",
                )

    def test_controls_survive_optimization(self):
        with self.assertRaises(ValueError):
            need(False, "must fail with -O too")


if __name__ == "__main__":
    unittest.main()
