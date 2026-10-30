"""Authenticate the complete ordinary backend before loading its tape vocabulary."""

import hashlib
import importlib
import json
from pathlib import Path, PurePosixPath
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE_SHA = "0fef1707c6460418fd01fd49faf0d8ff7945907fa57284765c852a12d2674d3c"
MANIFEST_SHA = "920cec57d358249261a539adb9265ee00fa2fb820641b83d3757158ff401f503"
BASE = "20ecf2891d80b5acf18d980b2164fb44ea7faa90"
PACKAGE = "research/physical-ordinary-interchange"
_temporary = None
_runtime = None


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(archive=None):
    path = HERE / "inputs/pr2899-export.tar.gz" if archive is None else Path(archive)
    require(path.is_file() and not path.is_symlink(), "regular backend archive")
    require(hashlib.sha256(path.read_bytes()).hexdigest() == ARCHIVE_SHA,
            "pinned backend archive bytes")
    with tarfile.open(path, "r:*") as source:
        members = source.getmembers()
        require(len(members) == 36 and all(m.isfile() for m in members),
                "complete regular backend export")
        names = [m.name for m in members]
        require(len(set(names)) == len(names), "unique backend paths")
        for member in members:
            name = PurePosixPath(member.name)
            require(not name.is_absolute() and ".." not in name.parts and member.size <= 2**26,
                    "contained bounded backend path")
        raw = source.extractfile(".research-export.json").read()
        require(hashlib.sha256(raw).hexdigest() == MANIFEST_SHA, "pinned backend manifest")
        manifest = json.loads(raw)
        require(manifest["commit"] == BASE and manifest["package"] == PACKAGE
                and len(manifest["files"]) == 35, "backend source identity")
        require(set(names) == {r["path"] for r in manifest["files"]} | {".research-export.json"},
                "exact backend member inventory")
        for row in manifest["files"]:
            value = source.extractfile(row["path"]).read()
            require(len(value) == row["size"] and hashlib.sha256(value).hexdigest() == row["sha256"],
                    "backend member: " + row["path"])
    return path


def runtime():
    global _temporary, _runtime
    if _runtime is not None:
        return _runtime
    require(not any(name in sys.modules for name in ("source", "ordinary", "encoded", "words")),
            "cold ordinary namespace")
    archive = authenticate()
    _temporary = tempfile.TemporaryDirectory(prefix="retuned-ordinary-")
    root = Path(_temporary.name)
    with tarfile.open(archive, "r:*") as source:
        source.extractall(root, filter="data")
    sys.path.insert(0, str(root / PACKAGE))
    source = importlib.import_module("source")
    source.activate()
    _runtime = tuple(importlib.import_module(name) for name in ("ordinary", "encoded", "binary"))
    return _runtime


def close():
    for name in ("source", "loader"):
        module = sys.modules.get(name)
        if module is not None:
            for value in tuple(vars(module).values()):
                if isinstance(value, tempfile.TemporaryDirectory):
                    value.cleanup()
    if _temporary is not None:
        _temporary.cleanup()
