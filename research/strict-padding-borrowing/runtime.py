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
    require(len(sources["files"]) == 5, "four input pins and catalogue provenance")
    paths = set()
    inputs = 0
    for row in sources["files"]:
        require(row["path"] not in paths, "unique source paths")
        paths.add(row["path"])
        if row["usage"] == "provenance":
            require(
                row["path"] == "docs/research/agent-task-catalog.json",
                "catalogue provenance",
            )
            continue
        require(row["usage"] == "input", "explicit source usage")
        inputs += 1
        require(
            sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"],
            "canonical source bytes: " + row["path"],
        )
    require(inputs == 4, "four consumed canonical sources")
    comparisons = sources["comparison_sources"]
    require(len(comparisons) == 1, "one retained premise comparison")
    comparison = comparisons[0]
    require(
        sha256((HERE / comparison["retained_path"]).read_bytes()).hexdigest()
        == comparison["sha256"],
        "retained PR3486 comparison bytes",
    )
    require(
        sha256((ROOT / ARCHIVE).read_bytes()).hexdigest()
        == "2ab59c6d0ad00c001ecbe44090b66871ec3d2c1fdc51daa503109e56f3285cab",
        "unchanged PR2808 archive",
    )


@contextmanager
def installed():
    authenticate()
    require("padding" not in sys.modules, "cold padding module namespace")
    old_cache = sys.pycache_prefix
    old_path = list(sys.path)
    with TemporaryDirectory(prefix="strict-padding-") as temporary:
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
                import padding

                yield padding
        finally:
            sys.modules.pop("padding", None)
            sys.path[:] = old_path
            sys.pycache_prefix = old_cache
