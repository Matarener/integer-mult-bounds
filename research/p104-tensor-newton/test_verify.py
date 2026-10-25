#!/usr/bin/env python3
"""Behavior and real optimized CLI controls for the scoped tensor certificate.

Nick Petalas. Apache-2.0.
"""

import copy
import json
import os
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
V = runpy.run_path(str(HERE / "verify.py"))


class TensorContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word, cls.native = V["load"]()

    def test_source_scalar_and_reverse_witnesses(self):
        certificate = V["scalar_certificate"](self.word)
        self.assertEqual(certificate["exponent_histogram"], {"0": 176, "2": 78, "4": 104})
        self.assertEqual(len(certificate["attaining_witnesses"]), 182)
        witness = certificate["attaining_witnesses"]["Y27"]
        self.assertEqual(V["reverse_coefficient"](self.word["program"], witness["event"],
                                                witness["target"], "Y27"),
                         Fraction(witness["coefficient"]))

    def test_changed_quarter_and_dirty_sign_reject(self):
        changed = copy.deepcopy(self.word)
        index = next(i for i, e in enumerate(changed["program"])
                     if e[0] == "add" and e[3] == "1/4")
        changed["program"][index][3] = "1/16"
        with self.assertRaisesRegex(ValueError, "sharp source exponent|private zero|restoration"):
            V["scalar_certificate"](changed)
        changed = copy.deepcopy(self.word)
        changed["program"][2034][3] = "1"
        with self.assertRaisesRegex(ValueError, "private zero"):
            V["scalar_certificate"](changed)

    def test_complete_occurrence_binding_and_mutants(self):
        _, certificate = V["bind"](self.word, self.native)
        self.assertEqual(certificate["occurrences"], 2070)
        changed = copy.deepcopy(self.native)
        changed["transports"][0]["old"] = [511]
        with self.assertRaisesRegex(ValueError, "occurrence binding"):
            V["bind"](self.word, changed)
        changed = copy.deepcopy(self.native)
        changed["transports"][0]["recipe"]["left"]["matrix_rows"] = [0] * 9
        with self.assertRaisesRegex(ValueError, "bijection"):
            V["bind"](self.word, changed)

    def test_tensor_constant_phase_is_repeated(self):
        record = next(r["recipe"]["right"] for r in self.native["transports"]
                      if r["recipe"]["right"]["phase"] != 0)
        original = V["wrapper_plan"](record)
        zero_phase = copy.deepcopy(record)
        zero_phase["phase"] = 0
        base = V["wrapper_plan"](zero_phase)
        values = [(0, 0)] * (1 << 18)
        values[0] = (1, 0)
        correct = V["tensor_wrapper"](values, original, 2)
        wrong = [V["rotate"](*v, record["phase"])
                 for v in V["tensor_wrapper"](values, base, 2)]
        self.assertNotEqual(correct, wrong)
        location = original[0][0] + 512 * original[0][0]
        self.assertEqual(correct[location], V["rotate"](1, 0, 2 * original[0][1]))

    def test_parity_and_slice_boundary(self):
        certificate = V["algebra_controls"]()
        self.assertEqual(certificate["small_pairs"], 2401)
        self.assertTrue(certificate["separate_slice_domains_fail_composition"])
        with self.assertRaisesRegex(ValueError, "nonintegral"):
            V["exact_pair"]((0, 0), (1, 0))
        with self.assertRaisesRegex(ValueError, "depth bound"):
            V["tensor_wrapper"]([], [], 0)

    def copy_export(self, destination):
        package = destination / "research/p104-tensor-newton"
        shutil.copytree(HERE, package)
        for name in (V["WORD"], V["NATIVE"]):
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(V["ROOT"] / name, target)
        return package

    def run_cli(self, package):
        return subprocess.run([sys.executable, "-I", "-O", "-Werror", "-B", str(package / "verify.py")],
                              cwd=package, env={**os.environ, "PATH": "/nonexistent"},
                              capture_output=True, text=True, timeout=100, check=False)

    def test_actual_optimized_cli_source_rejections(self):
        with tempfile.TemporaryDirectory(prefix="p104-tensor-controls-") as tmp:
            root = Path(tmp)
            package = self.copy_export(root)
            target = root / V["WORD"]
            saved = target.read_bytes()
            target.write_bytes(saved + b" ")
            failed = self.run_cli(package)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("source SHA256", failed.stderr)
            target.write_bytes(saved)
            (root / V["NATIVE"]).unlink()
            failed = self.run_cli(package)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("missing regular input", failed.stderr)

    def test_actual_optimized_cli_boolean_receipt_drift(self):
        with tempfile.TemporaryDirectory(prefix="p104-tensor-receipt-") as tmp:
            package = self.copy_export(Path(tmp))
            path = package / "RECEIPT.json"
            receipt = json.loads(path.read_text())
            receipt["schema_version"] = True
            path.write_text(json.dumps(receipt))
            failed = self.run_cli(package)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("complete receipt equality", failed.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
