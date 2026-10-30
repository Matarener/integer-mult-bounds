"""Authenticate the two source exports within one physical tape cohort."""

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
    "research/gmx-t74-borrow43-handoff/vendor/pr1673/capped-phase-fusion/TENSOR-COMPILER.md":
        "4d3b8466598a864a234b978e25976648d4e761840aad9153dd18d73d3dfe4d15",
}
PINS = {
    "t74-export.tar": (
        "d575e3480495fd1fa278f5cf42b8fa136cfecb5a0acff4815082fa4b0ccaf0f0",
        "46d232d7e2e1b9c9b7b692d1f4d28d501fe4a430a637c58c09bd9527013e0f1c",
        "20ecf2891d80b5acf18d980b2164fb44ea7faa90", "research/t74-physical-layer", 30),
    "ordinary-rate-export.tar": (
        "b1776cc42dda97aab058b0e5ffd797637fd262b849a89912e550d9116326bbc6",
        "6704cd4055cb54f2678a4b5f02329b2e14462e1d35fcd5be848de9a7abec8cc6",
        "abb93be8b9ceca07a2b17f3a97db7bb6b074271d", "research/retuned-ordinary-coupling", 17),
}
_active = None


def require(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate(name, path=None):
    require(name in PINS, "known source export")
    path = HERE / "inputs" / name if path is None else Path(path)
    expected, manifest_sha, commit, package, count = PINS[name]
    require(path.is_file() and not path.is_symlink(), "regular source export")
    require(sha256(path.read_bytes()).hexdigest() == expected, "pinned source export: " + name)
    with tarfile.open(path, "r:") as archive:
        members = archive.getmembers()
        names = [m.name for m in members]
        require(len(members) == count+1 and len(set(names)) == len(names), "complete unique source inventory")
        for member in members:
            part = PurePosixPath(member.name)
            require(member.isfile() and not part.is_absolute() and ".." not in part.parts
                    and "\\" not in member.name and part.as_posix() == member.name
                    and member.size <= 2**27, "bounded canonical regular source member")
        raw = archive.extractfile(".research-export.json").read()
        require(sha256(raw).hexdigest() == manifest_sha, "source manifest bytes")
        manifest = json.loads(raw)
        require((manifest["commit"], manifest["package"], len(manifest["files"]))
                == (commit, package, count), "source identity")
        require(set(names) == {row["path"] for row in manifest["files"]} | {".research-export.json"},
                "exact source members")
        for row in manifest["files"]:
            value = archive.extractfile(row["path"]).read()
            require(len(value) == row["size"] and sha256(value).hexdigest() == row["sha256"],
                    "source member: " + row["path"])
    return path


def authenticate_references():
    for name, digest in REFERENCES.items():
        path = ROOT / name
        require(path.is_file() and not path.is_symlink() and sha256(path.read_bytes()).hexdigest() == digest,
                "pinned conditional reference: " + name)


@contextmanager
def exports():
    authenticate_references()
    paths = {name: authenticate(name) for name in PINS}
    with tempfile.TemporaryDirectory(prefix="active-width-t74-") as directory:
        roots = {}
        for name, path in paths.items():
            destination = Path(directory) / name.removesuffix(".tar")
            destination.mkdir()
            with tarfile.open(path, "r:") as archive:
                archive.extractall(destination, filter="data")
            roots[name] = destination
        yield roots


def compare_backend(rate_root, backend):
    path = rate_root / "research/retuned-ordinary-coupling/inputs/pr2899-export.tar.gz"
    prefix = "research/physical-ordinary-interchange/"
    checked = []
    with tarfile.open(path, "r:*") as archive:
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
    require(_active is not None, "authenticated active T74 source context")
    return _active


def load_check(path, name):
    """Load an authenticated checker under a unique, non-runtime module name."""
    state = active()
    path = Path(path).resolve()
    require(path.is_file() and (path.is_relative_to(state.t74.resolve()) or path.is_relative_to(state.controller)),
            "checker inside authenticated source")
    require(name.startswith("active_check_") and name not in sys.modules, "fresh checker namespace")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_t74_binding(t74):
    """Adapt Hiroki Kumazaki's PR3576 namespace boundary (Apache-2.0)."""
    name = "active_t74_binding"
    require(name not in sys.modules, "fresh T74 binding namespace")
    path = (Path(t74) / "binding.py").resolve()
    previous_path = sys.path[:]
    previous_binding = sys.modules.get("binding")
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        require(Path(module.__file__).resolve() == path
                and sys.modules.get("binding") is previous_binding,
                "explicit T74 binding preserves the backend namespace")
        return module
    except BaseException:
        sys.modules.pop(name, None)
        raise
    finally:
        sys.path[:] = previous_path


@contextmanager
def opened():
    global _active
    require(_active is None and not any(name in sys.modules for name in
            ("predecessor", "cohort", "source", "ordinary", "encoded", "words")), "cold T74 cohort")
    with exports() as roots:
        t74 = roots["t74-export.tar"] / PINS["t74-export.tar"][3]
        rate = roots["ordinary-rate-export.tar"]
        sys.path.insert(0, str(t74))
        bundles = importlib.import_module("bundles")
        with bundles.opened() as (work, source, prepared):
            t74_binding = None
            try:
                predecessor = importlib.import_module("predecessor")
                predecessor.activate()
                importlib.import_module("t74_root")
                ordinary = importlib.import_module("ordinary")
                encoded = importlib.import_module("encoded")
                production = importlib.import_module("production_native")
                backend = Path(ordinary.__file__).resolve().parent
                controller = Path(sys.modules["machine"].__file__).resolve().parent
                checked = compare_backend(rate, backend)
                # The retained production factory imports these names lazily.
                # Resolve them in the ordinary cohort before loading the T74
                # source, whose module body temporarily changes sys.path.
                for name in ("catalogue", "node", "macro_binding", "macro_code"):
                    importlib.import_module(name)
                t74_binding = load_t74_binding(t74)
                _active = SimpleNamespace(t74=t74, rate=rate, roots=roots, work=work,
                                          source=source, prepared=prepared, backend=backend,
                                          controller=controller,
                                          ordinary=ordinary, encoded=encoded, production=production,
                                          compared_backend=checked, t74_binding=t74_binding)
                yield _active
            finally:
                _active = None
                if t74_binding is not None and sys.modules.get("active_t74_binding") is t74_binding:
                    del sys.modules["active_t74_binding"]
                if "predecessor" in sys.modules:
                    sys.modules["predecessor"].close_test_imports()
