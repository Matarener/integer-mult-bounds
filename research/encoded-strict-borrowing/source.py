# SPDX-License-Identifier: Apache-2.0
"""Load byte-authenticated, self-contained pending source without Git or network."""

import importlib.util
import json
import sys
import tarfile
from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    meta = json.loads((HERE / "PREDECESSOR.json").read_text())
    for row in (meta["archive"], meta["strict_padding"]):
        raw = (HERE / row["file"]).read_bytes()
        require(len(raw) == row["bytes"], "retained source size")
        require(sha256(raw).hexdigest() == row["sha256"], "retained source hash")
    return meta


@contextmanager
def installed():
    meta = authenticate()
    require(
        not {"selector", "strict_selector"}.intersection(sys.modules),
        "cold predecessor namespace",
    )
    old_path = list(sys.path)
    with TemporaryDirectory(prefix="strict-borrowing-") as temporary:
        root = Path(temporary)
        with tarfile.open(HERE / "pr3518.tar", "r:") as archive:
            members = archive.getmembers()
            require(len(members) == 21, "bounded retained export")
            rows = {row["path"]: row for row in meta["archive"]["files"]}
            require(len(rows) == 20, "unique retained source paths")
            for member in members:
                require(member.isfile(), "regular retained source")
                parts = Path(member.name).parts
                require(
                    not member.name.startswith("/") and ".." not in parts,
                    "contained retained source",
                )
                require(member.size <= 400000, "bounded retained source member")
                stream = archive.extractfile(member)
                require(stream is not None, "present retained source")
                with stream:
                    raw = stream.read(400001)
                if member.name != ".research-export.json":
                    row = rows.pop(member.name)
                    require(
                        sha256(raw).hexdigest() == row["sha256"],
                        "retained per-file hash",
                    )
                target = root / member.name
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open("xb") as output:
                    output.write(raw)
            require(not rows, "complete retained source export")
        path = root / "research/saturated-body-borrowing/runtime.py"
        spec = importlib.util.spec_from_file_location("retained_borrowing", path)
        require(spec is not None and spec.loader is not None, "source loader")
        runtime = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runtime)
        try:
            with runtime.installed():
                sys.path.insert(0, str(HERE))
                yield
        finally:
            for name in ("strict_selector",):
                sys.modules.pop(name, None)
            sys.path[:] = old_path
