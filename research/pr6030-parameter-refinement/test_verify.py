"""Regression and rejection controls for the source-bound exponent claim."""

from __future__ import annotations

import json
import tempfile
import unittest
from fractions import Fraction as Q
from pathlib import Path
from shutil import copytree

import verify as V


class RefinementTests(unittest.TestCase):
    def test_complete_certificate(self) -> None:
        expected = json.loads((V.HERE / "CERTIFICATE.json").read_text())
        self.assertEqual(V.encode(V.verify()), expected)
        self.assertEqual(Q(expected["improvement"]), Q(7, 10**9))

    def test_changed_paid_invoice_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "package"
            copytree(V.HERE, root)
            path = root / "vendor/RESULT.json"
            result = json.loads(path.read_text())
            result["complete_cost"]["paid"]["1"] -= 1
            path.write_text(json.dumps(result))
            with self.assertRaisesRegex(ValueError, "Changed pinned source"):
                V.authenticate(root)

    def test_exponent_above_raw_crossing_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Positive complete signed moment"):
            V.verify(Q(".003125812"), Q(".003125813"))

    def test_zero_compiler_gap_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "compiler gap"):
            V.compiler_threshold(Q(0))

    def test_closed_outer_precision_gap_rejected(self) -> None:
        params = V.parameters(V.KAPPA, V.TESTED)
        params["epsilon"] = Q(1)
        with self.assertRaisesRegex(ValueError, "Positive outer predicates"):
            V.outer_ledger(V.load("endpoint.py"), params)

    def test_insufficient_bit_contract_rejected(self) -> None:
        params = V.parameters(V.KAPPA, V.TESTED)
        params["bit_saving"] = Q(".003")
        with self.assertRaisesRegex(ValueError, "Positive outer predicates"):
            V.outer_ledger(V.load("endpoint.py"), params)

    def test_threshold_integer_inequality(self) -> None:
        result = V.compiler_threshold(Q(1, 14_000_000_000))
        self.assertEqual(result["H"], 707_182_000_000_000)
        self.assertLess((result["H"] + 1) ** 1024, 2**50513)
        self.assertGreaterEqual((14_000_000_000 * 50512 + 1) ** 1024, 2**50512)


if __name__ == "__main__":
    unittest.main()
