#!/usr/bin/env python3
"""Show current first steps and preserve the frozen task-picker output.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Historical-ceiling routing: Mihir Srivastava with OpenAI Codex assistance.
Arguments and selection are delegated to the historical picker CLI.
"""
import json
from pathlib import Path
import runpy
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / "scripts/choose_research_task.py"


def resolve_current_first_steps(result, root):
    """Resolve known startup routes at the CLI boundary; keep the source card."""
    old = ["python3", "-B", "scripts/research_baseline.py"]
    ceiling = ["python3", "-B", "research/complex-local-word-ceiling/verify.py"]
    current = "scripts/research_selected_baseline.py"
    cards = [card for card in result["suggestions"]
             if card["first_step"]["command"] in (old, ceiling)]
    if not cards:
        return []
    required = [
        (current, "missing current first-step script: " + current),
    ]
    package = "research/historical-complex-ceiling-replay"
    runner = "scripts/research_package.py"
    if any(card["first_step"]["command"] == ceiling for card in cards):
        required += [(name, "missing historical first-step reference: " + name)
                     for name in (runner, package + "/VERIFY.json", package + "/verify.py")]
    # Validate the whole route before changing any suggestion. These are entry
    # references only; the registered replay authenticates its own input closure.
    check_catalog_files = runpy.run_path(str(LEGACY))["check_catalog_files"]
    omitted = check_catalog_files(root, required)
    for card in cards:
        original = card["first_step"]
        card["catalog_first_step"] = original
        if original["command"] == ceiling:
            card["first_step"] = {
                "command": ["python3", "-B", current],
                "expected": "PASS_RESEARCH_BASELINE_BINDINGS_ONLY",
                "inspect": (
                    "Read the current selected certificate, review and reproduction "
                    "command; then run follow_up_steps in order."
                ),
                "scope": (
                    "Current selected source bindings and metadata orientation only; "
                    "not a cold replay or a current packing ceiling."
                ),
            }
            card["follow_up_steps"] = [{
                "command": ["python3", "-B", runner, "--package", package],
                "expected": "PASS_REGISTERED_RESEARCH_PACKAGE",
                "inspect": (
                    "Read the authenticated #1094 ceiling and the historical replay "
                    "README. Derive a source-bound cost law for a changed current "
                    "supplier before applying any historical ceiling or lever budget."
                ),
                "scope": (
                    "Historical #1094 positive control with #1042 comparison; "
                    "not a bound on the current supplier."
                ),
            }]
            card["first_step_resolution"] = (
                "Run current selected orientation first, then the authenticated "
                "historical positive control in follow_up_steps. catalog_first_step "
                "is the exact frozen card entry. The task and acceptance gate are "
                "unchanged; the historical planning budget needs a new applicability "
                "argument for the current construction. Materialize each route's "
                "inputs before execution; reference validation is not source authentication."
            )
            continue
        card["first_step"] = {**original, "command": ["python3", "-B", current]}
        card["first_step_resolution"] = (
            "The current CLI uses the selected-certificate baseline for generic "
            "orientation. catalog_first_step is the exact frozen card entry. "
            "The task, scientific checks and acceptance gate are unchanged."
        )
    return omitted


def main():
    child = subprocess.run([sys.executable, "-B", str(LEGACY), *sys.argv[1:]],
                           capture_output=True, text=True, encoding="utf-8")
    if child.returncode or any(arg in ("-h", "--help") for arg in sys.argv[1:]):
        sys.stdout.write(child.stdout)
        sys.stderr.write(child.stderr)
        return child.returncode
    try:
        result = json.loads(child.stdout)
        omitted = resolve_current_first_steps(result, ROOT)
        if omitted:
            sparse = result.setdefault("sparse_checkout", {"omitted_catalogue_paths": []})
            sparse["omitted_current_first_step_paths"] = omitted
            sparse["scope"] = (
                "These absent regular files match HEAD and skip-worktree index entries. "
                "Materialize the chosen task's inputs before running it; this validates "
                "first-step references, not replay dependencies."
            )
    except (OSError, ValueError, KeyError, TypeError) as exc:
        sys.stderr.write("current first-step resolution failed: " + str(exc) + "\n")
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
