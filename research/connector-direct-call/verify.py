#!/usr/bin/env python3
"""Charge one direct product call on a one-by-one dirty connector.

The published alphabet has only B and A. This checker adds one direct call
and prices it at one. It does not import the 945-pairing census.
"""

import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_CONNECTOR_DIRECT_CALL shorter_alphabet_word=false no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_CONNECTOR_DIRECT_CALL " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def apply_call(op, state):
    source, target, connector = state
    if op == "B":
        return (source, target, connector ^ source)
    if op == "A":
        return (source, target ^ connector, connector)
    if op == "D":
        return (source, target ^ source, connector)
    raise ValueError(op)


def realizes(word):
    for state in itertools.product((0, 1), repeat=3):
        current = state
        for op in word:
            current = apply_call(op, current)
        source, target, connector = state
        if current != (source, target ^ source, connector):
            return False
    return True


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {"research/universal-connector-boundary/README.md"}
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def evaluate():
    authenticate()
    note = (ROOT / "research/universal-connector-boundary/README.md").read_text(encoding="utf-8")
    require(
        "overwrites, direct A_i B_j calls, or other data operations in this alphabet." in note,
        "the alphabet sentence moved",
    )
    require(realizes(("B", "A", "B", "A")), "the four-call word missed a dirty state")
    require(realizes(("D",)), "the direct call missed a dirty state")
    shorter = any(
        realizes(word)
        for length in (1, 2, 3)
        for word in itertools.product(("A", "B"), repeat=length)
    )
    require(not shorter, "a shorter alphabet word meets the instance")
    return {
        "sources": 1,
        "outputs": 1,
        "alphabet_calls": 4,
        "direct_calls": 1,
        "direct_price": 1,
        "states_agree": 8,
        "shorter_alphabet_word": False,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
