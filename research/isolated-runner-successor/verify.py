#!/usr/bin/env python3
"""The isolated runner on main is outside the accepted successor list.

The checker hashes the runner and reads the published list. It does not edit it.
"""

import ast
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_ISOLATED_RUNNER_SUCCESSOR admitted=false successors=7 no_new_kappa"
RUNNER = "scripts/run_isolated_tests.py"
CHECKER = "scripts/verify_pr_reconciliation.py"


def fail(message):
    raise SystemExit("FAIL_ISOLATED_RUNNER_SUCCESSOR " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    require(set(pinned) == {"certificates/selected-result.json", RUNNER, CHECKER}, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def accepted_entry():
    tree = ast.parse((ROOT / CHECKER).read_text(encoding="utf-8"))
    found = None
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        for key, value in zip(node.keys, node.values):
            if isinstance(key, ast.Constant) and key.value == RUNNER:
                found = value
    require(found is not None, "the runner entry is absent")
    require(isinstance(found, ast.Tuple) and len(found.elts) == 2, "the runner entry moved")
    predecessor, successors = found.elts
    require(isinstance(predecessor, ast.Constant) and isinstance(successors, ast.Tuple), "the runner entry moved")
    require(all(isinstance(item, ast.Constant) and isinstance(item.value, str) for item in successors.elts),
            "a successor is not a digest")
    return predecessor.value, tuple(item.value for item in successors.elts)


def evaluate():
    authenticate()
    selected = json.loads((ROOT / "certificates/selected-result.json").read_text(encoding="utf-8"))
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    current = sha256(ROOT / RUNNER)
    predecessor, successors = accepted_entry()
    require(current != predecessor and current not in successors, "the current runner is already admitted")
    require(len(current) == 64 and len(set(successors)) == len(successors), "the successor digests moved")
    return {
        "current_sha256": current,
        "predecessor_sha256": predecessor,
        "accepted_successors": list(successors),
        "current_admitted": False,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
