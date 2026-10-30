"""Authenticate the retained Compact runtime and its ordinary-rate premise."""

from contextlib import contextmanager
from hashlib import sha256
import importlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import sys
import tarfile
import tempfile
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REFERENCES = {
    "research/gmx-t74-borrow43-handoff/vendor/pr1673/capped-phase-fusion/SUPPORT-ROUTER.md":
        "6ddb322e11883c1177ba6cd1a77d23a1dac827d7290b32eaf642457b1d762a54",
    "research/gmx-t74-borrow43-handoff/vendor/pr1673/capped-phase-fusion/SUPPLIER-SUPPORT-AUDIT.md":
        "bd5b06eca043c5c871227264f6a954473c55cd16ec85bb420ff538fb8ec1d8d6",
}
PINS = {
    "compact-export.tar": (
        "e2981c9dd828db201d2ce9ff68900e7d75911d70e04e2ebd9eae1efafa0b4025",
        "cf0e4d5aaca3b17dfbc40bd966cd85d693e76f6216ee582df58070c85e050e8a",
        "20ecf2891d80b5acf18d980b2164fb44ea7faa90", "research/physical-complex-compact", 36),
    "ordinary-rate-export.tar": (
        "b1776cc42dda97aab058b0e5ffd797637fd262b849a89912e550d9116326bbc6",
        "6704cd4055cb54f2678a4b5f02329b2e14462e1d35fcd5be848de9a7abec8cc6",
        "abb93be8b9ceca07a2b17f3a97db7bb6b074271d", "research/retuned-ordinary-coupling", 17),
}
_active = None


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(name, path=None):
    require(name in PINS, "known source export")
    path = HERE / "inputs" / name if path is None else Path(path)
    digest, manifest_digest, commit, package, count = PINS[name]
    require(path.is_file() and not path.is_symlink(), "regular source export")
    require(sha256(path.read_bytes()).hexdigest() == digest, "pinned source export: " + name)
    with tarfile.open(path, "r:") as archive:
        members = archive.getmembers()
        names = [member.name for member in members]
        require(len(names) == count+1 and len(set(names)) == len(names), "complete unique source inventory")
        for member in members:
            part = PurePosixPath(member.name)
            require(member.isfile() and not part.is_absolute() and ".." not in part.parts
                    and "\\" not in member.name and part.as_posix() == member.name
                    and member.size <= 2**27, "bounded regular canonical source member")
        raw = archive.extractfile(".research-export.json").read()
        require(sha256(raw).hexdigest() == manifest_digest, "source manifest bytes")
        manifest = json.loads(raw)
        require((manifest["commit"], manifest["package"], len(manifest["files"]))
                == (commit, package, count), "source export identity")
        require(set(names) == {row["path"] for row in manifest["files"]} | {".research-export.json"},
                "exact source members")
        for row in manifest["files"]:
            data = archive.extractfile(row["path"]).read()
            require(len(data) == row["size"] and sha256(data).hexdigest() == row["sha256"],
                    "source member: " + row["path"])
    return path


@contextmanager
def exports():
    for name, digest in REFERENCES.items():
        path = ROOT / name
        require(path.is_file() and not path.is_symlink() and sha256(path.read_bytes()).hexdigest() == digest,
                "pinned sparse-routing premise: " + name)
    paths = {name: authenticate(name) for name in PINS}
    with tempfile.TemporaryDirectory(prefix="sparse-xor-source-") as directory:
        roots = {}
        for name, path in paths.items():
            destination = Path(directory) / name.removesuffix(".tar")
            destination.mkdir()
            with tarfile.open(path, "r:") as archive:
                archive.extractall(destination, filter="data")
            roots[name] = destination
        yield roots


def compare_backend(rate, backend):
    source = rate / "research/retuned-ordinary-coupling/inputs/pr2899-export.tar.gz"
    prefix = "research/physical-ordinary-interchange/"
    checked = []
    with tarfile.open(source, "r:*") as archive:
        for member in archive.getmembers():
            if not member.isfile() or not member.name.startswith(prefix):
                continue
            relative = member.name[len(prefix):]
            actual = backend / relative
            require(actual.is_file() and not actual.is_symlink()
                    and actual.read_bytes() == archive.extractfile(member).read(),
                    "ordinary cohort bytes: " + relative)
            checked.append(relative)
    require(len(checked) == 23, "complete ordinary cohort comparison")
    return checked


def active():
    require(_active is not None, "authenticated sparse-batch cohort")
    return _active


def load_check(name, alias):
    require(alias.startswith("sparse_check_") and alias not in sys.modules, "fresh source-check namespace")
    path = active().compact / name
    require(path.is_file() and path.resolve().parent == active().compact.resolve(), "retained source checker")
    specification = importlib.util.spec_from_file_location(alias, path)
    module = importlib.util.module_from_spec(specification)
    sys.modules[alias] = module
    specification.loader.exec_module(module)
    return module


@contextmanager
def opened():
    global _active
    require(_active is None and not any(name in sys.modules for name in
            ("native_sources", "source", "loader", "words", "records", "ordinary", "compact_control")),
            "cold sparse-batch namespace")
    previous_path = sys.path[:]
    with exports() as roots:
        compact = roots["compact-export.tar"] / PINS["compact-export.tar"][3]
        sys.path.insert(0, str(compact))
        try:
            native = importlib.import_module("native_sources")
            require(Path(native.__file__).resolve() == (compact / "native_sources.py").resolve(),
                    "actual authenticated Compact loader")
            source, reference = native.activate()
            ordinary = importlib.import_module("ordinary")
            encoded = importlib.import_module("encoded")
            backend = Path(ordinary.__file__).resolve().parent
            checked = compare_backend(roots["ordinary-rate-export.tar"], backend)
            _active = SimpleNamespace(compact=compact, roots=roots, source=source, reference=reference,
                                      ordinary=ordinary, encoded=encoded, backend=backend,
                                      compared_backend=checked)
            yield _active
        finally:
            _active = None
            for name in ("source", "native_sources"):
                temporary = getattr(sys.modules.get(name), "_temporary", None)
                if temporary is not None:
                    temporary.cleanup()
            sys.path[:] = previous_path
