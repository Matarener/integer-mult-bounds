"""Behavioral and actual optimized-CLI rejection controls. Apache-2.0."""

import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("three_query_subject", HERE / "verify.py")
if spec is None or spec.loader is None:
    raise ValueError("verifier module loader")
subject = importlib.util.module_from_spec(spec)
spec.loader.exec_module(subject)


class Controls(unittest.TestCase):
    def test_invalid_algebra_and_capacity(self):
        for matrix in (((0, 0, 1),) * 3, ((1, 2), (3, 4))):
            with self.assertRaises(ValueError):
                subject.inverse(matrix)
        with self.assertRaisesRegex(ValueError, "collinear"):
            subject.triangle(((0, 0), (1, 1), (2, 2)))
        with self.assertRaisesRegex(ValueError, "capacity"):
            subject.binary_rank([0] * 225, 3)
        with self.assertRaisesRegex(ValueError, "binary row"):
            subject.binary_rank([8], 3)

    def test_disjoint_indicator_boundary(self):
        a, b, z = [0] * 112, [0] * 112, [F(1, 2)] * 112
        a[0] = b[0] = 1
        with self.assertRaisesRegex(ValueError, "disjoint"):
            subject.factors(a, b, z, ((1, 0, 0), (0, 1, 0), (0, 0, 1)))
        a[0] = 2
        with self.assertRaisesRegex(ValueError, "binary"):
            subject.factors(a, b, z, ((1, 0, 0), (0, 1, 0), (0, 0, 1)))
        with self.assertRaisesRegex(ValueError, "capacity"):
            subject.factors(a[:-1], b, z, ((1, 0, 0), (0, 1, 0), (0, 0, 1)))

    def test_three_distinct_cancellation_levels_and_outside_noise(self):
        a, b = [0] * 112, [0] * 112
        a[:3], b[3:6] = [1] * 3, [1] * 3
        seed = [F(-2, 3), F(-4, 5), F(-9, 7), F(-1, 3), F(-8, 5), F(-2, 7)]
        seed += [F(11, 13)] * 106
        matrix = ((F(2, 3), F(1, 3), 1), (F(4, 5), F(8, 5), 1), (F(9, 7), F(2, 7), 1))
        q, u = subject.factors(a, b, seed, matrix)
        nq, nu = subject.replace(a, b, seed, matrix)
        subject.identity(a, b, q, u)
        subject.identity(a, b, nq, nu)
        for i in range(3):
            self.assertEqual(q[i][i], 0)
            self.assertEqual(nq[i][i], 0)
            self.assertEqual(q[i][i + 3], 0)
            self.assertEqual(nq[i][i + 3], 0)
        self.assertTrue(all(q[i][p] for i in range(3) for p in range(6, 112)))
        self.assertTrue(all(nq[i][p] == 0 for i in range(3) for p in range(6, 112)))
        # The old seed is neither binary nor supported on the two groups.
        self.assertNotEqual(seed[6], 0)
        self.assertNotIn(seed[0], (0, 1))

    def test_repeated_coordinates_keep_reader_zeros(self):
        for points in (
            ((2, 7), (2, 11), (5, 13)),
            ((2, 7), (3, 7), (5, 13)),
            ((2, 7), (2, 11), (5, 7)),
        ):
            chosen = subject.triangle(points)
            old = subject.inverse([[*p, 1] for p in points])
            new = subject.inverse([[*p, 1] for p in chosen])
            self.assertTrue(
                all(
                    old[row][col] != 0 or new[row][col] == 0
                    for row in range(2)
                    for col in range(3)
                )
            )

    def test_unused_reader_has_zero_tariff(self):
        labels, groups = subject.load()
        planes = [g[i : i + 2] for g in groups for i in range(0, len(g), 2)]
        owners = {p: pair for pair in planes for p in pair}
        self.assertEqual(subject.bill(labels, owners, [[1] * 112], [[0] * 112]), 0)
        with self.assertRaisesRegex(ValueError, "three nonzero"):
            subject.replace(
                [0] * 112, [0] * 112, [0] * 112, ((1, 0, 0), (0, 1, 0), (0, 0, 1))
            )

    def test_optimized_cli_rejects_actual_corruptions(self):
        with tempfile.TemporaryDirectory(prefix="three-query-controls-") as tmp:
            root = Path(tmp)
            package, files = copy_fixture(root)
            originals = {path: path.read_bytes() for path in files}
            mutations = (
                (files[0], "receipt", b'"errors": 0', b'"errors": 1'),
                (
                    files[1],
                    "Git blob",
                    b"d9a4f84211182ca200c081ea061d724c8a2cfb70",
                    b"0" * 40,
                ),
                (files[1], "inventory", subject.INPUT.encode(), b"research/wrong.json"),
                (files[2], "SHA256", b"\n", b" \n"),
                (files[3], "SHA256", b"\n", b" \n"),
            )
            for path, expected, old, new in mutations:
                for target, raw in originals.items():
                    target.write_bytes(raw)
                changed = originals[path].replace(old, new)
                self.assertNotEqual(changed, originals[path])
                path.write_bytes(changed)
                proc = cli(root, package)
                self.assertNotEqual(proc.returncode, 0, expected)
                self.assertIn(expected, proc.stderr)
            for target, raw in originals.items():
                target.write_bytes(raw)
            good = cli(root, package)
            self.assertEqual(good.returncode, 0, good.stderr)
            self.assertIn("errors=0", good.stdout)


def copy_fixture(root):
    package = root / "research" / HERE.name
    package.mkdir(parents=True)
    for name in ("verify.py", "RESULT.json", "SOURCES.json", "RETAINED-RANK32.json"):
        shutil.copyfile(HERE / name, package / name)
    source = root / subject.INPUT
    source.parent.mkdir(parents=True)
    shutil.copyfile(HERE.parents[1] / subject.INPUT, source)
    return package, [
        package / "RESULT.json",
        package / "SOURCES.json",
        package / "RETAINED-RANK32.json",
        source,
    ]


def cli(root, package):
    return subprocess.run(
        [sys.executable, "-I", "-O", "-Werror", "-B", str(package / "verify.py")],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=30,
    )


if __name__ == "__main__":
    unittest.main(verbosity=2)
