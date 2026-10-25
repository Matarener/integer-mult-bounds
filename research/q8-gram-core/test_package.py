"""Behavioral fault and boundary controls, including optimized Python.

Nick Petalas, Apache-2.0.
"""

import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import gram
from linear import coordinates
import model
import oracle
import system
import verify


class Controls(unittest.TestCase):
    def test_actual_faults(self):
        counts = dict.fromkeys(("words", "dirty_columns", "call_intertwining", "coefficient_quotients"), 0)
        word = (model.Gate(2, 1, 1), model.Gate(4, 1, 1))
        # A real producer fault, not a receipt edit.
        with patch.object(gram, "normal_form", return_value=((model.Gate(2, 1, 1),) * 2, 1)):
            with self.assertRaisesRegex(ValueError, "full coefficient quotient"):
                verify.check_word(word, 1, counts)
        with patch.object(model, "group_product", side_effect=lambda a, b: oracle.product(b, a)):
            with self.assertRaisesRegex(ValueError, "Hamilton endpoint"):
                verify.check_word(word, 1, counts)
        with patch.object(oracle, "product", return_value=0):
            with self.assertRaisesRegex(ValueError, "Hamilton endpoint"):
                verify.check_word(word, 1, counts)

    def test_candidate_boundary_and_short_controls(self):
        for rows, labels in (((0,), (2,)), ((1,), (3,)), ((1,), ())):
            with self.assertRaises(ValueError):
                gram.normal_form(rows, labels)
        with self.assertRaisesRegex(ValueError, "outside span"):
            coordinates((1,), 2, 2)
        self.assertFalse(gram.negative_target((1,), (2,), 1, 0))
        self.assertTrue(gram.negative_target((7, 7, 7), (2, 2, 2), 1, 0))
        self.assertFalse(gram.negative_target((7, 7, 7), (2, 2, 2), 3, 0))
        # Equal diagonal/first-order parity does not imply the endpoint.
        self.assertFalse(gram.negative_target((1, 2, 4), (2, 2, 2), 3, 0))
        self.assertEqual(gram.normal_form((), ()), ((), 0))
        with self.assertRaisesRegex(ValueError, "rank-one idempotent"):
            model.endpoint((model.Gate(2, 1, 2),), 2)
        with self.assertRaisesRegex(ValueError, "target count"):
            gram.negative_target((1,), (2,), 2, 0)

    def test_symbolic_fault_and_export(self):
        c = system.build(3, 1, 0)
        self.assertTrue(c.evaluate((7, 7, 7), (2, 2, 2)))
        # Force the exported producer's formal product to be identity.
        with patch.object(system, "formal_product", side_effect=lambda circuit, rows, labels:
                          [tuple(circuit.const(1 << a) for a in range(3))]
                          + [tuple(circuit.const(0) for _ in range(3))] * 7):
            self.assertFalse(system.build(3, 1, 0).evaluate((7, 7, 7), (2, 2, 2)))
        with self.assertRaises(ValueError):
            system.build(17, 1, 0)
        with self.assertRaises(ValueError):
            c.smt(600_001)
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "system.smt2"
            args = ["system.py", "--calls", "3", "--i-targets", "1", "--j-targets", "0",
                    "--timeout-ms", "1000", "--output", str(path)]
            with patch.object(sys, "argv", args):
                system.main()
            self.assertIn("(set-logic QF_BV)", path.read_text())
            original = path.read_bytes()
            with patch.object(sys, "argv", args), self.assertRaises(FileExistsError):
                system.main()
            self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
