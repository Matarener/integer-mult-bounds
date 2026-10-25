"""Live-input authentication for direct commands as well as registered replay.

SPDX-License-Identifier: Apache-2.0
Git provenance is separately checked by the repository package validator.
"""
from pathlib import Path

from binding import need, read, sha

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def authenticate_sources(root=REPO):
    rows = [r for r in read(HERE / "SOURCES.json")["files"] if r["usage"] == "input"]
    for row in rows:
        path = root / row["path"]
        need(path.resolve().is_relative_to(root.resolve()) and not path.is_symlink(),
             "ordinary in-tree source input")
        need(sha(path) == row["sha256"], "changed live source: " + row["path"])
    return len(rows)
