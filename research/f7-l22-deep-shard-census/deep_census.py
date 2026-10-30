#!/usr/bin/env python3
"""Run length-22 seven-label split censuses over a prefix-free shard cover.

The engine is the merged union-budget engine of research/f7-l22-union-census,
used unchanged.  The cover is every restricted-growth prefix of length six,
except that 012345 (the only one with six distinct labels, and by far the
heaviest subtree) is replaced by its restricted-growth extensions of length
eight.  Every canonical length-22 word has exactly one prefix in the cover, so
running the engine once per cover prefix covers exactly the tree of one
unsharded run.  Shard node counts are raw per-shard counts: nodes above a
shard's prefix are counted once per descendant shard, so the raw sum is
compared only with sums over the same cover.

Engine outputs are kept in --work.  A shard whose complete engine output is
already there is reused, so an interrupted run resumes without recomputation.
"""
import argparse
import concurrent.futures
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "research/f7-l22-union-census/engine/union_census.c"
LABELS = 7
LENGTH = 22
DEPTH = 6
EXPANDED = {"012345": 8}


def extensions(prefix, depth, labels=LABELS):
    """Restricted-growth extensions of prefix to the given depth, in order."""
    if len(prefix) == depth:
        return [prefix]
    used = max((int(c) for c in prefix), default=-1) + 1
    out = []
    for label in range(min(used + 1, labels)):
        out += extensions(prefix + str(label), depth, labels)
    return out


def prefixes(depth=DEPTH, labels=LABELS):
    """All restricted-growth prefixes of the given depth, in order."""
    return extensions("", depth, labels)


def cover():
    """The prefix-free shard cover used by RESULT.json."""
    out = []
    for key in prefixes():
        out += extensions(key, EXPANDED[key]) if key in EXPANDED else [key]
    return out


def engine_sha256():
    return hashlib.sha256(ENGINE.read_bytes()).hexdigest()


def build(directory):
    binary = Path(directory) / "union_census_l22"
    cmd = ["cc", "-O3", "-Wall", "-Wextra", "-Werror", "-std=c11",
           f"-DN={LABELS}", f"-DL={LENGTH}", str(ENGINE), "-o", str(binary)]
    subprocess.run(cmd, check=True)
    return binary


def read_shard(split, shard, directory):
    """Parse one engine output; None if absent or incomplete."""
    hits = Path(directory) / f"hits_{split[0]}_{split[1]}_{shard}.txt"
    data = Path(directory) / f"result_{split[0]}_{split[1]}_{shard}.json"
    if not (hits.exists() and data.exists()) or data.stat().st_size == 0:
        return None
    payload = json.loads(data.read_text())
    total = payload["total"][0]
    if (payload["split"] != list(split) or payload["requested_shards"] != 1
            or payload["shards"][0]["prefix"] != shard):
        raise RuntimeError(f"{data} does not belong to shard {shard}")
    return {"prefix": shard, "complete": payload["complete"] is True,
            "nodes": total["nodes"], "hits": total["hits"],
            "candidate_restored_leaves": total["candidate_restored_leaves"],
            "hit_words": hits.read_text().split()}


def run_shard(binary, split, shard, directory):
    row = read_shard(split, shard, directory)
    if row is not None and row["complete"]:
        return row
    hits = Path(directory) / f"hits_{split[0]}_{split[1]}_{shard}.txt"
    data = Path(directory) / f"result_{split[0]}_{split[1]}_{shard}.json"
    for path in (hits, data):
        if path.exists():
            path.unlink()
    proc = subprocess.run([str(binary), f"{split[0]},{split[1]}", "--hits",
                           str(hits), "--json", str(data), shard],
                          capture_output=True, text=True)
    row = read_shard(split, shard, directory)
    if row is None:
        raise RuntimeError(f"shard {shard} wrote no output: {proc.stderr[-500:]}")
    row["complete"] = row["complete"] and proc.returncode == 0
    return row


def run_split(binary, split, workers, directory, shards):
    # Heaviest subtrees first: more distinct labels in the prefix run longer.
    order = sorted(shards, key=lambda k: -len(set(k)))
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        rows = dict(zip(order, pool.map(
            lambda s: run_shard(binary, split, s, directory), order)))
    return [rows[k] for k in shards]


def summarize(split, rows):
    return {"split": list(split), "shards": len(rows),
            "complete": all(r["complete"] for r in rows),
            "nodes": sum(r["nodes"] for r in rows),
            "hits": sum(r["hits"] for r in rows),
            "hit_words": sorted(w for r in rows for w in r["hit_words"]),
            "per_shard_nodes": {r["prefix"]: r["nodes"] for r in rows}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", action="append", required=True,
                        help="S,T; may repeat")
    parser.add_argument("--workers", type=int, default=os.cpu_count() or 4)
    parser.add_argument("--work", type=Path,
                        help="directory for engine outputs (enables resume)")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    keys = cover()
    out = {"engine": str(ENGINE.relative_to(ROOT)),
           "engine_sha256": engine_sha256(), "base_depth": DEPTH,
           "expanded": EXPANDED, "cover_size": len(keys), "splits": []}
    with tempfile.TemporaryDirectory(prefix="l22deep-") as tmp:
        work = args.work or Path(tmp)
        work.mkdir(parents=True, exist_ok=True)
        binary = build(tmp)
        for text in args.split:
            split = tuple(int(x) for x in text.split(","))
            summary = summarize(split, run_split(binary, split, args.workers,
                                                 work, keys))
            out["splits"].append(summary)
            print(json.dumps({k: summary[k] for k in
                              ("split", "shards", "complete", "nodes", "hits")}),
                  flush=True)
    text = json.dumps(out, indent=1, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text)
    ok = all(s["complete"] and s["hits"] == 0 for s in out["splits"])
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
