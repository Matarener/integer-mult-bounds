"""Behavioral controls for sharp-profile derivation and the paid invoice boundary."""

import copy
import gzip
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.roles = verify.nomination(verify.ROOT, verify.PACKAGE)
        cls.audit, cls.local = verify.audit_nomination(verify.ROOT, cls.roles)

    def test_exact_source_nomination(self):
        self.assertEqual(len(self.roles), 69120)
        self.assertEqual(self.audit["idle"], {1: 2431, 17: 1, 48: 4887})
        self.assertEqual(self.audit["rank_mass"], 1041408)
        self.assertEqual(self.audit["cross_replica_roles"], 60344)

    def test_literal_owner_change_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "package"
            shutil.copytree(verify.PACKAGE, package)
            rows = copy.deepcopy(self.roles)
            rows[0]["family"] += 1
            (package / "data/OWNERS.json.gz").write_bytes(
                gzip.compress(verify.canonical(rows))
            )
            with self.assertRaisesRegex(ValueError, "literal nomination differs"):
                verify.nomination(verify.ROOT, package)

    def test_retained_certificate_change_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "package"
            shutil.copytree(verify.PACKAGE, package)
            path = package / "predecessor/CERTIFICATE.json"
            path.write_bytes(path.read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "retained source bytes"):
                verify.check_sources(verify.ROOT, package)

    def test_paid_cost_or_type_change_rejected(self):
        baseline = {"cost": 1, "nested": {"row": 16469}, "template_sha256": "old"}
        serialization = {"nested": {"row": 16469}, "cost": 1, "template_sha256": "new"}
        self.assertEqual(
            verify.paid_invoice(baseline), verify.paid_invoice(serialization)
        )
        for mutated in (
            {"cost": True, "nested": {"row": 16469}},
            {"cost": 1.0, "nested": {"row": 16469}},
            {"cost": 1, "nested": {"row": 16470}},
            {"cost": 1},
            {"cost": 1, "nested": {"row": 16469}, "extra": 0},
        ):
            self.assertNotEqual(
                verify.paid_invoice(baseline), verify.paid_invoice(mutated)
            )

    def test_duplicate_json_key_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text('{"cost":1,"cost":2}')
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                verify.read_json(path)

    def test_source_mutation_at_actual_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "root"
            first = next(
                pin
                for pin in verify.read_json(verify.PACKAGE / "SOURCES.json")["files"]
                if pin["usage"] == "input"
            )
            changed = root / first["path"]
            changed.parent.mkdir(parents=True)
            changed.write_bytes((verify.ROOT / first["path"]).read_bytes() + b" ")
            work = Path(directory) / "work"
            result = subprocess.run(
                [
                    sys.executable,
                    "-I",
                    "-Werror",
                    "-B",
                    str(verify.PACKAGE / "verify.py"),
                    "--root",
                    str(root),
                    "--work",
                    str(work),
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
                env={k: v for k, v in os.environ.items() if k != "PYTHONOPTIMIZE"},
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source bytes:", result.stderr)
            self.assertFalse((work / "strict").exists())

    def test_optimized_full_admission_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [
                    sys.executable,
                    "-I",
                    "-O",
                    "-Werror",
                    "-B",
                    str(verify.PACKAGE / "verify.py"),
                    "--work",
                    str(Path(directory) / "work"),
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unchanged predecessor assertions", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
