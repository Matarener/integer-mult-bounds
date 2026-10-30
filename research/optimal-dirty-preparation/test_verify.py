"""Behavioral controls for the actual preparation and replay. Apache-2.0."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import compiler
import verify


def run_cli(root, package):
    command = [
        sys.executable,
        "-X",
        "pycache_prefix=" + str(root / "cache"),
        "-O",
        "-B",
        str(package / "verify.py"),
    ]
    return subprocess.run(
        command,
        cwd=root,
        env=dict(os.environ, PYTHONPATH=""),
        capture_output=True,
        text=True,
        timeout=30,
    )


def make_export(root):
    package = root / "research/optimal-dirty-preparation"
    package.mkdir(parents=True)
    for source in sorted(verify.PACKAGE.iterdir()):
        if source.is_file():
            shutil.copyfile(source, package / source.name)
    source = root / "research/q8-affine-dirty-compiler/README.md"
    source.parent.mkdir()
    shutil.copyfile(verify.ROOT / source.relative_to(root), source)
    return package, source


class PreparationTests(unittest.TestCase):
    def test_strict_improvement_and_dirty_spectator(self):
        pivot, program = compiler.preparation(4, 7, 7)
        self.assertEqual((pivot, len(program)), (0, 3))
        self.assertEqual(verify.dirty_fixture(4, 7, 7, 1, 3), 96)
        self.assertEqual(verify.dirty_fixture(4, 7, 7, 4, 7), 224)

    def test_invalid_boundaries(self):
        for args in (
            (0, 1, 1),
            (257, 1, 1),
            (3, 0, 1),
            (3, 8, 1),
            (3, True, 1),
            (2, 3, 3),
            (2, 1, 2),
        ):
            with self.subTest(args=args), self.assertRaises(ValueError):
                compiler.preparation(*args)
        row = [0] * 8
        for data, label, payload in (
            ([row, row], 1, 1),
            ([[0] * 8], 8, 1),
            ([[0] * 8], True, 1),
            ([[0] * 8], 1, 8),
            ([[False] * 8], 1, 1),
            ([[1 << 14336] * 8], 1, 1),
        ):
            with (
                self.subTest(label=label, payload=payload),
                self.assertRaises(ValueError),
            ):
                compiler.apply_coupling(data, 1, 1, label, payload)

    def test_deleted_or_reordered_preparation_rejected(self):
        original = compiler.preparation
        for kind in ("delete", "reverse"):

            def mutant(roles, u, v, kind=kind):
                pivot, program = original(roles, u, v)
                return pivot, program[:-1] if kind == "delete" else program[::-1]

            with (
                self.subTest(kind=kind),
                patch.object(compiler, "preparation", mutant),
                self.assertRaisesRegex(ValueError, "dirty Q8 operator mismatch"),
            ):
                verify.dirty_fixture(4, 7, 7, 1)

    def test_missing_return_and_wrong_pivot_rejected(self):
        execute = compiler.execute
        for kind in ("return", "pivot"):

            def mutant(data, pivot, program, swaps, payload, kind=kind):
                if kind == "pivot":
                    return execute(data, 3, program, swaps, payload)
                # Execute the correct program, then undo the required return.
                result = execute(data, pivot, program, swaps, payload)
                compiler.row_xors(result, program, payload)
                return result

            with (
                self.subTest(kind=kind),
                patch.object(compiler, "execute", mutant),
                self.assertRaisesRegex(ValueError, "dirty Q8 operator mismatch"),
            ):
                verify.dirty_fixture(4, 7, 7, 1)

    def test_correct_but_nonminimal_preparation_rejected(self):
        def two_star(roles, u, v):
            pivot = ((u & v) & -(u & v)).bit_length() - 1
            program = [(k, pivot) for k in range(roles) if k != pivot and u >> k & 1]
            program += [(pivot, k) for k in range(roles) if k != pivot and v >> k & 1]
            return pivot, tuple(program)

        with patch.object(compiler, "preparation", two_star):
            verify.dirty_fixture(4, 7, 7, 1)
        with (
            patch.object(verify, "preparation", two_star),
            self.assertRaisesRegex(ValueError, "BFS minimum mismatch"),
        ):
            verify.check_preparations()

    def test_git_free_cli_and_real_corruptions(self):
        with tempfile.TemporaryDirectory(prefix="optimal-preparation-") as temporary:
            root = Path(temporary)
            package, source = make_export(root)
            before = {p: p.read_bytes() for p in package.iterdir() if p.is_file()}
            good = run_cli(root, package)
            self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
            self.assertEqual(before, {p: p.read_bytes() for p in before})
            receipt = package / "RESULT.json"
            original = receipt.read_bytes()
            for kind in ("boolean", "cost", "duplicate"):
                value = json.loads(original)
                if kind == "boolean":
                    value["source_inputs"] = True
                elif kind == "cost":
                    value["three_role_noncentral_bit_xors"]["new"] = 65
                raw = json.dumps(value)
                if kind == "duplicate":
                    raw = raw[:-1] + ', "source_inputs":1}'
                receipt.write_text(raw)
                bad = run_cli(root, package)
                self.assertNotEqual(bad.returncode, 0, kind)
                self.assertIn(
                    "duplicate JSON key"
                    if kind == "duplicate"
                    else "typed receipt mismatch",
                    bad.stderr,
                )
            receipt.write_bytes(original)
            source.write_bytes(source.read_bytes() + b"\nchanged\n")
            bad = run_cli(root, package)
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("source drift", bad.stderr)
            source.unlink()
            bad = run_cli(root, package)
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("source missing or linked", bad.stderr)


if __name__ == "__main__":
    unittest.main()
