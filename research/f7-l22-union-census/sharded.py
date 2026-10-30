#!/usr/bin/env python3
"""Run one length-22 split census as disjoint restricted-growth prefix shards.

The corrected census engine accepts explicit prefix shards.  The canonical
words of a split partition by their first four letters, and every such prefix
is itself restricted-growth.  Running the fifteen length-four prefixes in
parallel and summing the shard receipts therefore covers exactly the same
tree as one unsharded run.  The reported node total is the raw sum over the
shards: shared prefix nodes are counted once per descendant shard, so the sum
exceeds an unsharded run by a split-dependent constant.  It is exact and
deterministic for sharded comparisons; do not compare it directly with an
unsharded node count.  Shard node counts, candidate leaves and hits are
otherwise additive; a split is complete only when every shard exits 0 with
complete=true.
"""
import argparse
import concurrent.futures
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SHARD_DEPTH = 4


def prefixes(depth=SHARD_DEPTH, labels=7):
    """All restricted-growth prefixes of the given depth."""
    out = []

    def walk(prefix, used):
        if len(prefix) == depth:
            out.append("".join(map(str, prefix)))
            return
        for label in range(min(used + 1, labels)):
            walk(prefix + [label], max(used, label + 1))

    walk([], 0)
    return out


def run_shard(binary, split, shard, directory, cap=0):
    hits = directory / f"hits_{shard}.txt"
    data = directory / f"result_{shard}.json"
    cmd = [str(binary), f"{split[0]},{split[1]}", "--hits", str(hits),
           "--json", str(data)]
    if cap:
        cmd += ["--cap", str(cap)]
    cmd.append(shard)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    payload = json.loads(data.read_text()) if data.exists() else None
    words = hits.read_text().splitlines() if hits.exists() else []
    return {"shard": shard, "exit": proc.returncode,
            "stderr": proc.stderr[-2000:], "data": payload,
            "words": words}


def run_split(binary, split, workers, directory=None, prefixes_override=None):
    directory = Path(directory or tempfile.mkdtemp(prefix="l22shard-"))
    directory.mkdir(parents=True, exist_ok=True)
    keys = prefixes_override or prefixes()
    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(run_shard, binary, split, key, directory)
                   for key in keys]
        for future in futures:
            rows.append(future.result())
    totals = {"nodes": 0, "candidate_restored_leaves": 0, "hits": 0,
              "even_budget_prunes": 0, "odd_budget_prunes": 0,
              "union_budget_prunes": 0}
    for row in rows:
        if row["data"] is None:
            raise RuntimeError(f"shard {row['shard']} wrote no JSON: {row['stderr']}")
        shard_total = row["data"]["total"][0]
        for key in totals:
            totals[key] += shard_total.get(key, 0)
        if row["words"]:
            raise RuntimeError(f"shard {row['shard']} wrote hit words")
    complete = all(r["exit"] == 0 and r["data"]["complete"] is True
                   for r in rows)
    return {"split": list(split), "shards": len(rows), "complete": complete,
            "aborted": not complete,
            "process_exits": sorted({r["exit"] for r in rows}),
            "hits": totals["hits"], "hit_words": [],
            "totals": totals, "per_shard": rows,
            "node_definition": "sum of per-shard node counts; includes "
                               "duplicated shared prefix nodes, so compare "
                               "with sharded totals only"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", required=True)
    parser.add_argument("--split", required=True)
    parser.add_argument("--workers", type=int, default=os.cpu_count() or 4)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    s, t = (int(x) for x in args.split.split(","))
    result = run_split(Path(args.binary), (s, t), args.workers)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text)
    print(json.dumps({k: result[k] for k in
                      ("split", "shards", "complete", "hits")}, sort_keys=True))
    print("nodes:", result["totals"]["nodes"])
    return 0 if result["complete"] and result["hits"] == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
