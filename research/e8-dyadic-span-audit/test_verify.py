#!/usr/bin/env python3
"""Whole-command corruption and regeneration controls for this certificate.

@CubeJerry, with OpenAI Codex assistance. Apache-2.0.
"""
from copy import deepcopy
from pathlib import Path
import gzip
import json
import shutil
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PYTHON = [sys.executable, "-I", "-W", "error", "-B"]
if sys.flags.optimize:
    PYTHON.insert(1, "-O")


def execute(script, *args):
    return subprocess.run([*PYTHON, str(script), *map(str, args)],
                          capture_output=True, text=True, timeout=120)


class WholeCommandTests(unittest.TestCase):
    def test_complete_positive(self):
        run = execute(PACKAGE / "verify.py")
        self.assertEqual(run.returncode, 0, run.stderr)
        result = json.loads(run.stdout)
        self.assertEqual(result["status"], "PASS_E8_DYADIC_SPAN_AUDIT")
        self.assertEqual(result["splittings"]["cases"], 6595)
        self.assertEqual(result["transports"]["signed_root_images"], 28800)

    def test_regenerated_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "rebuilt.gz"
            run = execute(PACKAGE / "build_certificate.py", "--output", output)
            self.assertEqual(run.returncode, 0, run.stderr)
            # gzip headers/streams are not the mathematical object.
            self.assertEqual(gzip.decompress(output.read_bytes()),
                             gzip.decompress((PACKAGE / "CERTIFICATE.json.gz").read_bytes()))

    def test_certificate_corruptions(self):
        original = json.loads(gzip.decompress((PACKAGE / "CERTIFICATE.json.gz").read_bytes()))
        mutations = []
        changed = deepcopy(original)
        changed["witnesses"][0]["coefficients"][0][0][1] *= -1
        mutations.append(("wrong combination", changed, "E=C A identity"))
        changed = deepcopy(original)
        del changed["witnesses"][-1]
        mutations.append(("omitted case", changed, "case count"))
        changed = deepcopy(original)
        changed["witnesses"][0]["case"] = ["S1", 123]
        mutations.append(("wrong case", changed, "case domain/order mismatch"))
        changed = deepcopy(original)
        item = next(w for w in changed["witnesses"] if w["case"][0] == "S3" and len(w["pivots"]) == 6)
        for field in ("pivots", "basis", "coefficients"):
            item[field].pop()
        mutations.append(("dependent boundary misclassified", changed, "A=A[:,J] E identity"))
        with tempfile.TemporaryDirectory() as tmp:
            for label, certificate, diagnostic in mutations:
                with self.subTest(label=label):
                    path = Path(tmp) / "mutant.gz"
                    path.write_bytes(gzip.compress(json.dumps(certificate).encode(), mtime=0))
                    run = execute(PACKAGE / "verify.py", "--certificate", path)
                    self.assertNotEqual(run.returncode, 0)
                    self.assertIn(diagnostic, run.stderr)
                    self.assertNotIn("PASS_E8_DYADIC_SPAN_AUDIT", run.stdout)

    def test_source_corruptions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "research/e8-dyadic-span-audit"
            shutil.copytree(PACKAGE, target, ignore=shutil.ignore_patterns("__pycache__"))
            manifest = json.loads((PACKAGE / "VERIFY.json").read_text())
            for name in manifest["inputs"]:
                destination = root / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, destination)
            inputs = [root / name for name in manifest["inputs"]]
            inputs.append(target / "predecessor/PR6198-PROOF.md")
            for path in inputs:
                with self.subTest(path=str(path.relative_to(root))):
                    original = path.read_bytes()
                    path.write_bytes(original + b"\ncorruption control\n")
                    run = execute(target / "verify.py")
                    self.assertNotEqual(run.returncode, 0)
                    self.assertIn("bytes changed", run.stderr)
                    self.assertNotIn("PASS_E8_DYADIC_SPAN_AUDIT", run.stdout)
                    path.write_bytes(original)


if __name__ == "__main__":
    unittest.main(verbosity=2)
