"""Five alternating fresh-process checkpoint pairs; writes JSON to stdout.

This contribution was produced by Nick Petalas. Apache-2.0.
"""

import argparse
import cProfile
import hashlib
import json
import os
import platform
import resource
import runpy
import statistics
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def context():
    checks = runpy.run_path(str(HERE / "verify.py"))
    pins = checks["authenticate"]()
    word = checks["workload"]()
    original = runpy.run_path(
        str(checks["ROOT"] / "research/p104-helper-subspace-splits/local.py")
    )
    return (
        checks,
        pins,
        word,
        {
            "dense": original["reverse_columns"],
            "packed": checks["P"]["reverse_columns"],
        },
    )


def child(side):
    _, pins, word, functions = context()
    start = time.perf_counter()
    result = functions[side](word)
    elapsed = time.perf_counter() - start
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if platform.system() != "Darwin":
        peak *= 1024
    print(
        json.dumps(
            {
                "side": side,
                "checkpoint_seconds": elapsed,
                "peak_rss_bytes": peak,
                "result": result,
                "events": len(word["program"]),
                "inputs": pins,
                "errors": 0,
            },
            sort_keys=True,
        )
    )


def profiles(functions, word):
    reports = {}
    for side in ("dense", "packed"):
        profiler = cProfile.Profile()
        result = profiler.runcall(functions[side], word)
        rows = []
        for entry in profiler.getstats():
            name = entry.code if isinstance(entry.code, str) else entry.code.co_name
            rows.append(
                {
                    "function": name,
                    "calls": entry.callcount,
                    "self_seconds": entry.inlinetime,
                    "inclusive_seconds": entry.totaltime,
                }
            )
        reports[side] = {
            "result": result,
            "top": sorted(rows, key=lambda x: x["self_seconds"], reverse=True)[:8],
        }
    return reports


def sample(side):
    start = time.perf_counter()
    completed = subprocess.run(
        [
            sys.executable,
            "-I",
            "-W",
            "error",
            "-B",
            str(HERE / "benchmark.py"),
            "--side",
            side,
        ],
        capture_output=True,
        text=True,
        timeout=120,
        check=True,
    )
    wall = time.perf_counter() - start
    if completed.stderr:
        raise ValueError("child diagnostics: " + completed.stderr)
    result = json.loads(completed.stdout)
    result["process_wall_seconds"] = wall
    return result


def summarize(samples):
    summary = {}
    for side in ("dense", "packed"):
        rows = [r for r in samples if r["side"] == side]
        summary[side] = {}
        for key in ("checkpoint_seconds", "process_wall_seconds", "peak_rss_bytes"):
            values = [r[key] for r in rows]
            summary[side][key] = {
                "median": statistics.median(values),
                "min": min(values),
                "max": max(values),
            }
    for key in ("checkpoint_seconds", "process_wall_seconds"):
        summary[key + "_speedup"] = (
            summary["dense"][key]["median"] / summary["packed"][key]["median"]
        )
    return summary


def run():
    checks, pins, word, functions = context()
    before = list(os.getloadavg())
    profiled = profiles(functions, word)
    samples = []
    for _ in range(5):
        for side in ("dense", "packed"):
            samples.append(sample(side))
    expected = samples[0]["result"]
    for row in samples:
        checks["require"](
            row["errors"] == 0 and row["result"] == expected,
            "every sample completed the same checkpoint",
        )
        checks["require"](row["inputs"] == pins, "same exact inputs")
    receipt = {
        "status": "PASS_PACKED_TRANSPOSE_BENCHMARK",
        "errors": 0,
        "pairs": 5,
        "order": "dense,packed repeated five times",
        "python": sys.version,
        "platform": platform.platform(),
        "cpu_count": os.cpu_count(),
        "load_before": before,
        "load_after": list(os.getloadavg()),
        "inputs": pins,
        "samples": samples,
        "summary": summarize(samples),
        "profile": profiled,
        "scope": "complete transpose checkpoint, not the complete supplier replay",
        "code_sha256": {
            name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
            for name in ("packed.py", "verify.py", "benchmark.py", "PROOF.md")
        },
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--side", choices=("dense", "packed"))
    arguments = parser.parse_args()
    if arguments.side:
        child(arguments.side)
    else:
        run()
