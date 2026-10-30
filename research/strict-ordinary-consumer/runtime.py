"""Authenticate canonical runtime and proof inputs before any import.

Nick Petalas. Apache-2.0. The retained loaders preserve original notices.
"""

import importlib
import json
import stat
import sys
from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    source_manifest = HERE / "SOURCES.json"
    require(source_manifest.stat().st_size <= 1024 * 1024, "bounded source manifest")
    manifest = json.loads(source_manifest.read_text())
    require(len(manifest["files"]) <= 64, "bounded source inventory")
    rows = [row for row in manifest["files"] if row["usage"] == "input"]
    require(len(rows) == 13, "complete thirteen-input source closure")
    require(len({row["path"] for row in rows}) == 13, "unique input paths")
    for row in rows:
        path = ROOT / row["path"]
        require(path.resolve().is_relative_to(ROOT), "contained input")
        info = path.lstat()
        require(stat.S_ISREG(info.st_mode), "regular input, never a link")
        require(info.st_size <= 200_000, "bounded source input")
        require(
            sha256(path.read_bytes()).hexdigest() == row["sha256"],
            "source bytes: " + row["path"],
        )


@contextmanager
def installed():
    authenticate()
    names = {"outer", "padding", "predecessor", "checks", "tape_padding"}
    require(not names.intersection(sys.modules), "cold runtime namespace")
    old_path, old_modules = list(sys.path), set(sys.modules)
    old_cache, old_bytecode = sys.pycache_prefix, sys.dont_write_bytecode
    with TemporaryDirectory(prefix="strict-consumer-bytecode-") as temporary:
        sys.pycache_prefix = temporary
        sys.dont_write_bytecode = True
        try:
            parent = ROOT / "research/selected-outer-borrowing-wrapper"
            sys.path.insert(0, str(parent))
            predecessor = importlib.import_module("predecessor")
            with predecessor.installed():
                sys.path.insert(0, str(parent))
                sys.path.insert(0, str(ROOT / "research/strict-padding-borrowing"))
                importlib.import_module("tape_padding")
                sys.path.insert(0, str(HERE))
                yield
        finally:
            sys.path[:] = old_path
            sys.pycache_prefix, sys.dont_write_bytecode = old_cache, old_bytecode
            for name in set(sys.modules) - old_modules:
                module = sys.modules.get(name)
                path = Path(getattr(module, "__file__", "") or ".").resolve()
                if path.is_relative_to(ROOT / "research"):
                    sys.modules.pop(name, None)
