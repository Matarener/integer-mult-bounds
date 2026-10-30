#!/usr/bin/env python3
"""Behavioral controls, including actual arithmetic and endpoint faults.

Nick Petalas. Apache-2.0.
"""

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("cyclic_verify", ROOT / "verify.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("verifier loader unavailable")
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)


class Behavior(unittest.TestCase):
    def test_real_arithmetic_and_action_faults(self):
        with mock.patch.object(V, "multiply", return_value=(0, 0)):
            with self.assertRaises(ValueError):
                V.matrix_cases(1)
        with mock.patch.object(V, "gate_action", return_value=(0,)):
            with self.assertRaises(ValueError):
                V.generic_check()
        with mock.patch.object(V, "rank", return_value=0):
            with self.assertRaises(ValueError):
                V.witness_check(ROOT)

    def test_necessary_hypotheses(self):
        a = (1, 0)
        singular_k = (0, 1)
        self.assertEqual(V.multiply(V.multiply(a, singular_k), a), (0, 0))
        cubic = V.multiply(V.multiply(a, V.multiply(singular_k, singular_k)), a)
        self.assertEqual(V.rank(cubic), 0)
        nilpotent_a = (2, 0)
        k = V.identity(2)
        self.assertEqual(V.multiply(V.multiply(nilpotent_a, k), nilpotent_a), (0, 0))
        self.assertEqual(V.rank(nilpotent_a), 1)
        self.assertNotEqual(V.multiply(nilpotent_a, nilpotent_a), nilpotent_a)
        # With one more dimension, an invertible three-cycle has two zero moments.
        a3, cycle = (1, 0, 0), (2, 4, 1)
        self.assertEqual(V.rank(cycle), 3)
        self.assertEqual(V.multiply(V.multiply(a3, cycle), a3), (0, 0, 0))
        square = V.multiply(cycle, cycle)
        self.assertEqual(V.multiply(V.multiply(a3, square), a3), (0, 0, 0))

    def test_domain_and_bounds(self):
        for roles, u, v in [(0, 1, 1), (9, 1, 1), (2, 0, 1), (2, 1, 2),
                            (2, 4, 1), (True, 1, 1)]:
            with self.assertRaises(ValueError):
                V.projector(roles, u, v)
        with self.assertRaises(ValueError):
            V.coefficients(1, ((1, 1),) * 17)
        with self.assertRaises(ValueError):
            V.gate_action((1,), 1, 1, 3)
        for targets in (0, 65, True):
            with self.assertRaises(ValueError):
                V.lower_bound(targets)
        self.assertEqual([V.lower_bound(t) for t in range(1, 6)], [3, 6, 9, 12, 11])
        for t in range(1, 65):
            value = V.lower_bound(t)
            self.assertGreater(value, 2 * t)
            self.assertEqual((value - 3 * t) % 4, 0)
            self.assertLessEqual(value, 3 * t)

    def test_source_and_receipt_fail_closed(self):
        with tempfile.TemporaryDirectory(prefix="cyclic-source-") as temporary:
            root = Path(temporary)
            (root / "SOURCE_HASHES.json").write_text(json.dumps({"proof": "0" * 64}))
            (root / "proof").write_text("changed proof")
            with self.assertRaisesRegex(ValueError, "source hash"):
                V.source_check(root)
        with mock.patch.object(V, "produce", return_value={"status": "actual"}):
            with mock.patch.object(sys, "argv", ["verify.py"]):
                with self.assertRaisesRegex(ValueError, "receipt"):
                    V.main()

    def test_exclusive_output(self):
        with tempfile.TemporaryDirectory(prefix="cyclic-output-") as temporary:
            output = Path(temporary) / "receipt.json"
            result = {"status": "actual"}
            with mock.patch.object(V, "produce", return_value=result):
                with mock.patch.object(sys, "argv", ["verify.py", "--write", str(output)]):
                    with contextlib.redirect_stdout(io.StringIO()):
                        V.main()
                    self.assertEqual(json.loads(output.read_text()), result)
                    with self.assertRaises(FileExistsError):
                        V.main()
                    self.assertEqual(json.loads(output.read_text()), result)


if __name__ == "__main__":
    unittest.main()
