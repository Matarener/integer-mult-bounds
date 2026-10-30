"""Load the exact retained toolkit without changing any predecessor source."""

import hashlib
import json
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent


def authenticate(root):
    """Reject a missing or changed member of the retained source closure."""
    manifest = json.loads((PACKAGE / "RETAINED.json").read_text())
    for record in manifest["files"]:
        path = root / record["path"]
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != record["sha256"]:
            raise ValueError("changed retained source: " + record["path"])
    return manifest


def install(root, mode):
    """Install the one explicit solver substitution, or retain the baseline."""
    if mode not in ("baseline", "candidate"):
        raise ValueError("unknown solver mode")
    authenticate(root)
    sys.path.insert(0, str(root / "alignbuild"))
    import rp

    if mode == "candidate":
        from solver import solve

        rp.solve = solve
    return rp
