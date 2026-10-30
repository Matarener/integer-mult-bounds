# SPDX-License-Identifier: Apache-2.0
"""Replay the new finite certificate; produced by Nick Petalas."""

import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys
import time

from census import run_census, require


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    started = time.monotonic()
    actual = run_census()
    package = Path(__file__).parent
    expected = json.loads((package / "RESULT.json").read_text())
    require(canonical(actual) == canonical(expected), "finite classification mismatch")
    digest = hashlib.sha256(canonical(actual).encode()).hexdigest()
    if args.receipt:
        files = ("census.py", "independent.py", "controls.py", "verify.py", "RESULT.json",
                 "README.md", "TASK.json", "SOURCES.json", "VERIFY.json")
        receipt = {"status": "PASS_BINARY_C5_TOTAL_SEVEN_ORBITS", "result_sha256": digest,
                   "python": sys.version, "platform": platform.platform(),
                   "elapsed_seconds": time.monotonic() - started,
                   "files": {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
                             for name in files}}
        args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    for result in actual["profiles"]:
        print({key: value for key, value in result.items() if key != "orbits"})
    print("PASS_BINARY_C5_TOTAL_SEVEN_ORBITS", digest)


if __name__ == "__main__":
    main()
