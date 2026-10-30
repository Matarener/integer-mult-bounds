#!/usr/bin/env python3
"""Measure complete metadata/pin validation, without running scientific checks.

Produced by Nick Petalas. Apache-2.0.
"""
import argparse
import gc
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time
import tracemalloc

ROOT = Path(__file__).resolve().parents[2]
BASE = "721c03822c421b7f7fcbb2598993b947c4d88419"
PACKAGE = "research/physical-gaussian-core"


def worker(source):
    spec = importlib.util.spec_from_file_location("measured_validator", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    gc.collect()
    tracemalloc.start()
    start = time.perf_counter()
    result = module.validate(ROOT, PACKAGE)
    seconds = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    encoded = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    return {"seconds": seconds, "peak_traced_bytes": peak,
            "result_sha256": hashlib.sha256(encoded).hexdigest()}


def measure(work, pairs):
    work.mkdir(parents=True, exist_ok=True)
    baseline = work / "baseline_research_package.py"
    raw = subprocess.run(["git", "show", BASE + ":scripts/research_package.py"],
                         cwd=ROOT, check=True, capture_output=True, timeout=30).stdout
    baseline.write_bytes(raw)
    candidate = ROOT / "scripts/research_package.py"
    samples = []
    command = [sys.executable, "-I", "-W", "error", "-B", str(Path(__file__).resolve())]
    for pair in range(pairs):
        for side, source in (("baseline", baseline), ("candidate", candidate)):
            completed = subprocess.run(command + ["--worker", str(source)], cwd=ROOT,
                                       check=True, capture_output=True, text=True, timeout=120)
            row = json.loads(completed.stdout)
            samples.append({"pair": pair, "side": side, **row})
    signatures = {row["result_sha256"] for row in samples}
    if len(signatures) != 1:
        raise ValueError("complete validation outputs differ")
    summaries = {}
    for side in ("baseline", "candidate"):
        rows = [row for row in samples if row["side"] == side]
        summaries[side] = {key: {"median": statistics.median(r[key] for r in rows),
                                "min": min(r[key] for r in rows),
                                "max": max(r[key] for r in rows)}
                           for key in ("seconds", "peak_traced_bytes")}
    return {"schema_version": 1, "base_commit": BASE, "package": PACKAGE,
            "python": sys.version, "platform": platform.platform(),
            "load_average": os.getloadavg(), "logical_cpus": os.cpu_count(),
            "baseline_sha256": hashlib.sha256(raw).hexdigest(),
            "candidate_sha256": hashlib.sha256(candidate.read_bytes()).hexdigest(),
            "benchmark_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "failures": 0, "pairs": pairs, "samples": samples, "summary": summaries,
            "scope": "Fresh-process complete metadata/pin validation; warm OS cache; traced Python allocation, not RSS. No scientific verifier."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path)
    parser.add_argument("--pairs", type=int, default=5, choices=range(5, 11))
    parser.add_argument("--worker", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker is not None:
        print(json.dumps(worker(args.worker)))
        return
    if args.work is None or not args.work.is_absolute():
        parser.error("--work must name an external absolute scratch directory")
    if args.work.resolve().is_relative_to(ROOT):
        parser.error("benchmark outputs must stay outside the checkout")
    result = measure(args.work, args.pairs)
    output = args.work / "BENCHMARK.json"
    with output.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
