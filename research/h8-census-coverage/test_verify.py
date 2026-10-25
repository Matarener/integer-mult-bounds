#!/usr/bin/env python3
"""Scoped coverage controls; no producer, optimizer or price engine is run.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
import copy
from collections import Counter
import csv
import gzip
import io
import itertools
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
V = runpy.run_path(str(HERE / "verify.py"), run_name="coverage_verifier")


class CoverageControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = V["authenticate"]()
        cls.original = V["inputs"](cls.data)

    def reject(self, mutate, message):
        args = copy.deepcopy(self.original)
        mutate(*args)
        with self.assertRaisesRegex(ValueError, message):
            V["analyze"](*args)

    def test_independent_inclusion_exclusion(self):
        # Count distinct serialized sampling requests without the set-union
        # implementation or its plan-normalization function. Defaults are
        # distinct from positive draws on the retained data (checked below).
        a, b, c, tuned, plan = self.original
        keys = Counter((r["punctured"], r["receivers"]) for r in b if r["draw"] != "0")
        p589 = " ".join(map(str, V["P589"]))
        sampled_elsewhere = sum(1 for p, _ in keys if p != p589)
        self.assertEqual(sampled_elsewhere, 5962)
        self.assertEqual(sum(n - 1 for n in keys.values()), 9)
        self.assertEqual(len(a) + len(c) - 1 + sampled_elsewhere, 43122)
        # Separate direct simulation of gen_p3.build's receiver assignments.
        receivers = {tuple(cell): owner for cell, owner in plan["rcv"]}
        for row in b:
            if row["draw"] == "0":
                continue
            values = []
            for p in map(int, row["punctured"].split()):
                cells = sorted(cell for cell in receivers if p in cell)
                owners = [receivers[cell] for cell in cells]
                if p not in owners:
                    owners[0] = p
                values.append(sum(2 ** i for i, owner in enumerate(owners) if owner == p))
            self.assertNotEqual(values, [int(s.split(":")[1]) for s in row["receivers"].split()])
        self.assertEqual(V["analyze"](*self.original)["coverage"]["represented_pairs"], 43122)

    def test_duplicate_a_hides_missing_set(self):
        def mutate(a, *_):
            a[-1] = a[0].copy()
        self.reject(mutate, "stage A unique")

    def test_failed_a_row(self):
        def mutate(a, *_):
            a[0]["status"] = "error"
        self.reject(mutate, "stage A failed")

    def test_duplicate_b_draw_preserves_row_count(self):
        def mutate(a, b, *_):
            b[1]["draw"] = "0"
        self.reject(mutate, "duplicate stage B draw")

    def test_b_unlisted_punctures(self):
        def mutate(a, b, *_):
            b[0]["punctured"] = "8 9 10 11 12 13 14 15 16"
        self.reject(mutate, "stage B domain")

    def test_b_wrong_receiver_labels(self):
        def mutate(a, b, *_):
            b[1]["receivers"] = b[1]["receivers"].replace("10:", "11:")
        self.reject(mutate, "receiver labels")

    def test_b_valid_alphabet_wrong_draw(self):
        def mutate(a, b, *_):
            pairs = b[1]["receivers"].split()
            p, x = pairs[0].split(":")
            pairs[0] = p + ":" + str(int(x) % 3 + 1)
            b[1]["receivers"] = " ".join(pairs)
        self.reject(mutate, "sampling rule")

    def test_c_duplicate_hides_missing_code(self):
        def mutate(a, b, c, *_):
            c[-1] = c[0].copy()
        self.reject(mutate, "stage C complete")

    def test_c_invalid_alphabet(self):
        def mutate(a, b, c, *_):
            c[0][V["COLUMN"]] = "111111110"
        self.reject(mutate, "invalid receiver code")

    def test_tuning_duplicate_hides_missing_choice(self):
        def mutate(a, b, c, tuned, *_):
            tuned[-1] = tuned[0].copy()
        self.reject(mutate, "tuning receiver inventory")

    def test_plan_receiver_outside_cell(self):
        def mutate(a, b, c, tuned, plan):
            plan["rcv"][0][1] = 119
        self.reject(mutate, "invalid plan receiver")

    def test_invalid_geometry_set_with_valid_labels(self):
        data = self.data.copy()
        admitted, domain = V["enumerate_sets"](data)
        invalid = next(p for p in itertools.combinations(domain["eligible_labels"], 9) if p not in admitted)
        rows = copy.deepcopy(self.original[0])
        b_sets = {r["punctured"] for r in self.original[1]}
        index = next(i for i, row in enumerate(rows) if row["punctured"] not in b_sets)
        rows[index]["punctured"] = " ".join(map(str, invalid))
        stream = io.StringIO(newline="")
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
        data[V["SOURCE"] + "data/STAGE-A.csv.gz"] = gzip.compress(stream.getvalue().encode(), mtime=0)
        with self.assertRaisesRegex(ValueError, "independently enumerated source domain"):
            V["report"](data)

    def test_partition_overlap(self):
        data = self.data.copy()
        blocks = json.loads(data[V["PARTITION"]])
        blocks[-1] = blocks[0]
        data[V["PARTITION"]] = json.dumps(blocks).encode()
        with self.assertRaisesRegex(ValueError, "D4 partition"):
            V["enumerate_sets"](data)

    def run_copy(self, mutation):
        # Exercise the real CLI and authentication, independently of in-memory
        # controls. Copy the closed input set; never modify a source or symlink.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / "research/h8-census-coverage"
            shutil.copytree(HERE, package)
            # The source export may be read-only. Only this disposable copy is
            # made writable for the intentional on-disk rejection controls.
            package.chmod(0o755)
            for path in package.rglob("*"):
                path.chmod(0o755 if path.is_dir() else 0o644)
            for path, raw in self.data.items():
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
            mutation(root, package)
            return subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py")],
                                  capture_output=True, text=True, timeout=20)

    def test_source_byte_drift(self):
        def mutate(root, package):
            p = root / V["PLAN"]
            p.write_bytes(p.read_bytes() + b"\n")
        process = self.run_copy(mutate)
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("source SHA256", process.stderr)
        self.assertNotIn("PASS_H8_CENSUS_COVERAGE", process.stdout)

    def test_false_full_coverage_receipt(self):
        def mutate(root, package):
            p = package / "RESULT.json"
            result = json.loads(p.read_text())
            result["coverage"]["full_joint_coverage"] = True
            p.write_text(json.dumps(result))
        process = self.run_copy(mutate)
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("complete receipt mismatch", process.stderr)

    def test_false_effort_reconciliation_receipt(self):
        def mutate(root, package):
            p = package / "RESULT.json"
            result = json.loads(p.read_text())
            result["effort_provenance"]["resolved_historical_run_effort"] = 2000
            p.write_text(json.dumps(result))
        process = self.run_copy(mutate)
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("complete receipt mismatch", process.stderr)


if __name__ == "__main__":
    unittest.main()
