"""Behavioral controls for endpoint, source and receipt failures."""

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from importlib import import_module
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
regular = import_module("independent")
m = import_module("model")
verify = import_module("verify")


def formal_columns(state: m.Matrix) -> tuple[int, ...]:
    result = []
    for source in range(8 * len(state)):
        column = 0
        for row in range(len(state)):
            entry = state[row][source // 8]
            for element in range(8):
                if (entry >> element) & 1:
                    column ^= 1 << (8 * row + m.group(element, source % 8))
        result.append(column)
    return tuple(result)


def export(destination: Path) -> Path:
    package = destination / "research/q8-inverse-uniform-tariff"
    package.mkdir(parents=True)
    for source in HERE.iterdir():
        if source.is_file() and source.suffix in (".py", ".json", ".md"):
            shutil.copyfile(source, package / source.name)
    manifest = json.loads((HERE / "SOURCES.json").read_bytes())
    for row in manifest["files"]:
        if row["usage"] == "input":
            target = destination / row["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(HERE.parents[1] / row["path"], target)
    return package


def run_script(path: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-I", "-O", "-Werror", "-B", str(path), *args],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


class BehavioralChecks(unittest.TestCase):
    def test_two_engines_on_full_dirty_input_space(self) -> None:
        cases = 0
        for roles in range(2, 9):
            for seed in range(24):
                word = tuple(
                    (
                        2 + n % 4,
                        1 + (7 * n + seed) % (2**roles - 1),
                        1 + (11 * n + 3 * seed) % (2**roles - 1),
                    )
                    for n in range(seed + 1)
                )
                formal = m.endpoint(roles, word)
                self.assertEqual(formal_columns(formal), regular.columns(roles, word))
                m.check_invariants(formal, word)
                cases += 1
        self.assertEqual(cases, 168)

    def test_real_bad_endpoint_and_tariff_producers(self) -> None:
        predecessor = verify.authenticate()
        with (
            patch.object(m, "step", side_effect=lambda state, _call: state),
            self.assertRaisesRegex(ValueError, "full dirty endpoint"),
        ):
            verify.attaining_checks(predecessor)
        original = m.tariff
        with (
            patch.object(
                m,
                "tariff",
                side_effect=lambda elements, a, b: original(elements, a, b) + 1,
            ),
            self.assertRaisesRegex(ValueError, "attaining tariff"),
        ):
            verify.attaining_checks(predecessor)
        with (
            patch.object(regular, "act", side_effect=lambda state, _call: state),
            self.assertRaisesRegex(ValueError, "faithful dirty endpoint"),
        ):
            regular.build()

    def test_git_free_cli_source_receipt_and_nonoverwrite(self) -> None:
        with tempfile.TemporaryDirectory(prefix="q8-inverse-controls-") as raw:
            root = Path(raw)
            package = export(root)
            before = {
                str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in root.rglob("*")
                if p.is_file()
            }
            for script in ("verify.py", "independent.py"):
                result = run_script(package / script)
                self.assertEqual(result.returncode, 0, result.stderr)
            after = {
                str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in root.rglob("*")
                if p.is_file()
            }
            self.assertEqual(before, after)
            source = root / "research/q8-inverse-label-pair-census/CERTIFICATE.json"
            original = source.read_bytes()
            source.write_bytes(original + b" ")
            failed = run_script(package / "verify.py")
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("changed source", failed.stderr)
            source.write_bytes(original)
            receipt = package / "RESULT.json"
            data = json.loads(receipt.read_bytes())
            data["attainment"]["predecessor_pairs"] = 63
            receipt.write_text(json.dumps(data))
            failed = run_script(package / "verify.py")
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("result receipt differs", failed.stderr)
            protected = root / "occupied.json"
            protected.write_text("retain me")
            failed = run_script(package / "verify.py", "--write", str(protected))
            self.assertNotEqual(failed.returncode, 0)
            self.assertEqual(protected.read_text(), "retain me")
            source.unlink()
            failed = run_script(package / "verify.py")
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("missing/linked source", failed.stderr)


if __name__ == "__main__":
    unittest.main()
