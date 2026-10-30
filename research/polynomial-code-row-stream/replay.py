"""Complete unchanged affine/vector certificate with an opt-in row engine."""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE))

from stream import PermutationStream, require  # noqa: E402


def authenticate():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    inputs = [row for row in manifest["files"] if row["usage"] == "input"]
    require(0 < len(inputs) <= 64, "Bounded nonempty source closure required")
    for row in inputs:
        path = ROOT / row["path"]
        require(path.resolve().is_relative_to(ROOT) and path.is_file()
                and not path.is_symlink(), "Regular in-root input required")
        with path.open("rb") as handle:
            data = handle.read(2 * 1024 * 1024 + 1)
        require(len(data) <= 2 * 1024 * 1024, "Input capacity exceeded")
        require(hashlib.sha256(data).hexdigest() == row["sha256"],
                "Input hash mismatch: " + row["path"])
    return len(inputs)


def cached_engine():
    path = ROOT / "research/cube-xor-replay/cached_xor.py"
    spec = importlib.util.spec_from_file_location("retained_cached_xor", path)
    require(spec is not None and spec.loader is not None, "Missing cached comparator")
    module = importlib.util.module_from_spec(spec)
    # Execute the authenticated source, without consulting a bytecode cache.
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module.CachedXorPermuter()


def complete(engine):
    require(engine in ("original", "cached", "incremental"), "Unknown row engine")
    authenticate()
    # Registered replay already has a private cache namespace. Direct replay
    # uses an absent namespace with bytecode writes disabled.
    if sys.pycache_prefix is None:
        absent = PACKAGE / ".no-bytecode-cache"
        require(not absent.exists(), "Direct bytecode namespace must be absent")
        sys.pycache_prefix = str(absent)
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(ROOT / "scripts"))
    import audit_affine_vectors
    from experiments import affine_vector_screens
    from prepare_layers import serializable
    previous = affine_vector_screens.xor_permute
    replacement = (PermutationStream() if engine == "incremental" else
                   cached_engine() if engine == "cached" else previous)
    try:
        affine_vector_screens.xor_permute = replacement
        result = serializable(audit_affine_vectors.certificate())
    finally:
        affine_vector_screens.xor_permute = previous
    expected = json.loads((ROOT / "certificates/affine-vector-screens.json").read_text())
    require(result == expected, "Complete nine-screen certificate changed")
    return result, replacement


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", choices=("original", "cached", "incremental"),
                        default="incremental")
    args = parser.parse_args()
    result, _ = complete(args.engine)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
