# SPDX-License-Identifier: Apache-2.0
"""Behavioral checks for complete helper scope and source authentication."""

import copy
import gzip
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import boundary
import io_support as io


def fixture():
    original = {"L" + str(i) for i in range(632)}
    helpers = {"L" + str(i) for i in range(224, 632)}
    events = [["zero_buffer", "alloc", "Z" + str(i)] for i in range(91)]
    events += [
        ["scalar", ["add", "L224", "L0", 1, 1], ()],
        ["scalar", ["add", "L224", "L0", -1, 1], ()],
    ]
    events += [["zero_buffer", "free", "Z" + str(i)] for i in range(91)]
    return events, original, helpers


class BoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blobs = io.inputs()
        cls.modules = io.modules(cls.blobs)

    def normalize(self, events, original, helpers, backward=False):
        return boundary.normalized(
            events, original, helpers, backward, self.modules["algebra"]
        )

    def test_all_outputs_positive(self):
        events, original, helpers = fixture()
        result = self.normalize(events, original, helpers)
        self.assertEqual(len(result["helper_outputs"]), 408)
        self.assertEqual(len(result["private_frees"]), 91)

    def test_helper_fault_without_private_fault(self):
        events, original, helpers = fixture()
        del events[92]
        with self.assertRaisesRegex(ValueError, "all dirty helper outputs restored"):
            self.normalize(events, original, helpers)

    def test_actual_source_all_helpers(self):
        source, algebra = self.modules["source"], self.modules["algebra"]
        for tag in ("base", "extra"):
            raw = self.blobs[self.modules["support"].WORDS[tag]]
            word = io.decode(gzip.decompress(raw))
            kept, original, _, _ = source.metadata(word)
            helpers = {"L" + str(i) for i in kept if i >= 224}
            for backward in (False, True):
                result = boundary.normalized(
                    source.expected(word, backward),
                    original,
                    helpers,
                    backward,
                    algebra,
                )
                self.assertEqual(len(result["helper_outputs"]), 408)

    def test_warp_cancellation_both_orientations(self):
        events, original, helpers = fixture()
        for backward in (False, True):
            changed = (
                events[:91] + [["warp", "L224", 3], ["warp", "L224", -3]] + events[91:]
            )
            self.normalize(changed, original, helpers, backward)
            del changed[92]
            with self.assertRaisesRegex(
                ValueError, "all dirty helper outputs restored"
            ):
                self.normalize(changed, original, helpers, backward)

    def test_lifetime_and_zero_at_free(self):
        events, original, helpers = fixture()
        changed = copy.deepcopy(events)
        changed.insert(91, ["scalar", ["add", "Z0", "L0", 1, 1], ()])
        with self.assertRaisesRegex(ValueError, "nonzero private at actual free"):
            self.normalize(changed, original, helpers)
        changed = copy.deepcopy(events)
        changed.insert(92, ["zero_buffer", "free", "Z0"])
        with self.assertRaisesRegex(ValueError, "matched private free"):
            self.normalize(changed, original, helpers)

    def test_copy_clear_and_scale(self):
        rows = {"a": {("a", ()): 1}, "b": {("b", ()): 1}}
        boundary.scalar(
            rows, set(), ["scalar", ["copy", "a", "b"]], self.modules["algebra"]
        )
        self.assertEqual(rows["a"], rows["b"])
        boundary.scalar(
            rows, set(), ["scalar", ["scale", "a", -2, 3]], self.modules["algebra"]
        )
        self.assertEqual(str(rows["a"][("b", ())]), "-2/3")
        boundary.scalar(
            rows, set(), ["scalar", ["clear", "a"]], self.modules["algebra"]
        )
        self.assertEqual(rows["a"], {})
        with self.assertRaisesRegex(ValueError, "nonzero scale"):
            boundary.scalar(
                rows, set(), ["scalar", ["scale", "a", 0, 1]], self.modules["algebra"]
            )

    def test_source_bytes_rejected_before_execution(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            for path, raw in self.blobs.items():
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
            first = next(iter(self.blobs))
            (root / first).write_bytes(b"raise RuntimeError('must not execute')\n")
            with self.assertRaisesRegex(ValueError, "source SHA256"):
                io.inputs(root)

    def test_duplicate_keys_and_capacity(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            io.decode(b'{"a":1,"a":2}')
        events, original, helpers = fixture()
        with self.assertRaisesRegex(ValueError, "finite stream domain"):
            self.normalize(events, original - {"L0"}, helpers)


if __name__ == "__main__":
    unittest.main(verbosity=2)
