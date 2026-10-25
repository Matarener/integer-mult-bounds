"""Authenticate the complete arbitrary-support export before opening its cohort."""

from contextlib import contextmanager
from hashlib import sha256
import importlib.util
import json
from pathlib import Path, PurePosixPath
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
PACKAGE = "research/t74-support-composition"
HEAD = "757df5a1a4ef3b2594521db45fbea82f79bf2713"
DIGEST = "19da34fb207d781ff29405a3ad35d911333520deadfdb99ae872ba2bb721c433"
MANIFEST = "cf7a2e44a8bfefdb4c210dcbf4d09846cf9be5505647b312d271ae7d28facf0f"
_active = None


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(path=None):
    path = HERE / "inputs/composed-export.tar" if path is None else Path(path)
    require(path.is_file() and not path.is_symlink(), "regular Fourier source export")
    require(sha256(path.read_bytes()).hexdigest() == DIGEST, "pinned Fourier source bytes")
    with tarfile.open(path, "r:") as archive:
        members = archive.getmembers()
        names = [member.name for member in members]
        require(len(names) == 17 and len(set(names)) == 17, "complete unique Fourier export")
        for member in members:
            part = PurePosixPath(member.name)
            require(member.isfile() and not part.is_absolute() and ".." not in part.parts
                    and "\\" not in member.name and part.as_posix() == member.name
                    and member.size <= 2**27, "bounded regular Fourier source member")
        raw = archive.extractfile(".research-export.json").read()
        require(sha256(raw).hexdigest() == MANIFEST, "pinned Fourier source receipt")
        manifest = json.loads(raw)
        require((manifest["commit"], manifest["package"], len(manifest["files"]))
                == (HEAD, PACKAGE, 16), "Fourier source identity")
        require(set(names) == {row["path"] for row in manifest["files"]} | {".research-export.json"},
                "exact Fourier source member set")
        for row in manifest["files"]:
            data = archive.extractfile(row["path"]).read()
            require(len(data) == row["size"] and sha256(data).hexdigest() == row["sha256"],
                    "Fourier source member: " + row["path"])
    return path


def active():
    require(_active is not None, "authenticated Fourier cohort")
    return _active


@contextmanager
def opened():
    global _active
    require(_active is None and "composed_sources" not in sys.modules, "cold Fourier namespace")
    path = authenticate()
    old_path = sys.path[:]
    with tempfile.TemporaryDirectory(prefix="fourier-source-") as directory:
        with tarfile.open(path, "r:") as archive:
            archive.extractall(directory, filter="data")
        package = Path(directory) / PACKAGE
        spec = importlib.util.spec_from_file_location("composed_sources", package / "composed_sources.py")
        source = importlib.util.module_from_spec(spec)
        sys.modules["composed_sources"] = source
        try:
            spec.loader.exec_module(source)
            sys.path.insert(0, str(package))
            with source.opened() as state:
                _active = state
                state.fourier_source = package
                yield state
        finally:
            _active = None
            sys.path[:] = old_path
            if sys.modules.get("composed_sources") is source:
                del sys.modules["composed_sources"]
