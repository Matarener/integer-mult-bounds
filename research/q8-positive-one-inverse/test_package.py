#!/usr/bin/env python3
"""Behavioral failures for the actual Q8 verifier. Nick Petalas. Apache-2.0."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import model  # noqa: E402
import verify  # noqa: E402


class BoundaryTests(unittest.TestCase):
    def test_wrong_producers(self):
        # Removing the sign-producing calls preserves the sign-blind quotient.
        genuine = model.construction

        def positive_only(targets, alpha, beta):
            return genuine(tuple(g & ~1 for g in targets), alpha, beta)

        with (
            patch.object(model, "construction", positive_only),
            self.assertRaisesRegex(ValueError, "tariff mismatch|endpoint"),
        ):
            verify.fixture_checks()
        with (
            patch.object(model, "tariff", return_value=0),
            self.assertRaisesRegex(ValueError, "tariff mismatch"),
        ):
            verify.fixture_checks()
        targets = (3, 4, 0)
        word = genuine(targets, 1, 1) + ((2, 4, 4),)
        # Active outputs remain correct, but the dirty spectator no longer restores.
        matrix = model.evaluate(word, 3)
        self.assertEqual(matrix[:6], model.endpoint(targets)[:6])
        with self.assertRaisesRegex(ValueError, "endpoint"):
            verify.check_word(word, targets)

    def test_scope_boundaries(self):
        for call in ((3, 1, 1), (4, 1, 2), (2, 0, 1), (2, 4, 1)):
            with self.assertRaises(ValueError):
                model.evaluate((call,), 2)
        for args in (((3, 5), 1, 1), ((1,), 1, 1), ((3,), -1, 2)):
            with self.assertRaises(ValueError):
                model.tariff(*args)
        with self.assertRaises(ValueError):
            model.evaluate(((2, 1, 1),) * 65, 1)

    def test_actual_receipt_source_and_overwrite_failures(self):
        # A relocated package uses the real CLI; all disposable paths stay in TMPDIR.
        with tempfile.TemporaryDirectory(prefix="q8-one-inverse-") as temporary:
            root = Path(temporary)
            relocated = root / "research" / PACKAGE.name
            relocated.mkdir(parents=True)
            for path in PACKAGE.rglob("*"):
                if path.is_file():
                    target = relocated / path.relative_to(PACKAGE)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(path.read_bytes())
            manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
            for row in manifest["files"]:
                if row["usage"] == "input":
                    target = root / row["path"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes((PACKAGE.parents[1] / row["path"]).read_bytes())
            self.run_cli(relocated, True)
            receipt = relocated / "RESULT.json"
            saved = receipt.read_bytes()
            mutated = saved.decode().replace('"new_kappa": false', '"new_kappa": 0')
            receipt.write_text(mutated)
            self.run_cli(relocated, False, "receipt differs")
            receipt.write_bytes(saved)
            self.run_cli(relocated, False, "FileExistsError", "--write", str(receipt))
            source = root / next(
                row["path"] for row in manifest["files"] if row["usage"] == "input"
            )
            source.write_bytes(source.read_bytes() + b"\n")
            self.run_cli(relocated, False, "source changed")

    def run_cli(self, package, succeeds, message="", *arguments):
        result = subprocess.run(
            [
                sys.executable,
                "-I",
                "-O",
                "-Werror",
                "-B",
                str(package / "verify.py"),
                *arguments,
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(
            result.returncode == 0, succeeds, result.stdout + result.stderr
        )
        if message:
            self.assertIn(message, result.stderr)


if __name__ == "__main__":
    unittest.main()
