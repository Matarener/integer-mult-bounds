#!/usr/bin/env python3
"""Behavioral controls for the conditional budget and standalone boundary."""

import gzip
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SPEC = importlib.util.spec_from_file_location("budget_check", HERE / "verify.py")
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)


class Controls(unittest.TestCase):
    def test_strict_mass_does_not_admit_a_supplier(self):
        self.assertEqual(V.budget(1792)["mass_margin"], -1368)
        equal = V.budget(1792, credit=1368)
        self.assertTrue(equal["conditional_fixed_credit_rejects_all_a_ge_zero"])
        strict = V.budget(1792, credit=1369)
        self.assertEqual(strict["mass_margin"], 1)
        result = V.report()
        self.assertIsNone(result["actual_idle_credit"])
        self.assertIsNone(result["actual_complete_moment"])
        self.assertIs(result["global_obstruction_proved"], False)

    def test_numeric_types_and_source_profile(self):
        for invalid in (True, 1.0, -1, 10001):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                V.budget(invalid)
        for value in ({"1": True}, {"1": 1.0}, {"01": 1}, {"73": 1}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                V.histogram(value)
        with self.assertRaises(ValueError):
            V.parse('{"x": 1, "x": 2}')
        data = V.sources()
        source = V.parse(gzip.decompress(data[V.INPUTS[3]]))
        for event in source["core_words"]["forward"]:
            if event[0] == "climb":
                event[5] += 1
                break
        with self.assertRaisesRegex(ValueError, "literal clean-J profile"):
            V.producer(gzip.compress(json.dumps(source).encode()))
        assembly = V.parse(data[V.INPUTS[0]])
        assembly["complex_profile"]["1"] += 1
        with self.assertRaisesRegex(ValueError, "selected profile binding"):
            V.selected(assembly, V.parse(data[V.INPUTS[1]]))

    def test_git_free_cli_and_mutants(self):
        files = [p for p in HERE.iterdir() if p.is_file()]
        self.assertLessEqual(len(files), 20)
        with tempfile.TemporaryDirectory(prefix="qq16-budget-controls-") as scratch:
            root = Path(scratch)
            for source in files + [ROOT / p for p in V.INPUTS]:
                target = root / source.relative_to(ROOT)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
            script = root / HERE.relative_to(ROOT) / "verify.py"
            result = self.run_cli(script)
            self.assertEqual(result.returncode, 0, result.stderr)
            mutations = [
                (root / V.INPUTS[7], b"\n", "input hash"),
                (script.parent / "SOURCES.json", b"\n", "source manifest binding"),
            ]
            for path, suffix, marker in mutations:
                original = path.read_bytes()
                path.write_bytes(original + suffix)
                result = self.run_cli(script)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(marker, result.stderr)
                path.write_bytes(original)
            path = script.parent / "SOURCES.json"
            original = path.read_bytes()
            source = json.loads(original)
            source["files"][-1]["usage"] = "provenance"
            path.write_text(json.dumps(source))
            outcome = self.run_cli(script)
            self.assertNotEqual(outcome.returncode, 0)
            self.assertIn("source manifest binding", outcome.stderr)
            path.write_bytes(original)
            path = script.parent / "RESULT.json"
            result = json.loads(path.read_bytes())
            result["global_obstruction_proved"] = 0
            path.write_text(json.dumps(result))
            outcome = self.run_cli(script)
            self.assertNotEqual(outcome.returncode, 0)
            self.assertIn("typed receipt mismatch", outcome.stderr)

    @staticmethod
    def run_cli(script):
        return subprocess.run(
            [sys.executable, "-I", "-O", "-Werror", "-B", str(script)],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )


if __name__ == "__main__":
    unittest.main()
