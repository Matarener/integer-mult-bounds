#!/usr/bin/env python3
"""Check the stored restore recipe for target 34.

Event 5807 returns Y34 from the full frame to the rank-8 frame. The native
checker compares the stored recipe with the operator of those physical frames
in that order.
"""

import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
TAIL = ROOT / "research/p104-tail-side-correction-seed749717"
CHANNEL = ROOT / "research/p104-native-channel"
MARKER = "PASS_P104_TAIL_FLAG0_RESTORE target=34 gates=9/21 no_new_kappa"
FULL = [1, 2, 4, 8, 16, 32, 64, 128, 256]
RANK8 = [499, 23, 232, 32, 112, 15, 7, 2]
OLD_PHYSICAL = [256, 128, 64, 32, 16, 8, 4, 2, 1]
NEW_PHYSICAL = [257, 129, 64, 32, 16, 8, 4, 2]
EQUATION = (
    "expected=N.adjoint(N.frame(a,9))+N.frame(b,9);"
    "N.equal(N.recipe(rec['recipe']),expected,'independent native boundary edge')"
)


def fail(message):
    raise SystemExit("FAIL_P104_TAIL_FLAG0_RESTORE " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def checker():
    path = CHANNEL / "vendor/native_verify.py"
    spec = importlib.util.spec_from_file_location("p104_tail_flag0_restore_native", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def same_operator(module, actual, expected):
    return module.tableau(actual) == module.tableau(expected) and module.state(actual) == module.state(expected)


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "research/p104-native-channel/check_native.py",
        "research/p104-native-channel/vendor/native_verify.py",
        "research/p104-tail-side-correction-seed749717/AUGMENTED-WITNESS.json.gz",
        "research/p104-tail-side-correction-seed749717/SIDE-TRANSPORTS.json.gz",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def evaluate():
    authenticate()
    checker_text = (CHANNEL / "check_native.py").read_text(encoding="utf-8")
    native_text = (CHANNEL / "vendor/native_verify.py").read_text(encoding="utf-8")
    require(EQUATION in checker_text, "the channel equation moved")
    require("tableau(actual) == tableau(expected)" in native_text, "the Pauli check moved")
    require("state(actual) == state(expected)" in native_text, "the phase check moved")
    tail = json.loads(gzip.decompress((TAIL / "AUGMENTED-WITNESS.json.gz").read_bytes()))
    compiled = json.loads(gzip.decompress((TAIL / "SIDE-TRANSPORTS.json.gz").read_bytes()))
    require(tail["program"][5807] == ["transport", "Y34", FULL, RANK8, 1], "event 5807 changed")
    rows = [
        row for row in compiled["transports"]
        if row["target"] == 34 and row["direction"] == "restore"
        and row["old_compressed"] == FULL and row["new_compressed"] == RANK8
    ]
    require(len(rows) == 1, "the restore record moved")
    row = rows[0]
    require(row["old_physical"] == OLD_PHYSICAL and row["new_physical"] == NEW_PHYSICAL, "the physical columns moved")
    require(row["recipe"]["rank"] == 1, "the recipe rank moved")
    module = checker()
    actual = module.recipe(row["recipe"])
    expected = module.adjoint(module.frame(tuple(OLD_PHYSICAL), 9)) + module.frame(tuple(NEW_PHYSICAL), 9)
    require(module.tableau(actual) == module.tableau(expected), "the signed Pauli action differs")
    require(module.state(actual) == module.state(expected), "the global phase differs")
    return {
        "target": 34,
        "direction": "restore",
        "event": 5807,
        "rank": 1,
        "old_physical": OLD_PHYSICAL,
        "new_physical": NEW_PHYSICAL,
        "recipe_gates": len(actual),
        "expected_gates": len(expected),
        "signed_pauli_action": True,
        "global_phase": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
