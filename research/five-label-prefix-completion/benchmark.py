#!/usr/bin/env python3
"""Fresh-process complete small-domain traversal timings; no hosted CI claim.
Prepared for SHIN09-git with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time
from types import ModuleType

HERE = Path(__file__).resolve().parent
MODES = ("none", "cheap", "cap11", "one_vertex", "two_vertex", "one_without_cap", "two_without_cap")


def core():
    path = HERE / "bounds.py"
    module = ModuleType("bounds")
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def worker(mode):
    started = time.perf_counter_ns()
    counts, _, hits = core().search(mode)
    digest = sha256("".join("".join(map(str, w)) + "\n" for w in hits).encode()).hexdigest()
    return {"mode": mode, "counts": counts, "universal_sha256": digest,
            "worker_ns": time.perf_counter_ns() - started}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", choices=MODES)
    parser.add_argument("--pairs", type=int, default=21)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.worker:
        print(json.dumps(worker(args.worker), sort_keys=True))
        return
    if not 1 <= args.pairs <= 100 or args.output is None:
        parser.error("provide --output and 1 <= --pairs <= 100")
    if args.output.exists():
        parser.error("output already exists")
    expected = json.loads((HERE / "RESULT.json").read_bytes())["oracle"]["universal_sha256"]
    pins = {name: sha256((HERE / name).read_bytes()).hexdigest() for name in ("bounds.py", "benchmark.py")}
    started = datetime.now(timezone.utc).isoformat()
    rows = []
    env = dict(os.environ)
    env.pop("PYTHONOPTIMIZE", None)
    for pair in range(args.pairs):
        order = list(MODES[pair % len(MODES):] + MODES[:pair % len(MODES)])
        if pair % 2:
            order.reverse()
        for position, mode in enumerate(order):
            before = time.perf_counter_ns()
            run = subprocess.run([sys.executable, "-I", "-B", str(Path(__file__).resolve()),
                                  "--worker", mode], cwd=HERE, env=env, capture_output=True,
                                 check=True, timeout=30)
            elapsed = time.perf_counter_ns() - before
            result = json.loads(run.stdout)
            if result["universal_sha256"] != expected or result["counts"]["universal"] != 828:
                raise ValueError("complete witness set mismatch")
            rows.append({"pair": pair, "position": position, "wall_ns": elapsed, **result})
    if pins != {name: sha256((HERE / name).read_bytes()).hexdigest() for name in pins}:
        raise ValueError("timed source changed")
    summaries = {}
    for mode in MODES:
        samples = [r["wall_ns"] / 1e9 for r in rows if r["mode"] == mode]
        summaries[mode] = {"median_wall_seconds": statistics.median(samples),
                           "minimum_wall_seconds": min(samples), "maximum_wall_seconds": max(samples)}
    comparisons = {}
    for candidate, baseline in (("cap11", "cheap"), ("one_vertex", "cap11"),
                                ("two_vertex", "one_vertex"), ("two_vertex", "cheap"), ("two_vertex", "none"),
                                ("one_without_cap", "cheap"), ("two_without_cap", "cheap"),
                                ("two_without_cap", "one_without_cap"), ("two_without_cap", "none")):
        ratios = []
        for pair in range(args.pairs):
            block = {r["mode"]: r["wall_ns"] for r in rows if r["pair"] == pair}
            ratios.append(block[candidate] / block[baseline])
        comparisons[candidate + "_over_" + baseline] = {
            "median_paired_ratio": statistics.median(ratios),
            "faster_pairs": sum(x < 1 for x in ratios), "pairs": args.pairs}
    output = {"schema": "five-label-prefix-completion-timing/v1", "started_at": started,
              "finished_at": datetime.now(timezone.utc).isoformat(), "python": sys.version,
              "platform": platform.platform(), "processes": len(rows), "source_sha256": pins,
              "context": "Sequential fresh processes, startup/import/source read/traversal/output included; rotating and reversing order. OS caches not flushed, host contention uncontrolled. Descriptive timings, never acceptance thresholds.",
              "summaries": summaries, "comparisons": comparisons, "rows": rows}
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(output, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"processes": len(rows), "comparisons": comparisons}, indent=2))


if __name__ == "__main__":
    main()

