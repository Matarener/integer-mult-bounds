#!/usr/bin/env python3
"""Behavioral controls for temporal, capacity, inventory and source claims."""

import copy
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("temporal", PACKAGE / "verify.py")
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)


class TemporalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan, cls.spec = V.load_sources()
        cls.model = V.source_model(cls.plan, cls.spec)
        cls.cert = V.read_json(PACKAGE / "CERTIFICATE.json")

    def test_both_literal_attainments(self):
        for name, expected in V.EXPECTED.items():
            profile = self.cert["profiles"][name]
            V.check_profile(profile, self.model, expected)
            rows = V.expand(profile, self.model)
            self.assertEqual(V.check_rows(rows, self.model), expected)
            self.assertEqual(sum(r * n for r, n in expected.items()), 237024)

    def test_flow_rejects_wrong_time_even_with_same_width(self):
        profile = copy.deepcopy(self.cert["profiles"]["old"])
        row = profile["flow"][0]
        row[1] = next(t for t in range(144) if t not in self.model.groups[row[0]].times)
        with self.assertRaisesRegex(ValueError, "outside window"):
            V.check_profile(profile, self.model, V.EXPECTED["old"])

    def test_inventory_and_typed_counts(self):
        for mutation in ("missing-flow", "duplicate-flow", "boolean-count", "missing-bin"):
            profile = copy.deepcopy(self.cert["profiles"]["old"])
            if mutation == "missing-flow":
                profile["flow"].pop()
            elif mutation == "duplicate-flow":
                profile["flow"].append(profile["flow"][0])
            elif mutation == "boolean-count":
                profile["flow"][0][-1] = True
            else:
                profile["allocation"].pop()
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                V.check_profile(profile, self.model, V.EXPECTED["old"])
        profile = copy.deepcopy(self.cert["profiles"]["old"])
        donor = next(r for r in profile["flow"] if r[3] > 1)
        recipient = next(r for r in profile["flow"]
                         if r[0] == donor[0] and r[2] == donor[2]
                         and r[1] != donor[1] and r[3] < 240)
        donor[3] -= 1
        recipient[3] += 1
        with self.assertRaisesRegex(ValueError, "per-call demand"):
            V.check_profile(profile, self.model, V.EXPECTED["old"])

    def test_overfull_pattern_and_wrong_idle_claim(self):
        profile = copy.deepcopy(self.cert["profiles"]["old"])
        profile["patterns"][0][1][-1] = 1
        with self.assertRaisesRegex(ValueError, "overfull"):
            V.check_profile(profile, self.model, V.EXPECTED["old"])
        profile = self.cert["profiles"]["old"]
        with self.assertRaisesRegex(ValueError, "idle profile"):
            V.check_profile(profile, self.model, {1: 2430, 18: 1, 48: 4887})

    def test_literal_controls_independent_of_flow(self):
        rows = V.expand(self.cert["profiles"]["old"], self.model)
        for field, value in ((5, rows[0][5] + 1), (6, rows[0][6] + 1), (4, 112)):
            mutant = list(rows)
            row = list(rows[0])
            row[field] = value
            mutant[0] = tuple(row)
            with self.subTest(field=field), self.assertRaises(ValueError):
                V.check_rows(mutant, self.model)
        mutant = list(rows)
        mutant[0] = mutant[1]
        with self.assertRaisesRegex(ValueError, "duplicate literal helper"):
            V.check_rows(mutant, self.model)
        mutant = list(rows)
        row = list(rows[0])
        row[0] = next(t for t in range(144) if t not in self.model.windows[row[2], row[3]][1])
        mutant[0] = tuple(row)
        with self.assertRaises(ValueError):
            V.check_rows(mutant, self.model)

    def test_source_inventory_and_window_rejections(self):
        for field in ("per_call_widths", "windows", "order"):
            mutant = copy.deepcopy(self.plan)
            if field == "per_call_widths":
                mutant[field][0]["widths"][0] = 8
            elif field == "windows":
                key = next(iter(mutant[field]))
                mutant[field][key][1].append(mutant[field][key][1][0])
            else:
                mutant[field][0] = mutant[field][1]
            with self.subTest(field=field), self.assertRaises(ValueError):
                V.source_model(mutant, self.spec)

    def test_real_source_drift_cli_under_optimization(self):
        with tempfile.TemporaryDirectory(prefix="t16-window-test-") as temporary:
            root = Path(temporary)
            package = root / "research/t16-window-cap"
            package.mkdir(parents=True)
            for name in ("verify.py", "SOURCES.json", "CERTIFICATE.json", "RESULT.json"):
                shutil.copyfile(PACKAGE / name, package / name)
            for pin in V.read_json(PACKAGE / "SOURCES.json")["files"]:
                if pin["usage"] == "input":
                    destination = root / pin["path"]
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(V.ROOT / pin["path"], destination)
            environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
            command = [sys.executable, "-I", "-O", "-Werror", "-B", str(package / "verify.py")]
            result = subprocess.run(command, capture_output=True, text=True,
                                    timeout=30, env=environment, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            plan = root / (V.PREFIX + "PLAN.json")
            plan.write_bytes(plan.read_bytes() + b"\n")
            result = subprocess.run(command, capture_output=True, text=True,
                                    timeout=30, env=environment, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source bytes", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
