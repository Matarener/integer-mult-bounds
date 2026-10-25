"""Open one authenticated Fourier cohort for its normalized-product consumer."""

from contextlib import contextmanager
from hashlib import sha256
import importlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
PACKAGE = "research/physical-synthetic-fourier"
HEAD = "d23db567a4b30075b41b44dfa1d69b4dbed954fa"
DIGEST = "30e460df0428ea1ff72dba6528537e53aec62fcec5dc6077bf736afd5cbbc7e8"
MANIFEST = "c2950df45cf6e4a4e36b039f65c64104c77c4f1c578e895720cd9f0ab1bd3ba3"
_active = None


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(path=None):
    path = HERE / "inputs/fourier-export.tar" if path is None else Path(path)
    require(path.is_file() and not path.is_symlink(), "regular ring-consumer source export")
    require(sha256(path.read_bytes()).hexdigest() == DIGEST, "pinned ring-consumer source bytes")
    with tarfile.open(path, "r:") as archive:
        members = archive.getmembers()
        names = [member.name for member in members]
        require(len(names) == 17 and len(set(names)) == 17, "complete unique ring source export")
        for member in members:
            part = PurePosixPath(member.name)
            require(member.isfile() and not part.is_absolute() and ".." not in part.parts
                    and "\\" not in member.name and part.as_posix() == member.name
                    and member.size <= 2**27, "bounded regular ring source member")
        raw = archive.extractfile(".research-export.json").read()
        require(sha256(raw).hexdigest() == MANIFEST, "pinned ring source receipt")
        manifest = json.loads(raw)
        require((manifest["commit"], manifest["package"], len(manifest["files"]))
                == (HEAD, PACKAGE, 16), "ring source identity")
        require(set(names) == {row["path"] for row in manifest["files"]} | {".research-export.json"},
                "exact ring source member set")
        for row in manifest["files"]:
            data = archive.extractfile(row["path"]).read()
            require(len(data) == row["size"] and sha256(data).hexdigest() == row["sha256"],
                    "ring source member: " + row["path"])
    return path


def active():
    require(_active is not None, "authenticated normalized-product cohort")
    return _active


@contextmanager
def opened():
    global _active
    require(_active is None and "fourier_sources" not in sys.modules, "cold normalized-product namespace")
    path = authenticate()
    old_path = sys.path[:]
    with tempfile.TemporaryDirectory(prefix="ring-source-") as directory:
        with tarfile.open(path, "r:") as archive:
            archive.extractall(directory, filter="data")
        package = Path(directory) / PACKAGE
        spec = importlib.util.spec_from_file_location("fourier_sources", package / "fourier_sources.py")
        source = importlib.util.module_from_spec(spec)
        sys.modules["fourier_sources"] = source
        try:
            spec.loader.exec_module(source)
            sys.path.insert(0, str(package))
            with source.opened() as state:
                _active = state
                state.fourier_package = package
                state.fourier = importlib.import_module("fourier_engine")
                require(Path(state.fourier.__file__).resolve() == (package / "fourier_engine.py").resolve(),
                        "actual authenticated Fourier consumer code")
                yield state
        finally:
            _active = None
            sys.path[:] = old_path
            if sys.modules.get("fourier_sources") is source:
                del sys.modules["fourier_sources"]
