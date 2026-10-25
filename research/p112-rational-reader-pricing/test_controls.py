"""Behavioral and actual optimized-CLI failure controls. Apache-2.0."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify  # noqa: E402


class Controls(unittest.TestCase):
    def test_all_seed_coefficient_cases_and_sharpness(self):
        receipt = json.loads(verify.read(HERE / "RESULT.json", 65536))
        self.assertEqual(
            {r["seed_coefficients_nonzero"] for r in receipt["rational_fixtures"]},
            {1, 2, 3},
        )
        sharp = [
            r
            for r in receipt["rational_fixtures"]
            if r["seed_coefficients_nonzero"] == 1
        ]
        self.assertTrue(sharp)
        self.assertTrue(all(r["actual"] == r["baseline"] for r in sharp))

    def test_singular_basis_and_rank_capacity(self):
        with self.assertRaisesRegex(ValueError, "singular"):
            verify.inverse([(1, 0, 0), (1, 0, 0), (0, 0, 1)])
        with self.assertRaisesRegex(ValueError, "capacity"):
            verify.rank([0] * 225, 9)
        with self.assertRaisesRegex(ValueError, "binary row"):
            verify.rank([512], 9)

    def test_seed_boundary(self):
        labels, groups = verify.load()
        identity = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
        p = groups[0][0]
        with self.assertRaisesRegex(ValueError, "binary seed"):
            verify.fixture(labels, groups, [0, 2], [p, p], identity)
        with self.assertRaisesRegex(ValueError, "genuinely external"):
            verify.fixture(labels, groups, [0, 2], groups[0][::2], identity)
        with self.assertRaisesRegex(ValueError, "seed domain"):
            verify.fixture(labels, groups, [0, 2], [groups[2][0]], identity)

    def test_binary_zero_preservation_is_necessary(self):
        points = ((0, 0), (-1, 0), (0, 2))
        grid = verify.domination(points)
        self.assertEqual([p[0] for p in grid], [0, -1, 0])
        self.assertTrue(
            all(
                points[i][j] + z != 0 or grid[i][j] + z == 0
                for i in range(3)
                for j in range(2)
                for z in (0, 1)
            )
        )
        # A nonbinary seed can have a zero at a generic rational coefficient.
        self.assertEqual(2 + (-2), 0)
        self.assertNotEqual(grid[2][1] + (-2), 0)

    def test_self_rank_is_not_the_actual_tariff(self):
        labels, groups = verify.load()
        source = [groups[0][0], groups[0][1]]
        self.assertEqual(verify.tariff(labels, source, source), 2)
        self.assertEqual(verify.tariff(labels, source, []), 0)
        # A source-only invoice would charge an unused query incorrectly.

    def test_actual_optimized_cli_rejects_corruption(self):
        cases = ("labels", "partition", "receipt", "matrix", "tariff")
        parent = os.environ.get("TMPDIR")
        with tempfile.TemporaryDirectory(
            prefix="p112-rational-controls-", dir=parent
        ) as tmp:
            root = Path(tmp)
            package = root / "research" / HERE.name
            package.mkdir(parents=True)
            for name in (
                "verify.py",
                "independent.py",
                "SOURCES.json",
                "RESULT.json",
                "RETAINED-RANK32.json",
            ):
                (package / name).write_bytes(verify.read(HERE / name))
            source = root / verify.INPUT
            source.parent.mkdir(parents=True)
            clean_source = verify.read(verify.ROOT / verify.INPUT)
            clean_partition = verify.read(HERE / "RETAINED-RANK32.json")
            clean_result = verify.read(HERE / "RESULT.json")
            for case in cases:
                source.write_bytes(clean_source)
                (package / "RETAINED-RANK32.json").write_bytes(clean_partition)
                (package / "RESULT.json").write_bytes(clean_result)
                self.corrupt(case, source, package)
                scripts = (
                    ("verify.py", "independent.py")
                    if case != "receipt"
                    else ("verify.py",)
                )
                for script in scripts:
                    result = subprocess.run(
                        [
                            sys.executable,
                            "-I",
                            "-O",
                            "-Werror",
                            "-B",
                            str(package / script),
                        ],
                        cwd=root,
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                    self.assertNotEqual(
                        result.returncode, 0, (case, script, result.stdout)
                    )
                    self.assertIn(
                        "ValueError", result.stderr, (case, script, result.stderr)
                    )

    def corrupt(self, case, source, package):
        if case == "labels":
            data = json.loads(source.read_bytes())
            data["recipes"][0]["q"] ^= 1
            source.write_text(json.dumps(data))
        elif case == "partition":
            path = package / "RETAINED-RANK32.json"
            data = json.loads(path.read_bytes())
            data["orthonormal_groups"][0][0] = data["orthonormal_groups"][0][1]
            path.write_text(json.dumps(data))
        else:
            path = package / "RESULT.json"
            data = json.loads(path.read_bytes())
            if case == "receipt":
                data["literal_global_tariff"] = 223
            elif case == "matrix":
                data["rational_fixtures"][0]["formal_matrix"][0] = ["0", "1", "0"]
            else:
                data["rational_fixtures"][0]["term_tariffs"][0] -= 1
            path.write_text(json.dumps(data))


if __name__ == "__main__":
    unittest.main()
