"""Load the declared, byte-pinned native predecessor modules."""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
for record in json.loads((HERE / "SOURCES.json").read_text())["files"]:
    if record["usage"] == "input":
        payload = (ROOT / record["path"]).read_bytes()
        if hashlib.sha256(payload).hexdigest() != record["sha256"]:
            raise ValueError("Source hash mismatch: "+record["path"])
sys.path.insert(0, str(HERE.parent / "clifford-tensor-gram"))
