"""Behavioral controls, also required under optimized Python. Apache-2.0."""

import subprocess
import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import invariant as inv
import oracle
import verify


class Controls(unittest.TestCase):
    def test_actual_arithmetic_and_order_faults(self):
        with patch.object(inv, "chronological", return_value=(0, 0, 0)):
            with self.assertRaisesRegex(ValueError, "chronological"):
                verify.check_word((7, 7, 7), (1, 1, 1))
        with patch.object(oracle, "LEFT_J", oracle.LEFT_I):
            with self.assertRaises(ValueError):
                verify.quotient_contract()
        with patch.object(inv, "rank", return_value=0):
            with self.assertRaisesRegex(ValueError, "rank"):
                verify.check_word((1, 2), (1, 2))
        real = inv.quotient_product
        with patch.object(inv, "quotient_product", side_effect=lambda a, b: real(b, a)):
            with self.assertRaisesRegex(ValueError, "chronological"):
                verify.check_word((1, 3), (1, 2))

    def test_boundaries_and_cli_collision(self):
        for rows, labels in (((0,), (1,)), ((1,), (True,)), ((1,), (3,)),
                             ((1,), ()), ((1,) * 13, (1,) * 13)):
            with self.assertRaises(ValueError):
                inv.chronological(rows, labels)
        with self.assertRaises(ValueError):
            inv.quotient_product(True, 1)
        with tempfile.TemporaryDirectory(prefix="q8-cli-control-") as temporary:
            receipt = Path(temporary) / "receipt.json"
            receipt.write_bytes(b"original\n")
            result = subprocess.run([sys.executable, "-I", "-O", "-B",
                                     str(verify.ROOT / "verify.py"), "--write", str(receipt)],
                                    capture_output=True, timeout=20)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b"refuse to overwrite", result.stderr)
            self.assertEqual(receipt.read_bytes(), b"original\n")

    def test_actual_native_action_fault(self):
        with tempfile.TemporaryDirectory(prefix="q8-native-control-") as temporary:
            root = Path(temporary)
            (root / "inputs").mkdir()
            for name in ("finite.cpp", "inputs/pr3471-RESULT.json", "inputs/pr3471-search.cpp"):
                source = verify.ROOT / name
                if not source.is_file() or source.is_symlink():
                    raise ValueError("source must be a regular file")
                raw = source.read_bytes()
                if name.endswith("search.cpp"):
                    old = b"const unsigned delta = s ^ t[f.g][s];"
                    self.assertEqual(raw.count(old), 1)
                    raw = raw.replace(old, b"const unsigned delta = s ^ t[f.g][s] ^ 1U;")
                with (root / name).open("xb") as output:
                    output.write(raw)
            with patch.object(verify, "ROOT", root):
                with self.assertRaises((ValueError, subprocess.CalledProcessError)):
                    verify.native_check(root)

    def test_actual_receipt_corruption(self):
        with tempfile.TemporaryDirectory(prefix="q8-receipt-control-") as temporary:
            root = Path(temporary)
            names = (*verify.source_hashes(), "RESULT.json")
            for name in names:
                source = verify.ROOT / name
                source_stat = source.lstat()
                self.assertTrue(stat.S_ISREG(source_stat.st_mode))
                self.assertEqual(source_stat.st_uid, os.getuid())
                destination = root / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                with destination.open("xb") as output:
                    output.write(source.read_bytes())
                copied = destination.lstat()
                self.assertNotEqual((copied.st_dev, copied.st_ino),
                                    (source_stat.st_dev, source_stat.st_ino))
            receipt = root / "RESULT.json"
            result = json.loads(receipt.read_text())
            result["status"] = "CORRUPTED"
            receipt.write_text(json.dumps(result))
            completed = subprocess.run([sys.executable, "-I", "-O", "-Werror", "-B",
                                        str(root / "verify.py")], capture_output=True, timeout=180)
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn(b"receipt mismatch", completed.stderr)


if __name__ == "__main__":
    unittest.main()
