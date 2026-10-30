# SPDX-License-Identifier: Apache-2.0
"""Authenticate the live inputs, then run the actual packet interpreter."""

from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError("load authenticated regular Python input")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def authenticate():
    sources = json.loads((HERE / "SOURCES.json").read_bytes())
    for entry in sources["files"]:
        if entry["usage"] != "input":
            continue
        path = ROOT / entry["path"]
        if not path.is_file() or path.is_symlink():
            raise ValueError("missing regular input: " + entry["path"])
        if sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError("input hash: " + entry["path"])


def main():
    authenticate()
    physical = load("phase_physical", ROOT / "research/synthetic-layout-independent/physical.py")
    packing = load("phase_packing", ROOT / "research/selected-conservative-outer/packing.py")
    packets = load("phase_packets", HERE / "packets.py")
    checks = load("phase_checks", HERE / "checks.py")
    if "--smoke" in sys.argv:
        print("PASS_PACKET_SMOKE " + json.dumps(checks.smoke(packets, physical, packing)))
        return
    result = checks.run(packets, physical, packing)
    if "--emit" in sys.argv:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    expected = json.loads((HERE / "RESULT.json").read_bytes())
    if result != expected:
        raise ValueError("complete deterministic receipt differs")
    print("PASS_SYNTHETIC_MONOMIAL_PACKETS " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
