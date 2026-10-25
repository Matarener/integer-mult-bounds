#!/usr/bin/env python3
"""Actual optimized CLI controls for the S4 cut certificate. Apache-2.0."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUTS = json.loads((HERE / "VERIFY.json").read_bytes())["inputs"]


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="s4-subspace-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.package = self.root / "research" / HERE.name
        self.package.mkdir(parents=True)
        for name in (
            "verify.py",
            "independent.py",
            "test_package.py",
            "RESULT.json",
            "SOURCES.json",
            "VERIFY.json",
        ):
            path = HERE / name
            self.assertFalse(path.is_symlink())
            raw = path.read_bytes()
            self.assertEqual((self.package / name).write_bytes(raw), len(raw))
        for relative in INPUTS:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / relative).read_bytes())

    def execute(self, name, success, message=""):
        result = subprocess.run(
            [sys.executable, "-I", "-O", "-Werror", "-B", str(self.package / name)],
            capture_output=True,
            text=True,
            timeout=60,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        if message:
            self.assertIn(message, result.stdout + result.stderr)

    def change(self, name, old, new):
        path = self.package / name
        source = path.read_text()
        self.assertIn(old, source)
        path.write_text(source.replace(old, new, 1))

    def test_git_free_optimized_positive(self):
        self.execute("verify.py", True, "PASS_S4_SUBSPACE_CUT_BOUNDARY")
        self.execute("independent.py", True, "PASS_INDEPENDENT_S4_SUBSPACE_CUTS")

    def test_counterfeit_source_and_capacity(self):
        source = self.root / INPUTS[0]
        source.write_bytes(source.read_bytes() + b"changed")
        self.execute("verify.py", False, "source SHA256")
        source.write_bytes(b"x" * 131073)
        self.execute("verify.py", False, "input capacity")

    def test_false_receipt_and_boolean_alias(self):
        path = self.package / "RESULT.json"
        original = path.read_text()
        receipt = json.loads(original)
        receipt["attainment"]["tuple_bound"] = 21
        path.write_text(json.dumps(receipt))
        self.execute("verify.py", False, "result receipt")
        receipt = json.loads(original)
        receipt["natural_binary"]["dimension_counts"][0] = True
        path.write_text(json.dumps(receipt))
        self.execute("verify.py", False, "result receipt")
        self.execute("independent.py", False, "complete independent inventory")

    def test_incomplete_noncoordinate_domain(self):
        self.change(
            "verify.py",
            "if vector not in space:",
            "if vector not in space and vector.bit_count() == 1:",
        )
        self.execute("verify.py", False, "Gaussian binomial completeness")

    def test_wrong_operator_and_wrong_dual(self):
        self.change("verify.py", "(3, 1, 2, 0)", "(0, 1, 2, 3)")
        self.execute("verify.py", False, "ordered-pair profile")
        self.change("independent.py", "(4, 2, 4)", "(4, 1, 4)")
        self.execute("independent.py", False, "strong module inequality")

    def test_duplicate_and_nonfinite_json(self):
        path = self.package / "RESULT.json"
        path.write_text('{"status":0,"status":1}')
        self.execute("verify.py", False, "duplicate JSON key")
        path.write_text('{"status":NaN}')
        self.execute("verify.py", False, "noninteger JSON number")


if __name__ == "__main__":
    unittest.main()
