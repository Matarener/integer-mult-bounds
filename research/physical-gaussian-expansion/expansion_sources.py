"""Authenticate the complete Gaussian cohort and the final-grid correction."""
from contextlib import contextmanager
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path, PurePosixPath
import shutil
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
CORE_PACKAGE = "research/physical-gaussian-core"
CORE_HEAD = "7ab67b4a84d28cd562b9711aa315ca5b47822b37"
COMPRESSED_DIGEST = "5aaa84523bfa22eb817023d3130e8b8879153e9207e8f836cc6c61435fd051b8"
CORE_DIGEST = "2d97e093634a4119d9990dcc5d175917df3eabda5e8d1c204f640381e92ab4a2"
CORE_RECEIPT = "d387e4d0a1a43b9b24104f76f8992603d4265bbe447601bea476d492e92e5340"
ROUNDING_HEAD = "988ef67986c313445936fc7103908b6163b9d47e"
ROUNDING_DIGEST = "31a553fc4aa4443e60f285633ceb309edc84ede4f64ef7c2646f8806e61da1e8"
_active = None


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    value = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(65536), b""):
            value.update(block)
    return value.hexdigest()


def regular(item):
    path = PurePosixPath(item.name)
    require((item.isfile() or item.isdir()) and not path.is_absolute()
            and ".." not in path.parts and "\\" not in item.name
            and path.as_posix() == item.name and item.size <= 2**27,
            "bounded regular expansion source member")


def authenticate_core(path):
    require(digest(path) == CORE_DIGEST, "complete uncompressed Gaussian core export")
    with tarfile.open(path, "r:") as archive:
        members = archive.getmembers()
        names = [item.name for item in members]
        require(len(names) == len(set(names)) == 43, "complete unique core export inventory")
        for item in members:
            regular(item)
            require(item.isfile(), "regular core export member")
        raw = archive.extractfile(".research-export.json").read()
        require(sha256(raw).hexdigest() == CORE_RECEIPT, "pinned complete core receipt")
        receipt = json.loads(raw)
        require((receipt["commit"], receipt["package"], len(receipt["files"]))
                == (CORE_HEAD, CORE_PACKAGE, 42), "Gaussian core source identity")
        require(set(names) == {row["path"] for row in receipt["files"]} | {".research-export.json"},
                "exact core source member set")
        for row in receipt["files"]:
            data = archive.extractfile(row["path"]).read()
            require(len(data) == row["size"] and sha256(data).hexdigest() == row["sha256"],
                    "core source member: " + row["path"])


def authenticate_rounding(path):
    require(path.is_file() and not path.is_symlink() and digest(path) == ROUNDING_DIGEST,
            "pinned final-grid correction source")
    with tarfile.open(path, "r:") as archive:
        require(archive.pax_headers.get("comment") == ROUNDING_HEAD,
                "exact final-grid correction commit")
        members = archive.getmembers()
        require(len({item.name for item in members}) == len(members), "unique correction source members")
        expected = {"LICENSE", "NOTICE", "notes/fast-gaussian-resampling.tex",
                    "scripts/check_fast_gaussian_rounding.py"}
        require({item.name for item in members if item.isfile()} == expected,
                "complete correction files and notices")
        for item in members:
            regular(item)
            require(item.name in expected | {"notes", "scripts"}, "correction source roots")


def active():
    require(_active is not None, "authenticated expansion physical cohort")
    return _active


@contextmanager
def opened():
    global _active
    require(_active is None and "gaussian_sources" not in sys.modules
            and "cardinal_counts" not in sys.modules, "cold expansion namespace")
    compressed = HERE / "inputs/core-export.tar.gz"
    require(compressed.is_file() and not compressed.is_symlink()
            and digest(compressed) == COMPRESSED_DIGEST, "pinned compressed core source")
    rounding = HERE / "inputs/rounding-source.tar"
    authenticate_rounding(rounding)
    old_path = sys.path[:]
    with tempfile.TemporaryDirectory(prefix="gaussian-expansion-source-") as directory:
        root = Path(directory)
        source_tar = root / "core.tar"
        with gzip.open(compressed, "rb") as source, source_tar.open("xb") as destination:
            shutil.copyfileobj(source, destination, 65536)
        require(source_tar.stat().st_size <= 2**27, "bounded decompressed core source")
        authenticate_core(source_tar)
        core_root, rounding_root = root / "core", root / "rounding"
        core_root.mkdir()
        rounding_root.mkdir()
        for path, target in ((source_tar, core_root), (rounding, rounding_root)):
            with tarfile.open(path, "r:") as archive:
                archive.extractall(target, filter="data")
        package = core_root / CORE_PACKAGE
        spec = importlib.util.spec_from_file_location("gaussian_sources", package / "gaussian_sources.py")
        source = importlib.util.module_from_spec(spec)
        sys.modules["gaussian_sources"] = source
        try:
            spec.loader.exec_module(source)
            sys.path.insert(0, str(package))
            with source.opened() as state:
                _active = state
                state.core_package = package
                state.rounding_root = rounding_root
                yield state
        finally:
            _active = None
            sys.path[:] = old_path
            if sys.modules.get("gaussian_sources") is source:
                del sys.modules["gaussian_sources"]
