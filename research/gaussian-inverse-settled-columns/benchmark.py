"""Alternate complete cold commands; timings are evidence, not CI thresholds."""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent


def measure(engine, fixture):
    command = [sys.executable, "-I", "-W", "error", "-B", str(HERE / "verify.py"),
               "--workload", "--engine", engine, "--fixture", fixture]
    started = time.perf_counter_ns()
    result = subprocess.run(command, capture_output=True, check=True, timeout=60)
    elapsed = time.perf_counter_ns() - started
    if result.stderr:
        raise ValueError("unexpected benchmark diagnostics")
    output = json.loads(result.stdout)
    if len(output["output"]) != int(fixture[-1]) or output["counts"] != {"get": 0, "set": 0}:
        raise ValueError("incomplete or instrumented benchmark workload")
    return elapsed, sha256(result.stdout).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", choices=("dense3", "dense4"), default="dense4")
    parser.add_argument("--pairs", type=int, choices=range(5, 16), default=9)
    args = parser.parse_args()
    rows = []
    for pair in range(args.pairs):
        order = ("baseline", "candidate") if pair % 2 == 0 else ("candidate", "baseline")
        for engine in order:
            elapsed, digest = measure(engine, args.fixture)
            rows.append({"pair": pair, "engine": engine, "elapsed_ns": elapsed, "stdout_sha256": digest})
    if len({row["stdout_sha256"] for row in rows}) != 1:
        raise ValueError("benchmark output disagreement")
    summary = {}
    for engine in ("baseline", "candidate"):
        samples = [row["elapsed_ns"] for row in rows if row["engine"] == engine]
        summary[engine] = {"median_ns": statistics.median(samples), "min_ns": min(samples),
                           "max_ns": max(samples), "runs": len(samples)}
    paths = sorted(HERE.glob("*.py")) + [HERE / "SOURCES.json"]
    source_hashes = {p.name: sha256(p.read_bytes()).hexdigest() for p in paths}
    print(json.dumps({"fixture": args.fixture, "rows": rows, "summary": summary,
                      "errors": 0, "outputs_equal": True, "python": sys.version,
                      "platform": platform.platform(), "cpu_count": os.cpu_count(),
                      "source_hashes": source_hashes}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
