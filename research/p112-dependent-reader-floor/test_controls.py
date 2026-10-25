"""Behavioral and optimized CLI controls. Nick Petalas. Apache-2.0."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
# The only dynamically selected import is this package's primary checker.
sys.path.insert(0, str(HERE))
import verify as subject  # noqa: E402


class Controls(unittest.TestCase):
    def test_axis_images_and_supports(self):
        directions = (
            (Fraction(1), Fraction(0)),
            (Fraction(0), Fraction(1)),
            (Fraction(1), Fraction(5, 7)),
        )
        images = subject.binary_directions(directions)
        self.assertEqual(images[directions[0]], (1, 0))
        self.assertEqual(images[directions[1]], (0, 1))
        self.assertEqual(images[directions[2]], (1, 1))
        self.assertEqual(
            subject.binary_solution([(1, 0), (0, 1), (1, 1)], 6, (1, 0)), 6
        )
        with self.assertRaisesRegex(ValueError, "no support-dominated"):
            subject.binary_solution([(1, 1)], 1, (1, 0))

    def test_direction_capacity_and_proportionality(self):
        self.assertEqual(subject.direction((Fraction(-2, 3), Fraction(-4, 3))), (1, 2))
        self.assertIsNone(subject.direction((0, 0)))
        with self.assertRaisesRegex(ValueError, "two or three"):
            subject.binary_directions(((1, 0), (0, 1), (1, 1), (1, 2)))
        with self.assertRaisesRegex(ValueError, "distinct"):
            subject.binary_directions(((1, 1), (1, 1)))

    def test_bad_reader_and_operator(self):
        a = [1] + [0] * 111
        b = [0, 1] + [0] * 110
        empty = [[0] * 112 for _ in range(3)]
        with self.assertRaisesRegex(ValueError, "no support-dominated"):
            subject.replace(((1, 1), (1, 2), (1, 3)), empty, a, b)
        with self.assertRaisesRegex(ValueError, "pair identity"):
            subject.identity(a, b, empty, empty)
        with self.assertRaisesRegex(ValueError, "disjoint"):
            subject.replace(((1, 0), (0, 1)), empty[:2], a, a)

    def test_rank_and_tariff_asymmetry(self):
        self.assertEqual(subject.rank([0b101, 0b011, 0b110], 3), 2)
        self.assertEqual(subject.rank([0b100, 0b010, 0b001], 3), 3)
        with self.assertRaisesRegex(ValueError, "binary row"):
            subject.rank([8], 3)
        # A zero actual reader costs zero even when the query has full source support.
        self.assertEqual(
            subject.bill([1, 2], {0: [0, 1], 1: [0, 1]}, [[1, 1]], [[0, 0]]), 0
        )

    def test_optimized_cli_mutants_and_restore(self):
        with tempfile.TemporaryDirectory(prefix="dependent-controls-") as directory:
            root = Path(directory)
            package = root / "research" / HERE.name
            shutil.copytree(
                HERE,
                package,
                copy_function=shutil.copyfile,
                ignore=shutil.ignore_patterns("__pycache__", ".ruff_cache"),
            )
            input_path = root / subject.INPUT
            input_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / subject.INPUT, input_path)
            changes = (
                (input_path, "verify.py", "source SHA256"),
                (package / "RETAINED-RANK32.json", "verify.py", "source SHA256"),
                (package / "RESULT.json", "verify.py", "receipt mismatch"),
                (input_path, "independent.py", "live labels"),
            )
            for path, script, message in changes:
                original = path.read_bytes()
                path.write_bytes(original + b" ")
                result = self.run_cli(package, script)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)
                path.write_bytes(original)
            # Receipt mutation must change a mathematical value, not merely formatting.
            receipt = package / "RESULT.json"
            original = receipt.read_bytes()
            value = json.loads(original)
            value["literal_baseline_tariff"] = 223
            receipt.write_text(json.dumps(value, indent=2) + "\n")
            result = self.run_cli(package, "verify.py")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("receipt mismatch", result.stderr)
            receipt.write_bytes(original)
            result = self.run_cli(package, "verify.py")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("PASS_DEPENDENT_READER_FLOOR", result.stdout)

    @staticmethod
    def run_cli(package, script):
        environment = dict(os.environ)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [sys.executable, "-I", "-O", "-Werror", "-B", str(package / script)],
            cwd=package.parents[1],
            env=environment,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
