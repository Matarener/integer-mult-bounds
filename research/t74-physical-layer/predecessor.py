# SPDX-License-Identifier: Apache-2.0
"""Authenticate the explicit PR3385 export before importing its physical code."""
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
import tempfile

MANIFEST_SHA = "ecdd89f1b528b58ab16bc9662b81c2e04017173fc467150184ff80e6803c5793"
COMMIT = "7e5a187214126d31afc241a8f89f4a652352b58c"
_active = None


def activate():
    global _active
    root = Path(os.environ["T74_CONTROLLER_EXPORT"]).resolve()
    if _active is not None:
        if root != _active:
            raise ValueError("one authenticated controller namespace")
        return root
    raw = (root / ".research-export.json").read_bytes()
    if sha256(raw).hexdigest() != MANIFEST_SHA:
        raise ValueError("pinned predecessor export manifest")
    manifest = json.loads(raw)
    if manifest["commit"] != COMMIT or len(manifest["files"]) != 74:
        raise ValueError("complete PR3385 export")
    for row in manifest["files"]:
        path = root / row["path"]
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError("regular contained predecessor input")
        value = path.read_bytes()
        if len(value) != row["size"] or sha256(value).hexdigest() != row["sha256"]:
            raise ValueError("predecessor input: " + row["path"])
    sys.path.insert(0, str(root / manifest["package"]))
    _active = root
    return root


def close_test_imports():
    """Close retained extraction directories at the end of a standalone check."""
    for name in ("source", "native_sources", "phase_sources", "leaf_sources"):
        module = sys.modules.get(name)
        if module is not None:
            for value in tuple(vars(module).values()):
                if isinstance(value, tempfile.TemporaryDirectory):
                    value.cleanup()
