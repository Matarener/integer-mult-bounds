"""Replay a bounded sparse-batch obligation in one authenticated cold cohort."""

import argparse
import importlib
import json
from pathlib import Path
import sys
from time import monotonic

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sparse_sources


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", required=True,
                        choices=("controls", "mixed", "multiple", "failures", "sources", "budget", "source-check"))
    parser.add_argument("--archive-name", choices=tuple(sparse_sources.PINS))
    parser.add_argument("--archive", type=Path)
    args = parser.parse_args()
    if args.suite == "source-check":
        sparse_sources.require(args.archive_name is not None and args.archive is not None, "explicit source check")
        sparse_sources.authenticate(args.archive_name, args.archive)
        print("PASS_SPARSE_SOURCE_BYTES")
        sys.exit(0)
    sparse_sources.require(args.archive is None and args.archive_name is None, "no replay input override")
    start = monotonic()
    if args.suite in ("sources", "budget"):
        result = importlib.import_module("check_sparse_" + args.suite).run()
    else:
        with sparse_sources.opened():
            if args.suite in ("mixed", "multiple"):
                result = getattr(importlib.import_module("check_sparse_payload"), args.suite)()
            else:
                result = importlib.import_module("check_sparse_" + args.suite).run()
    print(json.dumps({"suite": args.suite, "seconds": round(monotonic()-start, 3), "result": result}, sort_keys=True), flush=True)
    print("PASS_PHYSICAL_SPARSE_" + args.suite.upper(), flush=True)
