"""Current orientation must preserve frozen task-selection evidence."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("current_picker", ROOT / "scripts/choose_current_research_task.py")
current = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(current)
LEGACY = current.LEGACY
legacy = current.runpy.run_path(str(LEGACY))
CATALOG = json.loads((ROOT / legacy["CATALOG"]).read_text(encoding="utf-8"))


class CurrentResearchAssignmentTests(unittest.TestCase):
    def test_every_frozen_card_and_other_fields_stay_exact(self):
        before = copy.deepcopy(CATALOG)
        resolved = 0
        historical = 0
        for track in CATALOG["tracks"]:
            for task in track["tasks"]:
                result = legacy["select"](CATALOG, "a1" * 16, task_id=task["id"])
                original = copy.deepcopy(result)
                current.resolve_current_first_steps(result, ROOT)
                card = result["suggestions"][0]
                if task["first_step"]["command"] == ["python3", "-B", "scripts/research_baseline.py"]:
                    resolved += 1
                    self.assertEqual(card["catalog_first_step"], task["first_step"])
                    self.assertEqual(card["first_step"]["command"],
                                     ["python3", "-B", "scripts/research_selected_baseline.py"])
                    self.assertTrue(card.pop("first_step_resolution"))
                    card["first_step"] = card.pop("catalog_first_step")
                elif task["first_step"]["command"] == [
                        "python3", "-B", "research/complex-local-word-ceiling/verify.py"]:
                    historical += 1
                    self.assertEqual(card["catalog_first_step"], task["first_step"])
                    self.assertEqual(card["first_step"]["command"],
                                     ["python3", "-B", "scripts/research_selected_baseline.py"])
                    self.assertEqual(card["first_step"]["expected"],
                                     "PASS_RESEARCH_BASELINE_BINDINGS_ONLY")
                    follow_up, = card.pop("follow_up_steps")
                    self.assertEqual(follow_up["command"], [
                        "python3", "-B", "scripts/research_package.py", "--package",
                        "research/historical-complex-ceiling-replay"])
                    self.assertEqual(follow_up["expected"],
                                     "PASS_REGISTERED_RESEARCH_PACKAGE")
                    self.assertIn("#1094", follow_up["scope"])
                    self.assertIn("current supplier", follow_up["scope"])
                    self.assertNotIn("run levers.py", card["first_step"]["inspect"])
                    self.assertTrue(card.pop("first_step_resolution"))
                    card["first_step"] = card.pop("catalog_first_step")
                self.assertEqual(result, original)
        self.assertEqual(resolved, 16)
        self.assertEqual(historical, 4)
        self.assertEqual(CATALOG, before)

    def test_only_exact_generic_command_is_resolved(self):
        result = copy.deepcopy(legacy["select"](CATALOG, "0" * 32, task_id="portable-replay"))
        result["suggestions"][0]["first_step"]["command"].append("--historical-fixture")
        original = copy.deepcopy(result)
        self.assertEqual(current.resolve_current_first_steps(result, ROOT), [])
        self.assertEqual(result, original)

    def test_missing_current_helper_does_not_change_receipt(self):
        result = legacy["select"](CATALOG, "0" * 32, task_id="portable-replay")
        original = copy.deepcopy(result)
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "missing current first-step script"):
                current.resolve_current_first_steps(result, Path(directory))
        self.assertEqual(result, original)

    def test_nonexact_scientific_commands_are_not_reinterpreted(self):
        for command in (
            ["python3", "-B", "research/complex-local-word-ceiling/verify.py", "--write"],
            ["python3", "-B", "research/complex-local-word-ceiling/levers.py"],
            ["python3", "-O", "-B", "research/complex-local-word-ceiling/verify.py"],
        ):
            with self.subTest(command=command):
                result = copy.deepcopy(legacy["select"](
                    CATALOG, "0" * 32, task_id="centre-path-sharing"))
                result["suggestions"][0]["first_step"]["command"] = command
                original = copy.deepcopy(result)
                self.assertEqual(current.resolve_current_first_steps(result, ROOT), [])
                self.assertEqual(result, original)

    def test_missing_historical_reference_leaves_all_cards_unchanged(self):
        required = [
            "scripts/research_selected_baseline.py", "scripts/research_package.py",
            "research/historical-complex-ceiling-replay/VERIFY.json",
            "research/historical-complex-ceiling-replay/verify.py",
        ]
        for absent in required:
            with self.subTest(absent=absent), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                for name in required:
                    if name != absent:
                        path = root / name
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_text("fixture\n")
                result = legacy["select"](CATALOG, "0" * 32, task_id="portable-replay")
                result["suggestions"] += legacy["select"](
                    CATALOG, "0" * 32, task_id="centre-path-sharing")["suggestions"]
                original = copy.deepcopy(result)
                with self.assertRaises(ValueError) as raised:
                    current.resolve_current_first_steps(result, root)
                self.assertIn(absent, str(raised.exception))
                self.assertEqual(result, original)

    def cli(self, script, args):
        return subprocess.run([sys.executable, "-B", str(script), *args], cwd=ROOT,
                              capture_output=True, text=True, encoding="utf-8")

    def test_cli_preserves_legacy_output_and_emits_both_commands(self):
        args = ["--seed", "0" * 32, "--task", "portable-replay"]
        original = self.cli(LEGACY, args)
        output = self.cli(ROOT / "scripts/choose_current_research_task.py", args)
        self.assertEqual(original.returncode, 0)
        self.assertEqual(output.returncode, 0)
        old, new = json.loads(original.stdout), json.loads(output.stdout)
        card = new["suggestions"][0]
        self.assertEqual(card["first_step"]["command"],
                         ["python3", "-B", "scripts/research_selected_baseline.py"])
        self.assertEqual(card.pop("catalog_first_step"), old["suggestions"][0]["first_step"])
        self.assertTrue(card.pop("first_step_resolution"))
        card["first_step"] = old["suggestions"][0]["first_step"]
        self.assertEqual(new, old)
        self.assertEqual(self.cli(LEGACY, args).stdout, original.stdout)

    def test_help_and_error_preserve_child_status_and_output(self):
        for args, code in ((["--help"], 0), (["--unknown-option"], 2), (["--seed", "bad"], 2)):
            original = self.cli(LEGACY, args)
            output = self.cli(ROOT / "scripts/choose_current_research_task.py", args)
            self.assertEqual(output.returncode, code)
            self.assertEqual((output.stdout, output.stderr), (original.stdout, original.stderr))

    def test_cli_distinguishes_current_orientation_from_historical_control(self):
        args = ["--seed", "0" * 32, "--task", "complex-new-helper-inventory"]
        original = self.cli(LEGACY, args)
        output = self.cli(ROOT / "scripts/choose_current_research_task.py", args)
        self.assertEqual(original.returncode, 0, original.stderr)
        self.assertEqual(output.returncode, 0, output.stderr)
        old, new = json.loads(original.stdout), json.loads(output.stdout)
        card = new["suggestions"][0]
        self.assertEqual(card["first_step"]["command"][2], "scripts/research_selected_baseline.py")
        self.assertEqual(card["first_step"]["expected"], "PASS_RESEARCH_BASELINE_BINDINGS_ONLY")
        follow_up, = card.pop("follow_up_steps")
        self.assertEqual(follow_up["command"][-1], "research/historical-complex-ceiling-replay")
        self.assertIn("historical", follow_up["scope"].lower())
        self.assertIn("cost law", follow_up["inspect"])
        self.assertTrue(card.pop("first_step_resolution"))
        card["first_step"] = card.pop("catalog_first_step")
        self.assertEqual(new, old)
        self.assertEqual(self.cli(LEGACY, args).stdout, original.stdout)

    def test_sparse_historical_references_require_unchanged_head_entries(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            required = [
                "scripts/research_selected_baseline.py", "scripts/research_package.py",
                "research/historical-complex-ceiling-replay/VERIFY.json",
                "research/historical-complex-ceiling-replay/verify.py",
            ]
            for name in required:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("fixture\n")
            def git(*args):
                subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)
            git("init", "-q"); git("add", ".")
            git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                "-c", "core.hooksPath=/dev/null", "commit", "-qm", "references")
            omitted = required[1:]
            git("update-index", "--skip-worktree", *omitted)
            for name in omitted:
                (root / name).unlink()
            result = legacy["select"](CATALOG, "0" * 32, task_id="coverage-law-change")
            self.assertEqual(current.resolve_current_first_steps(result, root), sorted(omitted))
            # Ordinary deletion must not acquire the deliberate-sparse exemption.
            changed = omitted[-1]
            git("update-index", "--no-skip-worktree", changed)
            result = legacy["select"](CATALOG, "0" * 32, task_id="coverage-law-change")
            original = copy.deepcopy(result)
            with self.assertRaises(ValueError):
                current.resolve_current_first_steps(result, root)
            self.assertEqual(result, original)
            # Nor may a staged replacement masquerade as the original HEAD input.
            (root / changed).write_text("replacement\n")
            git("add", changed)
            git("update-index", "--skip-worktree", changed)
            (root / changed).unlink()
            with self.assertRaises(ValueError):
                current.resolve_current_first_steps(result, root)
            self.assertEqual(result, original)

    def test_sparse_helper_is_allowed_but_deletion_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            name = "scripts/research_selected_baseline.py"
            path = root / name; path.parent.mkdir(); path.write_text("print('fixture')\n")
            def git(*args):
                subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)
            git("init", "-q"); git("add", name)
            git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                "-c", "core.hooksPath=/dev/null", "commit", "-qm", "helper")
            git("update-index", "--skip-worktree", name); path.unlink()
            result = legacy["select"](CATALOG, "0" * 32, task_id="portable-replay")
            self.assertEqual(current.resolve_current_first_steps(result, root), [name])
            git("update-index", "--no-skip-worktree", name)
            result = legacy["select"](CATALOG, "0" * 32, task_id="portable-replay")
            with self.assertRaisesRegex(ValueError, "missing current first-step script"):
                current.resolve_current_first_steps(result, root)
