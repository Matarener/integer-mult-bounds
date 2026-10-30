"""Reject malformed caller contracts, leaked scratch and uncharged operations.

Clear1nsight, with substantial OpenAI ChatGPT assistance. Apache-2.0.
"""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tapes
import verify


class PhysicalAxisControls(unittest.TestCase):
    def good(self):
        return tapes.fixture([4, -2], [0, 2], 5, origins=[-8, 4, 22, 31, -11, 7])

    def test_valid_dirty_scratch(self):
        verify.check_case(tapes, [4, -2], [0, 2], 1, 5, 0, 1)
        verify.check_case(tapes, [4, -2], [0, 2], 1, 5, 0, -1, dirty=0)

    def test_invalid_line_parameters(self):
        for axis, sign in [(-1, 1), (1, 1), (0, 0), (0, 2)]:
            with self.subTest(axis=axis, sign=sign), self.assertRaises(ValueError):
                tapes.axis_kernel(self.good(), 1, 5, axis, sign)

    def test_forbid_data_scratch_alias(self):
        v = self.good()
        v[5] = v[0]
        with self.assertRaisesRegex(ValueError, "six distinct"):
            tapes.axis_kernel(v, 1, 5, 0)
        v = self.good()
        v[5].cells = v[0].cells
        with self.assertRaisesRegex(ValueError, "disjoint tape"):
            tapes.axis_kernel(v, 1, 5, 0)

    def test_forbid_borrowed_scratch(self):
        v = self.good()
        v[2].discardable = False
        with self.assertRaisesRegex(ValueError, "owned scratch"):
            tapes.axis_kernel(v, 1, 5, 0)

    def test_wrong_entry_heads(self):
        v = self.good()
        v[3].move(1)
        with self.assertRaisesRegex(ValueError, "entry heads"):
            tapes.axis_kernel(v, 1, 5, 0)

    def test_inexact_numerator_rejected(self):
        v = tapes.fixture([1, 0], [0, 0], 5)
        with self.assertRaisesRegex(ValueError, "nonexact half"):
            tapes.axis_kernel(v, 1, 5, 0)
        with self.assertRaisesRegex(ValueError, "oracle nonexact"):
            verify.oracle([1, 0], [0, 0], 0, 1, 5)

    def test_num_overflow_is_explicit_caller_duty(self):
        with self.assertRaisesRegex(ValueError, "oracle numerator overflow"):
            verify.oracle([15, 15], [15, -15], 0, 1, 5)

    def test_tape_move_cannot_escape(self):
        v = self.good()[2]
        with self.assertRaisesRegex(ValueError, "move outside"):
            v.move(-1)
        for _ in range(len(v.cells)):
            v.move(1)
        with self.assertRaisesRegex(ValueError, "read outside"):
            v.read()
        with self.assertRaisesRegex(ValueError, "write outside"):
            v.write(1)

    def test_missing_scratch_zero_rejected(self):
        original = tapes.Tape.write
        def corrupt(self, value):
            if self.discardable and value == 0 and self.count["read"]:
                self.record("write")  # pay operation while omitting its effect
            else:
                original(self, value)
        tapes.Tape.write = corrupt
        try:
            with self.assertRaisesRegex(ValueError, "scratch cleanup"):
                verify.check_case(tapes, [4, -2], [0, 2], 1, 5, 0, 1)
        finally:
            tapes.Tape.write = original

    def test_omitted_movement_charge_rejected(self):
        original = tapes.Tape.record
        def corrupt(self, action):
            if action != "move":
                original(self, action)
        tapes.Tape.record = corrupt
        try:
            with self.assertRaisesRegex(ValueError, "tariff"):
                verify.check_case(tapes, [4, -2], [0, 2], 1, 5, 0, 1)
        finally:
            tapes.Tape.record = original

    def test_dirty_exterior_never_touched(self):
        v = verify.check_case(tapes, [4, -2], [0, 2], 1, 5, 0, 1, trace=True)
        for tape in v:
            self.assertTrue(all(0 <= pos <= len(tape.cells)
                                for _, pos in tape.trace))
            self.assertTrue(all(pos < len(tape.cells)
                                for op, pos in tape.trace if op in ("read", "write")))

    def test_source_and_manifest_corruption_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            package = root / "research" / "qq16-gaussian-axis-tapes"
            package.mkdir(parents=True)
            shutil.copyfile(verify.PACKAGE / "SOURCES.json", package / "SOURCES.json")
            for name in verify.INPUTS:
                dst = root / name
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(verify.ROOT / name, dst)
            verify.sources(root, package)
            source = root / "research/qq16-native-rounded-components/vendor/native.py"
            source.write_bytes(source.read_bytes() + b"\n# changed source\n")
            with self.assertRaisesRegex(ValueError, "source SHA256"):
                verify.sources(root, package)
            shutil.copyfile(verify.ROOT / next(iter(verify.INPUTS)), source)
            mf = package / "SOURCES.json"
            mf.write_text(mf.read_text().replace("e1976b3a", "e1976b3b"))
            with self.assertRaisesRegex(ValueError, "source pin"):
                verify.sources(root, package)


if __name__ == "__main__":
    unittest.main()
