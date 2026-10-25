"""Behavioral controls for the caller proof and actual verifier boundary."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import common
import verify


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = common.geometry()
        cls.roots, _, cls.lines = verify.shell(cls.g)
        cls.a = cls.roots[0]
        cls.b = next(r for r in cls.roots if cls.g.dot(cls.a, r) == 0)
        pencils = verify.root_pencils(cls.g, cls.roots, cls.lines, cls.a)
        cls.candidates = verify.affine_candidates(pencils, cls.lines, cls.a, cls.b)

    def test_four_endpoints_really_attain_B2(self):
        directions = {
            common.primitive(r)
            for r in (
                self.a,
                self.b,
                verify.add(self.a, self.b),
                verify.add(self.a, self.b, -1),
            )
        }
        self.assertEqual(len(directions), 4)
        self.assertTrue(directions <= self.lines)

    def test_fifth_endpoint_failure_requires_second_pencil(self):
        first = []
        for u in self.candidates:
            if common.primitive(verify.add(u, self.a, -2)) in self.lines:
                first.append(u)
                self.assertNotIn(common.primitive(verify.add(u, self.b, 2)), self.lines)
        self.assertEqual(len(first), 32)
        self.assertTrue(
            all(
                common.primitive(verify.add(u, self.b, -1)) in self.lines for u in first
            )
        )

    def test_actual_relation_coefficients(self):
        # q0,q1 are eliminated. q2,q3,q4 give independent formal normal axes.
        t = Fraction(2)
        columns = ((0, 1), (1, 0), (1, 1), (1, -1), (1, t))
        vectors = ((0, 0, 0), (0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))
        expected = {
            (0, 2, 4): (-1, 0, 1),
            (0, 3, 4): (0, -1, 1),
            (1, 2, 4): (-t, 0, 1),
            (1, 3, 4): (0, t, 1),
            (2, 3, 4): (-(t + 1) / 2, (t - 1) / 2, 1),
        }
        for indices, wanted in expected.items():
            i, j, k = indices
            det = lambda p, q: p[0] * q[1] - p[1] * q[0]
            coefficients = (
                det(columns[j], columns[k]),
                det(columns[k], columns[i]),
                det(columns[i], columns[j]),
            )
            self.assertTrue(
                all(
                    sum(
                        c * columns[v][axis]
                        for c, v in zip(coefficients, indices, strict=True)
                    )
                    == 0
                    for axis in range(2)
                )
            )
            actual = tuple(
                sum(
                    c * vectors[v][axis]
                    for c, v in zip(coefficients, indices, strict=True)
                )
                for axis in range(3)
            )
            self.assertEqual(common.primitive(actual), common.primitive(wanted))

    def test_incidence_budget_boundary(self):
        self.assertEqual((3920 - (15 * 160 + 50 * 14 + 672) + 16) // 17, 9)
        self.assertEqual((3920 - (15 * 161 + 50 * 14 + 672) + 16) // 17, 8)
        self.assertEqual(verify.incidence_receipt()["pair_linear_triples_cap"], 8)

    def test_38_perpendicular_threshold_is_material(self):
        counts = [42, 28, 22, 14, 16, 23, 37, 63]
        self.assertEqual([i for i, n in enumerate(counts) if n >= 38], [0, 7])
        self.assertEqual([i for i, n in enumerate(counts) if n >= 37], [0, 6, 7])

    def test_normalization_cannot_discard_nonroot_shell(self):
        e8 = (0, 0, 0, 0, 0, 0, 0, 1)
        self.assertIn(e8, self.lines)
        self.assertNotIn(e8, {common.primitive(r) for r in self.roots})

    def test_json_duplicate_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            json.loads('{"x":1,"x":2}', object_pairs_hook=common.unique_object)

    def test_actual_optimized_cli_mutations(self):
        with tempfile.TemporaryDirectory(prefix="p112-three-endpoint-") as name:
            root = Path(name)
            package = root / "research" / common.PACKAGE.name
            package.mkdir(parents=True)
            names = (
                "common.py",
                "verify.py",
                "SOURCES.json",
                "PREDECESSORS.json",
                "RESULT.json",
                "predecessor-PROOF.md",
                "predecessor-RESULT.json",
            )
            for filename in names:
                shutil.copyfile(
                    common.PACKAGE / filename, package / filename, follow_symlinks=False
                )
            source = root / common.GEOMETRY
            source.parent.mkdir(parents=True)
            original = (common.ROOT / common.GEOMETRY).read_bytes()
            source.write_bytes(original)
            env = dict(os.environ, PYTHONPYCACHEPREFIX=str(root / "private-pycache"))
            command = [
                sys.executable,
                "-O",
                "-Werror",
                "-B",
                str(package / "verify.py"),
            ]

            def rejected(fragment):
                result = subprocess.run(
                    command,
                    cwd=root,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=60,
                    check=False,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(fragment, result.stderr)

            source.write_bytes(original + b"\n")
            rejected("changed source")
            source.unlink()
            source.symlink_to(common.ROOT / common.GEOMETRY)
            rejected("linked source")
            source.unlink()
            source.write_bytes(original)
            proof = package / "predecessor-PROOF.md"
            proof.write_bytes(proof.read_bytes() + b"\n")
            rejected("changed source")
            shutil.copyfile(common.PACKAGE / proof.name, proof)
            receipt = common.read_json(package / "RESULT.json")
            receipt["geometry"]["fifth_endpoint"]["second_pencil"] = False
            (package / "RESULT.json").write_text(json.dumps(receipt))
            rejected("changed result")


if __name__ == "__main__":
    unittest.main()
