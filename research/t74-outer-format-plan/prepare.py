# SPDX-License-Identifier: Apache-2.0
"""Materialize the exact closed retained runtime in an external directory."""

from hashlib import sha256
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def prepare(destination):
    require(not destination.exists(), "fresh runtime destination")
    receipt = json.loads((HERE / "RETENTION.json").read_text())
    require(len(receipt["files"]) == 74, "complete retained runtime inventory")
    destination.mkdir()
    for row in receipt["files"]:
        source = ROOT / row["storage"]
        require(source.resolve().is_relative_to(ROOT), "contained retained source path")
        raw = source.read_bytes()
        require(
            len(raw) == row["bytes"] and sha256(raw).hexdigest() == row["sha256"],
            "retained source bytes: " + row["path"],
        )
        target = destination / row["path"]
        require(
            target.resolve().is_relative_to(destination.resolve()),
            "contained retained runtime path",
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    controller = destination / "research/physical-complex-controller"
    for name in ("outer_root_plan.py", "word_order.py", "outer_layer.py"):
        shutil.copyfile(HERE / name, controller / name)
    return controller
