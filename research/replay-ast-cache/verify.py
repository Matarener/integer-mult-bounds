#!/usr/bin/env python3
"""Cache the coverage producer's stage list by source hash.

The coverage checker parses the producer on every contract read. This
checker times that parse against a hash-keyed reuse of the same stage
list. It does not run the frontier coverage command.
"""

import ast
import hashlib
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_REPLAY_AST_CACHE cached_twice_as_fast=true no_new_kappa"
ITERATIONS = 100
PRODUCER = "research/complex-sw4-frame8/verify.py"


def fail(message):
    raise SystemExit("FAIL_REPLAY_AST_CACHE " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def stage_names(data):
    tree = ast.parse(data)
    calls = [
        node.value
        for node in tree.body
        if isinstance(node, ast.Expr)
        and isinstance(node.value, ast.Call)
        and isinstance(node.value.func, ast.Name)
        and node.value.func.id == "run"
    ]
    return [ast.literal_eval(call.args[0]) for call in calls]


def cached_stages(data, cache):
    digest = hashlib.sha256(data).digest()
    if cache.get("digest") == digest:
        return cache["stages"]
    stages = stage_names(data)
    cache["digest"] = digest
    cache["stages"] = stages
    return stages


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "scripts/verify_replay_coverage.py",
        PRODUCER,
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def evaluate():
    authenticate()
    note = (ROOT / "scripts/verify_replay_coverage.py").read_text(encoding="utf-8")
    require("tree = ast.parse(producer.read_bytes())" in note, "the parse site moved")
    data = (ROOT / PRODUCER).read_bytes()
    fresh = stage_names(data)
    cache = {}
    require(cached_stages(data, cache) == fresh, "the first fill disagreed")
    started = time.perf_counter()
    for _ in range(ITERATIONS):
        require(stage_names(data) == fresh, "a fresh parse moved")
    cold = time.perf_counter() - started
    started = time.perf_counter()
    for _ in range(ITERATIONS):
        require(cached_stages(data, cache) == fresh, "a cache hit moved")
    warm = time.perf_counter() - started
    changed = data + b"\n# changed\n"
    stale = {"digest": b"stale", "stages": ["missing"]}
    recomputed = cached_stages(changed, stale)
    require(recomputed == stage_names(changed), "a changed producer was not reparsed")
    require(stale["stages"] != ["missing"], "the stale list was kept")
    require(warm * 2 < cold, "the cache was not twice as fast")
    return {
        "iterations": ITERATIONS,
        "stage_count": len(fresh),
        "first_stage": fresh[0],
        "last_stage": fresh[-1],
        "cached_twice_as_fast": True,
        "hit_equals_fresh": True,
        "changed_bytes_miss": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
