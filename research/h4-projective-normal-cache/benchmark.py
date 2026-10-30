"""Alternate complete H4 replay commands; write the timing receipt to stdout.

This contribution was produced by Nick Petalas. Apache-2.0.
"""

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
from statistics import median
import subprocess
import sys
from time import perf_counter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", type=int, choices=range(5, 16), default=5)
    args = parser.parse_args()
    scripts = {"baseline": ROOT / "research/h4-root-linear-copy-floor/verify.py",
               "accelerated": HERE / "replay.py"}
    commands = {name: [sys.executable, "-I", "-W", "error", "-B", str(script)]
                for name, script in scripts.items()}
    samples, expected = [], None
    for pair in range(args.pairs):
        order = ("baseline", "accelerated") if pair % 2 == 0 else ("accelerated", "baseline")
        for name in order:
            start = perf_counter()
            run = subprocess.run(commands[name], cwd=ROOT, capture_output=True,
                                 timeout=60, check=False)
            elapsed = perf_counter() - start
            if run.returncode or run.stderr or len(run.stdout) > 8192:
                raise ValueError("complete benchmark command failed: " + repr(run))
            result = json.loads(run.stdout)
            if result["status"] != "PASS_H4_ROOT_LINEAR_COPY_FLOOR":
                raise ValueError("benchmark work did not complete")
            if expected is None:
                expected = run.stdout
            if run.stdout != expected:
                raise ValueError("complete output changed")
            samples.append({"pair": pair, "side": name, "seconds": elapsed,
                            "exit_code": run.returncode,
                            "stdout_sha256": sha256(run.stdout).hexdigest()})
    summary = {}
    for name in scripts:
        times = [x["seconds"] for x in samples if x["side"] == name]
        summary[name] = {"median_seconds": median(times), "range_seconds": [min(times), max(times)]}
    gain = 1 - summary["accelerated"]["median_seconds"] / summary["baseline"]["median_seconds"]
    print(json.dumps({"status": "PASS_COMPLETE_H4_BENCHMARK", "errors": 0,
                      "python": sys.version, "platform": platform.platform(),
                      "cpu_count": os.cpu_count(), "load_average": os.getloadavg(),
                      "commands": commands, "samples": samples, "summary": summary,
                      "wall_time_reduction": gain,
                      "implementation_sha256": {name: sha256((HERE / name).read_bytes()).hexdigest()
                                                for name in ("accelerator.py", "replay.py", "benchmark.py", "SOURCES.json")},
                      "source_sha256": {n: sha256(p.read_bytes()).hexdigest() for n, p in scripts.items()}},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
