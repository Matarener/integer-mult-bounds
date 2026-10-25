#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Observable endpoint, dirty-state, frame-gap and source-export controls."""

import importlib.util
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
SPEC = importlib.util.spec_from_file_location(
    "p104_omitted_completion", HERE / "verify.py"
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("fixed local verifier loader unavailable")
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class CompletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word, cls.native = VERIFY.read_sources()
        cls.selected, cls.inputs, _, _ = VERIFY.projection(
            cls.word, VERIFY.bind_frames(cls.word, cls.native)
        )
        cls.full, cls.full_frames = VERIFY.linear_map(cls.word, None)
        cls.sliced, cls.slice_frames = VERIFY.linear_map(cls.word, cls.selected)
        cls.residual = VERIFY.residual_map(cls.full, cls.sliced, cls.inputs)
        cls.gather, cls.scatter = VERIFY.factor(cls.residual)

    def test_all_public_rows_and_minimum_summary_dimension(self):
        VERIFY.check_factor(self.residual, self.gather, self.scatter)
        square = [
            [self.residual[target].get(source, Fraction()) for source in VERIFY.COLUMNS]
            for target in VERIFY.BASIS
        ]
        determinant, _ = VERIFY.inverse_minor(square)
        self.assertEqual(determinant, Fraction(-1, 128))
        self.assertEqual(len(self.residual), 52)
        for name in self.inputs:
            self.assertEqual(self.full[name], self.sliced[name])

    def test_one_dirty_helper_for_all_104_source_columns(self):
        names = self.word["initial_frames"]
        for column in range(104):
            values = {name: Fraction() for name in names}
            source = f"Y{column}"
            values[source] = Fraction(2)
            for dirty in (Fraction(-7), Fraction(0), Fraction(11)):
                patched, restored = VERIFY.serial_completion(
                    values, dirty, self.gather, self.scatter
                )
                self.assertEqual(restored, dirty)
                for target in names:
                    expected = values[target] + 2 * self.residual.get(target, {}).get(
                        source, 0
                    )
                    self.assertEqual(patched[target], expected)
                    self.assertEqual(patched[target].denominator, 1)

    def test_zero_residual_does_not_supply_frames(self):
        omitted = set(self.full) - self.inputs
        zero = omitted - set(self.residual)
        self.assertEqual(len(zero), 41)
        self.assertEqual(len(omitted), 93)
        for name in omitted:
            self.assertNotEqual(self.slice_frames[name], self.full_frames[name])
        for name in zero:
            self.assertEqual(self.full[name], self.sliced[name])
        self.assertEqual(self.slice_frames["N10"], [])
        self.assertEqual(len(self.full_frames["N10"]), 9)

    def test_sparse_projection_cannot_be_an_all_bank_replacement(self):
        values = {name: Fraction() for name in self.word["initial_frames"]}
        target = VERIFY.BASIS[0]
        source = next(iter(self.residual[target]))
        values[source] = Fraction(4)
        full = VERIFY.evaluate(self.word, None, values)
        sliced = VERIFY.evaluate(self.word, self.selected, values)
        self.assertNotEqual(full[target], sliced[target])
        result, dirty = VERIFY.serial_completion(
            sliced, Fraction(17), self.gather, self.scatter
        )
        self.assertEqual(result, full)
        self.assertEqual(dirty, 17)

    def test_rejecting_controls(self):
        controls = VERIFY.controls(
            self.word, self.native, self.residual, self.gather, self.scatter
        )
        self.assertEqual(len(controls), 6)
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            json.loads('{"a":1,"a":2}', object_pairs_hook=VERIFY.unique)
        with self.assertRaisesRegex(ValueError, "singular minor"):
            VERIFY.inverse_minor([[Fraction()] * 8 for _ in range(8)])

    def test_optimized_git_free_export_cli_and_drift(self):
        with tempfile.TemporaryDirectory(prefix="p104-completion-") as directory:
            root = Path(directory)
            package = root / "research/p104-omitted-completion"
            package.mkdir(parents=True)
            for name in ("verify.py", "CERTIFICATE.json"):
                shutil.copyfile(HERE / name, package / name)
            for name in VERIFY.HASHES:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(VERIFY.ROOT / name, target)
            argv = [
                sys.executable,
                "-I",
                "-O",
                "-Werror",
                "-B",
                str(package / "verify.py"),
            ]
            env = dict(os.environ, PATH="/nonexistent", PYTHONDONTWRITEBYTECODE="1")

            def invoke():
                return subprocess.run(
                    argv,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=False,
                )

            run = invoke()
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn("rank=8 frame_gaps=93", run.stdout)
            source = root / VERIFY.WORD
            original = source.read_bytes()
            source.write_bytes(original + b"\n")
            run = invoke()
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("source hash", run.stderr)
            source.write_bytes(original)
            source.unlink()
            run = invoke()
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("missing/aliased source", run.stderr)
            source.write_bytes(original)
            receipt = package / "CERTIFICATE.json"
            data = json.loads(receipt.read_text())
            data["residual"]["rank"] = 7
            receipt.write_text(json.dumps(data))
            run = invoke()
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("certificate drift", run.stderr)
            data["residual"]["rank"] = 8
            data["fixtures"]["serial_helpers"] = True
            receipt.write_text(json.dumps(data))
            run = invoke()
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("certificate drift", run.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
