"""Exact source validation with bounded working-file comparison.

Produced by Nick Petalas. Apache-2.0.
"""
import errno
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import new_research_package as scaffold
import research_package as package
sys.path.pop(0)

BLOCK = 1024 * 1024


class FileComparisonTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "binary source λ.bin"

    def test_equal_binary_files_across_buffer_boundaries(self):
        for size in (0, 1, BLOCK - 1, BLOCK, BLOCK + 1, 2 * BLOCK + 19):
            with self.subTest(size=size):
                expected = (bytes(range(256)) * ((size + 255) // 256))[:size]
                self.path.write_bytes(expected)
                self.assertTrue(package.file_equals_bytes(self.path, expected))
                self.assertEqual(self.path.read_bytes(), expected)

    def test_every_boundary_mutation_rejects(self):
        expected = bytes(range(256)) * (2 * BLOCK // 256 + 1)
        for position in (0, BLOCK - 1, BLOCK, BLOCK + 1, 2 * BLOCK - 1,
                         2 * BLOCK, len(expected) - 1):
            with self.subTest(position=position):
                changed = bytearray(expected)
                changed[position] ^= 1
                self.path.write_bytes(changed)
                self.assertFalse(package.file_equals_bytes(self.path, expected))

    def test_empty_truncated_and_appended_sources_reject(self):
        for expected, actual in ((b"", b"\0"), (b"x", b""), (b"abc", b"ab"),
                                 (b"abc", b"abcd"), (b"a" * BLOCK, b"a" * BLOCK + b"z")):
            with self.subTest(lengths=(len(expected), len(actual))):
                self.path.write_bytes(actual)
                self.assertFalse(package.file_equals_bytes(self.path, expected))

    def test_open_error_propagates(self):
        with self.assertRaises(FileNotFoundError):
            package.file_equals_bytes(self.path, b"")

    def test_read_error_after_mismatch_propagates_and_closes(self):
        self.path.write_bytes(b"x" * (BLOCK + 1))
        stream = self.path.open("rb")
        reads = 0

        def readinto(buffer):
            nonlocal reads
            reads += 1
            if reads == 2:
                raise OSError(errno.EIO, "injected read failure")
            return stream.readinto(buffer)

        wrapped = mock.MagicMock()
        wrapped.__enter__.return_value = wrapped
        wrapped.__exit__.side_effect = lambda *args: stream.close()
        wrapped.fileno.return_value = stream.fileno()
        wrapped.readinto.side_effect = readinto
        with mock.patch.object(Path, "open", return_value=wrapped):
            with self.assertRaises(OSError) as caught:
                package.file_equals_bytes(self.path, b"y" * (BLOCK + 1))
        self.assertEqual(caught.exception.errno, errno.EIO)
        self.assertTrue(stream.closed)


class SourceValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True, timeout=30)
        for key, value in (("user.name", "Fixture"), ("user.email", "fixture@example.invalid"),
                           ("core.autocrlf", "false")):
            package.git(self.root, "config", key, value)
        catalog = self.root / "docs/research/agent-task-catalog.json"
        catalog.parent.mkdir(parents=True)
        catalog.write_text(json.dumps({"priority_revision": 1, "tracks": [{"tasks": [
            {"id": "fixture", "question": "Preserve exact source acceptance"}]}]}))
        selected = self.root / "certificates/selected-result.json"
        selected.parent.mkdir()
        selected.write_text("{}")
        self.payload = bytes(range(256)) * (BLOCK // 256 + 1)
        self.input = self.root / "source.bin"
        self.input.write_bytes(self.payload)
        package.git(self.root, "add", ".")
        package.git(self.root, "-c", "gc.auto=0", "commit", "-qm", "fixture")
        target = scaffold.create(self.root, "fixture", "fixture", "Fixture", ["source.bin"])
        task = json.loads((target / "TASK.json").read_text())
        task.update(outcome="completed", bottleneck_link="Exact source acceptance",
                    stop_rule="One fixture", evidence="Source drift controls", ai_assistance="Fixture",
                    open_questions=[], no_open_questions_reason="Bounded fixture only")
        (target / "TASK.json").write_text(json.dumps(task))
        manifest = json.loads((target / "VERIFY.json").read_text())
        manifest["status"] = "ready"
        manifest["commands"][0]["checks"] = "Source drift fixture"
        (target / "VERIFY.json").write_text(json.dumps(manifest))
        self.target = target

    def test_complete_validator_accepts_restored_source_and_rejects_drift(self):
        first = package.validate(self.root, "research/fixture")
        mutations = (b"", self.payload[:-1], self.payload + b"x",
                     b"x" + self.payload[1:], self.payload[:-1] + b"x")
        for changed in mutations:
            self.input.write_bytes(changed)
            with self.assertRaisesRegex(ValueError, "working source drift: source.bin"):
                package.validate(self.root, "research/fixture")
        self.input.write_bytes(self.payload)
        self.assertEqual(package.validate(self.root, "research/fixture"), first)
        self.assertEqual(hashlib.sha256(self.input.read_bytes()).digest(),
                         hashlib.sha256(self.payload).digest())

    def test_complete_validator_retains_blob_and_sha_rejections(self):
        path = self.target / "SOURCES.json"
        original = json.loads(path.read_text())
        for field, replacement in (("git_blob", "0" * 40), ("sha256", "0" * 64)):
            changed = json.loads(json.dumps(original))
            row = next(r for r in changed["files"] if r["path"] == "source.bin")
            row[field] = replacement
            path.write_text(json.dumps(changed))
            with self.assertRaisesRegex(ValueError, "provenance mismatch: source.bin"):
                package.validate(self.root, "research/fixture")
        path.write_text(json.dumps(original))
        package.validate(self.root, "research/fixture")


if __name__ == "__main__":
    unittest.main()
