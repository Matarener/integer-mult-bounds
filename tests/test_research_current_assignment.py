"""Current orientation must preserve frozen task-selection evidence.

Frozen fixtures and live-catalog coverage: Ali Romman with OpenAI Codex
assistance. Retain the original routing and test authors. Apache-2.0.
"""
import copy
from contextlib import contextmanager
import importlib.util
import json
from pathlib import Path
import subprocess
import shutil
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
FROZEN = json.loads((ROOT / "tests/fixtures/research-routing-v7.json").read_text())
FROZEN_CATALOG = {
    "schema_version": 1, "priority_revision": 7,
    "priority_log": "docs/research/routing-fixture.md",
    "tracks": [{"id": "routing-fixtures", "weight": 100, "tasks": FROZEN["cards"]}],
}


@contextmanager
def frozen_cli_tree():
    """Run the real scripts with exact old cards and inert reference files."""
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        required = {FROZEN_CATALOG["priority_log"],
                    "scripts/research_selected_baseline.py", "scripts/research_package.py",
                    "research/historical-complex-ceiling-replay/VERIFY.json",
                    "research/historical-complex-ceiling-replay/verify.py"}
        for card in FROZEN["cards"]:
            required.update(card["starting_points"])
            required.add(card["first_step"]["command"][-1])
        for name in required:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Inert reference for CLI validation only.\n")
        for name in ("choose_research_task.py", "choose_current_research_task.py"):
            shutil.copyfile(ROOT / "scripts" / name, root / "scripts" / name)
        path = root / legacy["CATALOG"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(FROZEN_CATALOG))
        path = root / "certificates/selected-result.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / "certificates/selected-result.json", path)
        yield root


class CurrentResearchAssignmentTests(unittest.TestCase):
    def check_card_round_trips(self, catalog):
        before = copy.deepcopy(catalog)
        resolved = 0
        historical = 0
        for track in catalog["tracks"]:
            for task in track["tasks"]:
                result = legacy["select"](catalog, "a1" * 16, task_id=task["id"])
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
        self.assertEqual(catalog, before)
        return resolved, historical

    def test_frozen_routes_and_other_fields_stay_exact(self):
        self.assertEqual(self.check_card_round_trips(FROZEN_CATALOG), (1, 1))

    def test_every_live_card_and_other_fields_stay_exact(self):
        self.assertTrue(CATALOG["tracks"])
        self.check_card_round_trips(CATALOG)

    def test_only_exact_generic_command_is_resolved(self):
        result = copy.deepcopy(legacy["select"](FROZEN_CATALOG, "0" * 32, task_id="portable-replay"))
        result["suggestions"][0]["first_step"]["command"].append("--historical-fixture")
        original = copy.deepcopy(result)
        self.assertEqual(current.resolve_current_first_steps(result, ROOT), [])
        self.assertEqual(result, original)

    def test_missing_current_helper_does_not_change_receipt(self):
        result = legacy["select"](FROZEN_CATALOG, "0" * 32, task_id="portable-replay")
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
                    FROZEN_CATALOG, "0" * 32, task_id="centre-path-sharing"))
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
                result = legacy["select"](FROZEN_CATALOG, "0" * 32, task_id="portable-replay")
                result["suggestions"] += legacy["select"](
                    FROZEN_CATALOG, "0" * 32, task_id="centre-path-sharing")["suggestions"]
                original = copy.deepcopy(result)
                with self.assertRaises(ValueError) as raised:
                    current.resolve_current_first_steps(result, root)
                self.assertIn(absent, str(raised.exception))
                self.assertEqual(result, original)

    def cli(self, script, args, root=ROOT):
        return subprocess.run([sys.executable, "-B", str(root / "scripts" / Path(script).name), *args], cwd=root,
                              capture_output=True, text=True, encoding="utf-8")

    def test_cli_preserves_legacy_output_and_emits_both_commands(self):
        with frozen_cli_tree() as root:
            args = ["--seed", "0" * 32, "--task", "portable-replay"]
            original = self.cli(LEGACY, args, root)
            output = self.cli(ROOT / "scripts/choose_current_research_task.py", args, root)
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
            self.assertEqual(self.cli(LEGACY, args, root).stdout, original.stdout)

    def test_live_cli_preserves_each_unmapped_command(self):
        checked = {tuple(card["first_step"]["command"]) for card in FROZEN["cards"]}
        for track in CATALOG["tracks"]:
            for task in track["tasks"]:
                command = tuple(task["first_step"]["command"])
                if command in checked:
                    continue
                checked.add(command)
                with self.subTest(task=task["id"]):
                    args = ["--seed", "0" * 32, "--task", task["id"]]
                    original = self.cli(LEGACY, args)
                    output = self.cli(ROOT / "scripts/choose_current_research_task.py", args)
                    self.assertEqual(original.returncode, 0, original.stderr)
                    self.assertEqual(output.returncode, 0, output.stderr)
                    self.assertEqual(json.loads(output.stdout), json.loads(original.stdout))
                    self.assertEqual(self.cli(LEGACY, args).stdout, original.stdout)

    def test_help_and_error_preserve_child_status_and_output(self):
        for args, code in ((["--help"], 0), (["--unknown-option"], 2), (["--seed", "bad"], 2)):
            original = self.cli(LEGACY, args)
            output = self.cli(ROOT / "scripts/choose_current_research_task.py", args)
            self.assertEqual(output.returncode, code)
            self.assertEqual((output.stdout, output.stderr), (original.stdout, original.stderr))

    def test_cli_distinguishes_current_orientation_from_historical_control(self):
        with frozen_cli_tree() as root:
            args = ["--seed", "0" * 32, "--task", "centre-path-sharing"]
            original = self.cli(LEGACY, args, root)
            output = self.cli(ROOT / "scripts/choose_current_research_task.py", args, root)
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
            self.assertEqual(self.cli(LEGACY, args, root).stdout, original.stdout)

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
            result = legacy["select"](FROZEN_CATALOG, "0" * 32, task_id="centre-path-sharing")
            self.assertEqual(current.resolve_current_first_steps(result, root), sorted(omitted))
            # Ordinary deletion must not acquire the deliberate-sparse exemption.
            changed = omitted[-1]
            git("update-index", "--no-skip-worktree", changed)
            result = legacy["select"](FROZEN_CATALOG, "0" * 32, task_id="centre-path-sharing")
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
            result = legacy["select"](FROZEN_CATALOG, "0" * 32, task_id="portable-replay")
            self.assertEqual(current.resolve_current_first_steps(result, root), [name])
            git("update-index", "--no-skip-worktree", name)
            result = legacy["select"](FROZEN_CATALOG, "0" * 32, task_id="portable-replay")
            with self.assertRaisesRegex(ValueError, "missing current first-step script"):
                current.resolve_current_first_steps(result, root)
