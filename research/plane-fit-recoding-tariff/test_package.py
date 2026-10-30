#!/usr/bin/env python3
"""Behavioral and actual-CLI failure controls for the scoped tariff package."""

import json
import os
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from hashlib import sha1, sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
API = runpy.run_path(str(HERE / "verify.py"), run_name="tariff_controls")


def repin(raw, pin):
    pin["sha256"] = sha256(raw).hexdigest()
    pin["git_blob"] = sha1(
        b"blob " + str(len(raw)).encode() + b"\0" + raw, usedforsecurity=False
    ).hexdigest()


class TariffBehavior(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.labels, cls.groups = API["load"]()
        cls.costs = API["closure_table"](cls.labels, cls.groups)

    def test_spanning_is_required(self):
        identity = [[int(i == j) for j in range(32)] for i in range(32)]
        self.assertEqual(API["query_bill"](identity, 2, self.costs), 224)
        identity[-1] = identity[0][:]
        with self.assertRaisesRegex(ValueError, "do not span"):
            API["query_bill"](identity, 2, self.costs)

    def test_outside_rowspace_is_not_admitted(self):
        query = [0] * 112
        for p in self.groups[0][::2]:
            query[p] = 1
        self.assertEqual(API["coordinates"](query, self.groups, 2)[0], 1)
        query[self.groups[0][0]] = 0
        with self.assertRaisesRegex(ValueError, "outside fixed"):
            API["coordinates"](query, self.groups, 2)

    def test_geometry_must_match_the_partition(self):
        groups = deepcopy(self.groups)
        groups[0][0] = groups[0][1]
        with self.assertRaisesRegex(ValueError, "partition"):
            API["validate_partition"](self.labels, groups)
        labels = self.labels[:]
        labels[self.groups[0][0]] ^= 1
        with self.assertRaisesRegex(ValueError, "Gram"):
            API["validate_partition"](labels, self.groups)

    def cli_case(self, mutation, diagnostic):
        with tempfile.TemporaryDirectory(prefix="tariff-control-") as scratch:
            root = Path(scratch)
            package = root / "research" / HERE.name
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
            private_files = list(package.rglob("*"))
            self.assertLessEqual(len(private_files), 32)
            package.chmod(0o700)
            for local in private_files:
                local.chmod(0o700 if local.is_dir() else 0o600)
            source = root / API["SOURCE"]
            source.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / API["SOURCE"], source)
            mutation(package, source)
            command = [
                sys.executable,
                "-I",
                "-X",
                "pycache_prefix=" + str(root / "cache"),
                "-Werror",
                "-B",
                str(package / "verify.py"),
            ]
            result = subprocess.run(
                command, check=False, text=True, capture_output=True, timeout=30
            )
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertNotIn("PASS_PLANE_FIT_RECODING_TARIFF", result.stdout)
            self.assertIn(diagnostic, result.stderr)

    def test_cli_source_bytes(self):
        def mutation(package, source):
            source.write_bytes(source.read_bytes() + b" ")

        self.cli_case(mutation, "source SHA256 differs")

    def test_cli_retained_bytes(self):
        def mutation(package, source):
            target = package / "RETAINED-RANK32.json"
            target.write_bytes(target.read_bytes() + b" ")

        self.cli_case(mutation, "source SHA256 differs")

    def test_cli_false_receipt(self):
        def mutation(package, source):
            target = package / "RESULT.json"
            value = json.loads(target.read_text())
            value["all_field_rowspace_tariff_minimum"] = 223
            target.write_text(json.dumps(value))

        self.cli_case(mutation, "result receipt differs")

    def test_cli_semantic_partition_after_repin(self):
        def mutation(package, source):
            target = package / "RETAINED-RANK32.json"
            value = json.loads(target.read_text())
            value["orthonormal_groups"][0][0] = value["orthonormal_groups"][0][1]
            raw = json.dumps(value).encode()
            target.write_bytes(raw)
            metadata = package / "SOURCES.json"
            pins = json.loads(metadata.read_text())
            repin(raw, pins["retained_rank32"])
            metadata.write_text(json.dumps(pins))

        self.cli_case(mutation, "exact port partition")


if __name__ == "__main__":
    if "TMPDIR" in os.environ:
        Path(os.environ["TMPDIR"]).mkdir(parents=True, exist_ok=True)
    unittest.main()
