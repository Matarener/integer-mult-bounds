#!/usr/bin/env python3
"""Behavioral and optimized actual-CLI controls for the reader boundary."""

import importlib.util
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
SPEC = importlib.util.spec_from_file_location("boundary_check", HERE / "verify.py")
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


def prepare_export(root):
    package = root / "research" / HERE.name
    shutil.copytree(HERE, package)
    source = root / CHECK.SOURCE
    source.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / CHECK.SOURCE, source)
    env = dict(os.environ, PATH="", PYTHONPYCACHEPREFIX=str(root / "pycache"))
    command = [
        sys.executable,
        "-I",
        "-O",
        "-Werror",
        "-B",
        str(package / "verify.py"),
    ]
    return package, source, env, command


class BoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.labels, cls.groups, cls.cert = CHECK.load()
        cls.queries, cls.outputs = CHECK.construct(cls.groups, cls.cert)

    def test_actual_reader_is_not_source(self):
        rows = CHECK.invoice(self.labels, self.groups, self.queries, self.outputs)
        self.assertEqual(sum(r["self_rank"] for r in rows), 218)
        self.assertEqual(sum(r["reader_rank"] for r in rows), 244)
        self.assertEqual((rows[0]["self_rank"], rows[0]["reader_rank"]), (2, 4))
        self.assertNotEqual(rows[0]["source_closure"], rows[0]["reader_closure"])

    def test_literal_fit_attains_224(self):
        supports = CHECK.geometry(self.groups)[2]
        rows = [[int(p in s) for p in range(112)] for s in supports]
        bill = CHECK.invoice(self.labels, self.groups, rows, rows)
        self.assertEqual(sum(r["reader_rank"] for r in bill), 224)
        self.assertEqual(CHECK.identities(self.labels, self.groups, rows, rows), 11392)

    def test_query_is_outside_old_rowspace(self):
        values = {self.queries[0][p] for p in self.groups[1][::2]}
        self.assertEqual(values, {0, 1})

    def test_wrong_decoder_rejects_exact_identity(self):
        wrong = [r[:] for r in self.outputs]
        wrong[0] = [0] * 112
        with self.assertRaisesRegex(ValueError, "UQ=K"):
            CHECK.identities(self.labels, self.groups, self.queries, wrong)

    def test_det2_needs_half_and_fails_mod_two(self):
        matrix = [CHECK.DIRECTIONS[k] for k in (2, 4, 5)]
        inverse = CHECK.inverse3(matrix)
        self.assertTrue(all(x.denominator == 2 for r in inverse[:2] for x in r))
        bits = [sum((x % 2) << j for j, x in enumerate(r)) for r in matrix]
        self.assertEqual(len(CHECK.binary_basis(bits, 3)), 2)
        with self.assertRaisesRegex(ValueError, "singular"):
            CHECK.inverse3([CHECK.DIRECTIONS[k] for k in (0, 1, 2)])

    def test_binary_capacity_rejects(self):
        with self.assertRaisesRegex(ValueError, "capacity"):
            CHECK.binary_basis([0] * 225, 9)
        with self.assertRaisesRegex(ValueError, "binary row"):
            CHECK.binary_basis([512], 9)

    def test_actual_cli_in_git_free_export(self):
        with tempfile.TemporaryDirectory(prefix="reader-boundary-") as directory:
            root = Path(directory)
            package, source, env, command = prepare_export(root)
            good = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=root,
                env=env,
                check=False,
            )
            self.assertEqual(good.returncode, 0, good.stderr)
            for filename, mode, error in (
                ("RESULT.json", "undercharge", "receipt differs"),
                ("CERTIFICATE.json", "duplicate", "duplicate seed"),
                ("RETAINED-RANK32.json", "bytes", "SHA256"),
            ):
                target = package / filename
                before = target.read_bytes()
                if mode == "bytes":
                    target.write_bytes(before + b" ")
                else:
                    value = json.loads(before)
                    if mode == "undercharge":
                        value["actual_source_reader_sum"] = 218
                    else:
                        value["replacements"][0]["seed_ports"] *= 2
                    target.write_text(json.dumps(value))
                mutated = target.read_bytes()
                bad = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=root,
                    env=env,
                    check=False,
                )
                self.assertNotEqual(bad.returncode, 0)
                self.assertIn(error, bad.stderr)
                self.assertEqual(target.read_bytes(), mutated)
                target.write_bytes(before)
            source.write_bytes(source.read_bytes() + b" ")
            bad = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=root,
                env=env,
                check=False,
            )
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("SHA256", bad.stderr)


if __name__ == "__main__":
    unittest.main()
