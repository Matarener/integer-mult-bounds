"""Alternate complete fresh-process builds; never use time as a replay gate.

Produced by Nick Petalas. Apache-2.0.
"""
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

HERE = Path(__file__).resolve().parent


def source_hashes():
    files = [HERE / "run_builder.py", HERE / "benchmark.py"]
    for directory in ("baseline", "candidate"):
        files.extend(sorted((HERE / directory).glob("*.py")))
    return {str(path.relative_to(HERE)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in files}


def sample(variant):
    start = time.perf_counter()
    completed = subprocess.run(
        [sys.executable, "-I", "-W", "error", "-B",
         str(HERE / "run_builder.py"), variant],
        text=True, capture_output=True, timeout=120, check=True)
    if completed.stderr:
        raise ValueError(completed.stderr)
    result = json.loads(completed.stdout)
    if result["errors"] != 0 or result["nodes"] != 509195:
        raise ValueError("incomplete benchmark workload")
    result["process_seconds"] = time.perf_counter() - start
    return result


def summarize(samples, metric):
    result = {}
    for variant in ("baseline", "candidate"):
        values = [row[metric] for row in samples if row["variant"] == variant]
        result[variant] = dict(median=statistics.median(values),
                               minimum=min(values), maximum=max(values))
    before = result["baseline"]["median"]
    after = result["candidate"]["median"]
    result.update(speedup=before / after, reduction=1 - after / before)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 5 <= args.rounds <= 10:
        parser.error("rounds must be in 5..10")
    if args.output.exists():
        parser.error("output path already exists")
    samples = []
    for _ in range(args.rounds):
        for variant in ("baseline", "candidate"):
            row = sample(variant)
            samples.append(row)
            print(json.dumps(row, sort_keys=True), flush=True)
    if len({row["signature"] for row in samples}) != 1:
        raise ValueError("benchmark structures disagree")
    report = dict(schema_version=1, workload="build(50,3,3,1,common=True)",
                  environment=dict(python=sys.version, executable=sys.executable,
                                   platform=platform.platform(),
                                   cpu_count=os.cpu_count(), load=os.getloadavg()),
                  source_sha256=source_hashes(), samples=samples,
                  errors=sum(row["errors"] for row in samples),
                  construction=summarize(samples, "build_seconds"),
                  complete_process=summarize(samples, "process_seconds"))
    with args.output.open("x") as stream:
        stream.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: report[key] for key in
                     ("construction", "complete_process", "errors")}, sort_keys=True))


if __name__ == "__main__":
    main()
