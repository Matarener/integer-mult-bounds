"""Behavioral faults, bounded inputs and actual Git-free CLI replay. Apache-2.0."""

import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as v


def export(destination):
    paths = tuple(v.ROOT.rglob("*"))
    v.m.require(len(paths) <= 64, "test export capacity")
    for source in paths:
        entry = source.lstat()
        v.m.require(not stat.S_ISLNK(entry.st_mode), "test source link")
        target = destination / source.relative_to(v.ROOT)
        if stat.S_ISDIR(entry.st_mode):
            target.mkdir(parents=True, exist_ok=True)
        else:
            v.m.require(stat.S_ISREG(entry.st_mode) and entry.st_uid == os.getuid(), "owned source")
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as stream:
                raw = source.read_bytes()
                v.m.require(stream.write(raw) == len(raw), "test export write")
            copied = target.lstat()
            v.m.require((entry.st_dev, entry.st_ino) != (copied.st_dev, copied.st_ino),
                        "disjoint test copy")


class Controls(unittest.TestCase):
    def test_actual_producer_faults(self):
        wanted = v.expected((5,) * 4, 4)
        with patch.object(v.m, "full_endpoint", return_value=wanted):
            with self.assertRaisesRegex(ValueError, "quotient false positive"):
                v.witness_check()
        bad = ((1, 2, 4, 8),) * 4
        with patch.object(v.m, "polynomial", return_value=bad):
            with self.assertRaisesRegex(ValueError, "polynomial receipt"):
                v.witness_check()
        with patch.object(v.oracle, "hamilton", side_effect=lambda a, b: a):
            with self.assertRaisesRegex(ValueError, "Hamilton product"):
                v.algebra_check()
        with patch.object(v.m, "rank", return_value=0):
            with self.assertRaisesRegex(ValueError, "invertible cubic defect"):
                v.witness_check()

    def test_boundary_failures(self):
        for gate, roles in [((0, 1, 1), 4), ((True, 1, 1), 4), ((1, 2, 1), 4),
                            ((1, 1, 3), 4), ((16, 1, 1), 4), ((1, 1, 1), 17)]:
            with self.assertRaises(ValueError):
                v.m.full_endpoint((gate,), roles)
        with self.assertRaisesRegex(ValueError, "call bound"):
            v.m.full_endpoint(((1, 1, 1),) * 49, 4)
        with self.assertRaisesRegex(ValueError, "span capacity"):
            v.oracle.span_rank((1,) * 9)
        with self.assertRaisesRegex(ValueError, "rank vector bound"):
            v.m.rank((1 << 128,))

    def test_git_free_replay_and_faults(self):
        with tempfile.TemporaryDirectory(prefix="q8-saturation-") as name:
            root = Path(name)
            export(root)
            command = [sys.executable, "-I", "-O", "-Werror", "-B", str(root / "verify.py")]
            completed = subprocess.run(command, cwd=root, capture_output=True, timeout=20)
            self.assertEqual(completed.returncode, 0, completed.stderr.decode())
            self.assertIn(b"PASS_Q8_QUADRATIC_SATURATION", completed.stdout)
            receipt = root / "RESULT.json"
            before = receipt.read_bytes()
            failed = subprocess.run(command + ["--write", str(receipt)], cwd=root,
                                    capture_output=True, timeout=20)
            self.assertNotEqual(failed.returncode, 0)
            self.assertEqual(receipt.read_bytes(), before)
            changed = json.loads(before)
            changed["witness"]["calls"] = 7
            receipt.write_text(json.dumps(changed))
            failed = subprocess.run(command, cwd=root, capture_output=True, timeout=20)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn(b"result receipt", failed.stderr)
            (root / "inputs/pr3536-PROOF.md").write_text("corrupted retained premise")
            with patch.object(v, "ROOT", root):
                with self.assertRaisesRegex(ValueError, "retained source hash"):
                    v.source_check()


if __name__ == "__main__":
    unittest.main()
