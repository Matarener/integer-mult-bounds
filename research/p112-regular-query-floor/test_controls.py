#!/usr/bin/env python3
"""Behavioral and real-CLI controls. Nick Petalas, Apache-2.0."""

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
API = runpy.run_path(str(HERE / "verify.py"), run_name="regular_query_test_api")


class Controls(unittest.TestCase):
    def test_nonregular_field_boundary(self):
        columns = [(1, 1, 0), (1, 0, 1), (0, 1, 1)]
        self.assertEqual(
            API["solve"](columns, (1, 0, 0)),
            [Fraction(1, 2), Fraction(1, 2), Fraction(-1, 2)],
        )
        self.assertIsNone(API["solve"](columns, (1, 0, 0), 2))
        indicators = [tuple(int(p == j) for p in range(112)) for j in range(3)]
        readers = [[1] * 112 for _ in columns]
        with self.assertRaisesRegex(ValueError, "support transfer failed"):
            API["transfer"](columns, readers, indicators)

    def test_omitted_actual_reader(self):
        _, _, all_indicators, _ = API["geometry"]()
        indicators = [all_indicators[j] for j in (0, 1, 2, 30)]
        queries, readers = API["make_factorization"](
            API["dictionaries"]()["graph"], indicators
        )
        self.assertEqual(API["check_operator"](queries, readers, indicators), 12544)
        port = indicators[0].index(1)
        self.assertNotEqual(readers[4][port], 0)
        readers[4][port] = 0
        with self.assertRaisesRegex(ValueError, "operator mismatch"):
            API["check_operator"](queries, readers, indicators)

    def test_capacity_and_field_contracts(self):
        for columns, target, modulus in [
            ([(1,)] * 11, (1,), 0),
            ([(1, 0)], (1,), 0),
            ([(1,)], (1,), 7),
            ([(Fraction(1, 2),)], (1,), 2),
        ]:
            with (
                self.subTest(columns=len(columns), modulus=modulus),
                self.assertRaises(ValueError),
            ):
                API["solve"](columns, target, modulus)
        with self.assertRaises(ValueError):
            API["determinant"]([[1] * 5 for _ in range(5)])
        with self.assertRaises(ValueError):
            API["binary_rank"]([1 << 224])

    def test_real_cli_corruptions_and_restore(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as name:
            root = Path(name)
            package = root / "research" / HERE.name
            package.mkdir(parents=True)
            paths = list(HERE.iterdir())
            self.assertLessEqual(len(paths), 32)
            for path in paths:
                self.assertFalse(path.is_symlink())
                if path.is_file():
                    shutil.copyfile(path, package / path.name)
            source = root / API["DATA_PATH"]
            source.parent.mkdir(parents=True)
            shutil.copyfile(HERE.parent.parent / API["DATA_PATH"], source)
            self.check_cli_changes(package, source)

    def check_cli_changes(self, package, source):
        receipt = package / "RESULT.json"
        fixture = package / "RETAINED-RANK32.json"
        original = {path: path.read_bytes() for path in (receipt, fixture, source)}
        wrong = json.loads(original[receipt])
        wrong["whole_K_floor"] = 223
        boolean = json.loads(original[receipt])
        boolean["dictionaries"]["graph"]["requests_per_field"] = True
        mutations = [
            (receipt, json.dumps(wrong).encode(), "receipt mismatch"),
            (receipt, json.dumps(boolean).encode(), "receipt mismatch"),
            (
                receipt,
                b'{"whole_K_floor":224,' + original[receipt][1:],
                "duplicate JSON key",
            ),
            (fixture, original[fixture] + b" ", "source drift"),
            (source, original[source] + b" ", "source drift"),
            (source, None, "FileNotFoundError"),
        ]
        command = [
            sys.executable,
            "-I",
            "-O",
            "-Werror",
            "-B",
            str(package / "verify.py"),
        ]
        for path, replacement, diagnostic in mutations:
            with self.subTest(path=path.name, diagnostic=diagnostic):
                if replacement is None:
                    path.unlink()
                else:
                    path.write_bytes(replacement)
                result = subprocess.run(
                    command, capture_output=True, text=True, timeout=30, check=False
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(diagnostic, result.stderr)
                path.write_bytes(original[path])
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=30, check=False
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS_REGULAR_QUERY_FLOOR", result.stdout)


if __name__ == "__main__":
    unittest.main()
