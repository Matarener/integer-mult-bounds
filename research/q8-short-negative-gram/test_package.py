"""Behavioral controls remain enabled under optimized Python. Apache-2.0."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

import algebra
import census
import controls
import oracle
import verify


class Behavior(unittest.TestCase):
    def test_real_endpoints_and_mutations(self):
        self.assertEqual(controls.small_replay()["positive_nine_call_words"], 8)
        original = census.census(3)
        with patch.object(census, "endpoint", side_effect=lambda a, mask: ((0,) * len(a),) * 8):
            self.assertNotEqual(census.census(3), original)
        with patch.object(algebra, "qmul", side_effect=lambda g, h: g ^ h):
            with self.assertRaisesRegex(ValueError, "independent action"):
                controls.small_replay()
        with patch.object(oracle, "LEFT_I", tuple(range(8))):
            with self.assertRaisesRegex(ValueError, "independent action"):
                controls.small_replay()
        with patch.object(census, "grams", side_effect=lambda n: iter(((1, 2, 4),))):
            with self.assertRaisesRegex(ValueError, "incomplete Gram"):
                census.census(3)

    def test_domains_receipt_and_enumeration(self):
        for args in [((0,), 0, 0, 0), ((1,), 2, 0, 0), ((1,), 0, -1, 0),
                     ((1,), 0, True, 0), ((1,) * 10, 0, 0, 0)]:
            with self.assertRaises(ValueError):
                algebra.accepts(*args)
        for n in (0, 6, True):
            with self.assertRaises(ValueError):
                algebra.grams(n)
        for n in range(1, 4):
            a = list(algebra.grams(n))
            self.assertEqual(a, [oracle.decode(k, n) for k in range(len(a))])
            self.assertEqual(len(set(a)), 1 << (n * (n - 1)))
        receipt = json.loads(Path(__file__).with_name("RESULT.json").read_bytes())
        original = json.loads(json.dumps(receipt))
        receipt["censuses"][1]["shapes"]["(3, 0)"]["accepted"] = 1
        with self.assertRaisesRegex(ValueError, "receipt mismatch"):
            verify.check_receipt(original, receipt)

    def test_cli_refuses_collision_before_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "keep"
            output.write_bytes(b"retained\n")
            command = [sys.executable, "-I", "-O", "-B", str(Path(verify.__file__).resolve()),
                       "--output", str(output)]
            result = subprocess.run(command, capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("output already exists", result.stderr)
            self.assertEqual(output.read_bytes(), b"retained\n")


if __name__ == "__main__":
    unittest.main()
