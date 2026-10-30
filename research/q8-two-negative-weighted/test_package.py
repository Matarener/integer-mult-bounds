"""Behavioral controls for real producers, dirty endpoints and scope guards."""

from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import oracle
import tariff
import verify

PACKAGE = Path(__file__).resolve().parent


class Controls(unittest.TestCase):
    def test_real_compiler_mutations(self):
        target = (0, 3, 5, 2)
        word = tariff.optimal_word(target, 100, 1)
        expected = oracle.expected(target)
        self.assertEqual(oracle.columns(word, target), expected)
        with patch.object(tariff, "witness", return_value=word[1:]):
            mutant = tariff.optimal_word(target, 100, 1)
            with self.assertRaisesRegex(ValueError, "witness counts"):
                verify.check_witness(target, mutant, tariff.counts(word))
        wrong = tariff.witness(target, 2)
        self.assertEqual(oracle.columns(wrong, target), expected)
        ni, nj = tariff.counts(wrong)
        self.assertGreater(100 * ni + nj, tariff.minimum(target, 100, 1))
        leaked = ((3, 2, 2),) + word[1:]
        self.assertNotEqual(oracle.columns(leaked, target), expected)

    def test_price_and_domain_boundaries(self):
        target = (3, 3)
        self.assertEqual(tariff.frontier(target), ((2, 4), (4, 2), (6, 0)))
        self.assertEqual(tariff.minimum(target, 10, 1), 24)
        self.assertEqual(tariff.minimum(target, 0, Fraction(7, 3)), 0)
        for bad in (-1, True, 1.0, "1"):
            with self.assertRaisesRegex(ValueError, "price"):
                tariff.minimum(target, bad, 1)
        for bad in ((3, 5, 3, 0), (3, 5, 2, 4), (3, 0), (3, 6), (True, 5)):
            with self.assertRaises(ValueError):
                tariff.frontier(bad)
        for pair in ((1, 7), (3, 3), (2, 2), (True, 6), (50, 0)):
            with self.assertRaises(ValueError):
                tariff.dominated(target, pair)

    def test_first_order_and_oracle_faults(self):
        target = (3, 5)
        word = tariff.witness(target, 1)
        with patch.object(oracle, "multiply", side_effect=lambda a, b: b):
            with self.assertRaisesRegex(ValueError, "independent group table"):
                verify.oracle_table()
        with patch.object(oracle, "columns", return_value=oracle.expected((0, 0))):
            with self.assertRaisesRegex(ValueError, "all dirty columns"):
                verify.check_witness(target, word, tariff.counts(word))
        for a in range(8):
            for b in range(8):
                self.assertEqual(oracle.multiply(a, b), verify.model.GROUP[a][b])

    def test_retained_bytes_and_receipt_guards(self):
        original = verify.PACKAGE
        with tempfile.TemporaryDirectory(prefix="q8-price-control-") as directory:
            temporary = Path(directory)
            (temporary / "inputs").mkdir()
            rows = json.loads((original / "inputs/RETENTION.json").read_text())
            rows[0]["sha256"] = "0" * 64
            (temporary / "inputs/RETENTION.json").write_text(json.dumps(rows))
            with patch.object(verify, "PACKAGE", temporary):
                with self.assertRaisesRegex(ValueError, "retained regular file"):
                    verify.retained_sources()
                first = temporary / rows[0]["retained_path"]
                first.parent.mkdir(parents=True)
                first.write_bytes((original / rows[0]["retained_path"]).read_bytes())
                with self.assertRaisesRegex(ValueError, "retained source drift"):
                    verify.retained_sources()
            receipt = temporary / "occupied.json"
            receipt.write_text("preserve me\n")
            command = [
                sys.executable,
                "-I",
                "-O",
                "-Werror",
                "-B",
                str(original / "verify.py"),
                "--write-result",
                str(receipt),
            ]
            done = subprocess.run(command, capture_output=True, text=True, timeout=30)
            self.assertNotEqual(done.returncode, 0)
            self.assertIn("refuse receipt overwrite", done.stderr)
            self.assertEqual(receipt.read_text(), "preserve me\n")


if __name__ == "__main__":
    unittest.main()
