"""Replay one complete support-router obligation in a cold source cohort."""

import argparse
import importlib
import json
from pathlib import Path
import sys
from time import monotonic

sys.path.insert(0, str(Path(__file__).resolve().parent))
import router_sources


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", required=True,
                        choices=("metadata", "literal", "forward", "inverse", "failures", "budget", "sources"))
    args = parser.parse_args()
    start = monotonic()
    with router_sources.opened():
        result = getattr(importlib.import_module("check_router"), args.suite)()
    print(json.dumps(dict(suite=args.suite, seconds=round(monotonic()-start, 3), result=result), sort_keys=True))
    print("PASS_PHYSICAL_SUPPORT_ROUTER_" + args.suite.upper(), flush=True)
