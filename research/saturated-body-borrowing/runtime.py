"""Authenticate the frozen PR2786 closure without activating a selected supplier."""

import importlib.util
import json
import sys
import tarfile
from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = "research/physical-ordinary-interchange/inputs/pr2808.tar"
MEMBERS = ("source.py", "padding.py", "PREDECESSOR.json", "predecessor.tar.gz")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    require(len(pairs) <= 1024, "bounded JSON object")
    result = {}
    for key, value in pairs:
        require(key not in result, "unique JSON object fields")
        result[key] = value
    return result


def read_json(path):
    require(path.stat().st_size <= 4 * 1024 * 1024, "bounded JSON file")
    return json.loads(path.read_text(), object_pairs_hook=unique_object)


def authenticate():
    sources = read_json(HERE / "SOURCES.json")
    require(len(sources["files"]) == 4, "three inputs and catalogue provenance")
    paths = set()
    for row in sources["files"]:
        require(row["path"] not in paths, "unique source paths")
        paths.add(row["path"])
        require(row["usage"] in ("input", "provenance"), "explicit source usage")
        if row["usage"] == "input":
            require(
                sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"],
                "canonical source bytes: " + row["path"],
            )
    for row in sources["comparison_sources"]:
        require(
            sha256((HERE / row["retained_path"]).read_bytes()).hexdigest()
            == row["sha256"],
            "retained comparison bytes",
        )


@contextmanager
def installed():
    authenticate()
    require(
        not {"padding", "selector", "count_math"}.intersection(sys.modules),
        "cold Count module namespace",
    )
    old_cache = sys.pycache_prefix
    old_path = list(sys.path)
    with TemporaryDirectory(prefix="saturated-borrowing-") as temporary:
        root = Path(temporary)
        sys.pycache_prefix = str(root / "bytecode")
        try:
            with tarfile.open(ROOT / ARCHIVE, "r:") as archive:
                for name in MEMBERS:
                    member = archive.getmember("vendor/pr2786/" + name)
                    require(
                        member.isfile() and member.size <= 200000,
                        "bounded regular export",
                    )
                    opened = archive.extractfile(member)
                    require(opened is not None, "present source member")
                    with opened:
                        (root / name).write_bytes(opened.read(200001))
            spec = importlib.util.spec_from_file_location(
                "padding_source", root / "source.py"
            )
            require(spec is not None and spec.loader is not None, "source loader")
            source = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(source)
            with source.installed():
                sys.path.insert(0, str(root))
                sys.path.insert(0, str(HERE))
                import padding

                yield padding
        finally:
            for name in ("padding", "selector", "count_math"):
                sys.modules.pop(name, None)
            sys.path[:] = old_path
            sys.pycache_prefix = old_cache
