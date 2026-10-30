"""Opt-in replay planner with invocation-local filesystem ancestor reuse.

Produced by Nick Petalas. Apache-2.0.
"""
import hashlib
import json
from pathlib import Path
import stat
import types

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def load_runner(root=ROOT):
    """Execute exactly the authenticated source, without consulting bytecode."""
    source = root / "scripts/research_package.py"
    pins = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    rows = [row for row in pins["files"] if row["path"] == "scripts/research_package.py"]
    if len(rows) != 1 or rows[0]["usage"] != "input":
        raise ValueError("exactly one live runner pin is required")
    raw = source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != rows[0]["sha256"]:
        raise ValueError("runner source SHA256 mismatch")
    module = types.ModuleType("ancestor_cache_runner")
    module.__file__ = str(source)
    exec(compile(raw, str(source), "exec"), module.__dict__)
    return module


class PathChecks:
    """Reuse successful component checks only while one plan owns this instance."""

    def __init__(self, root, canonical, require):
        self.root = root
        self.canonical = canonical
        self.require = require
        self.checked = {}
        self.lookups = 0
        self.hits = 0

    def __call__(self, root, name):
        self.require(root == self.root, "path cache cannot cross repository roots")
        parts = self.canonical(name).parts
        prefix = ""
        for part in parts:
            prefix = part if not prefix else prefix + "/" + part
            if prefix in self.checked:
                self.hits += 1
                if not self.checked[prefix]:
                    break
                continue
            self.lookups += 1
            try:
                info = (root / prefix).lstat()
            except (FileNotFoundError, NotADirectoryError):
                self.checked[prefix] = False
                break
            self.require(not stat.S_ISLNK(info.st_mode),
                         "symlink in repository-relative path: " + name)
            self.require(getattr(info, "st_reparse_tag", 0)
                         != getattr(stat, "IO_REPARSE_TAG_MOUNT_POINT", None),
                         "junction in repository-relative path: " + name)
            self.checked[prefix] = stat.S_ISDIR(info.st_mode)
            if not self.checked[prefix]:
                break
        return root / name


def install(runner):
    """Each plan gets fresh state; other runner entry points retain their guards."""
    original_plan = runner.plan_details
    original_guard = runner.symlink_free_relative_path

    def plan_details(root, changed):
        checks = PathChecks(root, runner.canonical_relative_path, runner.require)
        runner.symlink_free_relative_path = checks
        try:
            return original_plan(root, changed)
        finally:
            runner.symlink_free_relative_path = original_guard

    runner.plan_details = plan_details
    return runner


def main():
    # This private module is used by one synchronous CLI invocation. Delegating
    # its original main preserves all argument, output and failure contracts.
    runner = install(load_runner())
    runner.main()


if __name__ == "__main__":
    main()
