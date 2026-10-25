# SPDX-License-Identifier: Apache-2.0
"""Exercise the actual isolated CLI and its source/receipt failure boundaries."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


class Controls(unittest.TestCase):
    def test_actual_cli(self):
        with tempfile.TemporaryDirectory(prefix="synthetic-algebra-") as temporary:
            root = Path(temporary)
            package = root / "research/synthetic-allsize-identity"
            package.mkdir(parents=True)
            for name in ("verify.py", "RESULT.json", "SOURCES.json"):
                shutil.copyfile(HERE / name, package / name)
            sources = json.loads((package / "SOURCES.json").read_text())
            for row in sources["files"]:
                if row["usage"] == "input":
                    destination = root / row["path"]
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(ROOT / row["path"], destination)
            command = [sys.executable, "-I", "-O", "-Werror", "-B",
                       str(package / "verify.py")]
            good = subprocess.run(command, cwd=root, text=True, capture_output=True, timeout=120)
            self.assertEqual(good.returncode, 0, good.stderr)
            self.assertIn("PASS_SYNTHETIC_ALLSIZE_EVIDENCE", good.stdout)
            engine = root / "research/synthetic-layout-independent/physical.py"
            original = engine.read_bytes()
            engine.write_bytes(original + b"\n# changed source control\n")
            self.reject(command, root, "source bytes")
            engine.unlink()
            self.reject(command, root, "FileNotFoundError")
            engine.write_bytes(original)
            receipt = json.loads((package / "RESULT.json").read_text())
            receipt["matrices"]["residue_rings"].remove(15)
            (package / "RESULT.json").write_text(json.dumps(receipt))
            self.reject(command, root, "exact finite receipt")

    def reject(self, command, root, diagnostic):
        actual = subprocess.run(command, cwd=root, text=True, capture_output=True, timeout=120)
        self.assertNotEqual(actual.returncode, 0)
        self.assertIn(diagnostic, actual.stderr)
        self.assertNotIn("PASS_SYNTHETIC_ALLSIZE_EVIDENCE", actual.stdout)


if __name__ == "__main__":
    unittest.main()
