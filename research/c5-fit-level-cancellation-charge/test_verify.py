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
    WEIGHT16,
    build,
    diagonal_fit_cost,
    geometry,
    j_identity_extension_tariff,
    need,
    pairing_rank,
    sources,
)


class Controls(unittest.TestCase):
    def test_complete_plane_not_scalar_line(self):
        planes, _matching = geometry()
        self.assertEqual(pairing_rank(planes[0], planes[0]), 2)
        self.assertEqual(pairing_rank(planes[0][:1], planes[0][:1]), 1)

    def test_floors_beat_termwise_ceiling(self):
        result = json.loads((HERE / "RESULT.json").read_bytes())
        self.assertEqual(Fraction(result["weight_sum"]), Fraction(9, 4))
        self.assertEqual(Fraction(result["j_free_floor"]), 45)
        self.assertEqual(Fraction(result["one_j_floor"]), Fraction(561, 16))
        self.assertEqual(Fraction(result["termwise_ceiling"]), Fraction(180, 7))
        self.assertTrue(result["beats_termwise_ceiling_j_free"])
        self.assertTrue(result["beats_termwise_ceiling_one_j"])
        self.assertGreater(Fraction(result["j_free_floor"]), Fraction(180, 7))
        self.assertGreater(Fraction(result["one_j_floor"]), Fraction(180, 7))

    def test_weight_sum_and_rho(self):
        self.assertEqual(sum(WEIGHT16), 36)
        self.assertEqual(Fraction(sum(WEIGHT16), 16), Fraction(9, 4))
        result = json.loads((HERE / "RESULT.json").read_bytes())
        self.assertEqual(Fraction(result["rho"]), Fraction(303, 16))
        self.assertEqual(Fraction(result["j_credit"]), Fraction(159, 16))

    def test_named_fits_meet_floors(self):
        planes, matching = geometry()
        diagonal = diagonal_fit_cost(planes, matching)
        j_ext = j_identity_extension_tariff(planes, matching)
        self.assertEqual(diagonal["total_cost"], 224)
        self.assertEqual(diagonal["net_full_support_terms"], 0)
        self.assertEqual(j_ext["total_cost"], 16097)
        self.assertEqual(j_ext["net_full_support_terms"], 1)
        self.assertGreaterEqual(diagonal["total_cost"], 45)
        self.assertGreaterEqual(j_ext["total_cost"], Fraction(561, 16))

    def test_build_matches_receipt(self):
        self.assertEqual(build(), json.loads((HERE / "RESULT.json").read_bytes()))

    def manifest_control(self, change):
        doc = json.loads((HERE / "SOURCES.json").read_bytes())
        change(doc)
        with tempfile.TemporaryDirectory(prefix="c5-cancel-control-") as temp:
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
        with tempfile.TemporaryDirectory(prefix="c5-cancel-input-") as temp:
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
        mutated = json.loads(raw)
        mutated["beats_termwise_ceiling_j_free"] = False
        with tempfile.TemporaryDirectory(prefix="c5-cancel-receipt-") as temp:
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
