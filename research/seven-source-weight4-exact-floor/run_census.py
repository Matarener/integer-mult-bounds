#!/usr/bin/env python3
"""Rebuild CENSUS.json from census.c (native; not a registered replay).

usage: python3 run_census.py OUT_DIR [--check]

Compiles census.c into OUT_DIR, runs every census row and writes
OUT_DIR/CENSUS.json.  With --check, also requires it to equal the committed
CENSUS.json.  About 1.5 minutes single-threaded on an Apple M-series laptop.

Nick Petalas, with AI assistance.  Apache-2.0.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# argv tails for census: "n W c_1..c_n" or "lift K W c_1..c_6".
ROWS = [
    "7 4 2 2 2 2 2 2 2",
    "7 4 4 2 2 2 2 2 2",
    "7 4 6 2 2 2 2 2 2",
    "7 4 4 4 2 2 2 2 2",
    "7 3 4 4 2 2 2 2 2",
    "6 4 2 2 2 2 2 2",
    "6 4 4 2 2 2 2 2",
    "lift 4 4 4 4 2 2 2 2",
    "lift 6 4 6 2 2 2 2 2",
]


def main() -> None:
    if len(sys.argv) not in (2, 3) or sys.argv[2:] not in ([], ["--check"]):
        raise SystemExit(__doc__)
    out = Path(sys.argv[1]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    cc = shutil.which("cc")
    if cc is None:
        raise SystemExit("a C compiler named cc is required")
    binary = out / "census"
    subprocess.run([cc, "-O3", "-Wall", "-Wextra", "-Werror", "-o", str(binary),
                    str(HERE / "census.c")], check=True)
    runs = []
    for row in ROWS:
        done = subprocess.run([str(binary), *row.split()], check=True,
                              capture_output=True, text=True)
        runs.append(json.loads(done.stdout))
        print(row, "->", runs[-1]["max_coverage"], flush=True)
    lift22 = next(r for r in runs if r.get("lift_k") == 6)
    record = {
        "schema_version": 1,
        "generator": "research/seven-source-weight4-exact-floor/run_census.py",
        "model": "restored source words; mask covered iff q_a ^ q_b over boundaries 0..L-1",
        "runs": runs,
        "length22_full_cover": lift22["first_lift_at_max"],
    }
    text = json.dumps(record, indent=1) + "\n"
    (out / "CENSUS.json").write_text(text)
    if "--check" in sys.argv:
        if text != (HERE / "CENSUS.json").read_text():
            raise SystemExit("regenerated CENSUS.json differs from the committed record")
        print("CENSUS_JSON_MATCHES_COMMITTED")


if __name__ == "__main__":
    main()
