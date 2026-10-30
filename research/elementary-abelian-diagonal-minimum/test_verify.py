#!/usr/bin/env python3
"""Independent checks and failure controls for the diagonal minimum package.

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import verify  # noqa: E402


def poly_mul(left, right):
    """Separate multiplier: dictionaries of square-free monomials, not bit loops."""
    out = {}
    for mask, coeff in left.items():
        for other, weight in right.items():
            if mask & other:
                continue
            key = mask | other
            out[key] = out.get(key, 0) ^ (coeff & weight)
            if out[key] == 0:
                del out[key]
    return out


def as_dict(value):
    out = {}
    rest = value
    while rest:
        bit = (rest & -rest).bit_length() - 1
        out[bit] = 1
        rest ^= 1 << bit
    return out


def from_dict(value):
    out = 0
    for mask in value:
        out |= 1 << mask
    return out


class IndependentAlgebra(unittest.TestCase):
    def test_dictionary_multiplier_matches_bits(self):
        for left in range(16):
            for right in range(16):
                got = from_dict(poly_mul(as_dict(left), as_dict(right)))
                self.assertEqual(got, verify.bit_mul(left, right))

    def test_hand_product_on_one_register(self):
        # (1+z1)(1+z2) = 1+z1+z2+z1 z2.
        matrix = verify.apply(
            verify.apply(verify.eye(1), verify.delta(1), 1, 1, verify.bit_mul),
            verify.delta(2), 1, 1, verify.bit_mul)
        self.assertEqual(matrix[0][0], 1 ^ 2 ^ 4 ^ 8)

    def test_direct_word_omission(self):
        full = verify.direct([1, 2, 3], verify.bit_mul)
        short = verify.direct([1, 2, 0], verify.bit_mul)
        self.assertNotEqual(full, short)
        self.assertEqual(verify.diagonal_count(full), 3)
        self.assertEqual(verify.diagonal_count(short), 2)


def _tree(destination):
    names = [
        "research/elementary-abelian-diagonal-minimum/verify.py",
        "research/elementary-abelian-diagonal-minimum/RESULT.json",
        "research/elementary-abelian-diagonal-minimum/SOURCES.json",
        "research/elementary-abelian-diagonal-minimum/PROOF.md",
        "docs/research/agent-task-catalog.json",
        "certificates/selected-result.json",
        "research/bit-cyclic-root-barrier/PROOF.md",
        "research/bit-cyclic-root-barrier/README.md",
    ]
    for name in names:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, target)
    return destination / "research/elementary-abelian-diagonal-minimum/verify.py"


def _run(script, *args):
    return subprocess.run(
        [sys.executable, "-I", "-O", "-B", "-W", "error", str(script), *args],
        cwd=script.parents[2],
        capture_output=True,
        text=True,
    )


class FailureControls(unittest.TestCase):
    def test_default_verify_is_read_only(self):
        receipt = HERE / "RESULT.json"
        before = hashlib.sha256(receipt.read_bytes()).hexdigest()
        completed = _run(HERE / "verify.py")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(before, hashlib.sha256(receipt.read_bytes()).hexdigest())
        self.assertIn("PASS_ELEMENTARY_ABELIAN_DIAGONAL_MINIMUM", completed.stdout)

    def test_corrupt_receipt_fails_and_leaves_origin(self):
        origin = (HERE / "RESULT.json").read_bytes()
        with tempfile.TemporaryDirectory() as temporary:
            script = _tree(Path(temporary))
            receipt = script.parent / "RESULT.json"
            receipt.write_text(receipt.read_text(encoding="utf-8").replace(
                "PASS_ELEMENTARY_ABELIAN_DIAGONAL_MINIMUM", "FAIL", 1), encoding="utf-8")
            completed = _run(script)
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("receipt mismatch", completed.stderr + completed.stdout)
        self.assertEqual((HERE / "RESULT.json").read_bytes(), origin)

    def test_duplicate_json_key_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            script = _tree(Path(temporary))
            receipt = script.parent / "RESULT.json"
            text = receipt.read_text(encoding="utf-8")
            text = text.replace('{\n  "status"', '{\n  "status": "x",\n  "status"', 1)
            receipt.write_text(text, encoding="utf-8")
            completed = _run(script)
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("duplicate JSON key", completed.stderr + completed.stdout)

    def test_write_receipt_refuses_to_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            script = _tree(Path(temporary))
            receipt = script.parent / "RESULT.json"
            before = receipt.read_bytes()
            completed = _run(script, "--write-receipt")
            self.assertNotEqual(completed.returncode, 0)
            self.assertEqual(receipt.read_bytes(), before)
            self.assertIn("will not overwrite receipt", completed.stderr + completed.stdout)

    def test_algorithm_corruption_is_detected(self):
        origin = (HERE / "verify.py").read_bytes()
        with tempfile.TemporaryDirectory() as temporary:
            script = _tree(Path(temporary))
            source = script.read_text(encoding="utf-8")
            needle = 'need(image_dimension(graded, rank) <= expected, "graded column bound")'
            self.assertEqual(source.count(needle), 1)
            script.write_text(source.replace(needle, needle.replace("<=", "+ 1 <=", 1), 1),
                              encoding="utf-8")
            completed = _run(script)
            self.assertNotEqual(completed.returncode, 0)
        self.assertEqual((HERE / "verify.py").read_bytes(), origin)


if __name__ == "__main__":
    unittest.main()
