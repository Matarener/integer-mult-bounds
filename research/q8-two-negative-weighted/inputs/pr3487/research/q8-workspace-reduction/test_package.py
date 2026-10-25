"""Behavioral controls for full dirty restoration, both reductions and replay."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import finite
from model import direct_word
from reduction import check_intertwining, compress
from verify import fixtures

PACKAGE = Path(__file__).resolve().parent


class ReductionControls(unittest.TestCase):
    def test_real_reducer_faults_and_dirty_endpoint(self):
        name, target, word = fixtures()[2]
        self.assertEqual(name, "quotient-discarded-dirt")
        result = compress(word, target)
        self.assertEqual(result["route"], "quotient")
        self.assertEqual(len(result["target"]), 2)
        check_intertwining(word, target, result)
        with (
            patch(
                "reduction.signature",
                side_effect=lambda value, rows: value & ((1 << len(rows)) - 1),
            ),
            self.assertRaises(ValueError),
        ):
            compress(word, target, "quotient")
        with (
            patch("reduction.dot", return_value=0),
            self.assertRaisesRegex(ValueError, "quotient basis incomplete"),
        ):
            compress(word, target)
        dirty_fault = (*word, (1, 1, 2))
        with self.assertRaisesRegex(ValueError, "full dirty endpoint"):
            compress(dirty_fault, target)
        with self.assertRaisesRegex(ValueError, "full dirty endpoint"):
            compress(word[:-1], target)

    def test_boundaries_and_order(self):
        for word, target in (
            ([(0, 1, 2)], (2,)),
            ([(1, 1, 3)], (3,)),
            ([(1, 1, True)], (2,)),
            ([], (0,) * 13),
            ([(1, 1, 2)] * 49, (2,)),
            ([], (False,)),
        ):
            with (
                self.subTest(word=word[:2], target=target),
                self.assertRaises(ValueError),
            ):
                compress(word, target)
        word = direct_word((6, 0))
        with self.assertRaisesRegex(ValueError, "full dirty endpoint"):
            compress(tuple(reversed(word)), (6, 0))
        with self.assertRaisesRegex(ValueError, "route"):
            compress((), (0,), "unknown")

    def test_native_action_mutant_and_source_drift(self):
        compiler = shutil.which("clang++") or shutil.which("g++")
        self.assertIsNotNone(compiler)
        with tempfile.TemporaryDirectory(prefix="q8-controls-") as temp:
            directory = Path(temp)
            source = (PACKAGE / "inputs/pr3471-search.cpp").read_text()
            changed = source.replace("s ^ t[f.g][s]", "s ^ t[0][s]")
            self.assertNotEqual(source, changed)
            mutant = directory / "mutant.cpp"
            mutant.write_text(changed)
            executable = directory / "mutant"
            finite.run([compiler, *finite.FLAGS, str(mutant), "-o", str(executable)])
            finite.run([str(executable), "probes", str(directory)])
            receipt = json.loads((PACKAGE / "inputs/pr3471-RESULT.json").read_text())
            with self.assertRaisesRegex(ValueError, "Hamilton native probes"):
                finite.check_probes(directory, receipt)
            copied = directory / "package"
            shutil.copytree(PACKAGE, copied)
            with (copied / "inputs/pr3471-search.cpp").open("a") as handle:
                handle.write("\n// changed\n")
            with (
                patch.object(finite, "PACKAGE", copied),
                self.assertRaisesRegex(ValueError, "retained source drift"),
            ):
                finite.source_pins()

    def test_cli_refuses_overwrite(self):
        with tempfile.TemporaryDirectory(prefix="q8-cli-") as temp:
            destination = Path(temp) / "receipt.json"
            destination.write_text("keep\n")
            run = subprocess.run(
                [
                    sys.executable,
                    "-I",
                    "-O",
                    "-B",
                    str(PACKAGE / "verify.py"),
                    "--write-result",
                    str(destination),
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("refuse receipt overwrite", run.stderr)
            self.assertEqual(destination.read_text(), "keep\n")


if __name__ == "__main__":
    unittest.main()
