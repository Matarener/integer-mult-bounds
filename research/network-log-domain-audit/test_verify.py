#!/usr/bin/env python3
"""Cold, Git-free CLI controls for the logarithm-domain audit.

Prepared for roger-sato with substantial OpenAI Codex assistance. Apache-2.0.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = Path("research/network-log-domain-audit")


class AuditControls(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="network-log-domain-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.package = self.root / PACKAGE
        self.package.mkdir(parents=True)
        for source in HERE.iterdir():
            if source.is_file():
                shutil.copyfile(source, self.package / source.name)
        manifest = json.loads((HERE / "VERIFY.json").read_text(encoding="utf-8"))
        for name in manifest["inputs"]:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)

    def run_audit(self, optimize=False):
        return subprocess.run(
            [sys.executable, "-I", "-B", *(["-O"] if optimize else []),
             str(self.package / "verify.py")],
            cwd=self.root, capture_output=True, text=True, timeout=10,
        )

    def test_git_free_replay_normal_and_optimized(self):
        before = {p.relative_to(self.root): p.read_bytes()
                  for p in self.root.rglob("*") if p.is_file()}
        for optimize in (False, True):
            result = self.run_audit(optimize)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("production_guard_adopted=0", result.stdout)
        after = {p.relative_to(self.root): p.read_bytes()
                 for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_modified_helper_rejected_before_execution(self):
        (self.root / "scripts/certify.py").write_text(
            'raise RuntimeError("UNAUTHENTICATED_CODE_RAN")\n', encoding="utf-8")
        result = self.run_audit()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source drift: scripts/certify.py", result.stderr)
        self.assertNotIn("UNAUTHENTICATED_CODE_RAN", result.stderr)
        self.assertNotIn("PASS_NETWORK", result.stdout)

    def test_modified_receipt_rejected(self):
        path = self.package / "RESULT.json"
        receipt = json.loads(path.read_text(encoding="utf-8"))
        receipt["production_guard_adopted"] = True
        path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
        result = self.run_audit(True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("audit receipt differs", result.stderr)
        self.assertNotIn("PASS_NETWORK", result.stdout)

    def test_weakened_proposed_patch_rejected(self):
        path = self.package / "proposed-guard.patch"
        path.write_text(path.read_text(encoding="utf-8").replace(
            "log_bound > 0", "log_bound >= 0"), encoding="utf-8")
        result = self.run_audit()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("proposed patch differs from tested guard", result.stderr)
        self.assertNotIn("PASS_NETWORK", result.stdout)


if __name__ == "__main__":
    unittest.main()
