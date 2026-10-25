"""Join authenticated T74 and support-router exports in one tape cohort."""

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
PINS = {
    "t74-export.tar": (
        "7eae80a477788a72899e0a7d1992f20cf82d58db1387e1b209911f32e77c090c",
        "4a29daa6256f6f33c2a7bc9b4f2426cf0797a69751ad31a83682527b8fccb44b",
        "72df81b8cee17ffd990fc18b2d54024f65971556", "research/t74-retuned-physical-layer", 24),
    "router-export.tar": (
        "9f6947463a9ecc43878e908dde9fb823deb76b1ca7c08b7923440cad19ed1ba4",
        "fffb83e30c9fdb87b9b879c22da7190cd687f0b6b63f1a6adc5cf9466d40e21d",
        "51f3254a54aa5f419778c6e4bee89f7442a0d9c1", "research/physical-support-router", 13),
}
_active = None


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(name, path=None):
    require(name in PINS, "known composition export")
    path = HERE / "inputs" / name if path is None else Path(path)
    digest, manifest_digest, head, package, count = PINS[name]
    require(path.is_file() and not path.is_symlink(), "regular composition export")
    require(sha256(path.read_bytes()).hexdigest() == digest, "pinned composition source: " + name)
    with tarfile.open(path, "r:") as archive:
        members = archive.getmembers()
        names = [member.name for member in members]
        require(len(names) == count+1 and len(set(names)) == len(names), "complete unique composition export")
        for member in members:
            part = PurePosixPath(member.name)
            require(member.isfile() and not part.is_absolute() and ".." not in part.parts
                    and "\\" not in member.name and part.as_posix() == member.name
                    and member.size <= 2**27, "bounded regular canonical composition member")
        raw = archive.extractfile(".research-export.json").read()
        require(sha256(raw).hexdigest() == manifest_digest, "composition source manifest bytes")
        manifest = json.loads(raw)
        require((manifest["commit"], manifest["package"], len(manifest["files"]))
                == (head, package, count), "composition source identity")
        require(set(names) == {row["path"] for row in manifest["files"]} | {".research-export.json"},
                "exact composition source member set")
        for row in manifest["files"]:
            data = archive.extractfile(row["path"]).read()
            require(len(data) == row["size"] and sha256(data).hexdigest() == row["sha256"],
                    "composition source member: " + row["path"])
    return path


def load(name, path):
    require(name not in sys.modules, "fresh authenticated module: " + name)
    path = Path(path).resolve()
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    require(Path(module.__file__).resolve() == path, "actual authenticated module path")
    return module


def active():
    require(_active is not None, "authenticated composed T74 cohort")
    return _active


def compare_compact(export_root, compact, native_root):
    manifest = json.loads((export_root / ".research-export.json").read_text())
    prefix = "research/physical-complex-compact/"
    internal = external = 0
    for row in manifest["files"]:
        relative = row["path"]
        if relative.startswith(prefix):
            actual = compact / relative[len(prefix):]
            internal += 1
        else:
            actual = native_root / relative
            external += 1
        expected = export_root / relative
        require(actual.is_file() and not actual.is_symlink()
                and actual.read_bytes() == expected.read_bytes(), "shared Compact cohort bytes: " + relative)
    require((internal, external) == (21, 15), "complete Compact and external-input comparison")
    return internal, external


@contextmanager
def opened():
    global _active
    require(_active is None and not any(name in sys.modules for name in
            ("active_sources", "router_sources", "sparse_sources", "ordinary", "words", "root_layer")),
            "cold composition namespace")
    paths = {name: authenticate(name) for name in PINS}
    old_path = sys.path[:]
    router_sources = sparse_sources = None
    with tempfile.TemporaryDirectory(prefix="t74-support-source-") as directory:
        base = Path(directory)
        roots = {}
        for name, path in paths.items():
            destination = base / name.removesuffix(".tar")
            destination.mkdir()
            with tarfile.open(path, "r:") as archive:
                archive.extractall(destination, filter="data")
            roots[name] = destination
        root_package = roots["t74-export.tar"] / PINS["t74-export.tar"][3]
        router_package = roots["router-export.tar"] / PINS["router-export.tar"][3]
        try:
            sys.path.insert(0, str(root_package))
            root_sources = load("active_sources", root_package / "active_sources.py")
            with root_sources.opened() as root:
                router_sources = load("router_sources", router_package / "router_sources.py")
                nested = router_sources.authenticate()
                sparse_root = base / "sparse-source"
                sparse_root.mkdir()
                with tarfile.open(nested, "r:") as archive:
                    archive.extractall(sparse_root, filter="data")
                sparse_package = sparse_root / router_sources.PACKAGE
                sparse_sources = load("sparse_sources", sparse_package / "sparse_sources.py")
                # exports() authenticates inputs without opening another runtime.
                with sparse_sources.exports() as sparse_roots:
                    compact_engine = importlib.import_module("compact_engine")
                    native_sources = importlib.import_module("native_sources")
                    compact = Path(compact_engine.__file__).resolve().parent
                    compact_counts = compare_compact(sparse_roots["compact-export.tar"], compact,
                                                     native_sources.ROOT)
                    backend = sparse_sources.compare_backend(sparse_roots["ordinary-rate-export.tar"], root.backend)
                    backend_source, reference = native_sources.activate()
                    bridge = SimpleNamespace(compact=compact, roots=sparse_roots, source=backend_source,
                                             reference=reference, ordinary=root.ordinary, encoded=root.encoded,
                                             backend=root.backend, compared_backend=backend, sparse=sparse_package)
                    require(router_sources._active is None and sparse_sources._active is None,
                            "fresh router context registration")
                    router_sources._active = sparse_sources._active = bridge
                    sys.path[:0] = [str(router_package), str(sparse_package)]
                    router = importlib.import_module("router_engine")
                    sparse = importlib.import_module("sparse_engine")
                    root_layer = importlib.import_module("root_layer")
                    require(Path(router.__file__).resolve() == (router_package / "router_engine.py").resolve()
                            and Path(sparse.__file__).resolve() == (sparse_package / "sparse_engine.py").resolve(),
                            "actual authenticated router and sparse code")
                    require(router.Count is root_layer.Count and router.Tape is root_layer.Tape
                            and router.SparseEngine is sparse.SparseEngine
                            and issubclass(sparse.SparseEngine, compact_engine.CompactEngine),
                            "one Count Tape Compact Sparse vocabulary")
                    _active = SimpleNamespace(root=root, roots=roots, root_package=root_package,
                                              root_sources=root_sources, router_package=router_package,
                                              router=router, bridge=bridge, compact_counts=compact_counts)
                    try:
                        yield _active
                    finally:
                        _active = None
                        router_sources._active = sparse_sources._active = None
        finally:
            _active = None
            if router_sources is not None:
                router_sources._active = None
            if sparse_sources is not None:
                sparse_sources._active = None
            sys.path[:] = old_path
            for name, module in (("router_sources", router_sources), ("sparse_sources", sparse_sources)):
                if module is not None and sys.modules.get(name) is module:
                    del sys.modules[name]
