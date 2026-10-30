#!/usr/bin/env python3
"""Verify the prefix-cover sharded length-22 seven-label split census.

Modes:
  --check-receipt   RESULT.json structure, engine pin, cover partition,
                    totals, and the split-domain closure arithmetic.
  --control         Partition control: on small compiled domains with real
                    universal words, mixed-depth cover sharding reproduces the
                    unsharded engine's hit set exactly on every split.
  --replay S,T[:A:B]  (repeatable)
                    Fresh census of cover entries [A,B) of split (S,T), default
                    the whole cover; per-shard node counts, zero hits and
                    completion must equal RESULT.json.
"""
import argparse
import concurrent.futures
import hashlib
import itertools
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE))
import deep_census  # noqa: E402

PREDECESSOR = ROOT / "research/f7-l22-union-census/RESULT.json"
# The eleven splits (s >= t) admitted at length 22 by the four necessary
# conditions of research/f7-l22-split-domain, before its 17-point import.
DOMAIN = [(11, 11), (11, 10), (11, 9), (10, 10), (11, 8), (10, 9), (11, 7),
          (10, 8), (9, 9), (11, 6), (10, 7)]
SEVENTEEN_POINT = {(11, 6), (10, 7)}


def fail(message):
    raise SystemExit(f"FAIL: {message}")


def pinned_engine_sha256():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    for row in sources["files"]:
        if row["path"] == str(deep_census.ENGINE.relative_to(ROOT)):
            return row["sha256"]
    fail("engine is not pinned in SOURCES.json")


def check_cover(keys, labels):
    """Every restricted-growth word of the cover's maximum depth has exactly
    one prefix in the cover (prefix-free and complete)."""
    depth = max(len(k) for k in keys)
    if len(set(keys)) != len(keys):
        fail("duplicate cover prefix")
    for word in deep_census.extensions("", depth, labels):
        if sum(word.startswith(k) for k in keys) != 1:
            fail(f"cover is not a partition at {word}")


def mixed_cover(labels):
    """Depth-six prefixes with the most-distinct-label prefix expanded to
    depth eight: the same construction as deep_census.cover()."""
    base = deep_census.prefixes(depth=6, labels=labels)
    heavy = max(base, key=lambda k: (len(set(k)), k))
    out = []
    for key in base:
        out += deep_census.extensions(key, 8, labels) if key == heavy else [key]
    return out


def check_receipt():
    result = json.loads((PACKAGE / "RESULT.json").read_text())
    engine_hash = deep_census.engine_sha256()
    if engine_hash != pinned_engine_sha256():
        fail("engine bytes differ from the SOURCES.json pin")
    if result["engine_sha256"] != engine_hash:
        fail("RESULT.json engine hash differs from the engine")
    keys = deep_census.cover()
    check_cover(keys, labels=7)
    for mutant in (keys[:-1], keys + ["0123456"]):
        try:
            check_cover(mutant, labels=7)
        except SystemExit:
            continue
        fail("a mutated cover passed the partition check")
    if len(keys) != 251:
        fail("cover is not the 202 depth-six prefixes plus 49 extensions of 012345")
    if result["cover_size"] != 251 or result["expanded"] != {"012345": 8}:
        fail("receipt cover metadata")
    closed = {}
    for split in result["splits"]:
        s, t = split["split"]
        if list(split["per_shard_nodes"]) != keys:
            fail(f"{s},{t}: shard keys differ from the restricted-growth list")
        if split["shards"] != 251 or not split["complete"]:
            fail(f"{s},{t}: incomplete")
        if split["hits"] != 0 or split["hit_words"]:
            fail(f"{s},{t}: hits recorded")
        if sum(split["per_shard_nodes"].values()) != split["nodes"]:
            fail(f"{s},{t}: node total")
        closed[(s, t)] = split["nodes"]
    predecessor = json.loads(PREDECESSOR.read_text())
    prior_complete = {tuple(p["split"]) for p in predecessor["probes"]
                      if p["complete"] and p["hits"] == 0}
    prior_open = {tuple(p["split"]) for p in predecessor["probes"]
                  if not p["complete"]}
    if prior_open | SEVENTEEN_POINT != set(closed) - prior_complete:
        fail(f"closed splits {sorted(closed)} do not match the predecessor's "
             f"capped splits {sorted(prior_open)}")
    remaining = [d for d in DOMAIN if d not in closed and d not in prior_complete]
    for (s, t), nodes in sorted(closed.items()):
        print(f"split ({s},{t}): 251 shards complete, hits 0, nodes {nodes:,}")
    print(f"length-22 domain splits still open: {remaining}")
    if remaining:
        fail("domain not closed")
    print("PASS_F7_L22_DEEP_SHARD_RECEIPT closed_domain=11_of_11")


def control():
    """Compile small (N,L) engines and compare unsharded and sharded hit sets."""
    total_hits = 0
    rows = 0
    mutations = 0
    with tempfile.TemporaryDirectory(prefix="l22deep-control-") as tmp:
        for n, length in ((4, 8), (4, 10), (5, 12)):
            binary = Path(tmp) / f"engine_{n}_{length}"
            subprocess.run(["cc", "-O3", "-Wall", "-Wextra", "-Werror",
                            "-std=c11", f"-DN={n}", f"-DL={length}",
                            str(deep_census.ENGINE), "-o", str(binary)],
                           check=True)
            keys = mixed_cover(n)
            check_cover(keys, labels=n)
            for s, t in itertools.product(range(1, length // 2 + 1), repeat=2):
                whole = _run(binary, (s, t), [], tmp, f"w{n}{length}")
                with concurrent.futures.ThreadPoolExecutor(8) as pool:
                    parts = list(pool.map(
                        lambda k: _run(binary, (s, t), [k], tmp, f"p{n}{length}"),
                        keys))
                if whole is None:
                    if any(p is not None for p in parts):
                        fail(f"N={n} L={length} ({s},{t}) shard-only output")
                    continue
                if not (whole[0] and all(p[0] for p in parts)):
                    fail(f"N={n} L={length} ({s},{t}) incomplete")
                words = sorted(w for p in parts for w in p[1])
                if sorted(whole[1]) != words:
                    fail(f"N={n} L={length} ({s},{t}) sharded hit set differs")
                # Mutation: omitting any one hit-bearing prefix must be detected.
                for k, p in zip(keys, parts):
                    if p[1]:
                        dropped = sorted(w for q in parts if q is not p for w in q[1])
                        if dropped == sorted(whole[1]):
                            fail("dropped-prefix mutation not detected")
                        mutations += 1
                        break
                total_hits += len(words)
                rows += 1
    if total_hits == 0:
        fail("control has no positive universal words")
    print(f"control: {rows} small splits, {total_hits} universal words, "
          f"sharded hit sets equal unsharded; {mutations} dropped-prefix "
          "mutations detected")
    if mutations == 0:
        fail("no mutation control ran")
    print("PASS_F7_L22_DEEP_SHARD_CONTROL")


_counter = itertools.count()


def _run(binary, split, shards, tmp, tag):
    index = next(_counter)
    hits = Path(tmp) / f"{tag}_{index}.hits"
    data = Path(tmp) / f"{tag}_{index}.json"
    proc = subprocess.run([str(binary), f"{split[0]},{split[1]}", "--hits",
                           str(hits), "--json", str(data), *shards],
                          capture_output=True, text=True)
    if proc.returncode == 1 and not data.exists():
        return None
    payload = json.loads(data.read_text())
    return (payload["complete"] is True and proc.returncode == 0,
            hits.read_text().split())


def replay(text, workers):
    split_text, _, bounds = text.partition(":")
    first, last = (int(x) for x in bounds.split(":")) if bounds else (0, 251)
    s, t = (int(x) for x in split_text.split(","))
    result = json.loads((PACKAGE / "RESULT.json").read_text())
    record = next(r for r in result["splits"] if r["split"] == [s, t])
    keys = deep_census.cover()[first:last]
    if not keys:
        fail("empty prefix range")
    if deep_census.engine_sha256() != pinned_engine_sha256():
        fail("engine bytes differ from the SOURCES.json pin")
    with tempfile.TemporaryDirectory(prefix="l22deep-replay-") as tmp:
        binary = deep_census.build(tmp)
        start = time.monotonic()
        rows = deep_census.run_split(binary, (s, t), workers, tmp, keys)
        elapsed = time.monotonic() - start
    for row in rows:
        if not row["complete"] or row["hits"] or row["hit_words"]:
            fail(f"({s},{t}) shard {row['prefix']} not a complete zero-hit run")
        if row["nodes"] != record["per_shard_nodes"][row["prefix"]]:
            fail(f"({s},{t}) shard {row['prefix']} nodes {row['nodes']} != "
                 f"{record['per_shard_nodes'][row['prefix']]}")
    nodes = sum(r["nodes"] for r in rows)
    print(f"({s},{t}) prefixes [{first},{first + len(keys)}): {len(keys)} "
          f"shards complete, hits 0, nodes {nodes:,} equal RESULT.json "
          f"({elapsed:.1f} s, not compared)")
    print("PASS_F7_L22_DEEP_SHARD_REPLAY")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-receipt", action="store_true")
    parser.add_argument("--control", action="store_true")
    parser.add_argument("--replay", action="append", default=[])
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if args.check_receipt:
        check_receipt()
    if args.control:
        control()
    for text in args.replay:
        replay(text, args.workers)
    if not (args.check_receipt or args.control or args.replay):
        parser.error("choose a mode")


if __name__ == "__main__":
    main()
