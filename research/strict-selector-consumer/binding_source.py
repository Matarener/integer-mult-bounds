"""Authenticate both source closures and join their identical Count runtime.

Nick Petalas. Apache-2.0. Frozen source notices remain in the archives.
"""

import importlib
import io
import json
import stat
import sys
import tarfile
from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SELECTOR = ROOT / "research/encoded-strict-borrowing"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    require(len(pins["files"]) <= 16, "bounded input inventory")
    for row in pins["files"]:
        if row["usage"] != "input":
            continue
        path = ROOT / row["path"]
        require(path.resolve().is_relative_to(ROOT), "contained canonical input")
        require(stat.S_ISREG(path.lstat().st_mode), "regular canonical input")
        require(path.stat().st_size <= 500000, "bounded canonical input")
        require(sha256(path.read_bytes()).hexdigest() == row["sha256"], "input hash")
    meta = json.loads((HERE / "PREDECESSOR.json").read_text())
    raw = (HERE / meta["archive"]).read_bytes()
    require(len(raw) == meta["bytes"] <= 500000, "bounded consumer export")
    require(sha256(raw).hexdigest() == meta["sha256"], "consumer export hash")
    return meta


def unpack_consumer(root, meta):
    rows = {row["path"]: row for row in meta["files"]}
    require(len(rows) == 27, "complete consumer closure")
    with tarfile.open(HERE / meta["archive"], "r:") as archive:
        members = archive.getmembers()
        require(len(members) == 28, "bounded consumer members")
        for member in members:
            require(member.isfile() and member.size <= 200000, "regular member")
            parts = Path(member.name).parts
            require(not member.name.startswith("/") and ".." not in parts, "path")
            stream = archive.extractfile(member)
            require(stream is not None, "present consumer member")
            with stream:
                raw = stream.read(200001)
            if member.name != ".research-export.json":
                row = rows.pop(member.name)
                require(
                    sha256(raw).hexdigest() == row["sha256"], "consumer member hash"
                )
            target = root / member.name
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as output:
                require(output.write(raw) == len(raw), "complete exclusive copy")
    require(not rows, "all consumer members present")


def join_arithmetic(root):
    """Check the entire shared caller archive, then retain two exact modules."""
    with tarfile.open(SELECTOR / "pr3518.tar", "r:") as archive:
        opened = archive.extractfile(
            "research/physical-ordinary-interchange/inputs/pr2808.tar"
        )
        require(opened is not None, "present arithmetic caller export")
        with opened:
            raw = opened.read(400001)
        with tarfile.open(fileobj=io.BytesIO(raw), mode="r:") as caller:
            for name in (
                "source.py",
                "padding.py",
                "PREDECESSOR.json",
                "predecessor.tar.gz",
            ):
                opened = caller.extractfile("vendor/pr2786/" + name)
                require(opened is not None, "present shared runtime")
                with opened:
                    old = opened.read(200001)
                current = (
                    root
                    / "research/selected-outer-borrowing-wrapper/vendor/pr2786"
                    / name
                )
                require(old == current.read_bytes(), "identical complete Count runtime")
        arithmetic = root / "arithmetic"
        arithmetic.mkdir()
        for name in ("selector.py", "count_math.py"):
            opened = archive.extractfile("research/saturated-body-borrowing/" + name)
            require(opened is not None, "present exact arithmetic module")
            with opened:
                raw = opened.read(20001)
            require(len(raw) <= 20000, "bounded arithmetic module")
            with (arithmetic / name).open("xb") as output:
                require(output.write(raw) == len(raw), "complete arithmetic copy")
    return arithmetic


@contextmanager
def installed():
    meta = authenticate()
    names = {
        "runtime",
        "fixtures",
        "strict_outer",
        "selector",
        "count_math",
        "strict_selector",
    }
    require(not names.intersection(sys.modules), "cold composed namespace")
    old_path, old_modules = list(sys.path), set(sys.modules)
    old_cache, old_bytecode = sys.pycache_prefix, sys.dont_write_bytecode
    with TemporaryDirectory(prefix="strict-binding-") as temporary:
        root = Path(temporary)
        sys.pycache_prefix, sys.dont_write_bytecode = str(root / "bytecode"), True
        try:
            unpack_consumer(root, meta)
            arithmetic = join_arithmetic(root)
            parent = root / "research/strict-ordinary-consumer"
            sys.path.insert(0, str(parent))
            runtime = importlib.import_module("runtime")
            with runtime.installed():
                sys.path.append(str(arithmetic))
                sys.path.append(str(SELECTOR))
                sys.path.insert(0, str(HERE))
                yield
        finally:
            sys.path[:] = old_path
            sys.pycache_prefix, sys.dont_write_bytecode = old_cache, old_bytecode
            for name in set(sys.modules) - old_modules:
                file = Path(
                    getattr(sys.modules.get(name), "__file__", "") or "."
                ).resolve()
                if file.is_relative_to(root) or file.is_relative_to(ROOT / "research"):
                    sys.modules.pop(name, None)
