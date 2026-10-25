#!/usr/bin/env python3
"""Strict source and receipt wrapper for the PR3617 caller corroboration.

Clear1nsight, with substantial OpenAI assistance. Apache-2.0.
The physical diagonal is real; H, rounding, and layout are arithmetic oracles.
"""

from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
INVENTORY_SHA256 = "9e0f618b7207d76f7942e67d5324dc542932d631c741de26b91c47521cdce7df"
LAYER_SHA256 = "33f91624d60be8c7124ecc24be073f8a5a3759b671979b6a17a6e26538f4355e"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    strict = load("strict_matched_layer_receipt", ROOT.parent / "verify.py")
    raw = (ROOT / "SOURCE_INVENTORY.json").read_bytes()
    strict.need(sha256(raw).hexdigest() == INVENTORY_SHA256, "diagonal source inventory hash")
    path = ROOT.parent / "check_join.py"
    strict.need(sha256(path.read_bytes()).hexdigest() == LAYER_SHA256,
                "frozen arithmetic layer hash")
    layer = load("frozen_layer_arithmetic", path)
    join = load("diagonal_caller_corroboration", ROOT / "check_3617_join.py")
    actual = json.loads(json.dumps(join.run(layer), sort_keys=True))
    stored = json.loads((ROOT / "RECEIPT.json").read_bytes(), object_pairs_hook=strict.unique)
    strict.compare(actual, stored)
    print("PASS_TWIDDLE_DIAGONAL_CALLER: 12 completed arithmetic-H rounds with "
          "384 actual diagonal packets, plus wrong-K control; no physical H/root, "
          "all-round reuse, complete invoice or supplier admission")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        print("FAIL_TWIDDLE_DIAGONAL_CALLER: " + str(error), file=sys.stderr)
        raise SystemExit(1)
