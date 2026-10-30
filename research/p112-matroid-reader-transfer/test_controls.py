#!/usr/bin/env python3
"""Observable algebraic and optimized CLI rejection controls. Apache-2.0."""

import importlib.util
import itertools
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("matroid_verifier", HERE / "verify.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load verifier")
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


def copy_package(destination):
    destination.mkdir()
    for index, source in enumerate(itertools.islice(HERE.iterdir(), 17)):
        VERIFY.require(index < 16, "package entry capacity")
        VERIFY.require(
            not source.is_symlink() and source.is_file(), "regular package file"
        )
        VERIFY.require(source.stat().st_size <= 1 << 20, "package file capacity")
        shutil.copyfile(source, destination / source.name)


class Controls(unittest.TestCase):
    def test_field_and_capacity_boundaries(self):
        with self.assertRaises(ValueError):
            VERIFY.solve([(4,)], [1], 4)
        with self.assertRaises(ValueError):
            VERIFY.solve([(1,)], [1], 3)
        with self.assertRaises(ValueError):
            VERIFY.solve([(1,)] * 16, [1], 4)
        with self.assertRaises(ValueError):
            VERIFY.geometry([1, 1], [[0, 1]])
        with self.assertRaises(ValueError):
            VERIFY.geometry([1, 2, 4], [[0, 1, 2]])
        with self.assertRaises(ValueError):
            VERIFY.unique_object([("a", 1), ("a", 2)])
        self.assertEqual(VERIFY.solve([(1, 0)], [0, 1], 4), None)
        self.assertEqual(VERIFY.solve([(2, 0), (0, 3)], [1, 1], 4), [3, 2])

    def test_reader_omission_and_nonbinary_boundary(self):
        source = VERIFY.literal_geometry()
        targets = [source[2][j] for j in (0, 2, 4, 6)]
        queries, readers = VERIFY.make_factors(2, targets)
        self.assertEqual(VERIFY.check_operator(queries, readers, targets, 0), 12544)
        readers[0] = [0] * 112
        with self.assertRaises(ValueError):
            VERIFY.check_operator(queries, readers, targets, 0)
        good = VERIFY.ranks(VERIFY.dictionary(2, 4), 4)
        bad = VERIFY.ranks(VERIFY.dictionary(1, 4), 4)
        self.assertNotEqual(good, bad)
        pair = (1 << 5) | (1 << 6)
        self.assertEqual((good[pair], bad[pair]), (2, 1))

    def test_real_cli_corruptions(self):
        with tempfile.TemporaryDirectory(prefix="matroid-controls-") as temporary:
            root = Path(temporary)
            package = root / "research" / HERE.name
            package.parent.mkdir()
            copy_package(package)
            data = root / VERIFY.DATA
            data.parent.mkdir(parents=True)
            shutil.copyfile(HERE.parent.parent / VERIFY.DATA, data)
            expected = package / "RESULT.json"
            fixture = package / "RETAINED-RANK32.json"
            cases = [
                (expected, "verify.py"),
                (expected, "independent.py"),
                (data, "verify.py"),
                (data, "independent.py"),
                (fixture, "verify.py"),
                (fixture, "independent.py"),
            ]
            for path, script in cases:
                original = path.read_bytes()
                if path == expected:
                    payload = json.loads(original)
                    payload["rank_sha256"] = "0" * 64
                    path.write_text(json.dumps(payload))
                else:
                    path.write_bytes(original + b"\n")
                result = self.run_cli(root, package / script)
                self.assertNotEqual(result.returncode, 0, (script, str(path)))
                self.assertNotIn("PASS_", result.stdout)
                path.write_bytes(original)
            restored = self.run_cli(root, package / "verify.py")
            self.assertEqual(restored.returncode, 0, restored.stderr)
            self.assertIn("PASS_MATROID_READER_TRANSFER", restored.stdout)

    @staticmethod
    def run_cli(root, script):
        environment = dict(os.environ)
        environment.pop("PYTHONOPTIMIZE", None)
        return subprocess.run(
            [sys.executable, "-I", "-O", "-Werror", "-B", str(script)],
            cwd=root,
            env=environment,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )


if __name__ == "__main__":
    unittest.main()
