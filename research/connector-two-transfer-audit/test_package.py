"""Behavioral boundaries and faulty-producer controls. Nick Petalas. Apache-2.0."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import census
import independent

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def run_script(local, export, name):
    argv = [sys.executable, "-I", "-O", "-Werror", "-B", str(local / name)]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run(
        argv,
        cwd=export,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


class PackageTests(unittest.TestCase):
    def test_faulty_restoration_producer(self):
        with (
            patch.object(census, "restoring_ports", return_value=[0]),
            self.assertRaisesRegex(ValueError, "literal dirty restoration"),
        ):
            census.census(2, True)

    def test_faulty_query_producer(self):
        with (
            patch.object(census, "queries", return_value=(0, 1, 1, 1)),
            self.assertRaisesRegex(ValueError, "query-set reduction"),
        ):
            independent.run()

    def test_cold_boundaries(self):
        manifest = json.loads((HERE / "SOURCES.json").read_text())
        inputs = [ROOT / x["path"] for x in manifest["files"] if x["usage"] == "input"]
        package = [p for p in HERE.iterdir() if p.is_file()]
        self.assertLessEqual(len(package) + len(inputs), 32)
        with tempfile.TemporaryDirectory(prefix="connector-audit-") as directory:
            export = Path(directory)
            for source in package + inputs:
                self.assertFalse(source.is_symlink())
                target = export / source.relative_to(ROOT)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
                self.assertNotEqual(source.stat().st_ino, target.stat().st_ino)
            local = export / HERE.relative_to(ROOT)
            source = export / inputs[0].relative_to(ROOT)
            original = source.read_bytes()
            source.write_bytes(original + b"\nchanged\n")
            run = run_script(local, export, "verify.py")
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("source bytes changed", run.stderr)
            source.write_bytes(b"x" * ((1 << 20) + 1))
            run = run_script(local, export, "verify.py")
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("source exceeds one MiB", run.stderr)
            source.write_bytes(original)
            receipt = local / "RESULT.json"
            result = json.loads(receipt.read_text())
            result["rows"][-1]["restoring_assignments"] += 1
            receipt.write_text(json.dumps(result))
            run = run_script(local, export, "verify.py")
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("computed census differs", run.stderr)
            shutil.copyfile(HERE / "RESULT.json", receipt)
            before = {p: p.read_bytes() for p in local.iterdir() if p.is_file()}
            run = run_script(local, export, "controls.py")
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn("PASS_DIRTY_CONNECTOR_CONTROLS", run.stdout)
            self.assertEqual(before, {p: p.read_bytes() for p in before})
            self.assertFalse((export / ".git").exists())


if __name__ == "__main__":
    unittest.main()
