"""Read-only source-bound verification of the changed physical caller."""

import argparse
from hashlib import sha256
import importlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))


def authenticate():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for row in sources["files"]:
        if row["usage"] == "input":
            path = ROOT / row["path"]
            if not path.is_file() or path.is_symlink() or sha256(path.read_bytes()).hexdigest() != row["sha256"]:
                raise ValueError("pinned input: " + row["path"])


def physical():
    source = ROOT / "research/physical-ring-product"
    sys.path.insert(0, str(source))
    from ring_sources import opened
    with opened():
        # Frozen cohort loaders install their own paths. Keep the new adapter
        # first, followed by the authenticated live product implementation.
        sys.path.insert(0, str(source))
        sys.path.insert(0, str(HERE))
        module = importlib.import_module("physical")
        return module.run()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("algebra", "physical"), required=True)
    args = parser.parse_args()
    authenticate()
    if args.mode == "physical":
        result = physical()
    else:
        from checks import run
        result = run()
    files = {str(path.relative_to(HERE)): sha256(path.read_bytes()).hexdigest()
             for path in sorted(HERE.iterdir()) if path.is_file()}
    print(json.dumps({"status": "PASS_REVERSAL_FREE_CONVOLUTION", "mode": args.mode,
                      "result": result, "package_sha256": files}, sort_keys=True))


if __name__ == "__main__":
    main()
