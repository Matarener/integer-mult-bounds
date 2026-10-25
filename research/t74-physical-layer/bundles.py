# SPDX-License-Identifier: Apache-2.0
"""Open the two pinned regular-file archives in a fresh replay directory."""
from contextlib import contextmanager
from hashlib import sha256
import json
import os
from pathlib import Path, PurePosixPath
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
PINS = {
    "pr3385-controller.tar": "85c1442175741317a6f17f39586ddef54a4be8e8942a0bc517fcafa103ff7498",
    "t74-native-controller.tar": "21dd575587ee31e39f568c3cd3e0eb58b65aea0e78602d9eccefe482548029aa",
}


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def extract(name, destination):
    path = HERE / "inputs" / name
    need(sha256(path.read_bytes()).hexdigest() == PINS[name], "frozen archive: " + name)
    destination.mkdir()
    with tarfile.open(path, "r:") as archive:
        seen = set()
        for member in archive.getmembers():
            item = PurePosixPath(member.name)
            need(member.isfile() and not item.is_absolute() and ".." not in item.parts and
                 "\\" not in member.name and member.name not in seen and item.as_posix() == member.name,
                 "unique canonical regular archive entry")
            seen.add(member.name)
        archive.extractall(destination, filter="data")
    if name == "t74-native-controller.tar":
        manifest = json.loads((destination / "INPUTS.json").read_bytes())
        need(seen == set(manifest["files"]) | {"INPUTS.json"}, "complete input bundle inventory")
        for path, pin in manifest["files"].items():
            raw = (destination / path).read_bytes()
            need(len(raw) == pin["size"] and sha256(raw).hexdigest() == pin["sha256"], "input member: " + path)
        source = destination / "source"
        raw = (source / "MANIFEST.json").read_bytes()
        need(sha256(raw).hexdigest() == manifest["source_manifest_sha256"], "original full source manifest")
        pins = json.loads(raw)
        for path in source.rglob("*"):
            if path.is_file() and path != source / "MANIFEST.json":
                need(sha256(path.read_bytes()).hexdigest() == pins[path.relative_to(source).as_posix()],
                     "retained closed source subset")


def authenticate_prepared(prepared):
    """Bind the production constructor's finite inputs, including direct callers."""
    prepared = Path(prepared)
    path = HERE / "inputs/t74-native-controller.tar"
    need(sha256(path.read_bytes()).hexdigest() == PINS[path.name], "frozen constructor-input authority")
    with tarfile.open(path, "r:") as archive:
        pins = json.loads(archive.extractfile("INPUTS.json").read())["files"]
    names = ["hosted/GLOBAL-TEMPLATE.json.gz", "hosted/ACTUAL-SIGMAS.json.gz",
             "bound/base/work/complex-nine-native/DATA-PHASES.json"]
    names += ["bound/base/providers/" + pid + "/" + name for pid in ("gauge44", "extra")
              for name in ("CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz",
                           "CLIFFORD-RECIPES.json", "RESIDUAL-ADAPTERS.json")]
    for name in names:
        raw = (prepared / name).read_bytes()
        pin = pins["prepared/" + name]
        need(len(raw) == pin["size"] and sha256(raw).hexdigest() == pin["sha256"], "frozen T74 input: " + name)


@contextmanager
def opened():
    old = os.environ.get("T74_CONTROLLER_EXPORT")
    with tempfile.TemporaryDirectory(prefix="t74-physical-replay-") as temporary:
        work = Path(temporary)
        predecessor, current = work / "predecessor", work / "current"
        extract("pr3385-controller.tar", predecessor)
        extract("t74-native-controller.tar", current)
        os.environ["T74_CONTROLLER_EXPORT"] = str(predecessor)
        try:
            yield work, current / "source", current / "prepared"
        finally:
            if old is None:
                os.environ.pop("T74_CONTROLLER_EXPORT", None)
            else:
                os.environ["T74_CONTROLLER_EXPORT"] = old
