"""Public-entry controls for the composed boundary. Apache-2.0."""

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import boundary  # noqa: E402
import verify  # noqa: E402


class BoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word, _ = verify.sources(boundary.ROOT)

    def test_label_types_and_shapes_reject_in_both_modes(self):
        variants = []
        for value in (0.5, 0.0, True, "0", None):
            word = verify.fixture(self.word, paired=True)
            word["lines"][0][1] = value
            variants.append(word)
        for field, value in (("h", 8.0), ("v", True), ("lines", [])):
            word = copy.deepcopy(self.word)
            word[field] = value
            variants.append(word)
        word = copy.deepcopy(self.word)
        word["lines"][0].append(0)
        variants.append(word)
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            path = directory / "word.json"
            for index, word in enumerate(variants):
                path.write_text(json.dumps(word), encoding="utf-8")
                for mode in ("check", "export"):
                    output = (
                        directory / (str(index) + mode) if mode == "export" else None
                    )
                    with self.subTest(index=index, mode=mode), self.assertRaises(
                        ValueError
                    ):
                        boundary.execute(mode, path, output, scratch=directory)
                    if output is not None:
                        self.assertFalse(output.exists())

    def test_existing_output_and_input_unchanged(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            path, output = directory / "word.json", directory / "existing"
            path.write_text(json.dumps(self.word), encoding="utf-8")
            before = path.read_bytes()
            output.mkdir()
            (output / "sentinel").write_bytes(b"preserve")
            with self.assertRaises(ValueError):
                boundary.execute("export", path, output, scratch=directory)
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(list(output.iterdir()), [output / "sentinel"])
            self.assertEqual((output / "sentinel").read_bytes(), b"preserve")

    def test_public_cli_optimized_check_and_rejection(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            for bad in (False, True):
                word = verify.fixture(self.word, fractional=bad, paired=True)
                path = directory / "word.json"
                path.write_text(json.dumps(word), encoding="utf-8")
                run = subprocess.run(
                    [
                        sys.executable,
                        "-I",
                        "-O",
                        "-Werror",
                        "-B",
                        str(verify.PACKAGE / "boundary.py"),
                        "check",
                        str(path),
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                with self.subTest(fractional=bad):
                    self.assertEqual(run.returncode == 0, not bad, run.stderr)
                    if not bad:
                        result = json.loads(run.stdout)
                        self.assertEqual(result["schema"], "integer-xor-scatter-v1")
                        self.assertEqual(result["input_occurrences"], 529)
                        self.assertEqual(result["normalized_scatter_terms"], 527)

    def test_each_delegate_corruption_rejects_before_publication(self):
        bodies = boundary.sources(boundary.ROOT)
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            path = directory / "word.json"
            path.write_text(json.dumps(self.word), encoding="utf-8")
            for name, body in bodies.items():
                target = directory / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(body)
            for name, body in bodies.items():
                target = directory / name
                target.write_bytes(body + b" ")
                with self.subTest(source=name), self.assertRaisesRegex(
                    ValueError, "source pin"
                ):
                    boundary.execute(
                        "export", path, directory / "output", directory, directory
                    )
                self.assertFalse((directory / "output").exists())
                target.write_bytes(body)

    def test_input_replacement_after_validation_uses_same_snapshot(self):
        real_module = boundary.module
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            path = directory / "word.json"
            path.write_text(
                json.dumps(verify.fixture(self.word, paired=True)), encoding="utf-8"
            )

            def replace_after_validation(body, module_path):
                scope = real_module(body, module_path)
                if str(module_path).endswith(boundary.LABELS):
                    validate = scope["validate_labels"]

                    def validate_and_replace(word):
                        validate(word)
                        path.write_text(
                            json.dumps(verify.fixture(self.word, fractional=True)),
                            encoding="utf-8",
                        )

                    scope["validate_labels"] = validate_and_replace
                return scope

            with mock.patch.object(
                boundary, "module", side_effect=replace_after_validation
            ):
                result = boundary.execute(
                    "export", path, directory / "output", scratch=directory
                )
            self.assertEqual(result["input_occurrences"], 529)
            self.assertEqual(result["normalized_scatter_terms"], 527)
            expected = json.loads((verify.PACKAGE / "RESULT.json").read_bytes())
            self.assertEqual(
                verify.artifacts(directory / "output"), expected["accepted"]["baseline"]
            )
            self.assertEqual(json.loads(path.read_bytes())["lines"][0][1], 0.5)


if __name__ == "__main__":
    unittest.main()
