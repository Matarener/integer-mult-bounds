"""Behavioral fault controls, also run with optimized Python."""

import json
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
V = runpy.run_path(str(ROOT / "verify.py"))
GLOBALS = V["main"].__globals__


class Controls(unittest.TestCase):
    def test_noncommuting_group_action(self):
        with patch.dict(GLOBALS, group_product=lambda a, b: a ^ b):
            with self.assertRaisesRegex(ValueError, "Hamilton disagreement"):
                V["algebra_checks"]()

    def test_missing_cubic_correction(self):
        original = V["chronology"]

        def omit(word, roles, swapped=False):
            x, y, h, c, mi, mj = original(word, roles, swapped)
            return x, y, h, (0,) * len(c), mi, mj

        with patch.dict(GLOBALS, chronology=omit):
            with self.assertRaisesRegex(ValueError, "cubic chronology"):
                V["check_word"](((2, 1, 1), (1, 1, 1), (1, 1, 1)), 1)

    def test_independent_dirty_action(self):
        with patch.dict(
            GLOBALS, direct_column=lambda word, roles, column: (0,) * roles
        ):
            with self.assertRaisesRegex(ValueError, "dirty action"):
                V["check_word"](((1, 1, 1),), 1)

    def test_nonzero_product_is_charged(self):
        eye = V["ident"](2)
        a, b, p = V["rank"](eye), V["rank"](eye), V["rank"](V["mm"](eye, eye))
        self.assertGreater(a + b, 2)
        self.assertEqual(a + b, 2 + p)

    def test_cubic_hypotheses(self):
        check = V["cubic_rank_check"]
        with self.assertRaisesRegex(ValueError, "K invertibility"):
            check((1,), (1, 0), (0, 0))
        with self.assertRaisesRegex(ValueError, "XY identity"):
            check((1,), (0, 0), (2, 1))
        with self.assertRaisesRegex(ValueError, "XKY zero"):
            check((1,), (1, 0), (1, 2))

    def test_counts_and_domains(self):
        # The old n+min(ni,nj)>=3t bound admits this balanced eight-call pair.
        self.assertEqual(8 + min(4, 4), 3 * 4)
        self.assertFalse(V["admissible"](2, 2, 4, 4))
        self.assertTrue(V["admissible"](2, 2, 4, 6))
        for counts in ((True, 1, 3, 3), (0, 0, 0, 0), (33, 0, 96, 0)):
            with self.assertRaises(ValueError):
                V["admissible"](*counts)
        for word, roles in (
            (((3, 1, 1),), 1),
            (((1, 1, 2),), 2),
            (((1, 1, 1),) * 17, 1),
            (((1, 1, 1),), 0),
        ):
            with self.assertRaises(ValueError):
                V["validate_word"](word, roles)
        with self.assertRaises(ValueError):
            V["rank"]((1 << 16,))

    def test_retained_source_corruption(self):
        rows = json.loads((ROOT / "inputs/RETENTION.json").read_text())
        with tempfile.TemporaryDirectory(prefix="q8-source-control-") as directory:
            target = Path(directory)
            (target / "inputs").mkdir()
            (target / "inputs/RETENTION.json").write_text(json.dumps(rows))
            for item in rows["files"]:
                (target / item["retained_path"]).write_bytes(
                    (ROOT / item["retained_path"]).read_bytes()
                )
            (target / rows["files"][0]["retained_path"]).write_bytes(b"changed source")
            with patch.dict(GLOBALS, ROOT=target):
                with self.assertRaisesRegex(ValueError, "retained proof bytes"):
                    V["source_checks"]()

    def test_receipt_corruption(self):
        expected = json.loads((ROOT / "RESULT.json").read_text())
        changed = dict(expected, accepted_count_pairs=-1)
        with tempfile.TemporaryDirectory(prefix="q8-receipt-control-") as directory:
            target = Path(directory)
            (target / "RESULT.json").write_text(json.dumps(changed))
            with patch.dict(GLOBALS, ROOT=target, run_checks=lambda: expected):
                with self.assertRaisesRegex(ValueError, "finite receipt mismatch"):
                    V["main"]()


if __name__ == "__main__":
    unittest.main(verbosity=2)
