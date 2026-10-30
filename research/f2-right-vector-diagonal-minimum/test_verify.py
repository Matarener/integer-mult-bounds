#!/usr/bin/env python3
"""Independent checks and failure controls.

The algebra in this file does not call verify.py's product routines.
Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from itertools import permutations
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def klein_mul(left, right):
    """Coefficients (1, z1, z2, z1 z2). This is not verify.klein_bit."""
    a0, a1, a2, a3 = left
    b0, b1, b2, b3 = right
    return (
        a0 & b0,
        (a0 & b1) ^ (a1 & b0),
        (a0 & b2) ^ (a2 & b0),
        (a0 & b3) ^ (a3 & b0) ^ (a1 & b2) ^ (a2 & b1),
    )


def one_factor_binary(u0, u1, y):
    """Right-multiply I by I+(u0,u1) y^T with y in F2^2."""
    zero = (0, 0, 0, 0)
    one = (1, 0, 0, 0)
    p00, p01, p10, p11 = one, zero, zero, one
    if y & 1:
        p00 = klein_mul_add(p00, u0)
        p10 = klein_mul_add(p10, u1)
    if y & 2:
        p01 = klein_mul_add(p01, u0)
        p11 = klein_mul_add(p11, u1)
    return p00, p01, p10, p11


def klein_mul_add(base, extra):
    return tuple(x ^ y for x, y in zip(base, extra))


class IndependentAlgebra(unittest.TestCase):
    def test_socle_witness_is_one_ring_valued_factor(self):
        z1 = (0, 1, 0, 0)
        z2 = (0, 0, 1, 0)
        socle = klein_mul(z1, z2)
        self.assertEqual(socle, (0, 0, 0, 1))
        self.assertEqual(klein_mul(z1, z1), (0, 0, 0, 0))
        self.assertEqual(klein_mul(z2, z2), (0, 0, 0, 0))
        # Columns (z1, z2), right vector (z2, z1): diagonal socle, off-diagonal zero.
        self.assertEqual(klein_mul(z2, z1), socle)

    def test_no_binary_right_vector_saves_two_diagonal_entries(self):
        saved = 0
        for u0_bits in range(16):
            for u1_bits in range(16):
                u0 = tuple((u0_bits >> i) & 1 for i in range(4))
                u1 = tuple((u1_bits >> i) & 1 for i in range(4))
                for y in range(4):
                    p00, p01, p10, p11 = one_factor_binary(u0, u1, y)
                    if p01 != (0, 0, 0, 0) or p10 != (0, 0, 0, 0):
                        continue
                    count = (p00 != (1, 0, 0, 0)) + (p11 != (1, 0, 0, 0))
                    if count > 1:
                        saved += 1
        self.assertEqual(saved, 0)

    def test_s3_coordinate_word_without_verify(self):
        perms = list(permutations(range(3)))
        index = {perm: i for i, perm in enumerate(perms)}

        def mul(left, right):
            out = [0] * 6
            for i, coeff in enumerate(left):
                if not coeff:
                    continue
                for j, weight in enumerate(right):
                    if weight:
                        composed = tuple(perms[i][perms[j][k]] for k in range(3))
                        out[index[composed]] ^= 1
            return out

        def add(left, right):
            return [x ^ y for x, y in zip(left, right)]

        one = [1, 0, 0, 0, 0, 0]
        # permutations() order starts at the identity.
        self.assertEqual(perms[0], (0, 1, 2))
        transpositions = [(0, 2, 1), (1, 0, 2), (2, 1, 0)]
        matrix = [[one if i == j else [0] * 6 for j in range(3)] for i in range(3)]
        for slot, perm in enumerate(transpositions):
            step = add(one, [1 if i == index[perm] else 0 for i in range(6)])
            image = [[0] * 6 for _ in range(3)]
            image[slot] = mul(matrix[slot][slot], step)
            for source in range(3):
                matrix[source][slot] = add(matrix[source][slot], image[source])
        for row in range(3):
            for column in range(3):
                if row != column:
                    self.assertEqual(matrix[row][column], [0] * 6)
                else:
                    self.assertEqual(matrix[row][column][index[transpositions[row]]], 1)
                    self.assertEqual(sum(matrix[row][column]), 1)


def _tree(destination):
    names = [
        "research/f2-right-vector-diagonal-minimum/verify.py",
        "research/f2-right-vector-diagonal-minimum/RESULT.json",
        "research/f2-right-vector-diagonal-minimum/PROOF.md",
        "docs/research/agent-task-catalog.json",
        "certificates/selected-result.json",
        "research/bit-cyclic-root-barrier/PROOF.md",
        "research/bit-one-relation-any-registers/PROOF.md",
    ]
    for name in names:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, target)
    return destination / "research/f2-right-vector-diagonal-minimum/verify.py"


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
        self.assertIn("PASS_F2_RIGHT_VECTOR_DIAGONAL_MINIMUM", completed.stdout)

    def test_corrupt_receipt_fails_and_leaves_origin(self):
        origin = (HERE / "RESULT.json").read_bytes()
        with tempfile.TemporaryDirectory() as temporary:
            script = _tree(Path(temporary))
            receipt = script.parent / "RESULT.json"
            receipt.write_text(
                receipt.read_text(encoding="utf-8").replace(
                    "PASS_F2_RIGHT_VECTOR_DIAGONAL_MINIMUM", "FAIL", 1
                ),
                encoding="utf-8",
            )
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

    def test_span_corruption_is_detected(self):
        origin = (HERE / "verify.py").read_bytes()
        with tempfile.TemporaryDirectory() as temporary:
            script = _tree(Path(temporary))
            source = script.read_text(encoding="utf-8")
            needle = 'need(klein["violations"] == 0 and klein["span_failures"] == 0, "Klein exhaustion failed")'
            self.assertEqual(source.count(needle), 1)
            script.write_text(source.replace(needle, "need(True, \"Klein exhaustion failed\")", 1), encoding="utf-8")
            # A forced pass of that gate is not enough: also break the witness check.
            source = script.read_text(encoding="utf-8")
            witness = 'need(saved == 0, "F2 right vector realized t=2 in one factor")'
            self.assertEqual(source.count(witness), 1)
            script.write_text(
                source.replace(witness, 'need(saved == 1, "F2 right vector realized t=2 in one factor")', 1),
                encoding="utf-8",
            )
            completed = _run(script)
            self.assertNotEqual(completed.returncode, 0)
        self.assertEqual((HERE / "verify.py").read_bytes(), origin)


if __name__ == "__main__":
    unittest.main()
