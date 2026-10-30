#!/usr/bin/env python3
"""Authenticate retained sources and compare the exact bounded join receipt.

Clear1nsight, with substantial OpenAI assistance. Apache-2.0.
No production physical root or whole diagonal pass is executed here.
"""

from hashlib import sha1, sha256
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
INVENTORY_SHA256 = "fc211adace216387ea3e4475d82352c70bf0639dcffd60bfca36908cfd41dea6"


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def unique(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def compare(actual, stored, where="receipt"):
    need(type(actual) is type(stored), "receipt type: " + where)
    if isinstance(actual, dict):
        need(actual.keys() == stored.keys(), "receipt keys: " + where)
        for key in actual:
            compare(actual[key], stored[key], where + "." + key)
    elif isinstance(actual, list):
        need(len(actual) == len(stored), "receipt length: " + where)
        for index, (left, right) in enumerate(zip(actual, stored)):
            compare(left, right, where + "[" + str(index) + "]")
    else:
        need(actual == stored, "receipt value: " + where)


def main():
    raw = (ROOT / "SOURCE_INVENTORY.json").read_bytes()
    need(sha256(raw).hexdigest() == INVENTORY_SHA256, "source inventory hash")
    inventory = json.loads(raw, object_pairs_hook=unique)
    for source in inventory["scientific_sources"]:
        path = ROOT / source["local_path"]
        data = path.read_bytes()
        need(len(data) == source["bytes"], "source byte count: " + source["local_path"])
        need(sha256(data).hexdigest() == source["sha256"], "source SHA256: " + source["local_path"])
        blob = sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()
        need(blob == source["git_blob"], "source Git blob: " + source["local_path"])
    spec = importlib.util.spec_from_file_location("matched_join_audit", ROOT / "check_join.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # The component's public receipt is JSON; its internal tuples serialize
    # as arrays. Normalize that representation while preserving bool/int types.
    actual = json.loads(json.dumps(module.run(), sort_keys=True))
    stored = json.loads((ROOT / "RECEIPT.json").read_bytes(), object_pairs_hook=unique)
    compare(actual, stored)
    print("PASS_TWIDDLE_MATCHED_LAYER: exact source-relative layout/round audit; "
          "50 complete-cube round comparisons and two actual single-packet joins; "
          "no full physical root, full diagonal lifecycle or supplier admission")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        print("FAIL_TWIDDLE_MATCHED_LAYER: " + str(error), file=sys.stderr)
        raise SystemExit(1)
