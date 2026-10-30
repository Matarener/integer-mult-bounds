"""Time complete authenticated commands. Produced by Nick Petalas, Apache-2.0."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time


PACKAGE = Path(__file__).resolve().parent


def one(mode, expected):
    command = [sys.executable, "-W", "error", "-B", str(PACKAGE / "run.py")]
    if mode == "baseline":
        command.append("--baseline")
    started = time.perf_counter_ns()
    child = subprocess.run(command, capture_output=True, timeout=300, check=False)
    elapsed = time.perf_counter_ns() - started
    if child.returncode != 0 or child.stderr:
        raise RuntimeError(f"{mode} failed: {child.returncode}, {child.stderr!r}")
    if expected is not None and child.stdout != expected:
        raise RuntimeError("complete command stdout changed")
    if not child.stdout.endswith(b"positive rank-one frames\n"):
        raise RuntimeError("complete command did not finish")
    return ({"mode": mode, "elapsed_ns": elapsed, "returncode": child.returncode,
             "stdout_bytes": len(child.stdout), "stderr_bytes": len(child.stderr),
             "stdout_sha256": hashlib.sha256(child.stdout).hexdigest()}, child.stdout)


def benchmark(pairs):
    if not 5 <= pairs <= 9:
        raise ValueError("use five through nine alternating pairs")
    runs = []
    expected = None
    for _ in range(pairs):
        for mode in ("baseline", "accelerated"):
            run, expected = one(mode, expected)
            runs.append(run)
            print(json.dumps(run), flush=True)
    summary = {}
    for mode in ("baseline", "accelerated"):
        values = [r["elapsed_ns"] for r in runs if r["mode"] == mode]
        summary[mode] = {"median_ns": statistics.median(values),
                         "minimum_ns": min(values), "maximum_ns": max(values)}
    before, after = (summary[m]["median_ns"] for m in ("baseline", "accelerated"))
    return {"schema_version": 1, "pairs": pairs, "errors": 0, "runs": runs,
            "summary": summary, "saved_fraction": 1 - after / before,
            "environment": {"python": sys.version, "executable": sys.executable,
                            "platform": platform.platform(), "cores": os.cpu_count(),
                            "load_average_at_finish": list(os.getloadavg())},
            "implementation_sha256": {
                name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest()
                for name in ("fast_support.py", "run.py", "benchmark.py", "SOURCES.json")}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = benchmark(args.pairs)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
