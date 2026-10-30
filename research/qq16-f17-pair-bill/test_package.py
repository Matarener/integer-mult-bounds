#!/usr/bin/env python3
"""Reject certificate corruption and duplicate JSON keys for the F17 pair bill."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUTS = (
    "research/qq16-producer-entry-contract/README.md",
    "research/qq16-finite-dyadic-format/README.md",
    "research/qq16-rounded-pair-bit-circuit/README.md",
    "research/qq16-rounded-producer-envelope/README.md",
)


def run(root, optimized=False):
    package = root / "research" / HERE.name
    environment = dict(os.environ, PYTHONPYCACHEPREFIX=str(root / ".cache"))
    flags = ["-Werror", "-I", "-B"]
    if optimized:
        flags.insert(2, "-O")
    return subprocess.run(
        [sys.executable, *flags, str(package / "verify.py")],
        cwd=root, env=environment, capture_output=True, text=True, timeout=60,
    )


class PackageTests(unittest.TestCase):
    def test_live_package_passes(self):
        outcome = run(ROOT)
        self.assertEqual(outcome.returncode, 0, outcome.stderr)
        self.assertIn("PASS_QQ16_F17_PAIR_BILL", outcome.stdout)
        self.assertIn("dirty_width=unsupplied", outcome.stdout)

    def copy_tree(self, root):
        package = root / "research" / HERE.name
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
        for name in INPUTS:
            destination = root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, destination)
        return package

    def test_temp_copy_certificate_corruption(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = self.copy_tree(root)
            self.assertEqual(run(root).returncode, 0)
            self.assertEqual(run(root, optimized=True).returncode, 0)
            original = (package / "CERTIFICATE.json").read_bytes()
            payload = json.loads(original)
            payload["W"] = 531
            replacements = [
                json.dumps(payload).encode(),
                b'{"schema_version": 1, "schema_version": 1}\n',
                b'{"W": true}\n',
                b'{"status": "PASS_QQ16_F17_PAIR_BILL"}\n',
            ]
            for replacement in replacements:
                (package / "CERTIFICATE.json").write_bytes(replacement)
                for optimized in (False, True):
                    outcome = run(root, optimized=optimized)
                    self.assertNotEqual(outcome.returncode, 0)
                    self.assertIn("FAIL_QQ16_F17_PAIR_BILL", outcome.stderr)
            (package / "CERTIFICATE.json").write_bytes(original)
            self.assertEqual(run(root, optimized=True).returncode, 0)

    def test_duplicate_json_key_message(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = self.copy_tree(root)
            (package / "CERTIFICATE.json").write_text('{"W": 532, "W": 456}\n', encoding="utf-8")
            outcome = run(root, optimized=True)
            self.assertNotEqual(outcome.returncode, 0)
            self.assertIn("duplicate JSON key", outcome.stderr)

    def test_source_drift_and_independent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.copy_tree(root)
            source = root / INPUTS[0]
            source.write_bytes(source.read_bytes() + b"\n")
            outcome = run(root)
            self.assertNotEqual(outcome.returncode, 0)
            self.assertIn("source hash", outcome.stderr)
        environment = dict(os.environ, PYTHONPYCACHEPREFIX=str(ROOT / ".cache-independent"))
        outcome = subprocess.run(
            [sys.executable, "-Werror", "-I", "-B", str(HERE / "independent.py")],
            cwd=ROOT, env=environment, capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(outcome.returncode, 0, outcome.stderr)
        self.assertIn("PASS_QQ16_F17_PAIR_BILL_INDEPENDENT", outcome.stdout)
        source = (HERE / "independent.py").read_text(encoding="utf-8")
        self.assertNotIn("import verify", source)
        self.assertNotIn("from verify", source)


if __name__ == "__main__":
    unittest.main()
