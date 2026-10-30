"""Operator and rejecting CLI controls. Nick Petalas. Apache-2.0."""

import itertools
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import independent as other
import verify as v


class Controls(unittest.TestCase):
    def test_half_integral_operator(self):
        _, groups = v.load()
        supports = [groups[g][::2] for g in (11, 13, 15)]
        vectors = [tuple(int(p in support) for p in range(112)) for support in supports]
        ids = (2, 4, 5)  # 110, 101, 011 have determinant -2.
        coefficients = [v.solve(ids, target) for target in range(3)]
        self.assertTrue(
            all(abs(x) == Fraction(1, 2) for row in coefficients for x in row)
        )
        columns = []
        for slot, index in enumerate(ids):
            query = [
                sum(v.DIRECTIONS[index][j] * vectors[j][p] for j in range(3))
                for p in range(112)
            ]
            reader = [
                sum(coefficients[j][slot] * vectors[j][p] for j in range(3))
                for p in range(112)
            ]
            columns.append((reader, query))
        mismatches, omitted = 0, 0
        for p, q in itertools.product(range(112), repeat=2):
            target = sum(row[p] * row[q] for row in vectors)
            actual = sum(u[p] * query[q] for u, query in columns)
            broken = sum(u[p] * query[q] for u, query in columns[1:])
            mismatches += actual != target
            omitted += broken != target
        self.assertEqual(mismatches, 0)
        self.assertGreater(omitted, 0)

    def test_binary_and_rational_rank_differ(self):
        self.assertEqual(v.rank([6, 5, 3], 3), 2)
        self.assertEqual(other.binary_rank([[0, 1, 1], [1, 0, 1], [1, 1, 0]]), 2)
        self.assertEqual(other.dimension([(0, 1, 1), (1, 0, 1), (1, 1, 0)]), 3)

    def test_odd_characteristic_supports(self):
        # Check all subset/axis span requests in two actual prime fields.
        for mask in range(1, 128):
            rows = [v.DIRECTIONS[i] for i in range(7) if mask & (1 << i)]
            for target in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
                rational = other.dimension(rows) == other.dimension([*rows, target])
                for prime in (3, 5):
                    actual = prime_rank(rows, prime) == prime_rank(
                        [*rows, target], prime
                    )
                    self.assertEqual(actual, rational)

    def test_boundaries_and_geometry(self):
        for ids, target in [((7,), 0), ((0, 0), 0), ((0,), 3)]:
            with self.subTest(ids=ids, target=target), self.assertRaises(ValueError):
                v.solve(ids, target)
        self.assertIsNone(v.solve((0, 1), 2))
        for rows, width in [([8], 3), ([True], 1), ([0] * 25, 1), ([], 25)]:
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                v.rank(rows, width)
        labels, groups = v.load()
        groups[0][0] = groups[0][1]
        with self.assertRaisesRegex(ValueError, "partition"):
            v.validate_geometry(labels, groups)

    def test_dictionary_enumeration(self):
        primary = v.patterns(v.bases())
        self.assertEqual(primary, other.minimal_supports())
        self.assertEqual(len(primary), 729)
        self.assertIn((1, 2, 0, 4, 0, 0, 0), primary)
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            v.parse(b'{"minimum":0,"minimum":1}')

    def test_file_capacity(self):
        with tempfile.TemporaryDirectory(prefix="triple-capacity-") as directory:
            path = Path(directory) / "input"
            path.write_bytes(b"12345")
            with self.assertRaisesRegex(ValueError, "file capacity"):
                v.read(path, 4)

    def test_optimized_cli_corruptions(self):
        with tempfile.TemporaryDirectory(prefix="triple-cli-") as directory:
            root = Path(directory)
            package = root / "research" / v.HERE.name
            package.mkdir(parents=True)
            for path in v.HERE.iterdir():
                if path.is_file():
                    self.assertTrue(stat.S_ISREG(path.lstat().st_mode))
                    shutil.copyfile(path, package / path.name)
            source = root / v.INPUT
            source.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(v.ROOT / v.INPUT, source)
            self.assertEqual(run_cli(package).returncode, 0)
            original = (package / "RESULT.json").read_bytes()
            for change in ("bill", "boolean", "duplicate"):
                with self.subTest(change=change):
                    receipt = json.loads(original)
                    if change == "bill":
                        receipt["records"][0][4] -= 1
                    elif change == "boolean":
                        receipt["indicator_triples"] = True
                    raw = json.dumps(receipt).encode()
                    if change == "duplicate":
                        raw = b'{"status":null,' + raw[1:]
                    (package / "RESULT.json").write_bytes(raw)
                    self.assertNotEqual(run_cli(package).returncode, 0)
                    (package / "RESULT.json").write_bytes(original)
            for path in (source, package / "RETAINED-RANK32.json"):
                raw = path.read_bytes()
                path.write_bytes(raw + b" ")
                self.assertNotEqual(run_cli(package).returncode, 0)
                path.write_bytes(raw)
            source.rename(source.with_suffix(".missing"))
            self.assertNotEqual(run_cli(package).returncode, 0)
            source.with_suffix(".missing").rename(source)
            self.assertEqual(run_cli(package).returncode, 0)


def run_cli(package):
    command = [sys.executable, "-I", "-O", "-Werror", "-B", str(package / "verify.py")]
    environment = os.environ.copy()
    environment["PYTHONPYCACHEPREFIX"] = str(package.parent / "private-pycache")
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=90,
        env=environment,
        check=False,
    )


def prime_rank(vectors, prime):
    if prime not in (3, 5) or len(vectors) > 8:
        raise ValueError("prime control capacity")
    rows = [list(row) for row in vectors]
    used = 0
    for column in range(3):
        hit = next((i for i in range(used, len(rows)) if rows[i][column]), None)
        if hit is not None:
            rows[used], rows[hit] = rows[hit], rows[used]
            inverse = pow(rows[used][column], -1, prime)
            rows[used] = [(x * inverse) % prime for x in rows[used]]
            for row in range(used + 1, len(rows)):
                scalar = rows[row][column]
                rows[row] = [
                    (a - scalar * b) % prime
                    for a, b in zip(rows[row], rows[used], strict=True)
                ]
            used += 1
    return used


if __name__ == "__main__":
    unittest.main()
