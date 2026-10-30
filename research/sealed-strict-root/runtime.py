"""Authenticate the physical caller and retained strict-padding premises."""

import importlib
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


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    require(len(sources["files"]) <= 40, "bounded source inventory")
    for row in sources["files"]:
        if row["usage"] != "input":
            continue
        path = ROOT / row["path"]
        require(path.resolve().is_relative_to(ROOT), "contained source")
        require(stat.S_ISREG(path.lstat().st_mode), "regular source")
        require(path.stat().st_size <= 32000000, "bounded canonical source")
        require(sha256(path.read_bytes()).hexdigest() == row["sha256"], "source hash")
    retained = json.loads((HERE / "PREDECESSOR.json").read_text())
    require(len(retained["files"]) == 3, "retained premise inventory")
    for row in retained["files"]:
        path = HERE / row["retained_path"]
        require(path.resolve().is_relative_to(HERE), "contained retained source")
        require(stat.S_ISREG(path.lstat().st_mode), "regular retained source")
        require(path.stat().st_size <= 500000, "bounded retained source")
        raw = path.read_bytes()
        require(len(raw) == row["bytes"], "retained premise size")
        require(sha256(raw).hexdigest() == row["sha256"], "retained premise hash")


def unpack(root):
    meta = json.loads((HERE / "PR3542-SOURCES.json").read_text())
    rows = {row["path"]: row for row in meta["files"]}
    with tarfile.open(HERE / "pr3542.tar", "r:") as archive:
        members = archive.getmembers()
        require(len(members) == 28, "bounded consumer archive")
        for member in members:
            require(member.isfile() and member.size <= 200000, "regular member")
            require(
                not member.name.startswith("/") and ".." not in Path(member.name).parts,
                "member path",
            )
            stream = archive.extractfile(member)
            require(stream is not None, "present member")
            with stream:
                raw = stream.read(200001)
            if member.name != ".research-export.json":
                require(
                    sha256(raw).hexdigest() == rows.pop(member.name)["sha256"],
                    "member hash",
                )
            target = root / member.name
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as output:
                require(output.write(raw) == len(raw), "exclusive byte copy")
    require(not rows, "complete consumer closure")


def arithmetic(root):
    physical = ROOT / "research/physical-ordinary-interchange/inputs/pr2808.tar"
    with tarfile.open(physical, "r:") as old:
        for name in (
            "source.py",
            "padding.py",
            "PREDECESSOR.json",
            "predecessor.tar.gz",
        ):
            stream = old.extractfile("vendor/pr2786/" + name)
            require(stream is not None, "present shared runtime")
            with stream:
                raw = stream.read(200001)
            require(
                raw
                == (
                    root
                    / "research/selected-outer-borrowing-wrapper/vendor/pr2786"
                    / name
                ).read_bytes(),
                "identical shared Count runtime",
            )
    target = root / "arithmetic"
    target.mkdir()
    with tarfile.open(
        ROOT / "research/encoded-strict-borrowing/pr3518.tar", "r:"
    ) as archive:
        for name in ("selector.py", "count_math.py"):
            stream = archive.extractfile("research/saturated-body-borrowing/" + name)
            require(stream is not None, "present arithmetic")
            with stream:
                raw = stream.read(20001)
            require(len(raw) <= 20000, "bounded arithmetic")
            with (target / name).open("xb") as output:
                require(output.write(raw) == len(raw), "exclusive arithmetic copy")
    return target


@contextmanager
def installed():
    authenticate()
    names = {
        "source",
        "loader",
        "ordinary",
        "strict_outer",
        "strict_selector",
        "selector",
    }
    require(not names.intersection(sys.modules), "cold physical namespace")
    old_path, old_modules = list(sys.path), set(sys.modules)
    with TemporaryDirectory(prefix="sealed-strict-") as temporary:
        root = Path(temporary)
        try:
            unpack(root)
            shared = arithmetic(root)
            sys.path.insert(0, str(ROOT / "research/physical-ordinary-interchange"))
            importlib.import_module("source").activate()
            sys.path.extend(
                [
                    str(shared),
                    str(ROOT / "research/encoded-strict-borrowing"),
                    str(root / "research/strict-padding-borrowing"),
                    str(root / "research/strict-ordinary-consumer"),
                ]
            )
            sys.path.insert(0, str(HERE))
            yield
        finally:
            sys.path[:] = old_path
            # Retained loaders own nested temporary directories. Close them
            # before unloading their modules, including the failing-run path.
            for name in set(sys.modules) - old_modules:
                module = sys.modules.get(name)
                for value in tuple(vars(module).values()):
                    if isinstance(value, TemporaryDirectory):
                        value.cleanup()
            for name in set(sys.modules) - old_modules:
                sys.modules.pop(name, None)
