"""Authenticate PR3608 and open its physical runtime once."""

from contextlib import contextmanager
from hashlib import sha256
import importlib
import json
from pathlib import Path, PurePosixPath
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ARCHIVE_SHA = "c5767f3744338bb022a5d18863566da19c26a657be8b23b3a2ae775c431c7af5"
MANIFEST_SHA = "7d95b0a4288d2ce5c11aebe9d574569ad9b221d1bd3287c8276d357f98f987c6"
HEAD = "c6020096322012f7cc41236c3ac15a6b6cd3f8b9"
PACKAGE = "research/physical-sparse-xor-batch"
_active = None


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(path=None):
    path = HERE / "inputs/sparse-export.tar" if path is None else Path(path)
    require(path.is_file() and not path.is_symlink(), "regular sparse source export")
    require(sha256(path.read_bytes()).hexdigest() == ARCHIVE_SHA, "pinned sparse source bytes")
    with tarfile.open(path, "r:") as archive:
        members = archive.getmembers()
        names = [member.name for member in members]
        require(len(names) == 21 and len(set(names)) == 21, "complete unique sparse export")
        for member in members:
            name = PurePosixPath(member.name)
            require(member.isfile() and not name.is_absolute() and ".." not in name.parts
                    and "\\" not in member.name and name.as_posix() == member.name
                    and member.size <= 2**27, "bounded canonical source member")
        raw = archive.extractfile(".research-export.json").read()
        require(sha256(raw).hexdigest() == MANIFEST_SHA, "pinned sparse manifest")
        manifest = json.loads(raw)
        require((manifest["commit"], manifest["package"], len(manifest["files"]))
                == (HEAD, PACKAGE, 20), "sparse export identity")
        require(set(names) == {row["path"] for row in manifest["files"]} | {".research-export.json"},
                "exact sparse member set")
        for row in manifest["files"]:
            data = archive.extractfile(row["path"]).read()
            require(len(data) == row["size"] and sha256(data).hexdigest() == row["sha256"],
                    "sparse member bytes: " + row["path"])
    return path


def active():
    require(_active is not None, "authenticated router cohort")
    return _active


@contextmanager
def opened():
    global _active
    require(_active is None and "sparse_sources" not in sys.modules, "cold router namespace")
    path = authenticate()
    previous = sys.path[:]
    with tempfile.TemporaryDirectory(prefix="physical-router-source-") as directory:
        with tarfile.open(path, "r:") as archive:
            archive.extractall(directory, filter="data")
        package = Path(directory) / PACKAGE
        sys.path.insert(0, str(package))
        try:
            sparse = importlib.import_module("sparse_sources")
            require(Path(sparse.__file__).resolve() == (package / "sparse_sources.py").resolve(),
                    "actual retained sparse loader")
            with sparse.opened() as cohort:
                cohort.sparse = package
                _active = cohort
                yield cohort
        finally:
            _active = None
            sys.path[:] = previous
