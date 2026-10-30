"""Behavioral and optimized CLI controls. Nick Petalas. Apache-2.0."""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from hashlib import sha1, sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"
SPEC = importlib.util.spec_from_file_location("dense_reader", HERE / "verify.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("missing local verifier")
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)


class Controls(unittest.TestCase):
    def test_axis_and_missing_reader(self):
        labels, groups = V.load()
        owners, halves = V.geometry(groups)
        a, b = halves[:2]
        directions, readers = V.fixture(a, b, 4)
        with self.assertRaisesRegex(ValueError, "dense queries"):
            V.check_fixture(labels, owners, a, b, [(1, 0), *directions[1:]], readers)
        broken = [row[:] for row in readers]
        broken[0][a[0]] += 1
        with self.assertRaisesRegex(ValueError, "exact pair operator"):
            V.check_fixture(labels, owners, a, b, directions, broken)

    def test_cancellation_and_capacity(self):
        labels, groups = V.load()
        owners, halves = V.geometry(groups)
        a, b = halves[:2]
        directions, readers = V.fixture(a, b, 7)
        outside = next(p for p in range(112) if p not in a + b)
        readers[0][outside] += 1
        with self.assertRaisesRegex(ValueError, "exact pair operator"):
            V.check_fixture(labels, owners, a, b, directions, readers)
        with self.assertRaisesRegex(ValueError, "rank capacity"):
            V.rank([1] * 113, 1)
        with self.assertRaisesRegex(ValueError, "binary row"):
            V.rank([4], 2)

    def test_repeated_directions(self):
        labels, groups = V.load()
        owners, halves = V.geometry(groups)
        a, b = halves[:2]
        directions, readers = V.fixture(a, b, 7)
        last = [value / 2 for value in readers[-1]]
        result = V.check_fixture(
            labels,
            owners,
            a,
            b,
            [*directions, directions[-1]],
            [*readers[:-1], last, last[:]],
        )
        self.assertGreaterEqual(result[0], result[1])

    def test_rank_and_tight_witness(self):
        labels, groups = V.load()
        owners, halves = V.geometry(groups)
        for j in range(0, 32, 2):
            a, b = halves[j : j + 2]
            directions, readers = V.fixture(a, b, 2)
            bill, floor = V.check_fixture(labels, owners, a, b, directions, readers)
            self.assertEqual(bill, floor)
        self.assertEqual(V.rank([3, 3], 2), 1)

    def test_optimized_cli_mutations(self):
        with tempfile.TemporaryDirectory(prefix="dense-reader-controls-") as directory:
            root = Path(directory)
            package = root / "research" / HERE.name
            shutil.copytree(HERE, package, copy_function=shutil.copyfile)
            live = root / INPUT
            live.parent.mkdir(parents=True)
            shutil.copyfile(ROOT / INPUT, live)
            command = [
                sys.executable,
                "-I",
                "-O",
                "-Werror",
                "-B",
                str(package / "verify.py"),
            ]
            for relative in (INPUT, f"research/{HERE.name}/RETAINED-RANK32.json"):
                path = root / relative
                raw = path.read_bytes()
                path.write_bytes(raw + b" ")
                self.reject(command, root, "source SHA256")
                path.write_bytes(raw)
            receipt = package / "RESULT.json"
            raw = receipt.read_bytes()
            changed = json.loads(raw)
            changed["pairs"] = 495
            receipt.write_text(json.dumps(changed))
            self.reject(command, root, "receipt")
            receipt.write_bytes(raw)
            certificate = package / "RETAINED-RANK32.json"
            data = json.loads(certificate.read_bytes())
            data["orthonormal_groups"][0][0] = data["orthonormal_groups"][0][1]
            raw = (json.dumps(data) + "\n").encode()
            certificate.write_bytes(raw)
            metadata = json.loads((package / "SOURCES.json").read_bytes())
            metadata["retained_rank32"]["sha256"] = sha256(raw).hexdigest()
            metadata["retained_rank32"]["git_blob"] = sha1(
                b"blob " + str(len(raw)).encode() + b"\0" + raw, usedforsecurity=False
            ).hexdigest()
            (package / "SOURCES.json").write_text(json.dumps(metadata))
            self.reject(command, root, "partition")

    def reject(self, command, cwd, text):
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        result = subprocess.run(
            command, cwd=cwd, env=env, capture_output=True, text=True, timeout=60
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(text, result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
