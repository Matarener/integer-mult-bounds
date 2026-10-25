"""Behavioral controls for the published verifier and native arithmetic."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify
from oracle import require, tables


class PackageControls(unittest.TestCase):
    def test_native_faults(self):
        compiler = shutil.which("clang++") or shutil.which("g++")
        require(compiler is not None, "compiler required")
        _, multiply = tables()
        source = (verify.PACKAGE / "search.cpp").read_text()
        changes = [
            ("s ^ t[f.g][s]", "s ^ t[0][s]"),
            ("group(h, g)", "group(g, h)"),
            ("a[row] = b;", "a[row] = row == 3 ? 0U : b;"),
        ]
        with tempfile.TemporaryDirectory(prefix="q8-controls-") as name:
            directory = Path(name)
            for old, new in changes:
                with self.subTest(fault=old):
                    require(source.count(old) == 1, "mutation no longer unique")
                    altered = directory / "mutant.cpp"
                    altered.write_text(source.replace(old, new))
                    executable = directory / "mutant"
                    verify.run(
                        [compiler, *verify.FLAGS, str(altered), "-o", str(executable)],
                        120,
                    )
                    result = subprocess.run(
                        [str(executable), "probes", name],
                        capture_output=True,
                        timeout=30,
                    )
                    if result.returncode == 0:
                        with self.assertRaisesRegex(ValueError, "probe mismatch"):
                            verify.independent_probes(directory, multiply)

    def test_cli_boundaries(self):
        with tempfile.TemporaryDirectory(prefix="q8-cli-") as name:
            directory = Path(name)
            package = directory / "research" / verify.PACKAGE.name
            shutil.copytree(verify.PACKAGE, package)
            manifest = json.loads((package / "SOURCES.json").read_text())
            for row in manifest["files"]:
                if row["usage"] == "input":
                    target = directory / row["path"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(verify.PACKAGE.parent.parent / row["path"], target)
            command = [
                sys.executable,
                "-I",
                "-O",
                "-Werror",
                "-B",
                str(package / "verify.py"),
            ]
            receipt = directory / "existing.json"
            receipt.write_text("preserve\n")
            result = subprocess.run(
                command + ["--write-receipt", str(receipt)],
                capture_output=True,
                timeout=30,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b"refusing to overwrite", result.stderr)
            self.assertEqual(receipt.read_text(), "preserve\n")
            source = directory / manifest["files"][-1]["path"]
            source.write_bytes(source.read_bytes() + b"\nsource mutation\n")
            result = subprocess.run(command, capture_output=True, timeout=30)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b"input drift", result.stderr)
            source.write_bytes(source.read_bytes().removesuffix(b"\nsource mutation\n"))
            result_path = package / "RESULT.json"
            altered = json.loads(result_path.read_text())
            altered["search"][0]["hits"][0] = False
            result_path.write_text(json.dumps(altered))
            result = subprocess.run(command, capture_output=True, timeout=600)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b"receipt mismatch", result.stderr)


if __name__ == "__main__":
    unittest.main()
