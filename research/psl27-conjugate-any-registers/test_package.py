#!/usr/bin/env python3
"""Package tests for the any-register PSL(2,7) conjugate floor."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
if str(PACKAGE) not in sys.path:
    sys.path.insert(0, str(PACKAGE))

import verify as V  # noqa: E402
from algebra import X, Y, compose, mat_add, projector, rank_f2, subsequence_support  # noqa: E402


class PSL27ConjugateAnyRegistersTests(unittest.TestCase):
    def test_support_filter_only_xyx_yxy(self):
        xy = compose(X, Y)
        yx = compose(Y, X)
        both = []
        for labels in (
            (X,),
            (Y,),
            (X, Y),
            (Y, X),
            (X, X, Y),
            (X, Y, X),
            (Y, X, X),
            (Y, X, Y),
            (Y, Y, X),
        ):
            support = subsequence_support(labels)
            if xy in support and yx in support:
                both.append(labels)
        self.assertEqual(both, [(X, Y, X), (Y, X, Y)])

    def test_forced_matrix_not_rank_one(self):
        for roles in (2, 3, 4, 5, 8):
            forced = mat_add(projector(roles, 0), projector(roles, 1))
            self.assertEqual(rank_f2(forced, roles), 2)
            self.assertFalse(V.is_rank_one_idempotent(forced, roles))

    def test_certificate_and_pins(self):
        cert = V.build_certificate()
        self.assertEqual(cert["theorem"]["exact_minimum_calls"], 4)
        self.assertFalse(cert["theorem"]["new_kappa"])
        self.assertEqual(cert["algebra"]["order"], 168)
        self.assertEqual(cert["support_filter"]["both_support_patterns"], ["xyx", "yxy"])
        self.assertGreaterEqual(cert["source_pins"], 3)

    def test_read_only_verify_and_duplicate_json_reject(self):
        before = (PACKAGE / "CERTIFICATE.json").read_bytes()
        V.verify(write=False)
        after = (PACKAGE / "CERTIFICATE.json").read_bytes()
        self.assertEqual(before, after)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dup.json"
            path.write_text('{"a": 1, "a": 2}\n', encoding="utf-8")
            with self.assertRaises(ValueError):
                V.load_json_reject_duplicates(path)

    def test_cli_normal_and_optimized(self):
        for extra in ([], ["-O", "-Werror"]):
            cmd = [sys.executable, "-I", *extra, "-B", str(PACKAGE / "verify.py")]
            proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("PASS_PSL27_CONJUGATE_ANY_REGISTERS", proc.stdout)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(PSL27ConjugateAnyRegistersTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
