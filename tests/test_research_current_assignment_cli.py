"""Exercise sparse receipts and resolver failures through the real picker CLI.

Prepared by ToikY with substantial OpenAI Codex assistance. Reuses the frozen routing
fixtures by Ali Romman with OpenAI Codex assistance; retain the original routing
authors Douglas Colkitt and Mihir Srivastava. Apache-2.0.
"""
import json
import subprocess
import sys
import unittest

from test_research_current_assignment import frozen_cli_tree


CURRENT_HELPER = "scripts/research_selected_baseline.py"
HISTORICAL_REFERENCES = [
    "scripts/research_package.py",
    "research/historical-complex-ceiling-replay/VERIFY.json",
    "research/historical-complex-ceiling-replay/verify.py",
]


class CurrentResearchAssignmentCliTests(unittest.TestCase):
    def cli(self, root, script, task):
        return subprocess.run(
            [sys.executable, "-B", str(root / "scripts" / script),
             "--seed", "0" * 32, "--task", task],
            cwd=root, capture_output=True, text=True, encoding="utf-8",
        )

    def git(self, root, *args):
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)

    def test_materialized_routes_succeed_without_sparse_receipts(self):
        with frozen_cli_tree() as root:
            for task in ("portable-replay", "centre-path-sharing"):
                with self.subTest(task=task):
                    child = self.cli(root, "choose_research_task.py", task)
                    output = self.cli(root, "choose_current_research_task.py", task)
                    self.assertEqual(child.returncode, 0, child.stderr)
                    self.assertEqual(output.returncode, 0, output.stderr)
                    self.assertEqual(output.stderr, "")
                    receipt = json.loads(output.stdout)
                    self.assertNotIn("sparse_checkout", receipt)
                    card = receipt["suggestions"][0]
                    self.assertEqual(card["first_step"]["command"],
                                     ["python3", "-B", CURRENT_HELPER])
                    self.assertEqual(card["catalog_first_step"],
                                     json.loads(child.stdout)["suggestions"][0]["first_step"])

    def test_sparse_cli_reports_current_omissions_and_preserves_catalogue_omissions(self):
        cases = (
            ("portable-replay", [CURRENT_HELPER], []),
            ("centre-path-sharing", HISTORICAL_REFERENCES,
             ["research/complex-local-word-ceiling/README.md"]),
        )
        for task, current_omissions, catalogue_omissions in cases:
            with self.subTest(task=task), frozen_cli_tree() as root:
                self.git(root, "init", "-q")
                self.git(root, "add", ".")
                self.git(root, "-c", "user.name=Fixture",
                         "-c", "user.email=fixture@example.invalid",
                         "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false",
                         "commit", "-qm", "frozen routing references")
                omitted = current_omissions + catalogue_omissions
                self.git(root, "update-index", "--skip-worktree", *omitted)
                for name in omitted:
                    (root / name).unlink()
                child = self.cli(root, "choose_research_task.py", task)
                output = self.cli(root, "choose_current_research_task.py", task)
                self.assertEqual(child.returncode, 0, child.stderr)
                self.assertEqual(output.returncode, 0, output.stderr)
                self.assertEqual(output.stderr, "")
                receipt = json.loads(output.stdout)
                self.assertIn("sparse_checkout", receipt)
                sparse = receipt["sparse_checkout"]
                self.assertIn("omitted_current_first_step_paths", sparse)
                self.assertEqual(sparse["omitted_current_first_step_paths"],
                                 sorted(current_omissions))
                self.assertEqual(sparse["omitted_catalogue_paths"], catalogue_omissions)
                if catalogue_omissions:
                    self.assertEqual(sparse["omitted_catalogue_paths"],
                                     json.loads(child.stdout)["sparse_checkout"]["omitted_catalogue_paths"])
                self.assertIn("HEAD and skip-worktree", sparse["scope"])
                self.assertIn("not replay dependencies", sparse["scope"])
                self.assertEqual(receipt["suggestions"][0]["first_step"]["command"],
                                 ["python3", "-B", CURRENT_HELPER])

    def test_successful_child_then_missing_current_helper_fails_with_status_two(self):
        with frozen_cli_tree() as root:
            (root / CURRENT_HELPER).unlink()
            child = self.cli(root, "choose_research_task.py", "portable-replay")
            output = self.cli(root, "choose_current_research_task.py", "portable-replay")
            self.assertEqual(child.returncode, 0, child.stderr)
            self.assertEqual(json.loads(child.stdout)["suggestions"][0]["task_id"],
                             "portable-replay")
            self.assertEqual(output.returncode, 2, output.stderr)
            self.assertEqual(output.stdout, "")
            self.assertIn("current first-step resolution failed: missing current first-step script: "
                          + CURRENT_HELPER, output.stderr)
