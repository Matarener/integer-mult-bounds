#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls for the exact adapter certificate. Nick Petalas."""

import itertools
import os
import runpy
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).resolve().parent
V = runpy.run_path(str(HERE / "verify.py"))


def copy_fixture(root):
    package = root / "research/p104-omitted-frame-adapters"
    package.mkdir(parents=True)
    paths = sorted(HERE.rglob("*"))
    V["require"](len(paths) <= 32, "package fixture capacity")
    for path in paths:
        if path.is_file() and path.suffix in (".py", ".json", ".md"):
            target = package / path.relative_to(HERE)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(path.read_bytes())
    inputs = V["read_json"](HERE / "VERIFY.json")["inputs"]
    V["require"](len(inputs) == 3, "fixture input capacity")
    for name in inputs:
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((V["ROOT"] / name).read_bytes())
    return package


def run_cli(root, package):
    environment = dict(os.environ, PATH="/nonexistent", PYTHONDONTWRITEBYTECODE="1")
    argv = [sys.executable, "-I", "-O", "-Werror", "-B", str(package / "verify.py")]
    return subprocess.run(
        argv,
        capture_output=True,
        text=True,
        env=environment,
        cwd=root,
        timeout=60,
        check=False,
    )


class AdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = V["read_json"](HERE / "ADAPTERS.json")
        V["sources"]()
        cls.compiler, cls.kernel = V["engines"]()

    def test_complete_bank_profile(self):
        rows = self.receipt["omitted_banks"]
        self.assertEqual(len({row["bank"] for row in rows}), 93)
        self.assertEqual(sum(row["rank"] for row in rows), 785)
        self.assertEqual(self.receipt["profile"], {"8": 52, "9": 41})
        self.assertEqual(len(self.receipt["recipes"]), 53)

    def test_wrong_global_phase_preserves_tableau_but_fails(self):
        row = self.receipt["recipes"][1]
        recipe = deepcopy(row["recipe"])
        recipe["left"]["phase"] = (recipe["left"]["phase"] + 1) % 4
        correct = self.kernel["recipe_program"](row["recipe"])
        mutant = self.kernel["recipe_program"](recipe)
        self.assertEqual(
            self.kernel["program_table"](correct, {}),
            self.kernel["program_table"](mutant, {}),
        )
        with self.assertRaisesRegex(ValueError, "exact global phase mismatch"):
            V["check_recipe"](self.kernel, row["old"], row["new"], recipe, {})

    def test_wrong_rank_phase_and_endpoint_fail(self):
        row = self.receipt["recipes"][1]
        for field in ("rank", "linear_phase", "endpoint"):
            recipe, old = deepcopy(row["recipe"]), row["old"]
            if field == "rank":
                recipe["rank"] -= 1
            elif field == "linear_phase":
                recipe["right"]["linear_Z4"][0] ^= 1
            else:
                old = [old[0] ^ 1]
            with self.subTest(field=field), self.assertRaises(ValueError):
                V["check_recipe"](self.kernel, old, row["new"], recipe, {})

    def test_binary_rank_against_complete_small_span(self):
        for columns in itertools.product(range(8), repeat=3):
            span = {0}
            for column in columns:
                span |= {x ^ column for x in span}
            self.assertEqual(V["binary_rank"](columns), len(span).bit_length() - 1)
        for columns in ([True], [1 << 18], list(range(19))):
            with self.assertRaisesRegex(ValueError, "binary matrix capacity"):
                V["binary_rank"](columns)

    def test_optimized_git_free_cli_and_damaged_inputs(self):
        with tempfile.TemporaryDirectory(prefix="p104-adapter-controls-") as directory:
            root = Path(directory)
            package = copy_fixture(root)
            result = run_cli(root, package)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("rank_mass=785", result.stdout)
            cases = (
                ("ADAPTERS.json", b"{}", "adapter receipt mismatch"),
                ("inputs/PR3416_verify.py", b"# damage\n", "checker hash"),
            )
            for relative, data, message in cases:
                path = package / relative
                original = path.read_bytes()
                path.write_bytes(data)
                result = run_cli(root, package)
                path.write_bytes(original)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)
            path = root / V["WORD"]
            path.write_bytes(path.read_bytes() + b"\n")
            result = run_cli(root, package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source hash", result.stderr)
            path.unlink()
            result = run_cli(root, package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing source", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
