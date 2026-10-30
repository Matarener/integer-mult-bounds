"""Replay one composed arbitrary-support T74 obligation in a cold cohort."""

import argparse
import importlib
import json
from pathlib import Path
import sys
from time import monotonic

sys.path.insert(0, str(Path(__file__).resolve().parent))
import composed_sources


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", required=True,
                        choices=("sources", "metadata", "direct", "literal", "fast", "failures", "budget"))
    args = parser.parse_args()
    start = monotonic()
    with composed_sources.opened():
        result = getattr(importlib.import_module("check_composed"), args.suite)()
    print(json.dumps(dict(suite=args.suite, seconds=round(monotonic()-start, 3), result=result), sort_keys=True))
    print("PASS_COMPOSED_T74_" + args.suite.upper(), flush=True)
