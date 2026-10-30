"""Behavioral controls, including optimized Python. Apache-2.0."""

import contextlib
import io
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import model as m
import oracle as o
import verify as v


def copy_fixture(destination):
    names = (*v.sources(), "RESULT.json")
    m.require(len(names) <= 16, "copy fixture capacity")
    for name in names:
        source = v.ROOT / name
        target = destination / name
        before = source.lstat()
        m.require(stat.S_ISREG(before.st_mode) and before.st_uid == os.getuid(), "source ownership")
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as output:
            output.write(source.read_bytes())
        after = target.lstat()
        m.require((before.st_dev, before.st_ino) != (after.st_dev, after.st_ino), "copy alias")


class Controls(unittest.TestCase):
    def test_real_arithmetic_and_action_faults(self):
        conversion = o.coordinates()
        original = m.multiply

        def bad_multiply(a, b):
            result = original(a, b)
            return (result[0] ^ 1, *result[1:]) if result else result

        with patch.object(m, "multiply", bad_multiply), self.assertRaises(ValueError):
            v.matrix_action_checks(conversion)
        with patch.object(o, "left_generator", return_value=0), self.assertRaises(ValueError):
            v.matrix_action_checks(conversion)
        broken = [list(row) for row in o.GROUP]
        broken[2][1] = 3
        with patch.object(o, "GROUP", tuple(tuple(row) for row in broken)):
            with self.assertRaisesRegex(ValueError, "Hamilton"):
                v.algebra_checks()

    def test_rank_lemma_hypotheses(self):
        self.assertEqual(v.lemma_measure((1,), (1, 0), (2, 1)), 1)
        with self.assertRaisesRegex(ValueError, "invertibility"):
            v.lemma_measure((1,), (1, 0), (0, 0))
        with self.assertRaisesRegex(ValueError, "XY identity"):
            v.lemma_measure((1,), (0, 0), (2, 1))
        with self.assertRaisesRegex(ValueError, "XKY zero"):
            v.lemma_measure((1, 2), (1, 2), (1, 2))

    def test_correction_and_count_boundaries(self):
        word = ((1, 1, 1), (1, 1, 0), (1, 1, 0))
        self.assertEqual(m.predicted(1, word), ((1,), (1,), (1,)))
        x, y, _, h, correction, _ = m.call_matrices(1, word)
        self.assertEqual(m.multiply(m.multiply(x, correction), y), (1,))
        self.assertEqual(m.multiply(m.multiply(x, m.multiply(h, h)), y), (0,))
        self.assertFalse(m.count_constraints(3, 1, 3, 5))
        self.assertFalse(m.count_constraints(3, 1, 4, 4))
        self.assertTrue(m.count_constraints(3, 1, 5, 5))
        self.assertEqual(m.count_floor(3, 1), 10)
        for args in ((True, 1, 1, 1), (3, 1, -1, 9), (33, 0, 0, 0)):
            with self.assertRaises(ValueError):
                m.count_constraints(*args)
        for roles, invalid in ((0, ()), (7, ()), (1, ((1, 1, 0),) * 17),
                               (1, ((1, 1, True),)), (2, ((1, 2, 0),))):
            with self.assertRaises(ValueError):
                m.validate(roles, invalid)
        with self.assertRaises(ValueError):
            m.multiply((4,), (1, 2))
        with self.assertRaises(ValueError):
            o.act(1, (), 1, 0)

    def test_source_and_receipt_corruption(self):
        with tempfile.TemporaryDirectory(prefix="q8-cubic-controls-") as folder:
            root = Path(folder)
            copy_fixture(root)
            with patch.object(v, "ROOT", root):
                retained = root / "inputs/pr3551-WITNESS.json"
                original = retained.read_bytes()
                retained.write_bytes(original + b" ")
                with self.assertRaisesRegex(ValueError, "retained source changed"):
                    v.sources()
                retained.write_bytes(original)
                receipt = json.loads((root / "RESULT.json").read_text())
                receipt["count_floor_3_1"] = 8
                (root / "RESULT.json").write_text(json.dumps(receipt))
                with patch.object(sys, "argv", ["verify.py"]):
                    with self.assertRaisesRegex(ValueError, "receipt mismatch"):
                        v.main()

    def test_exclusive_output(self):
        with tempfile.TemporaryDirectory(prefix="q8-cubic-output-") as folder:
            target = Path(folder) / "receipt.json"
            target.write_bytes(b"preserve\n")
            with patch.object(sys, "argv", ["verify.py", "--write", str(target)]):
                with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(FileExistsError):
                    v.main()
            self.assertEqual(target.read_bytes(), b"preserve\n")


if __name__ == "__main__":
    unittest.main()
