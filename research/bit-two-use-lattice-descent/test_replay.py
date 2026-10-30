#!/usr/bin/env python3
"""CLI failure controls in isolated source trees, normal and optimized Python.

Prepared for @CubeJerry with OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha256, sha1
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
SOURCE = "research/bit-fifth-frame-determinant-obstruction/README.md"


class ReplayControls(unittest.TestCase):
    def run_case(self, mutate=None, expected_error=None):
        for optimized in (False, True):
            with self.subTest(optimized=optimized), tempfile.TemporaryDirectory(prefix="bit-descent-") as tmp:
                root = Path(tmp)
                package = root / "research" / PACKAGE.name
                package.mkdir(parents=True)
                for name in ("verify.py", "SOURCES.json", "RESULT.json"):
                    shutil.copyfile(PACKAGE / name, package / name)
                source = root / SOURCE
                source.parent.mkdir(parents=True)
                shutil.copyfile(ROOT / SOURCE, source)
                if mutate:
                    mutate(package, source)
                before = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}
                argv = [sys.executable, "-I", "-B", "-W", "error"]
                if optimized:
                    argv.append("-O")
                argv.append(str(package / "verify.py"))
                env = dict(os.environ, PATH="", PYTHONDONTWRITEBYTECODE="1")
                result = subprocess.run(argv, cwd=root, env=env, text=True, capture_output=True, timeout=60)
                after = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}
                self.assertEqual(before, after, "verification changed the exported inputs")
                if expected_error is None:
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn("PASS_BIT_TWO_USE_LATTICE_DESCENT", result.stdout)
                else:
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(expected_error, result.stderr)
                    self.assertNotIn("PASS_BIT_TWO_USE_LATTICE_DESCENT", result.stdout)

    def test_clean_source_export(self):
        self.run_case()

    def test_corrupted_source(self):
        self.run_case(lambda p, s: s.write_bytes(s.read_bytes() + b"\n"), "source SHA256 mismatch")

    def test_repinned_corrupted_source(self):
        def mutate(package, source):
            raw = source.read_bytes() + b" altered"
            source.write_bytes(raw)
            path = package / "SOURCES.json"
            data = json.loads(path.read_text())
            row = next(row for row in data["files"] if row["path"] == SOURCE)
            row["sha256"] = sha256(raw).hexdigest()
            row["git_blob"] = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            path.write_text(json.dumps(data))
        self.run_case(mutate, "source SHA256 mismatch")

    def test_manifest_pin_only(self):
        def mutate(package, source):
            path = package / "SOURCES.json"
            data = json.loads(path.read_text())
            next(row for row in data["files"] if row["path"] == SOURCE)["git_blob"] = "0" * 40
            path.write_text(json.dumps(data))
        self.run_case(mutate, "source manifest binding mismatch")

    def test_wrong_rank_receipt(self):
        self.receipt_mutation(lambda d: d["candidate"].update(contracted_target_rank=2))

    def test_wrong_profile_receipt(self):
        self.receipt_mutation(lambda d: d["candidate"]["profile"].update(S=1))

    def test_boolean_integer_receipt(self):
        self.receipt_mutation(lambda d: d["candidate"]["raw_characters"][0].update(calls=False))

    def receipt_mutation(self, change):
        def mutate(package, source):
            path = package / "RESULT.json"
            data = json.loads(path.read_text())
            change(data)
            path.write_text(json.dumps(data))
        self.run_case(mutate, "RESULT.json differs from recomputed evidence")


if __name__ == "__main__":
    unittest.main(verbosity=2)
