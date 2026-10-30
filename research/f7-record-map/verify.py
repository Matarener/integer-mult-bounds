#!/usr/bin/env python3
"""Check the f(7) record map and the second-engine length-22 census.

Default mode (well under two minutes):

1. Every live input matches its SHA256 pin in SOURCES.json.
2. Every quoted scope sentence in RESULT.json's record map occurs in the
   pinned README it is attributed to (whitespace-normalized), so the map
   fails closed if a cited record changes. This grounds the quotes only; the
   map's summaries around them are prose for a reviewer to check.
3. The length-24 witness is restored, uses all seven labels and is universal
   (P + P = F2^7); a direct XOR check, not a census.
4. The #4221 receipt summary has seven complete zero-hit splits, and with the
   #3731 and #3818 exclusions they are exactly the eleven-split #3708 domain.
   Shard rows are not replayed here; #4221's own verifier does that.
5. Second engine: #3005's census.cpp is rebuilt with exactly one textual
   change (max_length 20 -> 22, plus its error message). Controls: the L=18
   and three L=20 cases equal #3005's FULL.json in every field; a capped
   n=6, L=22 run finds hits and each hit is checked by direct XOR coverage;
   a capped n=7 run exits 2 with complete=false. Then the cheap n=7, L=22
   splits are replayed and must equal RESULT.json in every field.

--full replays every n=7, L=22 split that RESULT.json records as complete;
splits recorded as unfinished are not excluded and are not run. --splits
replays named splits and fails if one has no complete receipt. Wall times
are in RESULT.json (timing_local_only). Requires a C++20 compiler.

JosieElliston, Claude Opus 5.5 session. Apache-2.0.
"""

import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_F7_RECORD_MAP"
ENGINE = "research/f7-union-support-audit/census.cpp"
FULL = "research/f7-union-support-audit/FULL.json"
DEEP = "research/f7-l22-deep-shard-census/RESULT.json"
FLAGS = ["-std=c++20", "-O3", "-Wall", "-Wextra", "-Wpedantic", "-Wconversion",
         "-Wsign-conversion", "-Wshadow", "-Werror"]
EDITS = [
    ("constexpr int max_length = 20;", "constexpr int max_length = 22;"),
    ("even 2n<=L<=20", "even 2n<=L<=22"),
]
WITNESS = "010201030102010345464546"
QUICK_L22 = [(11, 6), (10, 7), (11, 7)]
L20_CONTROLS = [(18, 9, 9), (20, 10, 7), (20, 10, 8), (20, 9, 9)]


def fail(message):
    raise SystemExit("FAIL_F7_RECORD_MAP " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    rows = [row for row in sources["files"] if row["usage"] == "input"]
    require(len(rows) >= 20, "too few live inputs")
    for row in rows:
        require(sha256(ROOT / row["path"]) == row["sha256"], "pin mismatch " + row["path"])
    return {row["path"] for row in rows}


def normalized(text):
    return re.sub(r"\s+", " ", text).strip()


def check_map(result, pinned):
    rows = result["record_map"]
    quotes = 0
    for row in rows:
        for source in row["sources"]:
            path = source["path"]
            require(path in pinned, "map cites an unpinned file " + path)
            text = normalized((ROOT / path).read_text(encoding="utf-8"))
            for quote in source["quotes"]:
                require(normalized(quote) in text, f"quote not in {path}: {quote[:60]}")
                quotes += 1
    return len(rows), quotes


def universal(word, n):
    state, prefixes, counts = 0, [], [0] * n
    for ch in word:
        label = int(ch)
        prefixes.append(state)
        state ^= 1 << label
        counts[label] += 1
    restored = state == 0 and all(c > 0 and c % 2 == 0 for c in counts)
    sums = {a ^ b for a in prefixes for b in prefixes}
    return restored, len(sums) == 1 << n, len(set(prefixes))


def check_witness():
    restored, covered, distinct = universal(WITNESS, 7)
    require(len(WITNESS) == 24 and restored and covered, "length-24 witness")
    require(not universal(WITNESS[:-2], 7)[0], "a truncated witness must not be restored")
    # Negative control: drop label 6 entirely; the prefix set loses a coordinate.
    restored, covered, _ = universal(WITNESS.replace("6", ""), 7)
    require(not covered, "a word missing a label must not be universal")
    return distinct


def check_deep_receipt(result):
    deep = json.loads((ROOT / DEEP).read_text(encoding="utf-8"))
    closed = set()
    for row in deep["splits"]:
        require(row["complete"] and row["hits"] == 0 and not row["hit_words"], "deep receipt row")
        closed.add(tuple(row["split"]))
    require(len(closed) == 7, "deep receipt split count")
    domain = {tuple(s) for s in result["l22_domain"]["splits"]}
    earlier = {tuple(s) for s in result["l22_domain"]["excluded_by_3731_3818"]}
    require(len(domain) == 11 and closed | earlier == domain and not closed & earlier,
            "census route does not close the eleven-split domain")
    return sorted(closed)


def build(work):
    source = (ROOT / ENGINE).read_text(encoding="utf-8")
    for old, new in EDITS:
        require(source.count(old) == 1, "engine edit anchor " + old)
        source = source.replace(old, new)
    changed = [i for i, (a, b) in enumerate(zip(
        (ROOT / ENGINE).read_text(encoding="utf-8").splitlines(), source.splitlines())) if a != b]
    require(len(changed) == 2, "engine change is not exactly two lines")
    cpp = work / "census22.cpp"
    cpp.write_text(source, encoding="utf-8")
    binary = work / "census22"
    compiler = os.environ.get("CXX", "c++")
    subprocess.run([compiler, *FLAGS, "-o", str(binary), str(cpp)], check=True)
    return binary, hashlib.sha256(source.encode()).hexdigest()


def run(binary, work, n, length, s, t, cap=0):
    hits = work / f"hits_{n}_{length}_{s}_{t}_{cap}.txt"
    proc = subprocess.run([str(binary), str(n), str(length), str(s), str(t), "1", str(cap),
                           str(hits)], capture_output=True, text=True)
    require(proc.returncode in (0, 2), f"engine error {n},{length},{s},{t}: {proc.stderr}")
    summary = json.loads(proc.stdout)
    words = hits.read_text().split()
    return proc.returncode, summary, words


def controls(binary, work):
    full = {(c["length"], *c["split"]): c for c in
            json.loads((ROOT / FULL).read_text(encoding="utf-8"))["cases"]}
    for key in L20_CONTROLS:
        rc, summary, words = run(binary, work, 7, *key)
        require(rc == 0 and not words and summary == full[key], f"L<=20 control {key}")
    rc, summary, words = run(binary, work, 6, 22, 11, 11, cap=200000)
    require(rc == 2 and not summary["complete"] and summary["hits"] == len(words) > 0,
            "n=6 L=22 positive control")
    for word in words:
        restored, covered, distinct = universal(word, 6)
        require(len(word) == 22 and restored and covered and distinct == 22,
                "positive-control hit is not a simple universal restored word " + word)
    rc, summary, _ = run(binary, work, 7, 22, 10, 7, cap=1000)
    require(rc == 2 and summary["complete"] is False, "cap control must fail closed")
    return len(words)


def replay(binary, work, result, splits, workers):
    recorded = {tuple(r["split"]): r for r in result["second_engine_l22"]["runs"]
                if r.get("complete")}
    todo = list(splits)
    require(todo, "no split selected for replay")
    missing = [s for s in todo if s not in recorded]
    require(not missing, f"no complete RESULT.json receipt for requested split(s) {missing}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        outs = list(pool.map(lambda s: run(binary, work, 7, 22, *s), todo))
    for split, (rc, summary, words) in zip(todo, outs):
        require(rc == 0 and not words and summary == recorded[split],
                f"L=22 replay differs from RESULT.json at {split}")
    return todo


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--splits", default="",
                        help="completed L=22 splits to replay, for example 9:9,10:8")
    args = parser.parse_args()
    pinned = authenticate()
    result = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    rows, quotes = check_map(result, pinned)
    distinct = check_witness()
    closed = check_deep_receipt(result)
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        binary, digest = build(work)
        require(digest == result["second_engine_l22"]["engine_sha256"], "lifted engine digest")
        positive = controls(binary, work)
        if args.full:
            splits = [tuple(r["split"]) for r in result["second_engine_l22"]["runs"]
                      if r.get("complete")]
        elif args.splits:
            splits = [tuple(int(x) for x in item.split(":")) for item in args.splits.split(",")]
        else:
            splits = QUICK_L22
        done = replay(binary, work, result, splits, args.workers)
    print(f"{MARKER} map_rows={rows} quotes={quotes} witness_distinct_prefixes={distinct} "
          f"census_route_closed={len(closed)}+4 positive_hits={positive} "
          f"l22_replayed={len(done)} mode={'full' if args.full else 'splits' if args.splits else 'quick'} no_new_kappa")


if __name__ == "__main__":
    sys.exit(main())
